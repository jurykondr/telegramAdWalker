import re
from typing import Any


def extract_sponsored_url(sponsored_message: Any) -> str:
    if not sponsored_message:
        print("[WARN] Рекламное сообщение не получено.")
        return ""

    try:
        text = sponsored_message.get("message", {}).get("text", {}).get("text", "")
        entities = sponsored_message.get("message", {}).get("text", {}).get("entities", [])

        if not text:
            text = sponsored_message.get("message", {}).get("caption", {}).get("text", "")
            entities = sponsored_message.get("message", {}).get("caption", {}).get("entities", [])

        for entity in entities:
            url = entity.get("type", {}).get("url")
            if url:
                return url

        match = re.search(r"(https?://t\.me/[\w\d_/?=]+)", text)
        if match:
            return match.group(1)

    except Exception as e:
        print(f"[ERROR] Ошибка при разборе рекламного сообщения: {e}")

    return ""
