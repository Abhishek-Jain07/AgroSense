# utils/validators.py
import re

def normalize_str(s: str) -> str:
    return s.strip().lower().title()

def parse_npk_input(val: str):
    """
    Accepts numeric input or categorical 'Low'/'Medium'/'High' (insensitive to case).
    Returns tuple: (kind, value) where kind is 'numeric' or 'level', value is int/float or canonical str.
    Raises ValueError if invalid.
    """
    val_clean = val.strip()
    if not val_clean:
        raise ValueError("Empty input")
    # Try numeric
    try:
        num = float(val_clean)
        return ("numeric", num)
    except ValueError:
        # try level
        lw = val_clean.lower()
        if lw in ("low", "medium", "high"):
            return ("level", lw.title())
        else:
            raise ValueError("Enter a number or Low/Medium/High")

def validate_choice(val: str, choices: list[str]):
    normalized = normalize_str(val)
    for c in choices:
        if normalize_str(c) == normalized:
            return c
    raise ValueError(f"Invalid choice — expected one of {choices}")
