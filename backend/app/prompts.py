import os

PROMPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "prompts")

def load_prompt(filename: str) -> str:
    path = os.path.join(PROMPTS_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

class PromptManager:
    def __init__(self):
        self.system_role = load_prompt("system_role.md")
        self.intent_detection = load_prompt("intent_detection.md")
        self.emotion_risk = load_prompt("emotion_risk.md")
        self.strategy_routing = load_prompt("strategy_routing.md")
        self.response_generation = load_prompt("response_generation.md")

prompt_manager = PromptManager()
