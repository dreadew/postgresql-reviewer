import json
import re


def safe_extract_json(text: str) -> str:
    """Попытка извлечь JSON-объект или массив из текста ответа LLM.
    Поддерживает как одиночные объекты {}, так и массивы [{}].
    """
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    text = text.strip()

    candidates = []

    brace_count = 0
    start_pos = -1
    for i, char in enumerate(text):
        if char == "{":
            if brace_count == 0:
                start_pos = i
            brace_count += 1
        elif char == "}":
            brace_count -= 1
            if brace_count == 0 and start_pos != -1:
                candidate = text[start_pos : i + 1]
                candidates.append(candidate)
                start_pos = -1

    for i, candidate in enumerate(candidates):
        try:
            json.loads(candidate)
            return candidate
        except json.JSONDecodeError:
            continue
    raise ValueError("Не удалось найти валидный JSON объект или массив")
