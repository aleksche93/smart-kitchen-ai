import json
import os

LOCALES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "locales")

class I18n:
    def __init__(self, lang="uk"):
        self.lang = lang
        self.translations = {}
        self._load_translations()

    def _load_translations(self):
        file_path = os.path.join(LOCALES_PATH, f"{self.lang}.json")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.translations = json.load(f)
        except Exception:
            self.translations = {}

    def get(self, path: str, default: str = "") -> str | list:
        keys = path.split('.')
        val = self.translations
        for key in keys:
            if isinstance(val, dict) and key in val:
                val = val[key]
            else:
                return default
        return val

# Global instance for easy importing
i18n = I18n()
