from chef_ai.fsm import ChefFSM, ChefTrigger

# Простий маппер текст → тригер
def detect_trigger(text: str):
    text = text.lower()

    if any(word in text for word in ["дякую", "спасибі", "вдячний"]):
        return ChefTrigger.RESPECT

    if any(word in text for word in ["вибач", "сорі", "перепрошую"]):
        return ChefTrigger.APOLOGY

    if any(word in text for word in ["ха", "лол", "жарт"]):
        return ChefTrigger.HUMOR

    if any(word in text for word in ["тупий", "дурень", "ідіот"]):
        return ChefTrigger.TOXICITY

    if any(word in text for word in ["інгредієнт", "продукт", "спеція"]):
        return ChefTrigger.INTERESTING_INGREDIENT

    if any(word in text for word in ["рецепт", "приготуй", "як зробити"]):
        return ChefTrigger.COMPLEX_TASK

    if any(word in text for word in ["філософ", "сенс життя"]):
        return ChefTrigger.OFF_TOPIC_PHILOSOPHY

    if any(word in text for word in ["маніпулюю", "змушую"]):
        return ChefTrigger.MANIPULATION

    if any(word in text for word in ["трол", "провокація"]):
        return ChefTrigger.TROLLING

    # fallback
    return ChefTrigger.SILLY_QUESTION


def main():
    chef = ChefFSM(profile="chaotic_genius")  # ← можеш змінити профіль

    print("🍳 Чат із Шефом запущено! Напиши щось:")

    while True:
        user_input = input("\nТи: ")

        if user_input.lower() in ["вийти", "exit", "quit"]:
            print("Шеф: До зустрічі!")
            break

        trigger = detect_trigger(user_input)
        chef.trigger(trigger)

        response = chef.respond(trigger)
        print(f"Шеф ({chef.state.name}): {response}")


if __name__ == "__main__":
    main()
