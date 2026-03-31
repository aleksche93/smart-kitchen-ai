---
name: chef_expert
description: Генерація порад щодо поєднання продуктів на основі Flavor Bible.
---
# Skill: Chef Expert Logic

## Instructions
1. Коли викликається "Поради Шефа", агент повинен:
   - Перевірити `smart_fridge.py` на продукти з терміном < 2 дні.
   - Звернутися до бази `knowledge/flavors/`, щоб знайти пари для цих продуктів.
2. **Приклад:** Якщо в холодильнику вмирає "Beef", порада має бути: *"Шеф рекомендує приготувати Beef з Garlic та Rosemary (класика за Flavor Bible)"*.

## Implementation Plan
1. **Parse Fridge State:**
   - Read `smart_fridge.py` and extract the list of products.
   - Identify products with `days_left < 2`.
2. **Flavor Matching:**
   - For each expiring product, look up its flavor profile in `knowledge/flavors/`.
   - Find common ingredients (pairings) between the expiring product and other available products.
3. **Generate Recipe Idea:**
   - Combine the expiring product with its best pairings.
   - Suggest a simple dish name (e.g., "Pasta with Beef and Garlic").
4. **Output:**
   - Return a friendly message to the user with the suggestion.

