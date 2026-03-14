"""
dnd-voice-polish — pre_tts D&D Pronunciation Fixer

Fires before text is sent to the TTS engine.

D&D is full of abbreviations and notation that TTS reads
badly without help:
  "d20"   → TTS says "dee two zero" or "d-twenty?"
  "AC"    → TTS says "A.C." OK but "armour class" sounds better
  "HP"    → better as "hit points" in narrative
  "DC 15" → better as "difficulty fifteen"
  "1d6"   → "one dee six"
  "+3"    → "plus three" (fine usually, but "plus three to hit" reads oddly)
  "XP"    → "experience points"
  "CON"   → "Constitution"
  "STR"   → "Strength"

Also handles:
  - Markdown formatting (bold, italic, headers) that leaks into TTS
  - Stat block notation that shouldn't be read aloud
  - Common D&D proper nouns that TTS butchers
"""

import re


def pre_tts(event):
    text = event.tts_text or ""
    if not text:
        return

    text = _strip_markdown(text)
    text = _fix_dice_notation(text)
    text = _fix_abbreviations(text)
    text = _fix_stat_names(text)
    text = _fix_proper_nouns(text)
    text = _clean_up(text)

    event.tts_text = text


# ── Markdown stripping ────────────────────────────────────────────────────

def _strip_markdown(text: str) -> str:
    # Headers
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # Bold / italic
    text = re.sub(r"\*{1,3}([^*]+)\*{1,3}", r"\1", text)
    text = re.sub(r"_{1,3}([^_]+)_{1,3}", r"\1", text)
    # Inline code
    text = re.sub(r"`([^`]+)`", r"\1", text)
    # Bullet points — replace with natural pause
    text = re.sub(r"^\s*[-•]\s+", "", text, flags=re.MULTILINE)
    # Numbered lists — keep the content
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)
    return text


# ── Dice notation ─────────────────────────────────────────────────────────

def _fix_dice_notation(text: str) -> str:
    # "2d6+3" → "two dee six plus three"
    def replace_dice(m):
        count    = m.group(1) or "1"
        sides    = m.group(2)
        modifier = m.group(3) or ""
        count_w  = _num_to_word(count)
        sides_w  = _num_to_word(sides)
        result   = f"{count_w} dee {sides_w}"
        if modifier:
            sign = "plus" if modifier[0] == "+" else "minus"
            num  = modifier[1:]
            result += f" {sign} {num}"
        return result

    text = re.sub(
        r"(\d+)?[dD](\d+)([+-]\d+)?",
        replace_dice,
        text
    )
    return text


def _num_to_word(n: str) -> str:
    words = {
        "1": "one", "2": "two", "3": "three", "4": "four",
        "6": "six", "8": "eight", "10": "ten", "12": "twelve",
        "20": "twenty", "100": "one hundred", "4": "four"
    }
    return words.get(n, n)


# ── Abbreviations ─────────────────────────────────────────────────────────

def _fix_abbreviations(text: str) -> str:
    replacements = [
        # Dice / combat
        (r"\bAC\b",           "armour class"),
        (r"\bHP\b",           "hit points"),
        (r"\bXP\b",           "experience points"),
        (r"\bDC\s*(\d+)\b",   lambda m: f"difficulty {m.group(1)}"),
        (r"\bCR\s*(\d+)\b",   lambda m: f"challenge rating {m.group(1)}"),
        (r"\bNPC\b",          "N P C"),
        (r"\bDM\b",           "Dungeon Master"),
        (r"\bPC\b",           "player character"),
        (r"\bAoE\b",          "area of effect"),
        (r"\bDoT\b",          "damage over time"),
        (r"\bToHit\b",        "to hit"),
        # Conditions (expand for TTS naturalness)
        (r"\bcon\. check\b",  "constitution check"),
        (r"\bstr\. check\b",  "strength check"),
        (r"\bdex\. check\b",  "dexterity check"),
        # Common shorthand
        (r"\bshort rest\b",   "short rest"),   # fine as-is
        (r"\blong rest\b",    "long rest"),
        (r"\bbonus action\b", "bonus action"),
        (r"\bfree action\b",  "free action"),
        (r"\bopportunity attack\b", "opportunity attack"),
    ]

    for pattern, replacement in replacements:
        if callable(replacement):
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        else:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    # "+3 to hit" → "plus three to hit"
    text = re.sub(r"\+(\d+)\s+to hit", lambda m: f"plus {m.group(1)} to hit", text)
    # Plain "+5" in isolation → "plus five"
    text = re.sub(r"\+(\d+)\b", lambda m: f"plus {m.group(1)}", text)

    return text


# ── Stat names ────────────────────────────────────────────────────────────

def _fix_stat_names(text: str) -> str:
    stats = {
        r"\bSTR\b": "Strength",
        r"\bDEX\b": "Dexterity",
        r"\bCON\b": "Constitution",
        r"\bINT\b": "Intelligence",
        r"\bWIS\b": "Wisdom",
        r"\bCHA\b": "Charisma",
    }
    for pattern, word in stats.items():
        text = re.sub(pattern, word, text)
    return text


# ── Proper nouns TTS tends to mangle ─────────────────────────────────────

def _fix_proper_nouns(text: str) -> str:
    nouns = {
        r"\bElminster\b":    "El-min-ster",
        r"\bFaerûn\b":       "Fay-roon",
        r"\bWaterdeep\b":    "Water-deep",
        r"\bBaldur's Gate\b":"Baldurs Gate",
        r"\bMindflayer\b":   "mind flayer",
        r"\bMind Flayer\b":  "mind flayer",
        r"\bIllithid\b":     "il-ith-id",
        r"\bBeholder\b":     "be-holder",
        r"\bDrow\b":         "Drow",       # already fine, just keep consistent
        r"\bGithyanki\b":    "Gith-yan-ki",
        r"\bGithzerai\b":    "Gith-zer-eye",
        r"\bYuanti\b":       "You-an-ti",
        r"\bYuan-ti\b":      "You-an-ti",
        r"\bModron\b":       "Mod-ron",
        r"\bSlaad\b":        "Slaad",
        r"\bFjord\b":        "Fyord",
    }
    for pattern, replacement in nouns.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


# ── Final cleanup ─────────────────────────────────────────────────────────

def _clean_up(text: str) -> str:
    # Remove orphaned brackets like [auto] or [tool] that may have leaked
    text = re.sub(r"\[(auto|tool|dm system|campaign state)[^\]]*\]", "", text, flags=re.IGNORECASE)
    # Collapse multiple spaces
    text = re.sub(r"  +", " ", text)
    # Collapse multiple newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
