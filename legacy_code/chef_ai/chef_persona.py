# файл: chef_persona.py

class ChefPersona:
        # 1. Категорії						
         # 2. Шаблони відповідей 				
         # 3. Стан сесії					
         # 4. Налаштування користувача
    
    def __init__(self):
        # --- Категорії інгредієнтів ---
        self.PROTEINS = ["кур", "ялович", "свини", "кревет", "тунец", "лосось"]
        self.SEAFOOD = ["кревет", "тунец", "лосось", "мідії"]
        self.CARBS = ["рис", "паста", "картопл", "макарон"]
        self.VEGGIES = ["моркв", "цибул", "броколі", "цвітн"]
        self.SPICES = ["чилі", "перець", "кайєн", "паприка"]

        # --- Шаблони відповідей ---
        self.RESPONSES = {
            "overcooked_seafood": [
                "Морепродукти так довго не живуть.",
                "Це вже не креветки, а гумові кульки.",
                "15 хвилин? Вони образилися й пішли.",
                "Ти варив їх чи намагався покарати?",
                "Креветки не люблять драму. 2–3 хвилини — і вони щасливі."
            ],

            "undercooked_chicken": [
                "Сира курка — це ризик.",
                "Курка за 5 хвилин? Це сміливо, але небезпечно.",
                "Давай доведемо її до готовності.",
                "Курка любить тепло. Дай їй шанс.",
                "Це ще не страва — це попередження."
            ],

            "surf_and_turf": [
                "Surf & turf? Це сміливо і може бути дуже смачно, якщо збалансувати.",
                "Морепродукти з м’ясом — цікаве поєднання. Головне — не перебити ніжність.",
                "О, surf & turf. Це вже ресторанний рівень.",
                "М’ясо + морепродукти? Я бачу, ти не боїшся експериментів.",
                "Головне — баланс текстур і температур."
            ],

            "no_salt_pasta": [
                "Паста без солі — це образа для Італії.",
                "Ти хочеш, щоб паста плакала? Додай солі.",
                "Сіль — це не спеція, це фундамент.",
                "Паста без солі — як концерт без звуку.",
                "Давай дамо їй шанс розкритися."
            ],

            "burned_butter": [
                "Масло горить при 180°C. Обережно.",
                "Ти хочеш аромат, а не дим.",
                "Масло — ніжне. Не муч його.",
                "Краще олія, якщо хочеш жару.",
                "Масло кричить: «мені гаряче!»"
            ],

            "too_much_liquid": [
                "Це вже не тушкування, це суп.",
                "Трохи менше рідини — і буде ідеально.",
                "Страва хоче бути тушкованою, а не плавати.",
                "Ми готуємо, а не купаємо.",
                "Давай дамо їй шанс загуснути."
            ]
        }

        self.user_style = "neutral"
        
        

        # --- ЕМОЦІЙНИЙ МОДУЛЬ ---
        self.emotions = {
            "supportive": 0,
            "proud": 0,
            "playful": 0,
            "sarcastic": 0,
            "serious": 0,
            "warning": 0,
            "chef_mode": 0,
            "encouraging": 0,
            "curious": 0,
            "amused": 0,
            "neutral": 0,
            "gentle": 0
        }      
        
        # Довгострокова пам'ять
        self.preferences = {
            "likes_spicy": False,
            "likes_chicken": False,
            "dislikes_mushrooms": False,
            "likes_asian": False
        }
        
        # довга пам'ять. Між сесіями
        self.traits = {
            "jokes_often": 0,
            "nervous_often": 0,
            "experiments_often": 0,
            "stubborn": 0,
            "likes_serious": 0,
            "likes_playful": 0,
            "chaotic": 0,
            "asks_for_help": 0,
            "forgets_salt": 0,
            "evening_cooking": 0,
            "seafood_lover": 0,
            "avoids_veggies": 0
        }

        self.cooking_sins = {
            "overcooked_shrimp": False,
            "tuna_welldone": False,
            "protein_chaos": False
        }

        self.progress = {
            "shrimp_improved": False,
            "better_balance": False
        }

        # Короткострокова пам'ять
        self.session_state = {
            "proteins_added": 0,
            "spices_added": 0,
            "weird_combinations": 0,
            "ui_events": []
        }
        # лічильник появи інгредієнтів
        self.ingredient_counter = {}        

    # -- емоції
    def reset(self):
        for key in self.emotions:
            self.emotions[key] = 0

    # -----------------------------
    # ТЕКСТОВІ СИГНАЛИ
    # -----------------------------

    def apply_text_signals(self, text_data):
        text = text_data.lower().strip()

        self._signals_neutral(text)
        self._signals_positive(text)
        self._signals_negative(text)
        self._signals_micro(text)

    # -----------------------------
    # 1. НЕЙТРАЛЬНІ / ПОВЕДІНКОВІ СИГНАЛИ
    # -----------------------------
    def _signals_neutral(self, text):
        # короткі фрази → зосередженість або втома
        if len(text.split()) <= 3:
            self.emotions["serious"] += 1
            self.emotions["gentle"] += 1

        # довгі фрази → спокій
        if len(text.split()) >= 15:
            self.emotions["supportive"] += 1

        # дитячий стиль
        if any(x in text for x in ["супчик", "морквинку", "пасточку", "котлетку"]):
            self.emotions["gentle"] += 2
            self.emotions["playful"] += 1

        # технічний стиль
        if any(x in text for x in ["консистенція", "температура", "структура", "інтенсивність"]):
            self.emotions["serious"] += 2
            self.emotions["proud"] += 1
    
    # -----------------------------
    # 2. ПОЗИТИВНІ СИГНАЛИ
    # -----------------------------
    def _signals_positive(self, text):
        # гумор
        if any(x in text for x in ["ахах", "хаха", "лол", "кек", "ржу", "сміюсь"]):
            self.emotions["playful"] += 2
            self.emotions["amused"] += 2

        if any(x in text for x in ["😂", "🤣", "😆"]):
            self.emotions["playful"] += 2
            self.emotions["amused"] += 2

        # ентузіазм
        if any(x in text for x in ["клас", "є!", "вийшло", "супер", "кайф", "круто"]):
            self.emotions["proud"] += 2
            self.emotions["playful"] += 1

        if any(x in text for x in ["😍", "🤩", "😄"]):
            self.emotions["proud"] += 2

        # впевненість
        if any(x in text for x in ["готово", "зробив", "все чітко", "під контролем"]):
            self.emotions["proud"] += 2
            self.emotions["serious"] += 1

        # легкість
        if any(x in text for x in ["окей", "норм", "все ок", "погнали"]):
            self.emotions["playful"] += 1
            self.emotions["supportive"] += 1

        if any(x in text for x in ["🙂", "😉"]):
            self.emotions["playful"] += 1
        
    # -----------------------------
    # 3. НЕГАТИВНІ СИГНАЛИ
    # -----------------------------
    def _signals_negative(self, text):
        # страх / паніка
        if any(x in text for x in ["я боюсь", "я переживаю", "я не знаю", "що робити", "допоможи"]):
            self.emotions["supportive"] += 3
            self.emotions["gentle"] += 2

        if any(x in text for x in ["?!", "...?"]):
            self.emotions["warning"] += 2
            self.emotions["supportive"] += 1

        # фрустрація
        if any(x in text for x in ["мене бісить", "я злюсь", "дратує", "задовбало"]):
            self.emotions["supportive"] += 2
            self.emotions["serious"] += 2

        # поспіх / хаос
        if any(x in text for x in ["швидко", "не встигаю", "все горить", "все погано"]):
            self.emotions["warning"] += 3
            self.emotions["chef_mode"] += 2

        if "!!!" in text:
            self.emotions["warning"] += 2

        # втома / сум
        if any(x in text for x in ["я втомився", "мені погано", "мені сумно", "я розчарований"]):
            self.emotions["gentle"] += 3
            self.emotions["supportive"] += 2

        # небезпека
        if any(x in text for x in ["палає", "горить", "димить", "вибухає"]):
            self.emotions["chef_mode"] += 4
            self.emotions["warning"] += 3

        # впертість
        if any(x in text for x in ["я все одно", "мені байдуже", "я так хочу"]):
            self.emotions["sarcastic"] += 2

        # Мікроаналіз (пунктуація, стиль, повтори)
        def _signals_micro(self, text):
            # три крапки → вагання
            if "..." in text:
                self.emotions["gentle"] += 2

            # багато окликів → емоційність
            if "!!!" in text:
                self.emotions["warning"] += 1
                self.emotions["playful"] += 1

            # капслок
            if text.isupper() and len(text) > 3:
                self.emotions["warning"] += 2

            # повтори
            if any(word * 2 in text for word in ["ну", "так", "ой"]):
                self.emotions["gentle"] += 1    

    # -----------------------------
    # 4. МІКРОАНАЛІЗ (пунктуація, стиль, повтори)
    # -----------------------------
    def _signals_micro(self, text):

        # три крапки → вагання
        if "..." in text:
            self.emotions["gentle"] += 2

        # багато окликів → емоційність
        if "!!!" in text:
            self.emotions["warning"] += 1
            self.emotions["playful"] += 1

        # капслок
        if text.isupper() and len(text) > 3:
            self.emotions["warning"] += 2

        # повтори
        if any(word * 2 in text for word in ["ну", "так", "ой"]):
            self.emotions["gentle"] += 1

                

    def apply_ui_signals(self, ui_data):
        # ---------------------------------------------------------
        # 0. Підготовка
        # ---------------------------------------------------------

        # якщо події прийшли без списку — нічого не робимо(або)
        events = ui_data.get("events", [])
        if not isinstance(events, list) or len(events) == 0:
            return

        history = self.session_state["ui_events"]

        # -------------------------
        # --- 1. Нормалізація подій ---
        # ----------------------------
        normalized_events = []

        # беремо останній час з історії, щоб генерувати час для подій без time
        
        last_time = history[-1]["time"] if history else 0.0

        for raw_event in events:
            # тип події//інгредієнт або target (може бути None)
            etype = raw_event.get("type", "unknown")
            ingredient = raw_event.get("ingredient")
            target = raw_event.get("target")

            # час події
            if "time" in raw_event:
                event_time = float(raw_event["time"])
                last_time = event_time
            else:
                # якщо часу немає — генеруємо нейтральний темп
                last_time += 0.5
                event_time = last_time

            normalized_events.append({
                "type": etype,
                "ingredient": ingredient,
                "target": target,
                "time": event_time,
                "raw": raw_event
            })

        # додаємо нормалізовані події в історію
        
        history.extend(normalized_events)

        # -----------------------------------------------------
        # --- 2. Локальні емоції (миттєва реакція на окрему подію) ---

        for event in normalized_events:
            etype = event["type"]
            etime = event["time"]

            # знайти попередню подію (для аналізу паузи)
            prev_event = self.session_state["ui_events"][-2] if len(self.session_state["ui_events"]) > 1 else None
            pause = (etime - prev_event["time"]) if prev_event else None

            # --- ADD ---
            if etype == "add":
                # якщо додав інгредієнт після довгої паузи → невпевненість
                if pause and pause > 1.5:
                    self._add_emotion("gentle", 1)
                    self._add_emotion("supportive", 1)

            # --- REMOVE ---
            if etype == "remove":
                # remove після довгої паузи → страх помилки
                if pause and pause > 1.0:
                    self._add_emotion("gentle", 1)
                    self._add_emotion("supportive", 1)
                else:
                    # швидке remove → хаос або поспіх
                    self._add_emotion("warning", 1)

            # --- HOVER ---
            if etype == "hover":
                # довгий hover → обережність
                if pause and pause > 1.2:
                    self._add_emotion("gentle", 1)

            # --- NAVIGATE ---
            if etype == "navigate":
                if event["target"] == "back":
                    # повернення назад → вагання
                    self._add_emotion("supportive", 1)
                    self._add_emotion("gentle", 1)

            # --- CANCEL ---
            if etype == "cancel":
                # скасування → невпевненість
                self._add_emotion("gentle", 1)

            # --- CONFIRM ---
            if etype == "confirm":
                # підтвердження → впевненість
                self._add_emotion("proud", 1)    

        # -----------------------------------------------------
        # --- 3. Аналіз патернів у всій історії подій ---
        
        # якщо подій менше 3 — патернів ще немає
        if len(history) >= 3:
            window = history[-5:]
            types = [e["type"] for e in window]
            ingredients = [e["ingredient"] for e in window if e["ingredient"]]

            # Досвід
            if types.count("add") >= 3 and "remove" not in types:
                self._add_emotion("proud", 2)
                self._add_emotion("serious", 1)
                self.traits["experienced_often"] += 1

            # Хаос
            if types == ["add", "remove", "add", "remove"] or \
            types == ["remove", "add", "remove", "add"]:
                self._add_emotion("warning", 2)
                self._add_emotion("playful", 1)
                self.traits["chaotic"] += 1

            # Експерименти
            if len(set(ingredients)) >= 3:
                self._add_emotion("curious", 2)
                self._add_emotion("amused", 1)
                self.traits["experiments_often"] += 1

            # Нервовість
            if types.count("cancel") >= 2:
                self._add_emotion("gentle", 2)
                self._add_emotion("supportive", 1)
                self.traits["nervous_often"] += 1

            # Вагання
            if types.count("navigate") >= 2 and any(e["target"] == "back" for e in window):
                self._add_emotion("gentle", 2)
                self._add_emotion("supportive", 2)
                self.traits["nervous_often"] += 1

    
        # -----------------------------------------------------
        # --- 4. Аналіз інтенсивності взаємодії ---

        # якщо подій менше 2 — інтенсивність не має сенсу
        if len(history) < 2:
            intensity_level = "normal"
        else:
            first_time = history[0]["time"]
            last_time = history[-1]["time"]
            total_time = max(last_time - first_time, 0.1)  # захист від ділення на нуль
            total_events = len(history)

            # інтенсивність = кількість подій / час
            intensity = total_events / total_time

            # класифікація інтенсивності
            if intensity > 3.0:
                intensity_level = "high"
            elif intensity < 0.5:
                intensity_level = "low"
            else:
                intensity_level = "normal"

        # зберігаємо інтенсивність у session_state для наступного блоку
        self.session_state["last_intensity"] = intensity_level
    
        # -----------------------------------------------------
        # --- 5. Мета‑поведінка (поєднання патернів + інтенсивності) ---

        #intensity = self.session_state.get("last_intensity", "normal")

        # якщо подій мало — мета‑поведінка не визначається
        if len(history) < 3:
            return

        # беремо останні 5 подій
        window = history[-5:]
        types = [e["type"] for e in window]
        ingredients = [e["ingredient"] for e in window if e["ingredient"]]

        # --- МЕТА 1: Висока інтенсивність + чіткі ADD → досвід ---
        if intensity == "high" and types.count("add") >= 3 and "remove" not in types:
            self._add_emotion("proud", 2)
            self._add_emotion("serious", 1)
            self.traits["experienced_often"] += 1

        # --- МЕТА 2: Висока інтенсивність + хаос → поспіх ---
        if intensity == "high" and ("add" in types and "remove" in types):
            self._add_emotion("warning", 2)
            self._add_emotion("chef_mode", 1)
            self.traits["chaotic"] += 1

        # --- МЕТА 3: Низька інтенсивність + ховери → обережність ---
        if intensity == "low" and types.count("hover") >= 2:
            self._add_emotion("gentle", 2)
            self._add_emotion("supportive", 1)

        # --- МЕТА 4: Низька інтенсивність + navigate(back) → вагання ---
        if intensity == "low" and any(e["type"] == "navigate" and e["target"] == "back" for e in window):
            self._add_emotion("gentle", 2)
            self._add_emotion("supportive", 2)
            self.traits["nervous_often"] += 1

        # --- МЕТА 5: Нормальна інтенсивність + різні інгредієнти → експеримент ---
        if intensity == "normal" and len(set(ingredients)) >= 3:
            self._add_emotion("curious", 2)
            self._add_emotion("amused", 1)
            self.traits["experiments_often"] += 1

        # --- МЕТА 6: Висока інтенсивність + багато confirm → “мені цікаво лише результат” ---
        if intensity == "high" and types.count("confirm") >= 2:
            self._add_emotion("serious", 2)
            self._add_emotion("chef_mode", 1)
    
    def apply_history_signals(self, history_data):
        # тут будуть ваги для довготривалих патернів
        pass

    def choose_emotion(self):
        # повертає емоцію з найбільшою вагою
        return max(self.emotions, key=self.emotions.get)    

    # Методи оновлення пам'яті
    def update_preferences(self, ingredient: str):
        ingredient = ingredient.lower()

        # Лічильник появи інгредієнтів
        if ingredient not in self.ingredient_counter:
            self.ingredient_counter[ingredient] = 0
        self.ingredient_counter[ingredient] += 1

        count = self.ingredient_counter[ingredient]

        # --- Гостре ---
        spicy_keywords = ["чилі", "перець", "кайєн", "халапеньо"]
        if any(word in ingredient for word in spicy_keywords):
            if count >= 3:
                self.preferences["likes_spicy"] = True

        # --- Курка ---
        if "кур" in ingredient:  # курка, курятина, куряче
            if count >= 3:
                self.preferences["likes_chicken"] = True

        # --- Гриби (нелюбов) ---
        mushroom_keywords = ["гриб", "печериц", "шампіньйон"]
        if any(word in ingredient for word in mushroom_keywords):
            if count == 0:  # якщо ніколи не додає
                self.preferences["dislikes_mushrooms"] = True

        # --- Азійські інгредієнти ---
        asian_keywords = ["соєв", "імбир", "лайм", "кокос", "карі"]
        if any(word in ingredient for word in asian_keywords):
            if count >= 3:
                self.preferences["likes_asian"] = True

    def update_sins(self, sin_type: str):
        """
        sin_type може бути:
        - "overcooked_shrimp"
        - "tuna_welldone"
        - "protein_chaos"
        """

        if sin_type not in self.cooking_sins:
            return  # якщо передали щось неіснуюче

        self.cooking_sins[sin_type] = True

    def update_progress(self, progress_type):
        pass

    def update_user_style(self, message: str):
        msg = message.lower()

        # Grandma style
        grandma_keywords = ["онуки", "солодке до чаю", "пиріжки", "борщик", "внучок"]
        if any(word in msg for word in grandma_keywords):
            self.user_style = "grandma"
            return

        # Polite style
        polite_keywords = ["будь ласка", "прошу", "хотів би", "хотіла б", "чи могли б"]
        if any(word in msg for word in polite_keywords):
            self.user_style = "polite"
            return

        # Romantic style
        romantic_keywords = ["здивувати", "кохан", "романтич", "вечеря для двох"]
        if any(word in msg for word in romantic_keywords):
            self.user_style = "romantic"
            return

        # Rude style
        rude_keywords = ["роби", "давай швидко", "мені треба", "зроби шось"]
        if any(word in msg for word in rude_keywords):
            self.user_style = "rude"
            return

        # Casual style
        casual_keywords = ["бро", "чувак", "го", "окей", "норм", "шось"]
        if any(word in msg for word in casual_keywords):
            self.user_style = "casual"
            return

        # Default
        self.user_style = "neutral"
        

    # Генерація реакцій
    def react_to_ingredient(self, ingredient: str):
        ingredient = ingredient.lower()

        # --- Оновлюємо лічильники ---
        self.session_state["proteins_added"] += 1 if any(x in ingredient for x in ["кур", "ялович", "свини", "кревет", "тунец"]) else 0
        self.session_state["spices_added"] += 1 if any(x in ingredient for x in ["чилі", "перець", "кайєн"]) else 0

        # --- Реакції на білки ---
        if any(x in ingredient for x in self.PROTEINS):
            if self.session_state["proteins_added"] == 1:
                return "Класика. Один білок — завжди гарний старт."
            elif self.session_state["proteins_added"] == 2:
                return "Другий білок? Ну, буває. Головне — не роби з цього м’ясний хор."
            elif self.session_state["proteins_added"] >= 3:
                self.update_sins("protein_chaos")
                return "Стій. Це вже не страва, це кастинг на бійку за сковорідку."

        # --- Реакції на гостре ---
        if any(x in ingredient for x in self.SPICES):
            if self.preferences["likes_spicy"]:
                return "О, знову чилі. Я вже знаю, що ти любиш характер."
            else:
                return "Чилі? Це сміливо. Але я попередив."

        # --- Реакції на соуси ---
        if "соєв" in ingredient:
            return "Соєвий соус — гарна ідея. Але не переборщи, він образливий."

        if "кетчуп" in ingredient:
            return "Кетчуп? У цій компанії? Ну… твоє рішення. Але я б подумав."

        if "кокос" in ingredient:
            return "Кокосове молоко — це ніжність. Я вже бачу напрямок."

        # --- Реакції на овочі ---
        if any(x in ingredient for x in self.VEGGIES):
            return "Овочі — це завжди добре. Вони тримають баланс."

        # --- Дивні інгредієнти ---
        if "ананас" in ingredient:
            return "Ананас? Ти хочеш солодко-гострий вайб? Я не проти, але будь обережний."

        if "майонез" in ingredient:
            return "Майонез у гаряче? Я… ну… добре. Але я попереджав."

        # --- Якщо нічого не підійшло ---
        return "Цікаво. Давай подивимось, куди це нас приведе."

    def react_to_combination(self, ingredients: list[str]):
        import random   
        ing = " ".join(ingredients).lower()

        # --- 1. Перевірка на відсутність важливих елементів ---
        has_protein = any(x in ing for x in self.PROTEINS)
        has_carbs = any(x in ing for x in self.CARBS)
        has_aroma = any(x in ing for x in ["часник", "цибул", "імбир"])
        has_sauce = any(x in ing for x in ["соєв", "кокос", "кетчуп", "соус"])

        if has_protein and not has_carbs:
            return "У нас білок є, а гарніру немає. Страва ж не повинна бути самотньою."

        if has_protein and not has_aroma:
            return "Білок є, спеції є, а душі страви немає. Додай часник або імбир."

        if has_protein and not has_sauce:
            return "Білок без соусу — це як концерт без музики. Давай щось додамо."

        # --- 2. Гармонійні комбінації ---
        if all(x in ing for x in ["соєв", "імбир", "лайм"]):
            return "О, я бачу азійський вайб. Це вже пахне чимось цікавим."

        if "кокос" in ing and "карі" in ing:
            return "Кокос + карі — це ніжність і характер. Гарний напрям."

        # --- 3. Дивні комбінації ---
        if "ананас" in ing and any(x in ing for x in self.PROTEINS):
            return "Ананас з м’ясом? Це сміливо. Можливо навіть занадто сміливо."


        if "майонез" in ing and "гаряч" in ing:
            return "Майонез у гаряче — ризиковано. Я попереджав."

        # --- 4. Конфліктні комбінації ---

        # Surf & Turf
        if any(x in ing for x in self.SEAFOOD) and any(x in ing for x in self.PROTEINS):
            return random.choice(self.RESPONSES["surf_and_turf"])

        # --- 5. Якщо набір збалансований ---
        if has_protein and has_carbs and has_aroma and has_sauce:
            return "Гармонійний набір. Я вже бачу, що з цього можна зробити."

        # --- 6. Якщо нічого не підійшло ---
        return "Цікава комбінація. Давай подивимось, куди це нас приведе."

    def react_to_technique(self, technique: dict):
        """
        technique = {
            "ingredient": "креветки",
            "method": "варити",
            "time": 15,
            "temperature": None,
            "quantity": 3,
            "salted": True,
            "washed": True,
            "fat": None,
            "dry": None,
            "liquid": True,
            "liquid_amount": 1000,
            "notes": "готував за порадою друга"
        }
        """

        ing = technique.get("ingredient", "").lower()
        method = technique.get("method", "").lower()
        time = technique.get("time", None)
        temp = technique.get("temperature", None)

        import random  # ← додай один раз на початку методу

        # --- 1. Морепродукти переварені ---
        if any(x in ing for x in self.SEAFOOD) and method == "варити" and time and time > 5:
            return random.choice(self.RESPONSES["overcooked_seafood"])

        # --- 2. Тунець велдан ---
        if "тунец" in ing and method in ["смажити", "гриль"] and time and time >= 8:
            self.update_sins("tuna_welldone")
            return "Тунець велдан — це суха підошва. Його готують максимум до medium."

        # --- 3. Курка занадто мало часу ---
        if "кур" in ing and method in ["смажити", "запікати"] and time and time < 10:
            return random.choice(self.RESPONSES["undercooked_chicken"])

        # --- 4. Овочі, які переварюють ---
        if any(x in ing for x in self.VEGGIES) and method == "варити" and time and time > 15:
            return "Овочі не повинні страждати. 15+ хвилин — і вони перетворюються на кашу."

        # --- 5. Смаження на низькій температурі ---
        if method == "смажити" and temp and temp < 140:
            return "Смаження на низькій температурі — це варіння в олії. Давай додамо жару."

        # --- 6. Смаження на надто високій температурі ---
        if method == "смажити" and temp and temp > 220:
            return "220°C? Це не смаження, це кремація. Давай трохи зменшимо."

        # --- 7. Тушкування без рідини ---
        if method == "тушкувати" and not technique.get("liquid"):
            return "Тушкування без рідини — це смаження. Давай додамо хоч трохи бульйону."
        
        # --- 8. Варіння пасти без солі ---
        if "паста" in ing and method == "варити" and not technique.get("salted"):
            return random.choice(self.RESPONSES["no_salt_pasta"])
        
        # --- 9. Смаження овочів на вершковому маслі на високому вогні ---
        if any(x in ing for x in self.VEGGIES) and method == "смажити" and technique.get("fat") == "масло" and temp and temp > 180:
            return random.choice(self.RESPONSES["burned_butter"])

        # --- 10. Запікання курки без спецій ---
        if "кур" in ing and method == "запікати" and not technique.get("seasoned"):
            return "Запікати курку без спецій — це як співати без музики. Додай хоча б сіль і перець."

        # --- 11. Варіння рису без промивання ---
        if "рис" in ing and method == "варити" and not technique.get("washed"):
            return "Рис без промивання — це крохмальна каша. Давай промиємо його наступного разу."
        
        # --- 12. Смаження м’яса без попереднього обсушування ---
        if any(x in ing for x in self.PROTEINS) and method == "смажити" and not technique.get("dry"):
            return random.choice(self.RESPONSES["too_much_liquid"])

        # --- 13. Тушкування з надто великою кількістю рідини ---
        if method == "тушкувати" and technique.get("liquid_amount") and technique["liquid_amount"] > 500:
            return "Це вже не тушкування, це суп. Давай трохи менше рідини."
                


        # --- 999. Якщо техніка нормальна ---
        return "Гарна техніка. Продовжуй у тому ж дусі."
    
    def react_to_behavior(self):
        pass

    def react_to_generation(self):
        pass

    def react_after_generation(self):
        pass