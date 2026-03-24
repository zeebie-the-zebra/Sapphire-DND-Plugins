"""
dnd-scaffold/hooks/ooc_filter.py — from dnd-voice-polish

post_llm: strips OOC markers and character-breaking text from LLM output.
pre_tts: D&D pronunciation fixes for TTS engine.
"""

import re
from datetime import datetime


# ── post_llm: OOC filter ──────────────────────────────────────────────────────

STRIP_LINE_PATTERNS = [
    r"^as an ai\b",
    r"^i('m| am) an ai\b",
    r"^note:\s*(this is a fictional|this is just|remember that)",
    r"^\*?as the (dungeon master|dm)[,:]?\*?$",
    r"^\[dm narration",
    r"^\[tool (call|result)",
    r"^i'll (now )?(describe|narrate|continue)",
    r"^let me (describe|continue|narrate)",
    r"^\*clears throat\*",
    r"^\*checks (notes|map|sheet)\*$",
    r"^as remmi,?\s*(i |the dm )",
]

COMPILED = [re.compile(p, re.IGNORECASE) for p in STRIP_LINE_PATTERNS]


# ── Narrative watchdog helpers ───────────────────────────────────────────────

# Item acquisition: "takes", "finds", "picks up", "receives", "gets", "grabs", "loots", "obtains"
WD_ITEM_ACQUIRE_PATTERNS = [
    # takes/finds/picks up + a/the/an + item
    re.compile(r'\b(takes|finds|picks\s+up|receives|gets\s+grabbed?\s+loots?|obtains?|hands?\s+you|gives?\s+you|awardeds?\s+you)\s+(?:a|an|the|their|her|his|its)\s+([A-Za-z][A-Za-z\s\-]{1,50})', re.I),
    # item after "you now have", "you now possess"
    re.compile(r'\b(you\s+(?:now\s+)?(?:have|possess|carry))\s+(?:a|an|the)?\s*([A-Za-z][A-Za-z\s\-]{1,30})', re.I),
    # chest/room/loot reveals
    re.compile(r'\b(chest|room|body|loot|treasure|chest\s+contains?|chest\s+holds?)\s+(?:contains?|holds?|reveals?)\s+(?:a|an|the)?\s*([A-Za-z][A-Za-z\s\-]{1,40})', re.I),
    # "among the loot was" / "among the items was"
    re.compile(r'\b(?:among\s+(?:the\s+)?(?:loot|items|treasures?))\s+(?:was|were)\s+(?:a|an|the)?\s*([A-Za-z][A-Za-z\s\-]{1,40})', re.I),
]

# Item loss/removal: "sells", "loses", "drops", "destroys", "consumes", "gives away"
WD_ITEM_LOSS_PATTERNS = [
    re.compile(r'\b(sells?|loses?|drops?|destroys?|consumes?|gives?\s+(?:away|her|him|them)|loses?|get rid of|parts with)\s+(?:a|an|the|his|her|their)?\s*([A-Za-z][A-Za-z\s\-]{1,40})', re.I),
    re.compile(r'\b(?:the\s+)?([A-Za-z][A-Za-z\s\-]{1,40})\s+(?:is\s+)?(?:destroyed|consumed|lost|stolen|sold)', re.I),
]

# Gold/coin patterns
WD_GOLD_PATTERNS = [
    re.compile(r'\b(\d+)\s*gp\b'),
    re.compile(r'\b(\d+)\s*gold\s*pieces?', re.I),
    re.compile(r'\b(\d+)\s*pieces?\s*of\s*gold', re.I),
    re.compile(r'\b(\d+)\s*coins?\s*(?:of\s+gold)?', re.I),
]

# HP damage patterns: "takes X damage", "hit for Y", "deals Z damage"
WD_HP_DAMAGE_PATTERNS = [
    re.compile(r'\b([A-Z][a-z]+)\s+(?:takes?|suffers?|loses?|receives?)\s+(\d+)\s*(?:\s+damage)?\s*(?:hit|damage)?', re.I),
    re.compile(r'\b([A-Z][a-z]+)\s+(?:is\s+)?(?:hit|struck|wounded)\s+(?:for|with|by)?\s*(\d+)\s*(?:\s+damage)?', re.I),
    re.compile(r'\b(?:deals?|dealt)\s+(\d+)\s*(?:\s+damage)?\s*(?:to|on|against)?\s*([A-Z][a-z]+)', re.I),
    re.compile(r'\b([A-Z][a-z]+)\s+(?:loses?|drops?\s+to)\s+(?:[\d]+(?:\s+hp)?|(\d+)\s+hp)', re.I),
]

# HP healing patterns
WD_HP_HEAL_PATTERNS = [
    re.compile(r'\b([A-Z][a-z]+)\s+(?:heals?|recovers?|restores?)\s+(?:for)?\s*(\d+)\s*(?:\s+hp)?', re.I),
    re.compile(r'\b(?:heals?|recovers?|restores?)\s+([A-Z][a-z]+)\s+(?:for)?\s*(\d+)\s*(?:\s+hp)?', re.I),
    re.compile(r'\b(\d+)\s*hp\s+(?:restored|healed|recovered)', re.I),
    re.compile(r'\b([A-Z][a-z]+)\s+(?:is\s+)?(?:now\s+)?(?:at\s+)?(\d+)\s*(?:\s+hp)?\s*(?:again|restored|healed)', re.I),
]

# Condition patterns
WD_CONDITION_PATTERNS = [
    re.compile(r'\b([A-Z][a-z]+)\s+(?:is\s+)?(?:now\s+)?(poisoned|blinded|stunned|paralyzed|charmed|frightened|unconscious|incapacitated|restrained|grappled|invisible|petrified|prone)\b', re.I),
    re.compile(r'\b([A-Z][a-z]+)\s+(?:becomes?|falls?\s+(?:unconscious|to\s+the\s+ground))\b', re.I),
    re.compile(r'\b(poisoned|blinded|stunned|paralyzed|charmed|frightened|unconscious|incapacitated|restrained|grappled|invisible|petrified|prone)\b', re.I),
]

# Spell slot usage
WD_SPELL_CAST_PATTERNS = [
    re.compile(r'\b([A-Z][a-z]+)\s+(?:casts?|uses?)\s+(?:a\s+)?(?:(\d+)(?:st|nd|rd|th)\s+)?(?:level\s+)?([A-Za-z\s]+?)(?:\s+spell|\s+at|\s+using|,|\.|!|\n|$)', re.I),
    re.compile(r'\bcasts?\s+(?:a\s+)?(?:(\d+)(?:st|nd|rd|th)\s+)?(?:level\s+)?([A-Za-z]+(?:\s+[A-Za-z]+)?)\s+(?:spell|at\s+)', re.I),
]

# Resource usage patterns
WD_RESOURCE_USE_PATTERNS = [
    re.compile(r'\b([A-Z][a-z]+)\s+(?:activates?|enters?|uses?)\s+(?:their?\s+)?(?:Rage|Wild\s+Shape|Ki|Bardic\s+Inspiration|Channel\s+Divinity|Second\s+Wind|Action\s+Surge|Lay\s+on\s+Hands|Sorcery\s+Points|Mystic\s+Arcanum)', re.I),
    re.compile(r'\b([A-Z][a-z]+)\s+(?:spends?|uses?|activates?)\s+(\d+)\s+(?:ki\s+points?|sorcery\s+points?|rages?)', re.I),
]

# XP award patterns
WD_XP_PATTERNS = [
    re.compile(r'\b(\d+)\s*xp\b', re.I),
    re.compile(r'\b(\d+)\s*experience\s*points?', re.I),
]


def _wd_get_state():
    from core.plugin_loader import plugin_loader
    return plugin_loader.get_plugin_state("dnd-scaffold")


def _wd_is_dnd_active():
    try:
        state = _wd_get_state()
        return state.get("dnd_active", False)
    except Exception:
        return False


def _wd_get_recent_tool_calls(state, count=10):
    """Get the most recent tool calls from the audit log."""
    try:
        audit_log = state.get("audit_log") or []
        return audit_log[-count:]
    except Exception:
        return []


def _wd_normalize_item(text):
    """Clean up extracted item text to a reasonable item name."""
    text = text.strip().rstrip('.,!?;:"\'')
    text = re.sub(r'\s+', ' ', text)
    words = text.split()
    if len(words) > 8:
        text = ' '.join(words[:8])
    return text


def _wd_normalize_character(text):
    """Clean up extracted character name."""
    text = text.strip().rstrip('.,!?;:"\'')
    return text.split()[0] if text else text


def _wd_log_detection(state, warnings):
    """Log detected events for debugging/auditing."""
    try:
        log = state.get("watchdog_log") or []
        log.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "warnings": warnings,
        })
        if len(log) > 50:
            log = log[-50:]
        state.save("watchdog_log", log)
    except Exception:
        pass


def post_llm(event):
    """Strip OOC lines from LLM response, then run narrative watchdog scan."""
    text = event.response or ""
    if not text:
        return

    # ── 1. OOC stripping ────────────────────────────────────────────────────
    lines = text.split("\n")
    filtered = []
    stripped = 0

    for line in lines:
        stripped_line = line.strip()
        if any(p.match(stripped_line) for p in COMPILED):
            stripped += 1
            continue
        filtered.append(line)

    if stripped > 0:
        result = "\n".join(filtered)
        result = re.sub(r"\n{3,}", "\n\n", result).strip()
        event.response = result

    # ── 2. Narrative watchdog scan ──────────────────────────────────────────
    response = event.response or ""
    if not response or len(response) < 20:
        return

    if not _wd_is_dnd_active():
        return

    state = _wd_get_state()
    recent_calls = _wd_get_recent_tool_calls(state, count=8)

    recent_tools = {entry.get("fn", "") for entry in recent_calls}

    warnings = []

    # Check for item acquisition
    if "character_add_item" not in recent_tools:
        for pattern in WD_ITEM_ACQUIRE_PATTERNS:
            for match in pattern.finditer(response):
                raw = match.group(0)
                item = _wd_normalize_item(match.group(2) if match.lastindex >= 2 else (match.group(1) if match.lastindex >= 1 else ""))
                if item and len(item) > 1 and not any(skip in item.lower() for skip in ["you", "the", "a ", "an ", "their", "your", "hand", "way", "roll", "turn"]):
                    warnings.append(f"  • Item acquired: '{item}' — did you call character_add_item?")
                    break

    # Check for gold
    if "character_add_item" not in recent_tools:
        for pattern in WD_GOLD_PATTERNS:
            for match in pattern.finditer(response):
                amount = int(match.group(1))
                if amount > 0:
                    warnings.append(f"  • Gold mentioned: {amount} gp — did you call character_add_item for gold?")
                    break

    # Check for item loss/removal
    if "character_remove_item" not in recent_tools:
        for pattern in WD_ITEM_LOSS_PATTERNS:
            for match in pattern.finditer(response):
                raw = match.group(0)
                item = _wd_normalize_item(match.group(2) if match.lastindex >= 2 else (match.group(1) if match.lastindex >= 1 else ""))
                if item and len(item) > 1 and not any(skip in item.lower() for skip in ["you", "the", "a ", "an ", "their", "your", "hand", "way", "roll"]):
                    warnings.append(f"  • Item lost/disposed: '{item}' — did you call character_remove_item?")
                    break

    # Check for HP damage
    if "character_damage" not in recent_tools:
        for pattern in WD_HP_DAMAGE_PATTERNS:
            for match in pattern.finditer(response):
                if match.lastindex >= 2:
                    char = _wd_normalize_character(match.group(1))
                    amount = match.group(2)
                    if char and amount and char.lower() not in ["the", "a", "an", "they"]:
                        warnings.append(f"  • Damage dealt to {char}: {amount} HP — did you call character_damage?")
                elif match.lastindex == 1:
                    amount = match.group(1)
                    warnings.append(f"  • HP damage mentioned ({amount}) — did you call character_damage?")
                break

    # Check for HP healing
    if "character_heal" not in recent_tools:
        for pattern in WD_HP_HEAL_PATTERNS:
            for match in pattern.finditer(response):
                if match.lastindex >= 2:
                    char = _wd_normalize_character(match.group(1))
                    amount = match.group(2)
                    if char and amount:
                        warnings.append(f"  • Healing for {char}: {amount} HP — did you call character_heal?")
                elif match.lastindex == 1:
                    amount = match.group(1)
                    warnings.append(f"  • HP healing mentioned ({amount}) — did you call character_heal?")
                break

    # Check for conditions
    if "character_set_condition" not in recent_tools:
        for pattern in WD_CONDITION_PATTERNS:
            for match in pattern.finditer(response):
                if match.lastindex >= 2:
                    char = _wd_normalize_character(match.group(1))
                    cond = match.group(2)
                    if char and cond:
                        warnings.append(f"  • Condition applied: {char} is {cond} — did you call character_set_condition?")
                elif match.lastindex == 1:
                    cond = match.group(1)
                    warnings.append(f"  • Condition mentioned ({cond}) — did you call character_set_condition?")
                break

    # Check for spell casting
    if "character_use_spell_slot" not in recent_tools:
        for pattern in WD_SPELL_CAST_PATTERNS:
            for match in pattern.finditer(response):
                char = _wd_normalize_character(match.group(1)) if match.lastindex >= 1 else None
                level = match.group(2) if match.lastindex >= 2 else "1"
                spell = match.group(3) if match.lastindex >= 3 else ""
                if char:
                    warnings.append(f"  • Spell cast by {char} (L{level or 1}) — did you call character_use_spell_slot?")
                    break

    # Check for resource usage
    if "resource_use" not in recent_tools:
        for pattern in WD_RESOURCE_USE_PATTERNS:
            for match in pattern.finditer(response):
                char = _wd_normalize_character(match.group(1)) if match.lastindex >= 1 else None
                if char:
                    warnings.append(f"  • Class resource used by {char} — did you call resource_use?")
                    break

    # Check for XP awards
    if "xp_add" not in recent_tools:
        for pattern in WD_XP_PATTERNS:
            for match in pattern.finditer(response):
                xp = int(match.group(1))
                if xp > 0 and xp < 1000000:
                    warnings.append(f"  • XP awarded: {xp} XP — did you call xp_add?")
                    break

    if not warnings:
        return

    # De-duplicate and append warning
    warning_header = (
        "\n\n⚠️ **PENDING STATE CHANGES DETECTED**\n"
        "The following events were narrated but not yet recorded in game state.\n"
        "Game state MUST match narrative — call the required tools to record these changes:\n"
    )
    warning_footer = (
        "\n**Rules:** Narrating an event is NOT the same as recording it. "
        "The game engine tracks state — your prose alone does not change it. "
        "Call the missing tools NOW to synchronize state."
    )

    unique_warnings = []
    seen = set()
    for w in warnings:
        key = w.split("—")[0].strip() if "—" in w else w
        if key not in seen and len(unique_warnings) < 10:
            seen.add(key)
            unique_warnings.append(w)

    if unique_warnings:
        warning_text = warning_header + "\n".join(unique_warnings) + warning_footer
        event.response = event.response + warning_text

        try:
            _wd_log_detection(state, unique_warnings)
        except Exception:
            pass

        # ── Save violation state for the commit gate ────────────────────────
        try:
            from core.plugin_loader import plugin_loader
            state = plugin_loader.get_plugin_state("dnd-scaffold")
            state.save("pending_violations", True)
            state.save("violation_details", unique_warnings)
            state.save("violation_timestamp", datetime.now().strftime("%H:%M:%S"))
        except Exception:
            pass
    else:
        # No new violations — check if we were waiting for a correction
        # If correction_active was set, the LLM must have resolved them
        try:
            from core.plugin_loader import plugin_loader
            state = plugin_loader.get_plugin_state("dnd-scaffold")
            if state.get("correction_active", False):
                # Violations were corrected — clear all commit-gate flags
                state.save("pending_violations", False)
                state.save("violation_details", [])
                state.save("tts_blocked", False)
                state.save("correction_active", False)
                state.save("correction_prompt", "")
        except Exception:
            pass


# ── pre_tts: D&D pronunciation fixes ─────────────────────────────────────────

def pre_tts(event):
    """Fix D&D notation for TTS rendering."""
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


def _strip_markdown(text: str) -> str:
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*{1,3}([^*]+)\*{1,3}", r"\1", text)
    text = re.sub(r"_{1,3}([^_]+)_{1,3}", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"^\s*[-•]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)
    return text


def _fix_dice_notation(text: str) -> str:
    def replace_dice(m):
        count = m.group(1) or "1"
        sides = m.group(2)
        modifier = m.group(3) or ""
        count_w = _num_to_word(count)
        sides_w = _num_to_word(sides)
        result = f"{count_w} dee {sides_w}"
        if modifier:
            sign = "plus" if modifier[0] == "+" else "minus"
            num = modifier[1:]
            result += f" {sign} {num}"
        return result

    text = re.sub(r"(\d+)?[dD](\d+)([+-]\d+)?", replace_dice, text)
    return text


def _num_to_word(n: str) -> str:
    words = {
        "1": "one", "2": "two", "3": "three", "4": "four",
        "6": "six", "8": "eight", "10": "ten", "12": "twelve",
        "20": "twenty", "100": "one hundred",
    }
    return words.get(n, n)


def _fix_abbreviations(text: str) -> str:
    replacements = [
        (r"\bAC\b", "armour class"),
        (r"\bHP\b", "hit points"),
        (r"\bXP\b", "experience points"),
        (r"\bDC\s*(\d+)\b", lambda m: f"difficulty {m.group(1)}"),
        (r"\bCR\s*(\d+)\b", lambda m: f"challenge rating {m.group(1)}"),
        (r"\bNPC\b", "N P C"),
        (r"\bDM\b", "Dungeon Master"),
        (r"\bPC\b", "player character"),
        (r"\bAoE\b", "area of effect"),
        (r"\bDoT\b", "damage over time"),
        (r"\bToHit\b", "to hit"),
        (r"\bcon\. check\b", "constitution check"),
        (r"\bstr\. check\b", "strength check"),
        (r"\bdex\. check\b", "dexterity check"),
        (r"\blong rest\b", "long rest"),
        (r"\bshort rest\b", "short rest"),
        (r"\bbonus action\b", "bonus action"),
        (r"\bfree action\b", "free action"),
        (r"\bopportunity attack\b", "opportunity attack"),
    ]

    for pattern, replacement in replacements:
        if callable(replacement):
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        else:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    text = re.sub(r"\+(\d+)\s+to hit", lambda m: f"plus {m.group(1)} to hit", text)
    text = re.sub(r"\+(\d+)\b", lambda m: f"plus {m.group(1)}", text)

    return text


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


def _fix_proper_nouns(text: str) -> str:
    nouns = {
        r"\bElminster\b": "El-min-ster",
        r"\bFaerûn\b": "Fay-roon",
        r"\bWaterdeep\b": "Water-deep",
        r"\bBaldur's Gate\b": "Baldurs Gate",
        r"\bMindflayer\b": "mind flayer",
        r"\bMind Flayer\b": "mind flayer",
        r"\bIllithid\b": "il-ith-id",
        r"\bBeholder\b": "be-holder",
        r"\bDrow\b": "Drow",
        r"\bGithyanki\b": "Gith-yan-ki",
        r"\bGithzerai\b": "Gith-zer-eye",
        r"\bYuanti\b": "You-an-ti",
        r"\bYuan-ti\b": "You-an-ti",
        r"\bModron\b": "Mod-ron",
        r"\bSlaad\b": "Slaad",
        r"\bFjord\b": "Fyord",
    }
    for pattern, replacement in nouns.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def _clean_up(text: str) -> str:
    text = re.sub(r"\[(auto|tool|dm system|campaign state)[^\]]*\]", "", text, flags=re.IGNORECASE)
    text = re.sub(r"  +", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
