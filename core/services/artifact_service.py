from typing import Dict

# Typed JSON schemas for each artifact — instruct LLM to produce consistent structure
ARTIFACT_SCHEMAS: Dict[str, str] = {
    "RECIPE": (
        "You are a culinary data API. Return ONLY a valid JSON object with EXACTLY these fields: "
        "{\"name\": string, \"time\": string (e.g. '30 minutes'), \"difficulty\": string (Easy/Medium/Hard), "
        "\"ingredients\": array of strings (each: quantity + name, e.g. '2 large eggs'), "
        "\"instructions\": array of strings (each a numbered step), \"notes\": string}. "
        "No markdown, no extra text, no wrapper keys. Pure JSON only."
    ),
    "SHOPPING_LIST": (
        "You are a culinary data API. Return ONLY a valid JSON object with EXACTLY: "
        "{\"title\": string, \"categories\": [{\"name\": string, \"items\": [{\"name\": string, \"quantity\": string}]}]}. "
        "No markdown, no extra text. Pure JSON only."
    ),
    "WASTE_ALERT": (
        "You are a culinary data API. Return ONLY a valid JSON object with EXACTLY: "
        "{\"severity\": string (HIGH/MEDIUM/LOW), "
        "\"expiring_items\": [{\"name\": string, \"days_left\": integer, \"action\": string}], "
        "\"total_value_at_risk\": string, \"recommended_action\": string}. "
        "No markdown, no extra text. Pure JSON only."
    ),
    "PREP_SCHEDULE": (
        "You are a culinary data API. Return ONLY a valid JSON object with: "
        "{\"title\": string, \"steps\": [{\"time\": string, \"task\": string}]}. Pure JSON only."
    ),
    "TASK_LIST": (
        "You are a culinary data API. Return ONLY a valid JSON object with: "
        "{\"title\": string, \"tasks\": [{\"label\": string, \"done\": false}]}. Pure JSON only."
    ),
}