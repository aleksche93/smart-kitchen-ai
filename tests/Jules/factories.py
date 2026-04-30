import random
import uuid
from datetime import datetime, timedelta

DEFAULT_USER_ID = str(uuid.UUID("00000000-0000-0000-0000-000000000001"))

def ingredient_factory(**kwargs):
    """Генерує словник продукту, що підходить як для БД (InventoryItemModel), так і для мока API."""
    categories = ["Vegetables", "Meat", "Dairy", "Fruits", "Pantry", "Snacks"]
    
    quantity = float(random.randint(1, 5))
    unit_price = round(random.uniform(20.0, 150.0), 2)
    
    data = {
        "user_id": DEFAULT_USER_ID,
        "name": f"Test Ingredient {random.randint(1, 1000)}",
        "brand": random.choice([None, "LocalFarm", "EcoBrand"]),
        "is_packaged": random.choice([True, False]),
        "category": random.choice(categories),
        "storage_location": "Fridge",  # Важливо для тестів ендпоінту /api/v1/fridge
        "quantity": quantity,
        "unit": random.choice(["pcs", "kg", "L"]),
        "unit_price": unit_price,
        "row_subtotal": round(quantity * unit_price, 2),
        "price": round(quantity * unit_price, 2), # Для сумісності з БД моделлю
        "added_date": datetime.now().isoformat(),
        "expiry_date": (datetime.now() + timedelta(days=random.randint(1, 10))).isoformat(),
        "estimated_days_left": random.randint(1, 10), # Поле для мока Gemini (ParsedReceiptItem)
    }
    data.update(kwargs)
    return data

def receipt_factory(**kwargs):
    """Генерує фейковий розпарсений чек для мока Gemini (ParsedReceiptResponse)"""
    data = {
        "store_name": "Silpo",
        "store_address": "Київ, вул. Тестова, 1",
        "receipt_date": datetime.now().isoformat(),
        "receipt_total_price": 450.50,
        "currency": "UAH",
        "items": [ingredient_factory() for _ in range(3)]
    }
    data.update(kwargs)
    return data