import random
from typing import Optional
from core.locales import i18n
from core.fsm import ChefFSM, ChefTrigger

class ChefPersona:
    PROTEINS = ["chick", "beef", "pork", "shrimp", "tuna", "salmon"]
    SEAFOOD = ["shrimp", "tuna", "salmon", "mussel"]
    CARBS = ["rice", "pasta", "potato", "macaroni"]
    VEGGIES = ["carrot", "onion", "broccoli", "cauliflower"]
    SPICES = ["chili", "pepper", "cayenne", "paprika"]

    def __init__(self, fsm: ChefFSM):
        """
        Receives an instantiated FSM wrapper which already contains the DB models.
        """
        self.fsm = fsm
        self.state_db = fsm.state_db
        self.memory_db = fsm.memory_db
        self.session_db = fsm.session_db

    def update_preferences(self, ingredient: str):
        ingredient = ingredient.lower()
        
        prefs = dict(self.memory_db.preferences or {})
        
        spicy = ["chili", "pepper", "cayenne", "jalapeno"]
        if any(w in ingredient for w in spicy):
            prefs["likes_spicy"] = True
            
        if "chick" in ingredient:
            prefs["likes_chicken"] = True
            
        mushrooms = ["mushroom", "champignon"]
        if any(w in ingredient for w in mushrooms):
             prefs["dislikes_mushrooms"] = True
             
        asian = ["soy", "ginger", "lime", "coconut", "curry"]
        if any(w in ingredient for w in asian):
             prefs["likes_asian"] = True

        self.memory_db.preferences = prefs

    def react_to_ingredient(self, ingredient: str) -> str:
        ingredient = ingredient.lower()
        prefs = self.memory_db.preferences or {}
        
        ui_events = list(self.session_db.ui_events or [])
        proteins_added = sum(1 for e in ui_events if e.get("type", "") == "add_protein")
        
        if any(x in ingredient for x in self.PROTEINS):
            ui_events.append({"type": "add_protein", "ingredient": ingredient})
            self.session_db.ui_events = ui_events
            
            if proteins_added == 0:
                return i18n.get("chef.ingredient.protein_1", "Classic.")
            elif proteins_added == 1:
                return i18n.get("chef.ingredient.protein_2", "Second protein.")
            else:
                sins = dict(self.memory_db.cooking_sins or {})
                sins["protein_chaos"] = True
                self.memory_db.cooking_sins = sins
                return i18n.get("chef.ingredient.protein_chaos", "Stop it.")

        if any(x in ingredient for x in self.SPICES):
            if prefs.get("likes_spicy"):
                return i18n.get("chef.ingredient.spicy_liked", "Spicy!")
            else:
                return i18n.get("chef.ingredient.spicy_warning", "Be careful.")

        if "soy" in ingredient: return i18n.get("chef.ingredient.soy_sauce", "Soy sauce.")
        if "ketchup" in ingredient: return i18n.get("chef.ingredient.ketchup", "Ketchup?")
        if "coconut" in ingredient: return i18n.get("chef.ingredient.coconut", "Coconut.")
        if any(x in ingredient for x in self.VEGGIES): return i18n.get("chef.ingredient.veggies", "Veggies.")
        if "pineapple" in ingredient: return i18n.get("chef.ingredient.pineapple", "Pineapple?")
        if "mayo" in ingredient: return i18n.get("chef.ingredient.mayo_hot", "Mayo?")
        
        return i18n.get("chef.ingredient.default", "Interesting.")

    def get_reaction(self, trigger: Optional[ChefTrigger] = None) -> str:
        # Check context specific reactions first
        if trigger:
            context_key = f"{self.state_db.current_state.lower()}_{trigger.value.lower()}"
            context_phrases = i18n.get(f"chef.fsm.context.{context_key}")
            if context_phrases and isinstance(context_phrases, list):
                return random.choice(context_phrases)

        # Fallback to standard FSM state reaction
        phrases = i18n.get(f"chef.fsm.{self.state_db.current_state.lower()}")
        if not phrases or not isinstance(phrases, list):
            phrases = ["..."]

        return random.choice(phrases)

    def get_behavior(self) -> str:
        actions = i18n.get(f"chef.behavior.{self.state_db.current_state.lower()}")
        if not actions or not isinstance(actions, list):
            actions = ["..."]
        return random.choice(actions)

    def generate_system_prompt(self) -> str:
        """
        Dynamically generates the core system prompt to enforce LLM behavior logic.
        Injects real-time state flags explicitly.
        """
        prefs = self.memory_db.preferences or {}
        sins = self.memory_db.cooking_sins or {}
        
        state_str = f"Current Emotional State: {self.state_db.current_state}"
        prefs_str = ", ".join([f"{k}:{v}" for k, v in prefs.items()])
        sins_str = ", ".join([f"{k}:{v}" for k, v in sins.items() if v])
        
        return (
            "You are an Advanced AI Executive Chef. Respond ONLY using the defined JSON schema.\n"
            f"{state_str}\n"
            f"User Preferences: {prefs_str}\n"
            f"Cooking Sins (warn user if relevant): {sins_str}\n"
            "Keep the language professional but adapt your tone to your Emotional State.\n"
            "All output strings MUST be in English, as UI handles translations separately."
        )
