from app.ai_core import (
    analyze_ingredients,
    pretty_print_analysis,
    suggest_categories,
    suggest_dishes,
    generate_recipe
)
from app.ingredients import ingredient_map

# 🔥 Додаємо pairing-engine
from app.pairing_engine import load_flavors, get_pairings


def main():
    test = ["курка", "лимон", "борошно", "манго"]

    # --- 1. Аналіз інгредієнтів (твоя існуюча логіка)
    result = analyze_ingredients(test, ingredient_map)
    pretty_print_analysis(result)

    # --- 2. Показуємо pairing-engine для кожного відомого інгредієнта
    print("\n=== Рекомендації смакових поєднань ===")
    flavors = load_flavors()

    for ingr in result["known"]:
        info = ingredient_map.get(ingr.lower())
        if info:
            key = info["key"]   # ← ось це головне
            pair = get_pairings(key, flavors)
            if pair:
                print(f"\nІнгредієнт: {pair['label_uk']}")
                print("  Сильні поєднання:")
                for s in pair["strong"]:
                    print("   -", s)

                print("  Хороші поєднання:")
                for g in pair["good"]:
                    print("   -", g)

                print("  Комбінації:")
                for combo in pair["affinities"]:
                    print("   -", ' + '.join(combo))

    # --- 3. Твоя існуюча логіка категорій і страв
    categories = suggest_categories(result)

    if categories:
        choice = input("Введи номер категорії: ").strip()

        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(categories):
                chosen_category = categories[idx]
                dishes = suggest_dishes(chosen_category, result["known"])

                if dishes:
                    dish_choice = input("\nВведи номер страви: ").strip()
                    if dish_choice.isdigit():
                        d_idx = int(dish_choice) - 1
                        if 0 <= d_idx < len(dishes):
                            chosen_dish = dishes[d_idx]
                            generate_recipe(chosen_dish, result["known"])
                        else:
                            print("Неправильний номер страви.")
                    else:
                        print("Потрібно ввести число.")
            else:
                print("Неправильний номер категорії.")
        else:
            print("Потрібно ввести число.")

if __name__ == "__main__":
    main()