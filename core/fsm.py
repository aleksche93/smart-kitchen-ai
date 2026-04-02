from enum import Enum
import random

class ChefState(str, Enum):
    IDLE = 'IDLE'
    ACTIVE = 'ACTIVE'
    PLAYFUL = 'PLAYFUL'
    SERIOUS = 'SERIOUS'
    ANNOYED = 'ANNOYED'
    BOUNDARY = 'BOUNDARY'
    OFFLINE = 'OFFLINE'
    RETURNED = 'RETURNED'
    STUDY = 'STUDY'
    RESEARCH = 'RESEARCH'
    RECIPE_DEV = 'RECIPE_DEV'
    INGREDIENT_FETCH = 'INGREDIENT_FETCH'
    PREP_MODE = 'PREP_MODE'
    DEEP_FOCUS = 'DEEP_FOCUS'
    CREATIVE = 'CREATIVE'

class ChefTrigger(str, Enum):
    NON_CULINARY_TOPIC = 'NON_CULINARY_TOPIC'
    SILLY_QUESTION = 'SILLY_QUESTION'
    TOXICITY = 'TOXICITY'
    OFF_TOPIC_PHILOSOPHY = 'OFF_TOPIC_PHILOSOPHY'
    TIME_WASTING = 'TIME_WASTING'

    INTERESTING_INGREDIENT = 'INTERESTING_INGREDIENT'
    COMPLEX_TASK = 'COMPLEX_TASK'
    CREATIVE_IDEA = 'CREATIVE_IDEA'
    HUMOR = 'HUMOR'
    RESPECT = 'RESPECT'
    APOLOGY = 'APOLOGY'

    INSULT = 'INSULT'
    TROLLING = 'TROLLING'
    DISRESPECT_TO_KITCHEN = 'DISRESPECT_TO_KITCHEN'
    MANIPULATION = 'MANIPULATION'

TRIGGER_WEIGHTS = {
    ChefTrigger.NON_CULINARY_TOPIC: 3,
    ChefTrigger.SILLY_QUESTION: 4,
    ChefTrigger.TOXICITY: 5,
    ChefTrigger.OFF_TOPIC_PHILOSOPHY: 2,
    ChefTrigger.TIME_WASTING: 1,

    ChefTrigger.INTERESTING_INGREDIENT: -3,
    ChefTrigger.COMPLEX_TASK: -3,
    ChefTrigger.CREATIVE_IDEA: -3,
    ChefTrigger.HUMOR: -1,
    ChefTrigger.RESPECT: -2,

    ChefTrigger.INSULT: 3,
    ChefTrigger.TROLLING: 1,
    ChefTrigger.DISRESPECT_TO_KITCHEN: 3,
    ChefTrigger.MANIPULATION: 2,
}

class Personality:
    def __init__(self, patience=1.0, humor=1.0, sensitivity=1.0, discipline=1.0, creativity=1.0):
        self.patience = patience
        self.humor = humor
        self.sensitivity = sensitivity
        self.discipline = discipline
        self.creativity = creativity

EMOTIONAL_PROFILES = {
    "italian": Personality(patience=0.7, humor=1.4, sensitivity=1.3, discipline=1.1, creativity=1.5),
    "french": Personality(patience=0.9, humor=0.8, sensitivity=1.2, discipline=1.6, creativity=1.3),
    "japanese": Personality(patience=1.4, humor=0.6, sensitivity=0.8, discipline=1.8, creativity=1.2),
    "calm_master": Personality(patience=1.8, humor=1.0, sensitivity=0.7, discipline=1.0, creativity=1.4),
    "chaotic_genius": Personality(patience=0.6, humor=1.7, sensitivity=1.5, discipline=0.7, creativity=2.0),
    "neutral": Personality()
}

class ChefFSM:
    def __init__(self, state_db, memory_db, session_db):
        """
        Initializes the FSM taking SQLAlchemy db models representing the active state.
        By operating directly on these models, SQLAlchemy handles the tracking of dirty fields.
        """
        self.state_db = state_db
        self.memory_db = memory_db
        self.session_db = session_db
        
        self.personality = EMOTIONAL_PROFILES.get(
            self.state_db.personality_profile, EMOTIONAL_PROFILES["neutral"]
        )

    def trigger(self, trigger: ChefTrigger) -> str:
        # Update short term memory array
        recent = list(self.session_db.recent_triggers or [])
        recent.append(trigger.value)
        if len(recent) > 5:
            recent.pop(0)
        self.session_db.recent_triggers = recent

        # Update long term counters tracking
        counters = dict(self.memory_db.long_term_counters or {})
        counter_key = f"{trigger.value.lower()}_count"
        if trigger in [ChefTrigger.RESPECT, ChefTrigger.TOXICITY, ChefTrigger.HUMOR, ChefTrigger.APOLOGY]:
            counters[counter_key] = counters.get(counter_key, 0) + 1
        self.memory_db.long_term_counters = counters

        # Apply emotional weight based on predefined mapping
        weight = TRIGGER_WEIGHTS.get(trigger, 0)
        self.state_db.emotion_value += weight

        # Auto Cooldown
        if self.state_db.emotion_value > 0:
            self.state_db.emotion_value -= 0.5
        elif self.state_db.emotion_value < 0:
            self.state_db.emotion_value += 0.5
        
        if abs(self.state_db.emotion_value) < 0.1:
            self.state_db.emotion_value = 0.0

        # Boundaries clamp
        self.state_db.emotion_value = max(min(self.state_db.emotion_value, 10.0), -10.0)

        # Apply personality multipliers
        level = self.state_db.emotion_value * self.personality.sensitivity
        if trigger == ChefTrigger.TOXICITY:
            level += (1.0 - self.personality.patience)
        if trigger == ChefTrigger.HUMOR:
            level -= 0.3 * self.personality.humor
        if trigger == ChefTrigger.SILLY_QUESTION:
            level += 0.5 * self.personality.discipline
        if trigger == ChefTrigger.COMPLEX_TASK:
            level -= 0.4 * self.personality.creativity

        level += random.uniform(-0.3, 0.3)

        # Reaction to short-term traits
        if self.state_db.emotion_value > 3 and recent.count(ChefTrigger.TOXICITY.value) >= 2:
            level += 1.5
        if recent.count(ChefTrigger.RESPECT.value) >= 2:
            level -= 1.0

        # Reaction to long-term traits
        if counters.get("toxicity_count", 0) >= 10:
            level += 0.5
        if counters.get("respect_count", 0) >= 10:
            level -= 0.5
        if counters.get("humor_count", 0) >= 10:
            level -= 0.3
        if counters.get("apology_count", 0) >= 5:
            level -= 0.2

        # State transition 
        proposed_state = self._determine_state(level)
        self.state_db.current_state = self._smooth_transition(self.state_db.current_state, proposed_state)
        return self.state_db.current_state

    def _determine_state(self, level: float) -> str:
        offline_thresh = 9 * self.personality.patience
        boundary_thresh = 7 * self.personality.patience
        annoyed_thresh = 4 * self.personality.patience

        if level >= offline_thresh: return ChefState.OFFLINE.value
        if level >= boundary_thresh: return ChefState.BOUNDARY.value
        if level >= annoyed_thresh: return ChefState.ANNOYED.value
        if level <= -6: return ChefState.CREATIVE.value
        if level <= -3: return ChefState.ACTIVE.value
        if -1 < level < 1: return ChefState.IDLE.value
        
        return self.state_db.current_state

    def _smooth_transition(self, current: str, proposed: str) -> str:
        if current == proposed:
            return current
        if current == ChefState.PLAYFUL.value and proposed == ChefState.SERIOUS.value:
            return ChefState.ACTIVE.value
        if current == ChefState.SERIOUS.value and proposed == ChefState.PLAYFUL.value:
            return ChefState.ACTIVE.value
        if current == ChefState.ANNOYED.value and proposed == ChefState.PLAYFUL.value:
            return ChefState.SERIOUS.value if random.random() < 0.5 else ChefState.PLAYFUL.value
        if current == ChefState.ACTIVE.value and proposed == ChefState.DEEP_FOCUS.value:
            return ChefState.SERIOUS.value
        if current == ChefState.CREATIVE.value and proposed == ChefState.SERIOUS.value:
            return ChefState.SERIOUS.value
        if current == ChefState.OFFLINE.value and proposed != ChefState.OFFLINE.value:
            return ChefState.RETURNED.value
            
        return proposed
