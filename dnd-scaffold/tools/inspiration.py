"""
dnd-inspiration — tools

Tracks player inspiration — who has it, when it was used, narrative
prompts to award it, and usage history. Inspiration state is injected
into every prompt so Remmi never forgets to flag unspent inspiration
at dramatic moments.

Stored in plugin state under key "inspiration:{campaign_id}".
"""

from core.plugin_loader import plugin_loader
import json
import logging

logger = logging.getLogger("dnd-inspiration")

DEFAULT_CAMPAIGN_ID = "default"


def _get_campaign_id(config=None) -> str:
    try:
        campaign_state = plugin_loader.get_plugin_state("dnd-campaign")
        return campaign_state.get("active_campaign", DEFAULT_CAMPAIGN_ID)
    except Exception:
        return DEFAULT_CAMPAIGN_ID


def _state():
    return plugin_loader.get_plugin_state("dnd-scaffold")


def _load_all(config=None):
    campaign_id = _get_campaign_id(config)
    raw = _state().get(f"inspiration:{campaign_id}")
    if not raw:
        return {}
    return json.loads(raw) if isinstance(raw, str) else raw


def _save_all(data: dict, config=None):
    campaign_id = _get_campaign_id(config)
    _state().save(f"inspiration:{campaign_id}", json.dumps(data))


def inspiration_award(
    character_name: str,
    reason: str = "",
    session: str = ""
) -> str:
    """
    Award inspiration to a character.

    Args:
        character_name: Name of the character receiving inspiration
        reason: Why it was awarded (e.g. "great roleplay at the council meeting")
        session: Optional session identifier

    Returns:
        Confirmation message.
    """
    all_data = _load_all()
    key = character_name.strip().lower().replace(" ", "_")

    all_data[key] = {
        "character_name": character_name,
        "has_inspiration": True,
        "awarded_on_session": session,
        "awarded_for_reason": reason,
        "used": False,
        "used_in_combat": None,
        "used_on_roll": None,
    }
    _save_all(all_data)

    reason_str = f" ({reason})" if reason else ""
    return f"⭐ {character_name} has been awarded inspiration.{reason_str}"


def inspiration_use(
    character_name: str,
    roll_description: str = "",
    notes: str = ""
) -> str:
    """
    Record that a character spent their inspiration.

    Args:
        character_name: Name of the character using inspiration
        roll_description: What roll it was used on (e.g. "persuasion check to calm the guard")
        notes: Optional outcome notes

    Returns:
        Confirmation with usage details.
    """
    all_data = _load_all()
    key = character_name.strip().lower().replace(" ", "_")

    if key not in all_data or not all_data[key].get("has_inspiration"):
        return f"{character_name} doesn't have inspiration to spend."

    entry = all_data[key]
    entry["has_inspiration"] = False
    entry["used"] = True
    entry["used_on_roll"] = roll_description
    entry["used_notes"] = notes

    _save_all(all_data)

    roll_str = f" on {roll_description}" if roll_description else ""
    notes_str = f" Outcome: {notes}" if notes else ""
    return f"⭐ {character_name} spent inspiration{roll_str}.{notes_str}"


def inspiration_grant_if_none(
    character_name: str,
    reason: str = ""
) -> str:
    """
    Grant inspiration to a character only if they don't already have it.
    Use this to avoid duplicate awards.

    Args:
        character_name: Name of the character
        reason: Why it was awarded (if granted)

    Returns:
        Confirmation or skip message.
    """
    all_data = _load_all()
    key = character_name.strip().lower().replace(" ", "_")

    if key in all_data and all_data[key].get("has_inspiration"):
        return f"⏭️ {character_name} already has inspiration. Use inspiration_use first."

    return inspiration_award(character_name, reason)


def inspiration_reset(character_name: str) -> str:
    """
    Clear inspiration state for a character (start of new session).

    Args:
        character_name: Name of the character

    Returns:
        Confirmation.
    """
    all_data = _load_all()
    key = character_name.strip().lower().replace(" ", "_")

    if key in all_data:
        all_data[key]["has_inspiration"] = False
        all_data[key]["used"] = False
        all_data[key]["used_in_combat"] = None
        all_data[key]["used_on_roll"] = None
        _save_all(all_data)

    return f"🔄 {character_name}'s inspiration has been reset."


def inspiration_list(active_only: bool = True) -> str:
    """
    List all characters and their inspiration state.

    Args:
        active_only: If True, only show characters who currently have inspiration

    Returns:
        Formatted list of characters and their inspiration state.
    """
    all_data = _load_all()

    if not all_data:
        return "No inspiration tracked yet. Use inspiration_award to give a character inspiration."

    lines = ["⭐ Inspiration Tracker:"]
    has_any = False

    for entry in all_data.values():
        name = entry.get("character_name", "?")
        has_it = entry.get("has_inspiration", False)

        if active_only and not has_it:
            continue

        has_any = True
        reason = entry.get("awarded_for_reason", "")
        reason_str = f" — awarded for: {reason}" if reason else ""

        if has_it:
            lines.append(f"  ⭐ {name} has inspiration{reason_str}")
        else:
            lines.append(f"  — {name} (no inspiration){reason_str}")

    if active_only and not has_any:
        return "No characters currently have inspiration. Use inspiration_award to grant some."

    return "\n".join(lines)


def inspiration_history(character_name: str = "") -> str:
    """
    Get usage history for a character, or all characters if no name given.

    Args:
        character_name: Optional character name to filter by

    Returns:
        Usage history.
    """
    all_data = _load_all()

    if character_name:
        key = character_name.strip().lower().replace(" ", "_")
        entries = [all_data[key]] if key in all_data else []
    else:
        entries = list(all_data.values())

    if not entries:
        return "No inspiration history found."

    lines = ["📜 Inspiration History:"]
    for e in entries:
        name = e.get("character_name", "?")
        current = "⭐ has inspiration" if e.get("has_inspiration") else "— no inspiration"
        reason = e.get("awarded_for_reason", "")
        reason_str = f" (awarded: {reason})" if reason else ""
        roll = e.get("used_on_roll", "")
        roll_str = f" — used on: {roll}" if roll else " — never used"

        lines.append(f"  {name}: {current}{reason_str}{roll_str}")

    return "\n".join(lines)


def inspiration_prompt() -> str:
    """
    Return a short prompt inject listing which characters currently have
    inspiration. Called by the prompt_inject hook.

    Returns:
        One-line inspiration status for injection.
    """
    all_data = _load_all()
    with_insp = [e["character_name"] for e in all_data.values() if e.get("has_inspiration")]

    if not with_insp:
        return ""
    return f"⭐ Characters with inspiration: {', '.join(with_insp)}"


TOOLS = [
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "inspiration_award",
            "description": "Award inspiration to a character. Use this when a player does something exceptional — great roleplay, a clever idea, heroic sacrifice, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "character_name": {"type": "string", "description": "Name of the character receiving inspiration"},
                    "reason": {"type": "string", "description": "Why inspiration was awarded (e.g. 'great roleplay at the council meeting'). Default: ''"},
                    "session": {"type": "string", "description": "Optional session identifier. Default: ''"}
                },
                "required": ["character_name"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "inspiration_use",
            "description": "Record that a character spent their inspiration on a roll.",
            "parameters": {
                "type": "object",
                "properties": {
                    "character_name": {"type": "string", "description": "Name of the character using inspiration"},
                    "roll_description": {"type": "string", "description": "What roll it was used on (e.g. 'persuasion check to calm the guard'). Default: ''"},
                    "notes": {"type": "string", "description": "Optional outcome notes. Default: ''"}
                },
                "required": ["character_name"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "inspiration_grant_if_none",
            "description": "Grant inspiration only if the character doesn't already have it. Use this to avoid duplicate awards.",
            "parameters": {
                "type": "object",
                "properties": {
                    "character_name": {"type": "string", "description": "Name of the character"},
                    "reason": {"type": "string", "description": "Why inspiration was awarded (if granted). Default: ''"}
                },
                "required": ["character_name"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "inspiration_reset",
            "description": "Clear inspiration state for a character at the start of a new session.",
            "parameters": {
                "type": "object",
                "properties": {
                    "character_name": {"type": "string", "description": "Name of the character"}
                },
                "required": ["character_name"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "inspiration_list",
            "description": "List all characters and their current inspiration state.",
            "parameters": {
                "type": "object",
                "properties": {
                    "active_only": {"type": "boolean", "description": "If True, only show characters who currently have inspiration. Default: True"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "inspiration_history",
            "description": "Get inspiration usage history for a character or all characters.",
            "parameters": {
                "type": "object",
                "properties": {
                    "character_name": {"type": "string", "description": "Optional character name to filter by. Default: ''"}
                },
                "required": []
            }
        }
    },
]


def execute(function_name, arguments, config):
    if function_name == 'inspiration_award':
        return inspiration_award(
            character_name=arguments.get('character_name', ''),
            reason=arguments.get('reason', ''),
            session=arguments.get('session', '')
        ), True

    if function_name == 'inspiration_use':
        return inspiration_use(
            character_name=arguments.get('character_name', ''),
            roll_description=arguments.get('roll_description', ''),
            notes=arguments.get('notes', '')
        ), True

    if function_name == 'inspiration_grant_if_none':
        return inspiration_grant_if_none(
            character_name=arguments.get('character_name', ''),
            reason=arguments.get('reason', '')
        ), True

    if function_name == 'inspiration_reset':
        return inspiration_reset(character_name=arguments.get('character_name', '')), True

    if function_name == 'inspiration_list':
        return inspiration_list(active_only=arguments.get('active_only', True)), True

    if function_name == 'inspiration_history':
        return inspiration_history(character_name=arguments.get('character_name', '')), True

    return f"Unknown function: {function_name}", False
