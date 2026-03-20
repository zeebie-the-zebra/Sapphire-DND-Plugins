"""
dnd-npc-relations — tools

Tracks party reputation with named NPCs and factions. Stored separately
from dnd-npcs (which handles NPC lore/description) — this plugin owns
the *relationship* layer: attitude, history notes, and trust level.

Attitude scale:
  hostile (-2) | unfriendly (-1) | neutral (0) | friendly (1) | ally (2)

Supports multi-campaign: each campaign has its own relations namespace.
"""

from core.plugin_loader import plugin_loader
import json

_ATTITUDE_LABELS = {-2: "hostile", -1: "unfriendly", 0: "neutral", 1: "friendly", 2: "ally"}
_ATTITUDE_VALUES = {v: k for k, v in _ATTITUDE_LABELS.items()}

DEFAULT_CAMPAIGN_ID = "default"


def _get_campaign_id(config=None) -> str:
    """Get current campaign ID, defaulting to 'default' for backward compatibility."""
    from core.plugin_loader import plugin_loader

    try:
        campaign_state = plugin_loader.get_plugin_state("dnd-campaign")
        campaign_id = campaign_state.get("active_campaign", DEFAULT_CAMPAIGN_ID)
        if campaign_id:
            return campaign_id
    except Exception:
        pass

    return DEFAULT_CAMPAIGN_ID


def _migrate_if_needed(campaign_id: str):
    """Migrate legacy relations data to campaign scope if needed."""
    state = _state()
    migration_key = f"_legacy_migrated_{campaign_id}"

    if state.get(migration_key):
        return

    # Check for legacy data
    legacy = state.get("relations_index")
    if legacy:
        try:
            data = json.loads(legacy) if isinstance(legacy, str) else legacy
            if data:
                state.save(f"relations_index:{campaign_id}", legacy if isinstance(legacy, str) else json.dumps(data))
                state.save(migration_key, True)
        except Exception:
            pass


def _state():
    return plugin_loader.get_plugin_state("dnd-npc-relations")


def _load_all(config=None):
    """Return dict of all tracked entities for the current campaign: {name_lower: data_dict}"""
    campaign_id = _get_campaign_id(config)
    state = _state()

    # Migrate legacy data if needed
    _migrate_if_needed(campaign_id)

    # Try campaign-scoped data first
    raw = state.get(f"relations_index:{campaign_id}")
    if raw is not None:
        try:
            return json.loads(raw) if isinstance(raw, str) else raw
        except Exception:
            return {}

    # Fall back to legacy data for backward compatibility
    raw = state.get("relations_index")
    if not raw:
        return {}
    try:
        return json.loads(raw) if isinstance(raw, str) else raw
    except Exception:
        return {}


def _save_all(data: dict, config=None):
    campaign_id = _get_campaign_id(config)
    _state().save(f"relations_index:{campaign_id}", json.dumps(data))


def _key(name: str) -> str:
    return name.strip().lower().replace(" ", "_")


def relation_set(
    name: str,
    attitude: str = "neutral",
    notes: str = "",
    entity_type: str = "npc",
    tags: str = ""
) -> str:
    """
    Create or fully update a relationship entry for an NPC or faction.

    Args:
        name: NPC or faction name (e.g. "Petra", "City Guard", "Sea Prince")
        attitude: hostile | unfriendly | neutral | friendly | ally
        notes: Key history with this NPC — promises made, grudges, favours owed
        entity_type: npc | faction
        tags: Comma-separated location/scene tags for injection filtering
              (e.g. "rusty_flagon,harbor_district"). Leave empty to always inject.

    Returns:
        Confirmation string.
    """
    if attitude not in _ATTITUDE_VALUES:
        return f"ERROR: attitude must be one of: {', '.join(_ATTITUDE_VALUES.keys())}"

    all_data = _load_all()
    k = _key(name)
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []

    all_data[k] = {
        "name": name,
        "attitude": attitude,
        "attitude_score": _ATTITUDE_VALUES[attitude],
        "notes": notes,
        "entity_type": entity_type,
        "tags": tag_list
    }
    _save_all(all_data)
    return f"✅ {name} ({entity_type}) — attitude: {attitude}. Notes saved."


def relation_update(
    name: str,
    attitude: str = None,
    notes: str = None,
    append_note: str = None
) -> str:
    """
    Update attitude or notes for an existing NPC/faction. Use append_note to
    add to history without overwriting existing notes.

    Args:
        name: NPC or faction name (must already exist — use relation_set to create)
        attitude: New attitude (optional) — hostile | unfriendly | neutral | friendly | ally
        notes: Replace notes entirely (optional)
        append_note: Append to existing notes (optional, preferred over notes for incremental updates)

    Returns:
        Updated record summary.
    """
    all_data = _load_all()
    k = _key(name)

    if k not in all_data:
        return f"ERROR: '{name}' not found. Use relation_set to create them first."

    entry = all_data[k]

    if attitude is not None:
        if attitude not in _ATTITUDE_VALUES:
            return f"ERROR: attitude must be one of: {', '.join(_ATTITUDE_VALUES.keys())}"
        old = entry["attitude"]
        entry["attitude"] = attitude
        entry["attitude_score"] = _ATTITUDE_VALUES[attitude]

    if notes is not None:
        entry["notes"] = notes

    if append_note:
        existing = entry.get("notes", "")
        entry["notes"] = f"{existing} | {append_note}".strip(" |")

    all_data[k] = entry
    _save_all(all_data)

    return (
        f"✅ {entry['name']} updated. "
        f"Attitude: {entry['attitude']}. "
        f"Notes: {entry['notes'] or '(none)'}"
    )


def relation_get(name: str) -> str:
    """
    Get the relationship record for a named NPC or faction.

    Args:
        name: NPC or faction name

    Returns:
        Full relationship record or not-found message.
    """
    all_data = _load_all()
    k = _key(name)

    if k not in all_data:
        return f"'{name}' not found in relations tracker. Add them with relation_set."

    e = all_data[k]
    tags_str = ", ".join(e.get("tags", [])) or "all scenes"
    return (
        f"📋 {e['name']} ({e['entity_type']})\n"
        f"  Attitude: {e['attitude']}\n"
        f"  Notes: {e.get('notes') or '(none)'}\n"
        f"  Scene tags: {tags_str}"
    )


def relation_list(attitude_filter: str = "", entity_type: str = "") -> str:
    """
    List all tracked NPCs/factions, optionally filtered.

    Args:
        attitude_filter: Filter by attitude (e.g. "hostile" shows only hostile entities)
        entity_type: Filter by type — "npc" or "faction"

    Returns:
        Formatted list of all matching entries.
    """
    all_data = _load_all()
    if not all_data:
        return "No relationships tracked yet. Use relation_set to add NPCs or factions."

    entries = list(all_data.values())

    if attitude_filter:
        entries = [e for e in entries if e["attitude"] == attitude_filter]
    if entity_type:
        entries = [e for e in entries if e["entity_type"] == entity_type]

    if not entries:
        return "No entries match the given filters."

    # Sort by attitude score (hostile first, ally last)
    entries.sort(key=lambda e: e.get("attitude_score", 0))

    lines = [f"📋 Relations ({len(entries)} entries):"]
    for e in entries:
        tag_str = f" [{', '.join(e.get('tags', []))}]" if e.get("tags") else ""
        note_preview = (e.get("notes") or "")[:60]
        if len(e.get("notes", "")) > 60:
            note_preview += "..."
        lines.append(f"  {e['name']} — {e['attitude']}{tag_str}: {note_preview or '(no notes)'}")

    return "\n".join(lines)


def relation_delete(name: str) -> str:
    """
    Remove a relationship record.

    Args:
        name: NPC or faction name to remove

    Returns:
        Confirmation or not-found message.
    """
    all_data = _load_all()
    k = _key(name)

    if k not in all_data:
        return f"'{name}' not found in relations tracker."

    del all_data[k]
    _save_all(all_data)
    return f"🗑️ Removed '{name}' from relations tracker."


TOOLS = [
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "relation_set",
            "description": "Create or fully update a relationship entry for an NPC or faction. Attitude scale: hostile | unfriendly | neutral | friendly | ally.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "NPC or faction name (e.g. 'Petra', 'City Guard', 'Sea Prince')"},
                    "attitude": {"type": "string", "description": "Attitude: hostile | unfriendly | neutral | friendly | ally. Default: neutral"},
                    "notes": {"type": "string", "description": "Key history with this NPC — promises made, grudges, favours owed. Default: ''"},
                    "entity_type": {"type": "string", "description": "Type: npc | faction. Default: npc"},
                    "tags": {"type": "string", "description": "Comma-separated location/scene tags for injection filtering. Default: ''"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "relation_update",
            "description": "Update attitude or notes for an existing NPC/faction. Use append_note to add to history without overwriting.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "NPC or faction name (must already exist — use relation_set to create)"},
                    "attitude": {"type": "string", "description": "New attitude: hostile | unfriendly | neutral | friendly | ally"},
                    "notes": {"type": "string", "description": "Replace notes entirely"},
                    "append_note": {"type": "string", "description": "Append to existing notes (preferred for incremental updates)"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "relation_get",
            "description": "Get the relationship record for a named NPC or faction.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "NPC or faction name"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "relation_list",
            "description": "List all tracked NPCs/factions, optionally filtered by attitude or entity type.",
            "parameters": {
                "type": "object",
                "properties": {
                    "attitude_filter": {"type": "string", "description": "Filter by attitude (e.g. 'hostile' shows only hostile entities). Default: ''"},
                    "entity_type": {"type": "string", "description": "Filter by type: 'npc' or 'faction'. Default: ''"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "relation_delete",
            "description": "Remove a relationship record.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "NPC or faction name to remove"}
                },
                "required": ["name"]
            }
        }
    },
]


def execute(function_name, arguments, config):
    if function_name == 'relation_set':
        return relation_set(
            name=arguments.get('name', ''),
            attitude=arguments.get('attitude', 'neutral'),
            notes=arguments.get('notes', ''),
            entity_type=arguments.get('entity_type', 'npc'),
            tags=arguments.get('tags', '')
        ), True

    if function_name == 'relation_update':
        return relation_update(
            name=arguments.get('name', ''),
            attitude=arguments.get('attitude'),
            notes=arguments.get('notes'),
            append_note=arguments.get('append_note')
        ), True

    if function_name == 'relation_get':
        return relation_get(name=arguments.get('name', '')), True

    if function_name == 'relation_list':
        return relation_list(
            attitude_filter=arguments.get('attitude_filter', ''),
            entity_type=arguments.get('entity_type', '')
        ), True

    if function_name == 'relation_delete':
        return relation_delete(name=arguments.get('name', '')), True

    return f"Unknown function: {function_name}", False
