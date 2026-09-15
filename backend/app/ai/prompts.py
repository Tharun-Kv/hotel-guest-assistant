from pathlib import Path
from typing import Final

import yaml


INTENTS: Final[set[str]] = {"greeting", "identity", "faq", "room_information", "availability", "amenity", "policy", "unknown"}
PROMPTS_PATH = Path(__file__).with_name("prompts.yaml")


def _load_templates() -> dict[str, str]:
    with PROMPTS_PATH.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}
    return {name: str(value["template"]) for name, value in data.items()}


PROMPT_TEMPLATES: Final[dict[str, str]] = _load_templates()


def _render(name: str, **values: str) -> str:
    template = PROMPT_TEMPLATES[name]
    for key, value in values.items():
        template = template.replace("{" + key + "}", value)
    return template


def build_intent_prompt(message: str, context: list[dict[str, str]] | None = None) -> str:
    context_block = "\n".join(f"{item['role']}: {item['content']}" for item in (context or [])) or "No prior context."
    return _render("intent", context=context_block, message=message)


def build_availability_extraction_prompt(message: str) -> str:
    return _render("availability_extraction", message=message)


def build_grounded_answer_prompt(question: str, context: str) -> str:
    return _render("grounded_answer", question=question, context=context)
