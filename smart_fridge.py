import asyncio
import aiofiles
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Union, Tuple
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from google import genai
from google.genai import types
from scanner import scan_receipt
from core.locales import i18n

# Pydantic Модель для валідації введених продуктів
class ProductValidationModel(BaseModel):
    name: str = Field(..., min_length=1)
    amount: float = Field(..., gt=0)
    days_left: int = Field(..., ge=-3650) # Just to prevent extreme edge cases
    unit: str = Field("pcs")
    category: str = Field("Other")
    
    model_config = ConfigDict(extra="ignore")

# База знань (Flavor Bible) тепер читається динамічно Шефом (get_chef_advice)

TRANSLATIONS: Dict[str, str] = {
    "beef": "Beef",
    "garlic": "Garlic",
    "rosemary": "Rosemary",
    "egg": "Egg",
    "milk": "Milk"
}

class BaseProduct:
    total_items: int = 0

    def __init__(self, name: str, days_left: Optional[int] = None, expiration_date: Optional[str] = None, unit: str = "pcs", amount: float = 1.0, category: str = "Other", history_limit: int = 8, **kwargs: Any) -> None:
        # Pydantic validation
        days_for_validation = int(days_left) if days_left is not None else 0
        ProductValidationModel(name=name, amount=amount, days_left=days_for_validation, unit=unit, category=category)
        
        self.name: str = name
        self.unit: str = unit
        self.amount: float = amount
        self.category: str = category
        self.history_limit: int = history_limit
        self.history: List[str] = []

        self.pairings: List[str] = [] # Legacy field для старої логіки

        if expiration_date:
            self._expiration_date: datetime = datetime.fromisoformat(expiration_date)
        else:
            self._expiration_date = (datetime.now() + timedelta(days=days_for_validation)).replace(hour=23, minute=59, second=59)     
        
        BaseProduct.total_items += 1

    @property
    def expiration_date(self) -> str:
        return self._expiration_date.strftime("%Y-%m-%d")

    async def find_matches(self, available_prducts: List['BaseProduct']) -> List[str]:
        matches: List[str] = []
        for item in available_prducts:
            if item.name.lower() in self.pairings and item.name.lower() != self.name.lower():
                matches.append(item.name)
                matches.append(item.display_name)
        return list(set(matches))
        
    @property
    def display_name(self) -> str:
        return TRANSLATIONS.get(self.name, self.name.capitalize())

    async def add_history(self, event: str) -> None:
        timestamp: str = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.history.append(f"[{timestamp}] {event}")
        if len(self.history) > self.history_limit:
            removed: str = self.history.pop(0)
            print(f"⚠️ Oldest record deleted: {removed}")

    async def reduce_amount(self, amount_to_take: float) -> bool:
        if amount_to_take > self.amount:
            print(f"❌ Not enough {self.name}! Only {self.amount} {self.unit} left.")
            return False
        
        self.amount -= amount_to_take
        await self.add_history(f"Used {amount_to_take} {self.unit}")
        print(f"✅ Taken {amount_to_take} {self.unit} from '{self.name}'. Left: {self.amount:.2f} {self.unit}")
        return True

    async def show_history(self) -> None:
        print(f"📜 Product history for {self.name}:")
        for record in self.history:
            print(record)
                    
    async def get_status(self) -> str:
        days: int = self.days_left

        if days == 1:
            word = i18n.get("fridge.status.days_1", "day")
        elif 2 <= days <= 4:
            word = i18n.get("fridge.status.days_2_4", "days")
        else:
            word = i18n.get("fridge.status.days_many", "days")
        
        warning_msg: str = ""

        if days < 0:
            warning_msg = i18n.get("fridge.warnings.spoiled", " 🤢 SPOILED! DISCARD IMMEDIATELY!")
        elif days == 0:
            warning_msg = i18n.get("fridge.warnings.last_chance", " ⚠️ LAST CHANCE! Cook today.")
        elif days <= 2:
            warning_msg = i18n.get("fridge.warnings.soon", " 🕒 Will spoil soon.")
                
        template = i18n.get("fridge.status.product_info", "Product {name}: {days} {word} left{warning}")
        status: str = template.format(name=self.display_name, days=days, word=word, warning=warning_msg)
        return status

    @property
    def days_left(self) -> int:
        today: datetime = datetime.now()
        remaining: int = (self._expiration_date - today).days
        return max(0, remaining)
    
    def __str__(self) -> str:
        return self.name

    async def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "expiration_date": self._expiration_date.isoformat(),
            "unit": self.unit,
            "amount": self.amount,
            "category": self.category,
            "type": self.__class__.__name__
        }

    @classmethod
    async def from_dict(cls, data: Dict[str, Any]) -> 'BaseProduct':
        product_type: str = data.pop("type", "BaseProduct") 
        all_classes: List[type] = [cls] + cls.__subclasses__()
        target_class: type = next((c for c in all_classes if c.__name__ == product_type), cls)
        return target_class(**data)


class PackagedProduct(BaseProduct):
    def __init__(self, name: str, days_after_opening: Optional[int] = None, expiration_date: Optional[str] = None, is_open: bool = False, opened_date: Optional[str] = None, **kwargs: Any) -> None:
        super().__init__(name=name, expiration_date=expiration_date, **kwargs)

        self.days_after_opening: int = int(days_after_opening) if days_after_opening is not None else 0
        self.is_open: bool = bool(is_open)

        if opened_date:
            self._opened_date: Optional[datetime] = datetime.fromisoformat(opened_date)
        elif self.is_open:
            self._opened_date = datetime.now()
        else:
            self._opened_date = None

    async def open_package(self) -> None:
        if not self.is_open:
            self.is_open = True
            self._opened_date = datetime.now()

            new_exp_date: datetime = self._opened_date + timedelta(days=self.days_after_opening)

            if new_exp_date < self._expiration_date:
                self._expiration_date = new_exp_date.replace(hour=23, minute=59, second=59)
            
            opened_label = i18n.get("fridge.warnings.opened", " (opened)")
            if opened_label not in self.name:
                self.name = f"{self.name}{opened_label}"

            await self.add_history(f"Package opened. New expiration date: {self.expiration_date}")
            print(f"🔓 {self.name}! Expiration in: {self.days_left} days.") 
        else:
            print(f"⚠️ {self.name} was already opened before.")

    async def reduce_amount(self, amount_to_take: float) -> bool:
        if not self.is_open:
            await self.open_package()
        return await super().reduce_amount(amount_to_take)
    
    async def get_status(self) -> str:
        base_info: str = await super().get_status()
        if self.is_open:
            opened_label = i18n.get("fridge.warnings.opened", " (opened)")
            return f"🔓 {base_info}{opened_label}"
        return base_info

    async def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = await super().to_dict()
        data.update({
            "is_open": self.is_open,
            "days_after_opening": self.days_after_opening,
            "opened_date": self._opened_date.isoformat() if self._opened_date else None, 
            "type": self.__class__.__name__
        })
        return data


class PerishableProduct(BaseProduct):
    async def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = await super().to_dict()
        data["type"] = self.__class__.__name__
        return data

    async def get_status(self) -> str:
        status: str = await super().get_status()
        return status


class Fridge:
    def __init__(self, history_limit: int = 20) -> None:
        self.history_limit: int = history_limit
        self.__history: List[str] = []
        self.__items: List[BaseProduct] = []

    async def initialize(self) -> 'Fridge':
        await self.__load_products()
        return self

    @classmethod
    async def create(cls, history_limit: int = 20) -> 'Fridge':
        fridge = cls(history_limit)
        await fridge.initialize()
        return fridge

    async def __load_products(self) -> None:
        try:
            async with aiofiles.open("fridge_items.json", "r", encoding="utf-8") as f:
                content = await f.read()
                saved_data: List[Dict[str, Any]] = json.loads(content)

                for item_data in saved_data:
                    product_type: str = item_data.pop("type", "BaseProduct")
                    
                    if product_type == "PackagedProduct":
                        product: BaseProduct = PackagedProduct(**item_data)
                    elif product_type == "PerishableProduct":
                        product = PerishableProduct(**item_data)
                    else:
                        product = BaseProduct(**item_data)
                    
                    self.__items.append(product)
                
                print(f"✅ Loaded {len(self.__items)} products from history.")
                
        except FileNotFoundError:
            print("ℹ️ Product history not found. Starting with a clean slate.")
    
    async def suggest_pairings(self, product_name: str) -> None:
        target: Optional[BaseProduct] = next((p for p in self.__items if p.name.lower() == product_name.lower()), None)

        if not target:
            print(f"❌ '{product_name}' not found in the fridge.")
            return

        matches: List[str] = await target.find_matches(self.__items)
        if matches:
            print(f"✨ Perfect pairings for '{target.display_name}': {', '.join(matches)}")
        else:
            print(f"😔 No pairings found right now for '{target.display_name}' in the fridge.")

    async def analyze_fridge(self) -> Dict[str, Dict[str, Any]]:
        urgent_items: List[BaseProduct] = await self.get_urgent_list() 
        recommendations: Dict[str, Dict[str, Any]] = {}

        for item in urgent_items:
            pairs: List[str] = await item.find_matches(self.__items) 
            if pairs:
                if item.category not in recommendations:
                    recommendations[item.category] = {}
                recommendations[item.category][item.display_name] = {
                    "days": item.days_left,
                    "unit": item.unit,
                    "pairs": pairs
                }
        return recommendations

    async def show_recommendations(self) -> None:
        data: Dict[str, Dict[str, Any]] = await self.analyze_fridge()
        if not data:
            print("\n✅ All products are perfectly fine.")
            return

        print("\n👨‍🍳 CHEF'S ADVICE:")
        for category, products in data.items():
            print(f"\n--- {category.upper()} ---")
            for product, details in products.items():
                days: int = details["days"]
                pairs: str = ", ".join(details["pairs"])
                print(f"  💡 {product} (left: {days} days): pairs well with {pairs}")   

    async def get_chef_advice(self) -> None:
        print("\n👨‍🍳 CHEF: Analyzing your critical inventory...")
        urgent_items = await self.get_urgent_list()
        
        if not urgent_items:
            print("✨ You are lucky, nothing is spoiling!")
            return

        try:
            async with aiofiles.open("knowledge/flavors.json", "r", encoding="utf-8") as f:
                content = await f.read()
                knowledge_data = json.loads(content)
        except Exception:
            print("⚠️ Chef's knowledge base is unavailable (error reading knowledge/flavors.json).")
            for item in urgent_items:
                print(f"🔥 {item.display_name} is spoiling soon (left {item.days_left} days), but culinary advice is impossible without knowledge base.")
            return

        flavor_map = {item["ingredient"].lower(): item["pairings"] for item in knowledge_data}
        available_pairings_for_items = {}

        for item in urgent_items:
            product_key = item.name.lower()
            if product_key in flavor_map:
                pairings = flavor_map[product_key]
                best_pairs = [
                    p["paired_with"] for p in pairings 
                    if p.get("affinity") in ["classic", "highly recommended"]
                ]
                
                if best_pairs:
                    pairs_str = ", ".join(best_pairs)
                    print(f"🔥 {item.display_name} is spoiling soon! The Chef recommends pairing it with: {pairs_str}")
                    available_pairings_for_items[item.display_name.lower()] = best_pairs
                else:
                    print(f"🔥 {item.display_name} is spoiling soon (left {item.days_left} days) without any special recommendations.")
            else:
                print(f"🔥 {item.display_name} is spoiling soon (left {item.days_left} days), no special Chef advice available.")

        if not available_pairings_for_items:
            return
            
        print("\n" + "="*50)
        target = await async_input("Chef, which product do we save first? (Enter name or press Enter to cancel): ")
        target = target.strip().lower()
        if not target:
            return

        selected_display_name = next((k for k in available_pairings_for_items.keys() if k == target), None)
        
        if selected_display_name:
            recipe = await generate_recipe_from_pairings(selected_display_name.capitalize(), available_pairings_for_items[selected_display_name])
            print("\n" + "="*50)
            print(f"👨‍🍳 RECIPE FROM THE CHEF ({selected_display_name.upper()}):\n")
            print(recipe)
            print("="*50 + "\n")
        else:
            print(f"❌ '{target}' not found among critical products with perfect pairings.")

    async def __add_fridge_log(self, message: str) -> None:
        timestamp: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry: str = f"[{timestamp}] {message}"
        
        self.__history.append(log_entry)
        
        if len(self.__history) > self.history_limit:
            self.__history.pop(0)

    async def __check_warnings(self, new_product_name: str) -> str:
        warnings: List[str] = []
        same_items: List[BaseProduct] = [p for p in self.__items if p.name.lower() == new_product_name.lower()]

        for old_p in same_items:
            if getattr(old_p, 'is_open', False):
                warnings.append(f"an open package of {old_p.name} exists")

            days: int = old_p.days_left
            if days < 0:
                warnings.append(f"an item {old_p.name} is already spoiled! (term {days} days)")
            elif days <= 2:
                warnings.append(f"expiration date of {old_p.name} is ending (left {days} days)")

        if warnings:
            unique_warnings: List[str] = list(set(warnings))
            return "⚠️ Advice: " + "; ".join(unique_warnings)
        return ""
               
    async def add_product(self, product: BaseProduct, silent: bool = False) -> bool:
        if product.days_left < 0:
            if not silent:
                days: int = product.days_left
                print(f"🔮 Attempting to add {product.name}... Something's not fresh =(")
                print(f"⚠️ Rejected: expiration '{days} days' — not suitable for storage.")
            
            await product.add_history(f"Rejected (expiration {product.days_left} days)")
            return False
            
        self.__items.append(product)
        warning: str = await self.__check_warnings(product.name)

        is_open: bool = getattr(product, "is_open", False)
        prefix: str = "🔓 " if is_open else ""
        log_msg: str = f"Added: {prefix}{product.name}. {warning}".strip()

        await self.__add_fridge_log(log_msg)

        if not silent:
            print(f"{prefix}{product.name} added to the fridge. {warning}\n")
            await self.__save_products()
            await self.__save_history()
        return True

    async def add_mulitiply_products(self, products_list: List[BaseProduct]) -> None:
        if not products_list: 
            return

        all_attempt_names: str = ", ".join(set([p.name for p in products_list]))
        print(f"🔮 Attempting to add {all_attempt_names} — {len(products_list)} items...")

        added_items: List[BaseProduct] = []
        rejected_by_days: Dict[int, int] = {} 
        rejected_units: Dict[str, int] = {}
        
        for p in products_list:
            if await self.add_product(p, silent=True):
                added_items.append(p)
            else:
                d: int = p.days_left
                rejected_by_days[d] = rejected_by_days.get(d, 0) + 1
                rejected_units[p.unit] = rejected_units.get(p.unit, 0) + 1

        if rejected_by_days:
            print("⚠️ Rejected:")
            for days, count in rejected_by_days.items():
                print(f" - {count} items : expiration '{days} days' — not suitable for storage.")
        
        if added_items:
            names: str = ", ".join(set([p.name for p in added_items]))
            print(f"📦 Successfully added: {names} — {len(added_items)} items.\n")

        if rejected_units:
            summary: str = ", ".join([f"{count} {unit}" for unit, count in rejected_units.items()])
            print(f"❌ Total spoiled items rejected: {summary}\n")

    async def find_by_category(self, category_name: str) -> List[BaseProduct]:
        results: List[BaseProduct] = [
            item for item in self.__items
            if item.category.lower() == category_name.lower()
        ]
        print(f"🔍 Searching by category '{category_name}': found {len(results)} items.")
        return results

    async def find_by_name(self, search_name: str) -> List[BaseProduct]:
        return [
            item for item in self.__items
            if item.name.lower() == search_name.lower()
        ]

    async def remove_product(self, product_name: str) -> bool:
        for item in self.__items:
            if item.name == product_name:
                await item.add_history("Removed from the fridge")
                self.__items.remove(item)
                await self.__add_fridge_log(f"Removed: {product_name}")
                await self.__save_history()
                await self.__save_products()
                return True  
        print(f"❓ Product {product_name} is not in the fridge, can't take it out.")
        return False
            
    async def has_product(self, product_name: str) -> bool:
        for item in self.__items:
            if item.name == product_name and item.days_left > 0:
                return True     
        return False
        
    async def check_fridge(self) -> None:
        print("_"*66)
        if not self.__items:
            print("📭 The fridge is empty.")
            return

        urgent_items: List[BaseProduct] = [p for p in self.__items if p.days_left <= 2]
                
        if urgent_items:
            print("\n--- FRIDGE AUDIT ---\n")
            print("🔥 CONSUME URGENTLY:")
            grouped: Dict[Tuple[str, str, int], float] = {}
            for p in urgent_items:
                key = (p.name, p.unit, p.days_left)
                grouped[key] = grouped.get(key, 0) + p.amount
                
            for (name, unit, days), total in grouped.items():
                print(f" - {name} ({days} days) — {total} {unit}")

            print("_"*66)
        
        print(f"📦 Total items in fridge: {len(self.__items)}.")

        status_counts: Dict[Tuple[str, str], float] = {}
        for item in self.__items:
            status_str = await item.get_status()
            status = (status_str, item.unit)
            status_counts[status] = status_counts.get(status, 0) + item.amount
        
        print("\n❄️ FRIDGE CONTENTS:")
        for (status_str, unit), count in status_counts.items():
            print(f"- {status_str} | Quantity: {count} {unit}")
        
        print("_"*66)

    async def clear_spoiled(self) -> None:
        fresh_items: List[BaseProduct] = [
            item for item in self.__items 
            if item.days_left > 0
        ]

        spoiled_count: int = len(self.__items) - len(fresh_items)
        self.__items = fresh_items
        if spoiled_count > 0:
            print(f"🧹 Cleanup complete! Discarded spoiled products: {spoiled_count}")
        else:
            print("✨ All clean! No spoiled products found.")

    async def get_urgent_list(self) -> List[BaseProduct]:
        urgent_items: List[BaseProduct] = [
            item for item in self.__items 
            if item.days_left <= 2
        ]
        return urgent_items

    def is_empty(self) -> bool:
        return len(self.__items) == 0

    async def get_statistics(self) -> Dict[Tuple[str, str, bool, str], float]:
        stats: Dict[Tuple[str, str, bool, str], float] = {}
        for item in self.__items:
            status: bool = getattr(item, "is_open", False)
            key = (item.name, item.unit, status, item.category)
            stats[key] = stats.get(key, 0) + item.amount

        print("\n📊 FRIDGE STATISTICS:")
        for (name, unit, is_open, category), count in stats.items():
            prefix: str = "🔓 " if is_open else ""
            log_msg: str = f"{category} | {prefix}{name}: {count} {unit}".strip()
            print(log_msg)

        return stats

    async def get_total_amount(self, product_name: str) -> float:
        total: float = sum(item.amount for item in self.__items if item.name.lower() == product_name.lower())

        sample: Optional[BaseProduct] = next((p for p in self.__items if p.name.lower() == product_name.lower()), None)
        unit: str = sample.unit if sample else ""

        print(f"📊 Total stock of '{product_name}': {total} {unit}")
        return total

    async def use_product(self, product_name: str, amount_to_use: float) -> Optional[str]:
        found_products: List[BaseProduct] = [p for p in self.__items if p.name.lower().startswith(product_name.lower())]

        if not found_products:
            print(f"❌ '{product_name}' not found in the fridge.")
            return None

        total_available: float = sum(p.amount for p in found_products)

        if total_available < amount_to_use:
            print(f"⚠️ Not enough '{product_name}'. Need {amount_to_use}, only have {total_available}.")
            return None

        remaining_to_take: float = amount_to_use
        print(f"🍴 Starting to take {amount_to_use} {found_products[0].unit} of '{product_name}'...")

        for p in found_products:
            if remaining_to_take <= 0:
                break
            
            if p.amount <= remaining_to_take:
                taken: float = p.amount
                remaining_to_take -= taken
                self.__items.remove(p)
                print(f" ✅ Used entirely: {p.name} ({taken} {p.unit})")
            else:
                await p.reduce_amount(remaining_to_take)
                remaining_to_take = 0
        
        left_over: float = sum(p.amount for p in found_products if p in self.__items)
        log_msg: str = f"Used {amount_to_use:.2f} '{product_name}'. Left: {left_over:.2f} {found_products[0].unit}"
        await self.__add_fridge_log(log_msg)
        print(log_msg)
        print(f"✨ Done! You took everything you needed.")
        return log_msg

    async def __save_products(self) -> None:
        data_to_save: List[Dict[str, Any]] = [await p.to_dict() for p in self.__items]
        
        async with aiofiles.open("fridge_items.json", "w", encoding="utf-8") as f:
            content = json.dumps(data_to_save, ensure_ascii=False, indent=4)
            await f.write(content)

    async def __save_history(self) -> None:
        async with aiofiles.open("fridge_history.json", "w", encoding="utf-8") as f:
            content = json.dumps(self.__history, ensure_ascii=False, indent=4)
            await f.write(content)


class Recipe:
    def __init__(self, name: str, ingredients: List[BaseProduct]) -> None:
        self.name: str = name
        self.ingredients: List[BaseProduct] = ingredients 
    
    async def can_cook(self, fridge: Fridge) -> bool:
        print("_"*66)
        if fridge.is_empty():
            print("📭 The fridge is completely empty!")
            return False

        missing_items: List[str] = []
        print("\n--- RECIPE CHECK ---")
        
        for ingredient in self.ingredients:
            if not await fridge.has_product(ingredient.name):
                missing_items.append(ingredient.name)
        
        if not missing_items:
                print(f"\n✅ Bingo! All ingredients for '{self.name}' are available.")
                return True
        else:        
            items_str: str = ", ".join(missing_items)
            print(f"🛒 Oops! For the recipe '{self.name}' you should buy: {items_str}")
            return False
        
    async def cook(self, fridge: Fridge) -> None:
        if await self.can_cook(fridge):
            print(f"👨‍🍳 Cooking {self.name}...")
            for ingredient in self.ingredients:
                await fridge.remove_product(ingredient.name)
            print(f"🍽️ {self.name} is ready!")
        else:
            print(f"🚫 Cannot cook {self.name}. Check your shopping list.")

    @classmethod
    async def print_search_results(cls, results: List[BaseProduct]) -> None:
        if not results:
            print("🔍 Nothing found.")
        else:
            product_name: str = results[0].name
            print(f"🔍 Found {len(results)} items for '{product_name}':")

            for item in results:
                print(await item.get_status())


async def async_input(prompt: str) -> str:
    return await asyncio.to_thread(input, prompt)

# Клієнт автоматично підтягне GEMINI_API_KEY з середовища (env)
try:
    client = genai.Client()
except Exception as e:
    client = None # Запобіжник, щоб імпорт не падав

async def generate_recipe_from_pairings(ingredient: str, pairings: list) -> str:
    prompt = f"You are an Executive Chef. The user has an ingredient expiring soon: {ingredient}. Perfect pairings: {pairings}. Generate ONE very short, precise 15-minute recipe to save this product. Use professional kitchen terminology (mise-en-place, sear, deglaze). No extra fluff."
    
    try:
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"❌ API Error: {e}"

async def get_user_product_input() -> Optional[BaseProduct]:
    print("\n--- 📝 Adding a new product ---")
    
    name_input = await async_input("Name (English): ")
    name = name_input.lower().strip()
    category_input = await async_input("Category (Meat, Veggies, Dairy): ")
    category = category_input.strip()
    
    try:
        days_input = await async_input("Expiration date (days): ")
        days: int = int(days_input)
        amount_input = await async_input("Quantity (numbers): ")
        amount: float = float(amount_input)
    except ValueError:
        print("❌ Error: please enter a numeric value!")
        return None

    unit_input = await async_input("Unit (kg, pcs, l): ")
    unit = unit_input.strip()

    print("\nChoose product type:")
    print("1. Standard (BaseProduct)")
    print("2. Packaged (PackagedProduct)")
    print("3. Perishable (PerishableProduct)")
    
    choice = await async_input("Your choice (1-3): ")

    try:
        if choice == "1":
            return BaseProduct(
                name=name, 
                category=category, 
                days_left=days, 
                amount=amount, 
                unit=unit
            )
            
        elif choice == "2":
            ans_input = await async_input("Is the package already opened? (yes/no): ")
            ans = ans_input.lower().strip()
            is_open_bool: bool = (ans == "yes")
            try:
                days_after_input = await async_input("Expiration days after opening: ")
                days_after: int = int(days_after_input)
            except ValueError:
                print("❌ Error: please enter a numeric value!")
                return None
            return PackagedProduct(
                name=name, 
                category=category, 
                days_left=days, 
                amount=amount, 
                unit=unit, 
                is_open=is_open_bool,
                days_after_opening=days_after
            )
            
        elif choice == "3":
            return PerishableProduct(
                name=name, 
                category=category, 
                days_left=days, 
                amount=amount, 
                unit=unit
            )
            
        else:
            print("❌ Invalid type selection.")
            return None
    except ValidationError as e:
        print(f"❌ Validation error: {e}")
        return None

async def main() -> None:
    my_fridge = await Fridge.create()
    
    while True:
        print("\n--- 🧊 SMART FRIDGE ---")
        print("1. Add product ➕")
        print("2. What's in the fridge? 📋")
        print("3. Chef's Advice 👨‍🍳")
        print("4. Urgent Chef's Advice 👨‍🍳🔥")
        print("5. Scan shopping receipt 📸")
        print("0. Exit 🚪")

        choice = await async_input("\nChoose an action: ")

        if choice == "1":
            new_product = await get_user_product_input()
            if new_product:
                await my_fridge.add_product(new_product)
                
        elif choice == "2":
            await my_fridge.check_fridge()
        elif choice == "3":
            await my_fridge.show_recommendations()
        elif choice == "4":
            await my_fridge.get_chef_advice()
        elif choice == "5":
            img_path = await async_input("Enter path to receipt photo (Enter for 'receipt.jpg'): ")
            if not img_path.strip():
                img_path = "receipt.jpg"
                
            if not os.path.exists(img_path):
                print(f"❌ File '{img_path}' not found.")
            else:
                try:
                    print(f"🔄 Starting AI receipt scan (this might take a few seconds)...")
                    items = await asyncio.to_thread(scan_receipt, img_path)
                    if items:
                        total_items = len(items)
                        added_to_fridge = 0
                        
                        for item in items:
                            try:
                                cat = item.get("category", "Other").lower()
                                p_name = item.get("name", "Unknown")
                                
                                if cat == "fridge":
                                    product = BaseProduct(
                                        name=p_name,
                                        category="fridge",
                                        amount=float(item.get("quantity", 1.0)),
                                        unit=item.get("unit", "pcs"),
                                        days_left=7
                                    )
                                    await my_fridge.add_product(product, silent=True)
                                    print(f"❄️ Added {p_name} to the Fridge.")
                                    added_to_fridge += 1
                                else:
                                    print(f"🗄️ {p_name} sent to {cat} zone (Module in development).")
                                    
                            except Exception as e:
                                print(f"⚠️ Error processing product {item.get('name')}: {e}")
                                
                        print(f"✅ Successfully recognized {total_items} products. Added to fridge: {added_to_fridge}.")
                    else:
                        print("❌ No products found or an error occurred.")
                except Exception as e:
                    print(f"❌ Processing error: {e}")
        elif choice == "0":
            print("👋 See you later!")
            break
        else:
            print("❌ Invalid choice. Try again.")

if __name__ == "__main__":
    asyncio.run(main())
