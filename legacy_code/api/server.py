from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.ai_core import (
    analyze_ingredients,
    suggest_categories,
    suggest_dishes,
    generate_recipe,
    generate_recipe_json
)
from app.ingredients import ingredient_map
from chef_ai.fsm import ChefFSM, ChefTrigger

app = FastAPI(title="Culinary AI Assistant")

chef = ChefFSM(profile="chaotic_genius") # або будь-який інший профіль

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # дозволяємо всі домени
    allow_credentials=True,
    allow_methods=["*"],  # дозволяємо всі методи (POST, GET, OPTIONS...)
    allow_headers=["*"],  # дозволяємо всі заголовки
)

class ChatRequest(BaseModel):
    message: str

def detect_trigger(text: str):
    text = text.lower()

    if any(w in text for w in ["дякую", "спасибі", "вдячний"]):
        return ChefTrigger.RESPECT
    if any(w in text for w in ["вибач", "сорі", "перепрошую"]):
        return ChefTrigger.APOLOGY
    if any(w in text for w in ["ха", "лол", "жарт"]):
        return ChefTrigger.HUMOR
    if any(w in text for w in ["тупий", "дурень", "ідіот"]):
        return ChefTrigger.TOXICITY
    if any(w in text for w in ["інгредієнт", "продукт", "спеція"]):
        return ChefTrigger.INTERESTING_INGREDIENT
    if any(w in text for w in ["рецепт", "приготуй", "як зробити"]):
        return ChefTrigger.COMPLEX_TASK

    return ChefTrigger.SILLY_QUESTION



class IngredientsRequest(BaseModel):
    ingredients: list[str]

class CategoryRequest(BaseModel):
    ingredients: list[str]
    category: str

class DishRequest(BaseModel):
    ingredients: list[str]
    dish: str

class FullFlowRequest(BaseModel):
    ingredients: list[str]

@app.post("/chat")
def chat(req: ChatRequest):
    trigger = detect_trigger(req.message)
    chef.trigger(trigger)
    reply = chef.respond(trigger)
    return {
        "state": chef.state.name,
        "reply": reply
    }

@app.post("/analyze")
def analyze(req: IngredientsRequest):
    result = analyze_ingredients(req.ingredients, ingredient_map)
    return result


@app.post("/categories")
def categories(req: IngredientsRequest):
    result = analyze_ingredients(req.ingredients, ingredient_map)
    cats = suggest_categories(result)
    return {"categories": cats}


@app.post("/dishes")
def dishes(req: CategoryRequest):
    result = analyze_ingredients(req.ingredients, ingredient_map)
    dishes = suggest_dishes(req.category, result["known"])
    return {"dishes": dishes}


@app.post("/recipe")
def recipe(req: DishRequest):
    result = analyze_ingredients(req.ingredients, ingredient_map)
    return generate_recipe_json(req.dish, result["known"])
# generate_recipe друкує, але нам треба повернути JSON
    # тому тут ми зробимо окрему версію, яка повертає дані

# ============================================
#  NEW: Kitchen Chef Endpoint (FSM-based)
# ============================================

class ChefKitchenRequest(BaseModel):
    message: str
    ingredients: list[str] = []

@app.post("/chef")
def chef_kitchen(req: ChefKitchenRequest):
    """
    Ендпоінт для кухонного шефа.
    Приймає повідомлення та інгредієнти.
    Використовує ChefFSM для відповіді.
    """

    # 1. Визначаємо тригер (як у /chat)
    trigger = detect_trigger(req.message)

    # 2. Передаємо тригер FSM
    chef.trigger(trigger)

    # 3. Отримуємо відповідь
    reply = chef.respond(trigger)

    # 4. Повертаємо стан і відповідь
    return {
        "state": chef.state.name,
        "reply": reply
    }
    
@app.post("/full_flow")
def full_flow(req: FullFlowRequest):
    # 1. Аналіз інгредієнтів
    analysis = analyze_ingredients(req.ingredients, ingredient_map)

    # 2. Категорії
    categories = suggest_categories(analysis)

    # 3. Страви (беремо першу категорію для прикладу)
    dishes = []
    if categories:
        dishes = suggest_dishes(categories[0], analysis["known"])

    # 4. Рецепт (беремо першу страву)
    recipe = {}
    if dishes:
        recipe = generate_recipe_json(dishes[0], analysis["known"])

    return {
        "analysis": analysis,
        "categories": categories,
        "dishes": dishes,
        "recipe": recipe
    }