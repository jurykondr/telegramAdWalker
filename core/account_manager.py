import json
from typing import List, Dict


def load_accounts(config_path: str = "config/accounts.json") -> List[Dict]:
    with open(config_path, "r", encoding="utf-8") as f:
        accounts = json.load(f)

    validated_accounts = []
    for acc in accounts:
        if all(k in acc for k in ("phone", "api_id", "api_hash")):
            validated_accounts.append(acc)
        else:
            print(f"[WARN] Неполные данные аккаунта: {acc}")

    return validated_accounts
