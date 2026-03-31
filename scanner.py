from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import List
from PIL import Image
import json
import os

# 1. Визначаємо жорстку схему даних (Data Schema), яку вимагаємо від ШІ
class ScannedItem(BaseModel):
    name: str
    category: str
    quantity: float
    unit: str

class ReceiptResponse(BaseModel):
    items: List[ScannedItem]

# Ініціалізація клієнта
client = genai.Client()

def scan_receipt(image_path: str):
    print(f"📷 Сканування чеку: {image_path}...")
    
    try:
        # Завантажуємо зображення через PIL
        img = Image.open(image_path)
        
        # Твій промпт, перенесений з TSX
        prompt = """
        You are an intelligent kitchen inventory assistant. 
        Analyze the provided receipt image and extract the purchased grocery items.
        Ignore non-food items. Categorize items primarily into 'fridge', 'pantry', or 'freezer'.
        Map names to standard English names.
        
        CRITICAL RULES FOR CATEGORIZATION:
        1. All fresh raw meat (pork, beef, poultry), fresh seafood, and deli meats MUST be categorized as 'fridge' unless explicitly labeled as "frozen" or "ice" on the receipt.
        2. Snacks, dried fish, beer, and dry goods go to 'pantry'.
        """
        
        # Виклик Vision-моделі (використовуємо стабільний 2.0-flash під твій ключ)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[img, prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ReceiptResponse, # Жорстко фіксуємо формат виводу
                temperature=0.1 # Знижуємо креативність для точної екстракції даних
            )
        )
        
        # Результат вже гарантовано буде у форматі JSON
        data = json.loads(response.text)
        return data.get("items", [])
        
    except Exception as e:
        print(f"❌ Помилка сканування: {e}")
        return []

# Блок для тестування файлу окремо
if __name__ == "__main__":
    # Переконайся, що файл receipt.jpg лежить у цій же папці
    items = scan_receipt("receipt.jpg")
    print("\n📦 РОЗПІЗНАНІ ПРОДУКТИ:")
    for item in items:
        print(f"- {item['name']} ({item['quantity']} {item['unit']}) -> [Zone: {item['category']}]")