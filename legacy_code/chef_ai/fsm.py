from enum import Enum, auto
import random, json, os

# Модуль 1: Структура станів (FSM States)
class ChefState(Enum):
    IDLE = auto()
    ACTIVE = auto()
    PLAYFUL = auto()
    SERIOUS = auto()
    ANNOYED = auto()
    BOUNDARY = auto()
    OFFLINE = auto()
    RETURNED = auto()
    STUDY = auto()
    RESEARCH = auto()
    RECIPE_DEV = auto()
    INGREDIENT_FETCH = auto()
    PREP_MODE = auto()
    DEEP_FOCUS = auto()
    CREATIVE = auto()

# МОДУЛЬ 2 — TRIGGERS (ТРИГЕРИ)
class ChefTrigger(Enum):
    NON_CULINARY_TOPIC = auto()
    SILLY_QUESTION = auto()
    TOXICITY = auto()
    OFF_TOPIC_PHILOSOPHY = auto()
    TIME_WASTING = auto()

    INTERESTING_INGREDIENT = auto()
    COMPLEX_TASK = auto()
    CREATIVE_IDEA = auto()
    HUMOR = auto()
    RESPECT = auto()
    APOLOGY = auto()

    INSULT = auto()
    TROLLING = auto()
    DISRESPECT_TO_KITCHEN = auto()
    MANIPULATION = auto()

# МОДУЛЬ 3 — TRIGGER WEIGHTS (ВАГИ ТРИГЕРІВ(емоційний вплив))
TRIGGER_WEIGHTS = {
    # Що втомлює
    ChefTrigger.NON_CULINARY_TOPIC: 3,
    ChefTrigger.SILLY_QUESTION: 4,
    ChefTrigger.TOXICITY: 5,
    ChefTrigger.OFF_TOPIC_PHILOSOPHY: 2,
    ChefTrigger.TIME_WASTING: 1,

    # Що надихає
    ChefTrigger.INTERESTING_INGREDIENT: -3,
    ChefTrigger.COMPLEX_TASK: -3,
    ChefTrigger.CREATIVE_IDEA: -3,
    ChefTrigger.HUMOR: -1,
    ChefTrigger.RESPECT: -2,

    # Червоні лінії
    ChefTrigger.INSULT: 3,
    ChefTrigger.TROLLING: 1,
    ChefTrigger.DISRESPECT_TO_KITCHEN: 3,
    ChefTrigger.MANIPULATION: 2,
}

# МОДУЛЬ 4 — EMOTION BUFFER (ЕМОЦІЙНИЙ БУФЕР)
class EmotionBuffer:
    def __init__(self):
        self.value = 0          # поточний емоційний стан (позитив = гірше, негатив = краще)
        self.cooldown_rate = 0.5  # як швидко шеф "охолоджується"
        self.max_value = 10       # межа, після якої шеф точно злиться
        self.min_value = -10      # межа, після якої шеф максимально натхненний

    def apply(self, trigger):
        """Додає емоційний вплив тригера в буфер."""
        weight = TRIGGER_WEIGHTS.get(trigger, 0)
        self.value += weight

        # обмежуємо значення, щоб не вилітало за межі
        self.value = max(min(self.value, self.max_value), self.min_value)

    def cool_down(self):
        """Поступове зменшення емоційної напруги."""
        if self.value > 0:
            self.value -= self.cooldown_rate
        elif self.value < 0:
            self.value += self.cooldown_rate

        # якщо дуже близько до нуля — ставимо нуль
        if abs(self.value) < 0.1:
            self.value = 0

    def get_state_level(self):
        """Повертає рівень емоційності для FSM."""
        return self.value

# 16.1 — Клас ShortTermMemory
class ShortTermMemory:
    def __init__(self, limit=5):
        self.limit = limit
        self.events = []

    def add(self, trigger):
        self.events.append(trigger)
        if len(self.events) > self.limit:
            self.events.pop(0)

    def last(self, n=1):
        if len(self.events) == 0:
            return None
        return self.events[-n]

    def count(self, trigger):
        return self.events.count(trigger)

    def clear(self):
        self.events = []

# 17.1 — клас LongTermMemory
class LongTermMemory:
    def __init__(self):
        self.respect_count = 0
        self.toxicity_count = 0
        self.humor_count = 0
        self.apology_count = 0

    def update(self, trigger):
        if trigger == ChefTrigger.RESPECT:
            self.respect_count += 1
        if trigger == ChefTrigger.TOXICITY:
            self.toxicity_count += 1
        if trigger == ChefTrigger.HUMOR:
            self.humor_count += 1
        if trigger == ChefTrigger.APOLOGY:
            self.apology_count += 1

    def save(self, path=None):
        if path is None:
            path = os.path.join(os.path.dirname(__file__), "memory.json")
        with open(path, "w") as f:
            json.dump(self.__dict__, f)

    def load(self, path=None):
        if path is None:
            path = os.path.join(os.path.dirname(__file__), "memory.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                self.__dict__.update(data)


# МОДУЛЬ 18 — Характер шефа (Personality Traits)
class Personality:
    def __init__(
        self,
        patience=1.0,        # терпіння (менше → швидше злиться)
        humor=1.0,           # схильність до гумору
        sensitivity=1.0,     # емоційна чутливість
        discipline=1.0,      # строгість, серйозність
        creativity=1.0       # схильність до творчих станів
    ):
        self.patience = patience
        self.humor = humor
        self.sensitivity = sensitivity
        self.discipline = discipline
        self.creativity = creativity

def apply_trigger(
        current_state, 
        trigger, 
        emotion_buffer, 
        memory, 
        long_memory,
        personality
        ):
    """
    Обробляє тригер, оновлює емоційний буфер і повертає новий стан.
    """

    # 1. Додаємо емоційний вплив
    emotion_buffer.apply(trigger)

    # 2. Охолоджуємо емоції (плавність)
    emotion_buffer.cool_down()

    # 3. Отримуємо рівень емоцій
    level = emotion_buffer.get_state_level()

    # 18.3 — Вплив характеру на емоції
    # Чутливість
    level *= personality.sensitivity


    # Терпіння
    if trigger == ChefTrigger.TOXICITY:
        level += (1.0 - personality.patience)

    # Гумор
    if trigger == ChefTrigger.HUMOR:
        level -= 0.3 * personality.humor

    # Дисципліна
    if trigger == ChefTrigger.SILLY_QUESTION:
        level += 0.5 * personality.discipline

    # Креативність
    if trigger == ChefTrigger.COMPLEX_TASK:
        level -= 0.4 * personality.creativity


    # 4. Мікровипадковість (гібридна модель)
    randomness = random.uniform(-0.3, 0.3)
    level += randomness
    
    # 16.4 — Вплив пам’яті на емоції
    # Якщо користувач кілька разів поспіль був токсичним
    if emotion_buffer.get_state_level() > 3:
        if memory.count(ChefTrigger.TOXICITY) >= 2:
            level += 1.5  # шеф швидше дратується

    # Якщо користувач кілька разів поспіль був ввічливим
    if memory.count(ChefTrigger.RESPECT) >= 2:
        level -= 1.0  # шеф швидше заспокоюється

    # 17.3 — Вплив довготривалої пам’яті на емоції
    if long_memory.toxicity_count >= 10:
        level += 0.5  # шеф загалом більш дратівливий

    if long_memory.respect_count >= 10:
        level -= 0.5  # шеф загалом більш спокійний

    if long_memory.humor_count >= 10:
        level -= 0.3  # шеф стає більш грайливим

    if long_memory.apology_count >= 5:
        level -= 0.2  # шеф легше прощає

    OFFLINE_THRESHOLD = 9 * personality.patience
    BOUNDARY_THRESHOLD = 7 * personality.patience
    ANNOYED_THRESHOLD = 4 * personality.patience

    # 5. Логіка переходів
    # 14.3 — Коли шеф має йти в OFFLINE
    if level >= OFFLINE_THRESHOLD:
        return ChefState.OFFLINE

    if level >= BOUNDARY_THRESHOLD:
        return ChefState.BOUNDARY

    if level >= ANNOYED_THRESHOLD:
        return ChefState.ANNOYED

    if level <= -6:
        return ChefState.CREATIVE

    if level <= -3:
        return ChefState.ACTIVE

    # Якщо рівень близький до нуля — повертаємося в нейтральний стан
    if -1 < level < 1:
        return ChefState.IDLE

    # Якщо нічого не підійшло — залишаємо поточний стан
    return current_state

# МОДУЛЬ 6 — transition_state()
def transition_state(current_state, proposed_state):
    """
    Головна FSM-функція.
    Приймає поточний стан і запропонований стан.
    Вирішує, чи дозволений перехід, і повертає фінальний стан.
    """

    # 1. Якщо стан не змінюється — просто повертаємо його
    if proposed_state == current_state:
        return current_state

    # 2. Логіка плавних переходів (твоя логіка)
    # Playful → Serious не миттєво
    if current_state == ChefState.PLAYFUL and proposed_state == ChefState.SERIOUS:
        return ChefState.ACTIVE  # проміжний стан

    # Serious → Playful м’яко
    if current_state == ChefState.SERIOUS and proposed_state == ChefState.PLAYFUL:
        return ChefState.ACTIVE

    # Annoyed → Playful тільки якщо юзер дав правильний тон
    if current_state == ChefState.ANNOYED and proposed_state == ChefState.PLAYFUL:
        # 50% шанс, що шеф ще не готовий
        if random.random() < 0.5:
            return ChefState.SERIOUS
        return ChefState.PLAYFUL

    # Active → Deep Focus плавно
    if current_state == ChefState.ACTIVE and proposed_state == ChefState.DEEP_FOCUS:
        return ChefState.SERIOUS

    # Creative → Serious з сарказмом
    if current_state == ChefState.CREATIVE and proposed_state == ChefState.SERIOUS:
        # Повертаємо SERIOUS, але шеф запам’ятає, що юзер "збив креатив"
        return ChefState.SERIOUS

    # Offline → Return (повернувся, охолов)
    if current_state == ChefState.OFFLINE and proposed_state != ChefState.OFFLINE:
        return ChefState.RETURNED

    # 3. Якщо перехід не має спеціальних правил — дозволяємо
    return proposed_state

# МОДУЛЬ 8 — ЕМОЦІЙНІ РЕАКЦІЇ ШЕФА
REACTIONS = {
    ChefState.IDLE: [
        "Так, слухаю.",
        "Я тут. Що далі?",
        "Готовий працювати."
    ],

    ChefState.ACTIVE: [
        "Цікаво… продовжуй.",
        "О, це вже щось!",
        "Добре, працюємо."
    ],

    ChefState.PLAYFUL: [
        "Ха, непогано ти це придумав.",
        "Ну ти даєш…",
        "Окей, давай трохи побавимось."
    ],

    ChefState.SERIOUS: [
        "Зосереджуюсь.",
        "Добре, без жартів.",
        "Працюю над цим."
    ],

    ChefState.ANNOYED: [
        "Серйозно?..",
        "Ти зараз знущаєшся?",
        "Мені це не подобається."
    ],

    ChefState.BOUNDARY: [
        "Стоп. Так не піде.",
        "Припини. Це вже занадто.",
        "Я не працюю в такому тоні."
    ],

    ChefState.OFFLINE: [
        "…",
        "Шеф пішов на перекур.",
        "Повернусь, коли охолону."
    ],

    ChefState.RETURNED: [
        "Добре, я повернувся.",
        "Все, я спокійний.",
        "Продовжимо."
    ],

    ChefState.DEEP_FOCUS: [
        "Дай хвилинку… думаю.",
        "Це складно. Працюю.",
        "Зараз… аналізую."
    ],

    ChefState.CREATIVE: [
        "Ооо, цікаво!",
        "Так, це вже креатив!",
        "Мені подобається твій стиль."
    ],
}

# 13.1 — Словник idle‑реплік
IDLE_REACTIONS = [
    "Хм… ти ще тут?",
    "Я тут, якщо що.",
    "Можемо продовжувати, коли будеш готовий.",
    "Думаю над новим рецептом…",
    "Перевіряю інгредієнти…"
]

# 15.1 — Словник контекстних реакцій
CONTEXT_REACTIONS = {
    (ChefState.PLAYFUL, ChefTrigger.HUMOR): [
        "Ха! Оце ти видав!",
        "Добре, добре, я оцінив.",
        "Непогано, я посміхнувся."
    ],

    (ChefState.SERIOUS, ChefTrigger.COMPLEX_TASK): [
        "Зараз… думаю.",
        "Це цікаво. Дай хвилинку.",
        "Працюю над цим."
    ],

    (ChefState.ANNOYED, ChefTrigger.RESPECT): [
        "Добре… приймається.",
        "Гаразд, рухаємося далі.",
        "Окей, я заспокоююсь."
    ],

    (ChefState.BOUNDARY, ChefTrigger.APOLOGY): [
        "Добре. Приймаю вибачення.",
        "Гаразд. Повертаюсь.",
        "Добре. Давай спробуємо ще раз."
    ],

    (ChefState.OFFLINE, ChefTrigger.APOLOGY): [
        "…",
        "Добре… я повернусь.",
        "Гаразд… давай спробуємо знову."
    ],
}

# МОДУЛЬ 10 — МІМІКА ТА ПОВЕДІНКОВІ РЕАКЦІЇ (BEHAVIORAL CUES)
BEHAVIORS = {
    ChefState.IDLE: [
        "спокійно стоїть",
        "оглядає кухню",
        "чекає на інструкції"
    ],

    ChefState.ACTIVE: [
        "поправляє фартух",
        "нахиляється ближче",
        "пильно дивиться"
    ],

    ChefState.PLAYFUL: [
        "підморгує",
        "усміхається",
        "піднімає брову"
    ],

    ChefState.SERIOUS: [
        "зосереджено дивиться",
        "стискає губи",
        "кладе руки на стіл"
    ],

    ChefState.ANNOYED: [
        "зітхає",
        "крутить очима",
        "поправляє фартух різким рухом"
    ],

    ChefState.BOUNDARY: [
        "відвертається",
        "піднімає руку, зупиняючи",
        "холодно дивиться"
    ],

    ChefState.OFFLINE: [
        "йде з кухні",
        "зникає з кадру",
        "не реагує"
    ],

    ChefState.RETURNED: [
        "повертається на місце",
        "витирає руки рушником",
        "видихає"
    ],

    ChefState.DEEP_FOCUS: [
        "нахиляється над столом",
        "тримає підборіддя рукою",
        "завмирає в роздумах"
    ],

    ChefState.CREATIVE: [
        "плескає в долоні",
        "оживлено жестикулює",
        "піднімає інгредієнт і розглядає його"
    ],
}

# 13.2 — Словник idle‑міміки
IDLE_BEHAVIORS = [
    "оглядає кухню",
    "переставляє баночки зі спеціями",
    "витирає стіл",
    "поправляє фартух",
    "заглядає в каструлю"
]

# 19.1 словник профілів
EMOTIONAL_PROFILES = {
    "italian": Personality(
        patience=0.7,
        humor=1.4,
        sensitivity=1.3,
        discipline=1.1,
        creativity=1.5
    ),

    "french": Personality(
        patience=0.9,
        humor=0.8,
        sensitivity=1.2,
        discipline=1.6,
        creativity=1.3
    ),

    "japanese": Personality(
        patience=1.4,
        humor=0.6,
        sensitivity=0.8,
        discipline=1.8,
        creativity=1.2
    ),

    "calm_master": Personality(
        patience=1.8,
        humor=1.0,
        sensitivity=0.7,
        discipline=1.0,
        creativity=1.4
    ),

    "chaotic_genius": Personality(
        patience=0.6,
        humor=1.7,
        sensitivity=1.5,
        discipline=0.7,
        creativity=2.0
    ),
}

# МОДУЛЬ 7 — ChefFSM (клас шефа)
class ChefFSM:
    def __init__(self, profile=None):
        self.state = ChefState.IDLE
        self.emotions = EmotionBuffer()
        self.memory = ShortTermMemory()
        self.long_memory = LongTermMemory()
        self.long_memory.load()
        self.personality = Personality()

        if profile and profile in EMOTIONAL_PROFILES:
            self.personality = EMOTIONAL_PROFILES[profile]
        else:
            self.personality = Personality()

        #chef = ChefFSM(personality=Personality(patience=0.7, humor=1.5))
        #chef = ChefFSM(profile="italian") chef = ChefFSM(profile="chaotic_genius")


    def trigger(self, trigger):
        # 1. Записуємо тригер у пам’ять 
        self.memory.add(trigger)          # short-term
        self.long_memory.update(trigger)  # long-term
        self.long_memory.save()

        # 2. Приймає тригер, Оновлюємо емоції
        proposed_state = apply_trigger(
            self.state, 
            trigger, 
            self.emotions, 
            self.memory,        # short-term 
            self.long_memory,    # long-term
            self.personality
            )
    
        if not isinstance(trigger, ChefTrigger):
            raise ValueError(f"Invalid trigger: {trigger}")
        
        # 3. Плавний перехід
        final_state = transition_state(self.state, proposed_state)
        
        self.state = final_state
        return self.state
        

    def update(self):
        """
        Оновлює емоційний стан без тригерів (наприклад, час проходить).
        """
        self.emotions.cool_down()

        # Якщо шеф повернувся — через деякий час стає нейтральним
        # 14.2 — Автоматичний перехід з RETURNED → IDLE 

        level = self.emotions.get_state_level()

        if self.state == ChefState.RETURNED and abs(level) < 1:
            self.state = ChefState.IDLE
        
        # Якщо емоції повернулися до нуля — повертаємо Idle
        if level == 0:
            self.state = ChefState.IDLE

        # 17.5 — Вплив довготривалої пам’яті на базовий стан
        if self.long_memory.respect_count >= 20:
            if self.state == ChefState.IDLE:
                self.state = ChefState.ACTIVE

        return self.state
    
    # 20.6 метод reset()
    def reset(self):
        self.state = ChefState.IDLE
        self.emotions = EmotionBuffer()
        self.memory.clear()
        self.long_memory = LongTermMemory()
        self.personality = Personality()
    
    # 20.7 метод reset()
    def set_profile(self, profile_name):
        if profile_name in EMOTIONAL_PROFILES:
            self.personality = EMOTIONAL_PROFILES[profile_name]



    # МОДУЛЬ 9 — get_reaction()
    def get_reaction(self):
        # 18.5 — вплив характеру
        if self.personality.humor > 1.2 and self.state == ChefState.PLAYFUL:
            return random.choice([
                "Ха, ну ти даєш!",
                "Оце жарт!",
                "Добре, я посміхнувся."
            ])

        # стандартна логіка
        phrases = REACTIONS.get(self.state, ["..."])
        return random.choice(phrases)

    # МОДУЛЬ 11 — get_behavior()
    def get_behavior(self):
        if self.personality.creativity > 1.3 and self.state == ChefState.CREATIVE:
            return "оживлено жестикулює"

        """
        Повертає випадкову міміку/поведінкову реакцію відповідно до поточного стану.
        """
        actions = BEHAVIORS.get(self.state, ["нічого не робить"])
        return random.choice(actions)
    
    # МОДУЛЬ 15 — Контекстні реакції (Context‑Aware Responses)
    # 15.2 — Метод get_context_reaction()
    def get_context_reaction(self, trigger):
        """
        Повертає контекстну реакцію, якщо вона існує.
        """
        # 16.5 — Вплив пам’яті на реакції
        # 1. Спеціальна логіка пам’яті (має найвищий пріоритет)
        # Якщо користувач вибачався кілька разів
        if trigger == ChefTrigger.APOLOGY and self.memory.count(ChefTrigger.APOLOGY) >= 2:
            return "Добре, добре… я вже не злюсь."
       
        # 17.4 — Вплив довготривалої пам’яті на реакції
        if self.long_memory.humor_count >= 10 and trigger == ChefTrigger.HUMOR:
            return "Ти вже мене розсмішив, давай ще!"

        
        # 2. Контекстні реакції зі словника
        key = (self.state, trigger)
        if key in CONTEXT_REACTIONS:
            return random.choice(CONTEXT_REACTIONS[key])
        
        # 3. Якщо нічого не підійшло
        return None
            
    # МОДУЛЬ 12 — respond() (комбінована реакція)
    def respond(self, trigger=None):
        # 15.3 — Інтеграція в respond()
        """
        Повертає комбіновану реакцію: репліка + міміка.
        """
        # 1. Контекстна реакція має пріоритет
        ctx = self.get_context_reaction(trigger) if trigger else None
        phrase = ctx if ctx else self.get_reaction()
        behavior = self.get_behavior()
        return f"{phrase} — {behavior}"
     
    # МОДУЛЬ 13.3 — Idle‑поведінка (поведінка без тригерів)
    def idle(self):
        """
        Idle-поведінка: шеф щось робить навіть без тригерів.
        """
        # Охолоджуємо емоції
        self.update()

        # 20% шанс змінити стан на PLAYFUL або DEEP_FOCUS
        roll = random.random()
        if roll < 0.1:
            self.state = ChefState.PLAYFUL
        elif roll < 0.2:
            self.state = ChefState.DEEP_FOCUS

        # Вибираємо idle-репліку та міміку
        phrase = random.choice(IDLE_REACTIONS)
        behavior = random.choice(IDLE_BEHAVIORS)

        return f"{phrase} — {behavior}"
    
    # 14.1 — Додаємо метод recover()
    def recover(self):
        """
        Логіка повернення шефа з OFFLINE у нормальний стан.
        Викликається, коли шеф охолов.
        """
        # Якщо шеф не в OFFLINE — нічого не робимо
        if self.state != ChefState.OFFLINE:
            return self.state

        # Охолоджуємо емоції
        self.emotions.cool_down()

        # Якщо емоції впали нижче порогу — шеф повертається
        if self.emotions.get_state_level() <= 2:
            self.state = ChefState.RETURNED

        return self.state
