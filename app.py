import os
import shutil
import tempfile
import asyncio
import json
import aiofiles

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel

# Імортуємо нашу існуючу логіку
from scanner import scan_receipt
from smart_fridge import Fridge, BaseProduct, generate_recipe_from_pairings

app = FastAPI(
    title="Smart Kitchen AI",
    description="Екосистема розумної кухні на базі FastAPI",
    version="0.1"
)

# CORS для підключення будь-яких фронтендів (scanner_app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Глобальний інстанс холодильника
my_fridge = None

@app.on_event("startup")
async def startup_event():
    global my_fridge
    my_fridge = await Fridge.create()
    print("✅ Web API: Fridge initialized.")

@app.get("/")
def read_root():
    return {"message": "Welcome to Smart Kitchen AI Ecosystem API!"}

@app.post("/api/v1/scan-receipt")
async def scan_receipt_api(file: UploadFile = File(...)):
    """
    Приймає зображення чеку, розпізнає продукти через Gemini Vision 
    і автоматично додає 'fridge' елементи у базу.
    """
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        raise HTTPException(status_code=400, detail="Only JPG/PNG images are allowed.")
    
    # Створюємо тимчасовий файл, щоб передати шлях у синхронний сканер
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_file_path = temp_file.name

    try:
        print(f"🔄 Web API: Розпізнавання чеку {file.filename}...")
        # Асинхронний виклик старого синхронного коду сканера, щоб не блокувати Event Loop
        items = await asyncio.to_thread(scan_receipt, temp_file_path)
        
        if not items:
            return {"status": "success", "message": "Сканер не знайшов продуктів на цьому чеку.", "added_to_fridge": 0, "recognized_items": []}

        total_items = len(items)
        added_to_fridge = 0
        added_items_details = []
        routed_items = []
        
        for item in items:
            cat = item.get("category", "Інше").lower()
            p_name = item.get("name", "Unknown")
            
            if cat == "fridge":
                product = BaseProduct(
                    name=p_name,
                    category=item.get("category", "fridge"),
                    amount=float(item.get("quantity", 1.0)),
                    unit=item.get("unit", "шт."),
                    days_left=7
                )
                await my_fridge.add_product(product, silent=True)
                added_to_fridge += 1
                added_items_details.append(p_name)
            else:
                routed_items.append({"name": p_name, "zone": cat, "status": "Module in development"})
                
        return {
            "status": "success", 
            "total_recognized": total_items, 
            "added_to_fridge_count": added_to_fridge,
            "fridge_items_added": added_items_details,
            "other_routed_items": routed_items
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.get("/api/v1/fridge")
async def get_fridge_inventory():
    """Повертає поточний вміст холодильника (всі свіжі продукти) у форматі JSON."""
    if not my_fridge:
        raise HTTPException(status_code=500, detail="Fridge not initialized")
    
    items_data = []
    # Звертаємось до поля _Fridge__items (для швидкої інтеграції, 
    # в ідеалі варто додати метод get_all_items() у Fridge)
    for item in my_fridge._Fridge__items: 
        if item.days_left > 0:
            items_data.append(await item.to_dict())
        
    return {"status": "success", "total_fresh": len(items_data), "inventory": items_data}

class RecipeRequest(BaseModel):
    ingredient: str

@app.post("/api/v1/chef/advice")
async def get_chef_recipe(request: RecipeRequest):
    """
    Генерує рецепт від Шефа для обранного критичного інгредієнта, 
    використовуючи базу поєднань Flavor Bible.
    """
    if not my_fridge:
        raise HTTPException(status_code=500, detail="Fridge not initialized")

    urgent_items = await my_fridge.get_urgent_list()
    target_name = request.ingredient.lower()
    
    # Перевіряємо чи є цей продукт серед тих, що псуються
    has_target = next((item for item in urgent_items if item.name.lower() == target_name), None)
    if not has_target:
        raise HTTPException(
            status_code=400, 
            detail=f"Інгредієнт '{request.ingredient}' не знайдено серед термінових продуктів (<= 2 днів) у холодильнику."
        )

    # Читаємо базу знань
    try:
        async with aiofiles.open("knowledge/flavors.json", "r", encoding="utf-8") as f:
            knowledge_data = json.loads(await f.read())
    except Exception:
        raise HTTPException(status_code=500, detail="Flavor Knowledge DB unavailable (knowledge/flavors.json)")
        
    flavor_map = {item["ingredient"].lower(): item["pairings"] for item in knowledge_data}
    
    if target_name not in flavor_map:
        raise HTTPException(status_code=404, detail=f"Бракує даних про смакові поєднання для: {request.ingredient}")
        
    best_pairs = [
        p["paired_with"] for p in flavor_map[target_name]
        if p.get("affinity") in ["classic", "highly recommended"]
    ]
    
    if not best_pairs:
         raise HTTPException(status_code=404, detail=f"Немає 'classic' поєднань для {request.ingredient}")

    # Викликаємо генеративний ШІ Gemini
    try:
        recipe = await generate_recipe_from_pairings(has_target.display_name.capitalize(), best_pairs)
        return {
            "status": "success",
            "ingredient_to_save": has_target.display_name,
            "days_left": has_target.days_left,
            "suggested_pairings": best_pairs,
            "ai_recipe": recipe
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
