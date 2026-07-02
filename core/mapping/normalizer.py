from __future__ import annotations

import re
import unicodedata


def normalize_name(value: str) -> str:
    value = str(value or "")

    value = unicodedata.normalize("NFD", value)
    value = "".join(char for char in value if unicodedata.category(char) != "Mn")

    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value)

    return value.strip("_")
