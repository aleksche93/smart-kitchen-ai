from .ingredients import ingredient_map, dish_database, recipe_database


def get_ingredient_info(name: str):
    info = ingredient_map.get(name)
    if not info:
        return None

    return {
        "categories": info.get("categories", []),
        "roles": info.get("roles", []),
        "critical": info.get("critical", False),
        "substitutes": info.get("substitutes", []),
        "allow_substitution": info.get("allow_substitution", True),

        # розширені дані
        "flavor_profile": info.get("flavor_profile"),
        "texture": info.get("texture"),
        "techniques": info.get("techniques"),
        "pairs_with": info.get("pairs_with"),
        "boosters": info.get("boosters"),
        "seasonality": info.get("seasonality"),
        "cuisine": info.get("cuisine"),
        "role": info.get("role")  # опціонально
    }


def analyze_ingredients(user_ingredients, ingredient_map):
    analysis = {
        "known": [],
        "unknown": [],
        "known_details": {},
        "categories": list(dish_database.keys()),  # ← винесено сюди
        "roles": set(),
        "critical": [],
        "substitutable": []
    }

    for item in user_ingredients:
        item = item.lower().strip()

        if item in ingredient_map:
            analysis["known"].append(item)

            info = get_ingredient_info(item)
            if info:
                analysis["known_details"][item] = info

                # ролі
                for r in info.get("roles", []):
                    analysis["roles"].add(r)

                # критичність
                if info.get("critical"):
                    analysis["critical"].append(item)

                # заміни
                analysis["known_details"][item]["substitutes"] = info.get("substitutes", [])

        else:
            analysis["unknown"].append(item)

    analysis["roles"] = list(analysis["roles"])
    return analysis


def pretty_print_analysis(analysis):
    print("🧠 Аналіз інгредієнтів:\n__________________________\n")

    print("✅ Відомі інгредієнти:")
    for item in analysis["known"]:
        print("  -", item)

    print("\n❓ Невідомі інгредієнти:")
    for item in analysis["unknown"]:
        print("  -", item)

    print("\n📂 Категорії:")
    for c in analysis["categories"]:
        print("  -", c)

    print("\n🎭 Ролі:")
    for r in analysis["roles"]:
        print("  -", r)

    print("\n⚠️ Критичні інгредієнти:")
    if analysis["critical"]:
        for item in analysis["critical"]:
            print("  -", item)
    else:
        print("  (немає)")

    print("\n🔄 Можна замінити:")
    for item in analysis["substitutable"]:
        print("  -", item)


def suggest_categories(analysis):
    categories = list(analysis["categories"])

    if not categories:
        print("\n🤔 На жаль, я не можу визначити категорії зі знайдених інгредієнтів.")
        return []

    print("\n👨‍🍳 З твоїх інгредієнтів я бачу кілька можливих напрямків:")
    for i, c in enumerate(categories, start=1):
        print(f"  {i}. {c}")

    print("\n🧠 Обери номер категорії, яка тобі цікава.")
    return categories


def suggest_dishes(category, known_ingredients):
    if category not in dish_database:
        print("🤔 У мене поки немає страв у цій категорії.")
        return []

    possible = []

    for dish in dish_database[category]:
        if any(ing in known_ingredients for ing in dish["ingredients"]):
            possible.append(dish["name"])

    return possible


def generate_recipe(dish_name, known_ingredients):
    if dish_name not in recipe_database:
        print("\n🤔 У мене поки немає рецепта для цієї страви.")
        return

    data = recipe_database[dish_name]
    required = data["ingredients"]

    missing = [i for i in required if i not in known_ingredients]
    available = [i for i in required if i in known_ingredients]

    print(f"\n🍽️ Рецепт: {dish_name}\n")

    print("🧾 Необхідні інгредієнти:")
    for i in required:
        mark = "✓" if i in available else "✗"
        print(f"  {mark} {i}")

    if missing:
        print("\n⚠️ У тебе немає:")
        for i in missing:
            print("  -", i)

    print("\n👨‍🍳 Кроки приготування:")
    for step in data["steps"]:
        print("  -", step)

    print("\n✨ Готово! Смачного!")


def generate_recipe_json(dish, known):
    dish_key = dish.lower()

    if dish_key not in recipe_database:
        return {"error": f"Рецепт '{dish}' не знайдено"}

    recipe = recipe_database[dish_key]

    required = recipe["ingredients"]
    available = [i for i in required if i in known]
    missing = [i for i in required if i not in known]

    pair_recommendations = {}

    for ing in available:
        info = ingredient_map.get(ing)
        if not info:
            continue

        pairs_raw = info.get("pairs_with")
        if not pairs_raw:
            continue

        flat_pairs = []

        if isinstance(pairs_raw, dict):
            for group_name, values in pairs_raw.items():
                if group_name == "classic_trios":
                    for trio in values:
                        for p in trio:
                            if p != ing:
                                flat_pairs.append(p)
                else:
                    flat_pairs.extend(values)
        else:
            flat_pairs = list(pairs_raw)

        filtered_pairs = [
            p for p in flat_pairs
            if p != ing
            and p not in required
            and p not in known
            and p != dish_key
        ]

        filtered_pairs = list(dict.fromkeys(filtered_pairs))

        if filtered_pairs:
            pair_recommendations[ing] = filtered_pairs

    return {
        "dish": dish_key,
        "ingredients_required": required,
        "ingredients_available": available,
        "ingredients_missing": missing,
        "steps": recipe["steps"],
        "substitutes": {
            ing: ingredient_map.get(ing, {}).get("substitutes", [])
            for ing in missing
        },
        "pairings": pair_recommendations
    }


