"""
dnd-homebrew — Homebrew content manager

Stores and retrieves user-created D&D content: monsters, items, and spells.
Supports category filtering, tagging, and full-text search.
"""

import json
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger("dnd-homebrew")

DEFAULT_CAMPAIGN_ID = "default"

VALID_TYPES = {"monster", "item", "spell", "character"}
VALID_RARITIES = {"common", "uncommon", "rare", "very rare", "legendary", "artifact", "varies"}
VALID_MONSTER_TYPES = {
    "aberration", "beast", "celestial", "construct", "dragon",
    "elemental", "fey", "fiend", "giant", "humanoid", "monstrosity",
    "ooze", "plant", "undead"
}
VALID_SPELL_SCHOOLS = {
    "abjuration", "conjuration", "divination", "enchantment",
    "evocation", "illusion", "necromancy", "transmutation"
}


def _get_state():
    from core.plugin_loader import plugin_loader
    return plugin_loader.get_plugin_state("dnd-homebrew")


def _get_campaign_id(config=None) -> str:
    from core.plugin_loader import plugin_loader
    try:
        campaign_state = plugin_loader.get_plugin_state("dnd-campaign")
        campaign_id = campaign_state.get("active_campaign", DEFAULT_CAMPAIGN_ID)
        if campaign_id:
            return campaign_id
    except Exception:
        pass
    return DEFAULT_CAMPAIGN_ID


def _prof_bonus(level: int) -> int:
    """Proficiency bonus by level (PHB table)."""
    if level < 5:   return 2
    if level < 9:   return 3
    if level < 13:  return 4
    if level < 17:  return 5
    return 6


def _auto_create_character_entry(args: dict, campaign_id: str):
    """When linked_character is set, create the corresponding dnd-characters entry."""
    linked_name = args.get("linked_character", "").strip()
    if not linked_name:
        return

    try:
        from core.plugin_loader import plugin_loader
        char_state = plugin_loader.get_plugin_state("dnd-characters")
    except Exception:
        return  # dnd-characters not available

    # Load existing characters for this campaign
    campaign_chars = char_state.get(f"characters:{campaign_id}") or {}

    # Check if already exists (case-insensitive)
    key = linked_name.lower().strip()
    for k in campaign_chars:
        if k.lower() == key:
            return  # Already exists — don't overwrite

    # Map homebrew fields to dnd-characters character structure
    stats = args.get("character_stats", {})
    level = args.get("character_level", 1)

    char = {
        "name":             linked_name,
        "player":           "",
        "race":             args.get("character_race", ""),
        "class_name":       args.get("character_class", ""),
        "level":            level,
        "background":       args.get("character_background", ""),
        "alignment":        args.get("character_alignment", ""),
        "backstory":        args.get("content", ""),
        "hp_max":           args.get("character_hp", 10),
        "hp_current":       args.get("character_hp", 10),
        "hp_temp":          0,
        "ac":               args.get("character_ac", 10),
        "speed":            30,
        "str":              stats.get("str", 10),
        "dex":              stats.get("dex", 10),
        "con":              stats.get("con", 10),
        "int":              stats.get("int", 10),
        "wis":              stats.get("wis", 10),
        "cha":              stats.get("cha", 10),
        "proficiency_bonus": _prof_bonus(level),
        "spell_slots_max":     {},
        "spell_slots_current": {},
        "inventory":        [],
        "gold":             0,
        "conditions":       [],
        "death_saves":      {"successes": 0, "failures": 0},
        "created":          "",  # dnd-characters will fill this
        "user_controlled":  False,
    }

    campaign_chars[linked_name] = char
    char_state.save(f"characters:{campaign_id}", campaign_chars)
    logger.info(f"[dnd-homebrew] Auto-created dnd-characters entry: {linked_name}")


def _load_all(campaign_id: str) -> Dict[str, Any]:
    """Load all homebrew entries for a campaign."""
    state = _get_state()
    all_data = state.get(f"homebrew:{campaign_id}")
    if all_data:
        return all_data
    return {}


def _save_all(campaign_id: str, data: Dict[str, Any]):
    """Save all homebrew entries for a campaign."""
    state = _get_state()
    state.save(f"homebrew:{campaign_id}", data)


def _make_entry_id(name: str, type_: str) -> str:
    """Create a lowercase hyphenated entry ID."""
    return f"{type_.lower()}:{name.lower().replace(' ', '-')}"


def _find_entry(name: str, type_: str, data: Dict[str, Any]) -> Optional[tuple]:
    """Find entry by name (case-insensitive) and type. Returns (id, entry) or None."""
    name_lower = name.lower()
    type_lower = type_.lower()
    for entry_id, entry in data.items():
        if entry.get("type", "").lower() == type_lower and entry.get("name", "").lower() == name_lower:
            return entry_id, entry
    return None


# ── Tool handlers ──────────────────────────────────────────────────────────────

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "homebrew_add",
            "description": "Add a new homebrew monster, item, spell, or character to the campaign's homebrew library.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the homebrew entry (e.g. 'Crimson Drake', 'Blade of the Fallen', 'Aldric the Bold')"},
                    "type": {"type": "string", "enum": ["monster", "item", "spell", "character"], "description": "Category of homebrew content"},
                    "category": {"type": "string", "description": "Sub-type (e.g. dragon/undead for monsters, longsword/potion for items, evocation/3rd-level for spells)"},
                    "description": {"type": "string", "description": "Brief description of this entry"},
                    "content": {"type": "string", "description": "The full stat block, item description, spell details, or character backstory. Can be multi-paragraph."},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Optional tags for filtering and search (e.g. ['fire', 'sentient', 'legendary'])"},
                    "cr": {"type": "string", "description": "Challenge Rating (monsters only, e.g. '5', '1/2', '21')"},
                    "rarity": {"type": "string", "description": "Rarity (items only): common, uncommon, rare, very rare, legendary, artifact"},
                    "spell_level": {"type": "integer", "description": "Spell level (spells only, 0-9, where 0 is a cantrip)"},
                    "character_class": {"type": "string", "description": "Class (characters only, e.g. 'Fighter', 'Wizard', 'Rogue')"},
                    "character_level": {"type": "integer", "description": "Level (characters only, 1-20)"},
                    "character_race": {"type": "string", "description": "Race (characters only, e.g. 'Human', 'Elf', 'Dwarf')"},
                    "character_hp": {"type": "integer", "description": "Max HP (characters only)"},
                    "character_ac": {"type": "integer", "description": "Armor Class (characters only)"},
                    "character_stats": {"type": "object", "description": "Ability scores (characters only), e.g. {'str': 16, 'dex': 14, 'con': 15, 'int': 10, 'wis': 12, 'cha': 8}"},
                    "character_alignment": {"type": "string", "description": "Alignment (characters only, e.g. 'Lawful Good', 'Chaotic Neutral')"},
                    "character_background": {"type": "string", "description": "Background (characters only, e.g. 'Soldier', 'Sage', 'Criminal')"},
                    "linked_character": {"type": "string", "description": "Name of the corresponding dnd-characters entry if this character is combat-tracked (characters only). Use this to link to the full character sheet for HP/inventory management."},
                },
                "required": ["name", "type", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "homebrew_get",
            "description": "Retrieve a specific homebrew entry by name and type.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the homebrew entry"},
                    "type": {"type": "string", "enum": ["monster", "item", "spell", "character"], "description": "Category of homebrew content"},
                },
                "required": ["name", "type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "homebrew_list",
            "description": "List all homebrew entries of a type, optionally filtered by category or tags.",
            "parameters": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["monster", "item", "spell", "character"], "description": "Category to list"},
                    "category": {"type": "string", "description": "Optional sub-category filter"},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Return only entries that have ALL of these tags"},
                },
                "required": ["type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "homebrew_update",
            "description": "Update fields on an existing homebrew entry.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the homebrew entry to update"},
                    "type": {"type": "string", "enum": ["monster", "item", "spell"], "description": "Category of the entry"},
                    "description": {"type": "string", "description": "New brief description"},
                    "content": {"type": "string", "description": "New full content/stat block"},
                    "category": {"type": "string", "description": "New sub-category"},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "New tags list"},
                    "cr": {"type": "string", "description": "New Challenge Rating (monsters only)"},
                    "rarity": {"type": "string", "description": "New rarity (items only)"},
                    "spell_level": {"type": "integer", "description": "New spell level (spells only)"},
                    "character_class": {"type": "string", "description": "New class (characters only)"},
                    "character_level": {"type": "integer", "description": "New level (characters only)"},
                    "character_race": {"type": "string", "description": "New race (characters only)"},
                    "character_hp": {"type": "integer", "description": "New max HP (characters only)"},
                    "character_ac": {"type": "integer", "description": "New AC (characters only)"},
                    "character_stats": {"type": "object", "description": "New ability scores (characters only)"},
                    "character_alignment": {"type": "string", "description": "New alignment (characters only)"},
                    "character_background": {"type": "string", "description": "New background (characters only)"},
                    "linked_character": {"type": "string", "description": "New linked dnd-characters name (characters only)"},
                },
                "required": ["name", "type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "homebrew_delete",
            "description": "Delete a homebrew entry from the library.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the homebrew entry to delete"},
                    "type": {"type": "string", "enum": ["monster", "item", "spell", "character"], "description": "Category of the entry"},
                },
                "required": ["name", "type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "homebrew_search",
            "description": "Search homebrew entries by name, description, or tags.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search term to match against name, description, and tags"},
                    "type": {"type": "string", "enum": ["monster", "item", "spell", "character"], "description": "Optional: limit search to one category"},
                    "limit": {"type": "integer", "description": "Maximum results to return (default 10)"},
                },
                "required": ["query"]
            }
        }
    },
]


def execute(function_name, arguments, config):
    """Dispatch tool calls."""

    # Resolve campaign
    campaign_id = _get_campaign_id(config)

    if function_name == "homebrew_add":
        return _homebrew_add(arguments, campaign_id)

    if function_name == "homebrew_get":
        return _homebrew_get(arguments, campaign_id)

    if function_name == "homebrew_list":
        return _homebrew_list(arguments, campaign_id)

    if function_name == "homebrew_update":
        return _homebrew_update(arguments, campaign_id)

    if function_name == "homebrew_delete":
        return _homebrew_delete(arguments, campaign_id)

    if function_name == "homebrew_search":
        return _homebrew_search(arguments, campaign_id)

    return f"Unknown homebrew tool: {function_name}", False


def _homebrew_add(args: dict, campaign_id: str) -> tuple:
    name = args.get("name", "").strip()
    type_ = args.get("type", "").lower()
    category = args.get("category", "")
    description = args.get("description", "")
    content = args.get("content", "")
    tags = args.get("tags", [])
    cr = args.get("cr", "")
    rarity = args.get("rarity", "")
    spell_level = args.get("spell_level")

    # Character-specific fields
    character_class = args.get("character_class", "")
    character_level = args.get("character_level")
    character_race = args.get("character_race", "")
    character_hp = args.get("character_hp")
    character_ac = args.get("character_ac")
    character_stats = args.get("character_stats", {})
    character_alignment = args.get("character_alignment", "")
    character_background = args.get("character_background", "")
    linked_character = args.get("linked_character", "")

    if not name:
        return "Name is required.", False
    if not type_ or type_ not in VALID_TYPES:
        return f"Type must be one of: {', '.join(VALID_TYPES)}", False
    if not content:
        return "Content (stat block / item details / spell / backstory) is required.", False

    data = _load_all(campaign_id)

    # Check for duplicate
    existing = _find_entry(name, type_, data)
    if existing:
        entry_id, _ = existing
        return f"A homebrew {type_} named '{name}' already exists (ID: {entry_id}). Use homebrew_update to modify it.", False

    entry_id = _make_entry_id(name, type_)

    entry = {
        "name": name,
        "type": type_,
        "category": category,
        "description": description,
        "content": content,
        "tags": tags,
        "cr": cr,
        "rarity": rarity,
        "spell_level": spell_level,
    }

    # Add character fields if applicable
    if type_ == "character":
        if character_class:
            entry["character_class"] = character_class
        if character_level is not None:
            entry["character_level"] = character_level
        if character_race:
            entry["character_race"] = character_race
        if character_hp is not None:
            entry["character_hp"] = character_hp
        if character_ac is not None:
            entry["character_ac"] = character_ac
        if character_stats:
            entry["character_stats"] = character_stats
        if character_alignment:
            entry["character_alignment"] = character_alignment
        if character_background:
            entry["character_background"] = character_background
        if linked_character:
            entry["linked_character"] = linked_character

    data[entry_id] = entry
    _save_all(campaign_id, data)

    # Auto-create the linked dnd-characters entry
    if type_ == "character" and linked_character:
        _auto_create_character_entry(args, campaign_id)

    extra = []
    if cr:
        extra.append(f"CR {cr}")
    if rarity:
        extra.append(rarity)
    if category:
        extra.append(category)
    if type_ == "character":
        parts = []
        if character_class:
            parts.append(character_class)
        if character_level:
            parts.append(f"Lv{character_level}")
        if character_race:
            parts.append(character_race)
        if parts:
            extra.append(" ".join(parts))
    extra_str = f" ({', '.join(extra)})" if extra else ""

    linked_note = ""
    if type_ == "character" and linked_character:
        linked_note = f" | dnd-characters entry '{linked_character}' auto-created for combat tracking."

    logger.info(f"[dnd-homebrew] Added {type_}: {name}{extra_str} in campaign {campaign_id}")
    return f"✅ Added **{name}** ({type_}) to the homebrew library{extra_str}.{linked_note}", True


def _homebrew_get(args: dict, campaign_id: str) -> tuple:
    name = args.get("name", "").strip()
    type_ = args.get("type", "").lower()

    if not name or not type_:
        return "Name and type are required for homebrew_get.", False

    data = _load_all(campaign_id)
    result = _find_entry(name, type_, data)

    if not result:
        return f"No homebrew {type_} found named '{name}'.", False

    entry_id, entry = result

    lines = [f"## {entry['name']}"]
    if entry.get("category"):
        lines.append(f"**Category:** {entry['category']}")
    if entry.get("rarity"):
        lines.append(f"**Rarity:** {entry['rarity']}")
    if entry.get("cr"):
        lines.append(f"**CR:** {entry['cr']}")
    if entry.get("spell_level") is not None:
        level = entry["spell_level"]
        suffix = " (cantrip)" if level == 0 else f" (level {level})"
        lines.append(f"**Level:** {level}{suffix}")

    # Character-specific fields
    if type_ == "character":
        if entry.get("character_class"):
            lines.append(f"**Class:** {entry['character_class']}")
        if entry.get("character_level"):
            lines.append(f"**Level:** {entry['character_level']}")
        if entry.get("character_race"):
            lines.append(f"**Race:** {entry['character_race']}")
        if entry.get("character_alignment"):
            lines.append(f"**Alignment:** {entry['character_alignment']}")
        if entry.get("character_background"):
            lines.append(f"**Background:** {entry['character_background']}")
        if entry.get("linked_character"):
            lines.append(f"**Linked dnd-characters:** {entry['linked_character']} *(use character_* tools for full combat tracking)*")
        if entry.get("character_hp") is not None:
            lines.append(f"**HP:** {entry['character_hp']}")
        if entry.get("character_ac") is not None:
            lines.append(f"**AC:** {entry['character_ac']}")
        if entry.get("character_stats"):
            stats = entry["character_stats"]
            stat_lines = []
            for abbr, val in stats.items():
                modifier = (val - 10) // 2
                sign = "+" if modifier >= 0 else str(modifier)
                stat_lines.append(f"{abbr.upper()}: {val} ({sign})")
            lines.append(f"**Stats:** {', '.join(stat_lines)}")

    if entry.get("description"):
        lines.append(f"\n{entry['description']}")
    if entry.get("tags"):
        lines.append(f"**Tags:** {', '.join(entry['tags'])}")
    lines.append(f"\n---")
    lines.append(entry["content"])

    return "\n".join(lines), True


def _homebrew_list(args: dict, campaign_id: str) -> tuple:
    type_ = args.get("type", "").lower()
    category = args.get("category", "").lower()
    tags = args.get("tags", [])

    if not type_ or type_ not in VALID_TYPES:
        return f"Type must be one of: {', '.join(VALID_TYPES)}", False

    data = _load_all(campaign_id)

    results = []
    for entry_id, entry in data.items():
        if entry.get("type", "").lower() != type_:
            continue
        if category and entry.get("category", "").lower() != category:
            continue
        if tags:
            entry_tags = [t.lower() for t in entry.get("tags", [])]
            if not all(t.lower() in entry_tags for t in tags):
                continue
        results.append((entry_id, entry))

    if not results:
        return f"No homebrew {type_}(s) found.", True

    # Sort by name
    results.sort(key=lambda x: x[1].get("name", ""))

    lines = [f"## Homebrew {type_.title()}s"]
    if category:
        lines.append(f"*Category: {category}*")
    if tags:
        lines.append(f"*Tags: {', '.join(tags)}*")
    lines.append("")

    for entry_id, entry in results:
        name = entry.get("name", entry_id)
        parts = [f"**{name}**"]
        if entry.get("category"):
            parts.append(entry["category"])
        if entry.get("rarity"):
            parts.append(entry["rarity"])
        if entry.get("cr"):
            parts.append(f"CR {entry['cr']}")
        if entry.get("spell_level") is not None:
            lvl = entry["spell_level"]
            parts.append(f"Lv{lvl}" if lvl > 0 else "cantrip")
        # Character-specific
        if type_ == "character":
            char_parts = []
            if entry.get("character_race"):
                char_parts.append(entry["character_race"])
            if entry.get("character_class"):
                char_parts.append(entry["character_class"])
            if entry.get("character_level"):
                char_parts.append(f"Lv{entry['character_level']}")
            if char_parts:
                parts.append(" ".join(char_parts))
        if entry.get("description"):
            desc = entry["description"]
            parts.append(f"— {desc[:80]}{'...' if len(desc) > 80 else ''}")
        lines.append(" • ".join(parts))

    lines.append(f"\n*{len(results)} total*")
    return "\n".join(lines), True


def _homebrew_update(args: dict, campaign_id: str) -> tuple:
    name = args.get("name", "").strip()
    type_ = args.get("type", "").lower()

    if not name or not type_:
        return "Name and type are required.", False

    data = _load_all(campaign_id)
    result = _find_entry(name, type_, data)

    if not result:
        return f"No homebrew {type_} found named '{name}'.", False

    entry_id, entry = result

    # Allowed update fields
    for field in ("description", "content", "category", "tags", "cr", "rarity", "spell_level"):
        if field in args and args[field] is not None:
            entry[field] = args[field]
    # Character-specific fields
    for field in ("character_class", "character_level", "character_race",
                   "character_hp", "character_ac", "character_stats",
                   "character_alignment", "character_background", "linked_character"):
        if field in args and args[field] is not None:
            entry[field] = args[field]

    _save_all(campaign_id, data)
    logger.info(f"[dnd-homebrew] Updated {type_}: {name} in campaign {campaign_id}")
    return f"✅ Updated **{entry['name']}** ({type_}).", True


def _homebrew_delete(args: dict, campaign_id: str) -> tuple:
    name = args.get("name", "").strip()
    type_ = args.get("type", "").lower()

    if not name or not type_:
        return "Name and type are required.", False

    data = _load_all(campaign_id)
    result = _find_entry(name, type_, data)

    if not result:
        return f"No homebrew {type_} found named '{name}'.", False

    entry_id, entry = result
    del data[entry_id]
    _save_all(campaign_id, data)

    logger.info(f"[dnd-homebrew] Deleted {type_}: {name} from campaign {campaign_id}")
    return f"🗑️ Deleted **{entry['name']}** ({type_}).", True


def _homebrew_search(args: dict, campaign_id: str) -> tuple:
    query = args.get("query", "").lower().strip()
    type_ = args.get("type", "").lower()
    limit = min(args.get("limit", 10) or 10, 50)

    if not query:
        return "Search query is required.", False

    data = _load_all(campaign_id)
    results = []

    for entry_id, entry in data.items():
        if type_ and entry.get("type", "").lower() != type_:
            continue

        # Score the match
        score = 0
        name_lower = entry.get("name", "").lower()
        desc_lower = entry.get("description", "").lower()
        content_lower = entry.get("content", "").lower()
        tags = entry.get("tags", [])

        if query in name_lower:
            score += 10
        if query in desc_lower:
            score += 5
        if query in content_lower[:200]:  # Boost front-matter match
            score += 2
        if any(query in tag.lower() for tag in tags):
            score += 3

        if score > 0:
            results.append((score, entry_id, entry))

    if not results:
        return f"No homebrew entries found matching '{query}'.", True

    # Sort by score descending, then name
    results.sort(key=lambda x: (-x[0], x[2].get("name", "")))

    lines = [f"## Homebrew Search: \"{query}\""]
    if type_:
        lines.append(f"*Type: {type_}*")
    lines.append("")

    for score, entry_id, entry in results[:limit]:
        name = entry.get("name", entry_id)
        parts = [f"**{name}** ({entry.get('type', '')})"]
        if entry.get("category"):
            parts.append(entry["category"])
        if entry.get("description"):
            desc = entry["description"]
            parts.append(f"— {desc[:60]}{'...' if len(desc) > 60 else ''}")
        lines.append(" • ".join(parts))

    total = len(results)
    shown = min(len(results), limit)
    lines.append(f"\n*Showing {shown} of {total} result{'s' if total != 1 else ''}*")

    return "\n".join(lines), True
