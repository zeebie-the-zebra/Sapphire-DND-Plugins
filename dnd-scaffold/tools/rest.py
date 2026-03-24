"""
dnd-rest — tools

Manages long vs short rest mechanics. Tracks what resources reset on
which rest type, hit dice expenditure during a rest, and whether
characters have benefited from a long rest today. Works with
dnd-characters and dnd-resources.

Stored in plugin state under "rest_state:{campaign_id}".
"""

from core.plugin_loader import plugin_loader
import json
import logging

logger = logging.getLogger("dnd-rest")

# Import resource_restore so rest_long/rest_short can auto-restore resources
from tools.resources import resource_restore

DEFAULT_CAMPAIGN_ID = "default"

# Resources that reset on each rest type
SHORT_REST_RESETS = [
    "action_surge",    # Fighter
    "second_wind",     # Fighter
    "ki",              # Monk (minimum 2)
    "sorcery_points",  # Sorcerer (must spend HD to recover all)
    "bardic_inspiration",  # Bard (if using optional rule)
    "channel_divinity",    # Cleric/Paladin (if using optional rule)
    "wild_shape",      # Druid (minimum 2, restored on long rest)
    "rage",            # Barbarian (minimum 2)
    "lay_on_hands",    # Paladin
    "hunter_prey",     # Ranger (optional)
    "metamorphosis",   # Warlock (optional)
]

LONG_REST_RESETS = [
    "hp",              # All: restore to max
    "hit_dice",        # All: recover half HD
    "spell_slots",     # All casters
    " ki",             # Monk: all ki
    "rage",            # Barbarian: all rages
    " bardic_inspiration",  # Bard: all uses
    " channel_divinity",    # Cleric/Paladin: all uses
    "wild_shape",      # Druid: all uses
    "action_surge",    # Fighter: all uses
    "second_wind",     # Fighter: all uses
    "sorcery_points",  # Sorcerer: all points
    "lay_on_hands",    # Paladin: all
    "metamorphosis",   # Warlock: all
    "exhaustion",      # All: reduce by 1
]


def _get_campaign_id(config=None) -> str:
    try:
        campaign_state = plugin_loader.get_plugin_state("dnd-campaign")
        return campaign_state.get("active_campaign", DEFAULT_CAMPAIGN_ID)
    except Exception:
        return DEFAULT_CAMPAIGN_ID


def _state():
    return plugin_loader.get_plugin_state("dnd-rest")


def _load(config=None):
    campaign_id = _get_campaign_id(config)
    raw = _state().get(f"rest_state:{campaign_id}")
    if not raw:
        return _default_state()
    return json.loads(raw) if isinstance(raw, str) else raw


def _save(data: dict, config=None):
    campaign_id = _get_campaign_id(config)
    _state().save(f"rest_state:{campaign_id}", json.dumps(data))


def _default_state():
    return {
        "rest_history": [],  # list of past rests
        "long_rest_today": {},  # character_name -> True if already long-rested today
        "short_rest_today": {},  # character_name -> count of short rests today
        "hit_dice_expended": {},  # character_name -> HD used this rest period
        "current_day": 0,
    }


def rest_long(
    character_names: str = "",
    day: int = None,
    recover_hp: bool = True,
    resources: dict = None,
    config=None
) -> str:
    """
    Begin a long rest (6+ hours). All characters recover HP to max,
    recover half their max hit dice, and reset most resources.

    Args:
        character_names: Comma-separated list of character names resting
        day: Current in-game day number (from dnd-time). Default: None
        recover_hp: Whether to restore HP to max. Default: True
        resources: Optional dict of {character_name: {resource_name: current_value}} for
                   resources tracked by dnd-resources. Values are used to set
                   new totals after rest.

    Returns:
        Long rest summary for each character.
    """
    if not character_names:
        return "ERROR: character_names is required (comma-separated list)."

    names = [n.strip() for n in character_names.split(",") if n.strip()]
    data = _load()
    current_day = day if day is not None else data.get("current_day", 0)

    lines = [f"🌙 Long Rest — Day {current_day}"]

    for name in names:
        key = name.strip().lower().replace(" ", "_")

        # Mark long rest done today
        if "long_rest_today" not in data:
            data["long_rest_today"] = {}
        data["long_rest_today"][key] = True

        # Reset short rest counter
        if "short_rest_today" not in data:
            data["short_rest_today"] = {}
        data["short_rest_today"][key] = 0

        char_lines = [f"  🌙 {name}:"]

        if recover_hp:
            char_lines.append(f"    HP restored to maximum")

        # Auto-restore resources via dnd-resources
        try:
            res_result = resource_restore(name, "long", config)
            if res_result and not res_result.startswith("No resources"):
                # Strip the header line since we embed into a longer response
                res_lines = res_result.split("\n")
                if len(res_lines) > 1:
                    for line in res_lines[1:]:
                        if line.strip():
                            char_lines.append(f"    {line.strip()}")
        except Exception:
            pass

        # Hit dice recovery (half, rounded down)
        hd_used = data.get("hit_dice_expended", {}).get(key, 0)
        if hd_used > 0:
            recovered_hd = hd_used // 2
            data["hit_dice_expended"][key] = hd_used - recovered_hd
            char_lines.append(f"    Hit Dice: recovered {recovered_hd} HD ({data['hit_dice_expended'][key]} remaining)")
        else:
            char_lines.append(f"    Hit Dice: no expenditure to recover")

        # Resource summary if provided
        if resources and name in resources:
            char_res = resources[name]
            short_rest = [r for r in SHORT_REST_RESETS if r.strip() in char_res]
            if short_rest:
                char_lines.append(f"    Short-rest resources: {', '.join(short_rest)} reset to max")
            long_rest = [r for r in LONG_REST_RESETS if r.strip() in char_res]
            if long_rest:
                char_lines.append(f"    Long-rest resources: {', '.join(long_rest)} reset to max")

        lines.append("\n".join(char_lines))

    data["current_day"] = current_day

    # Record history
    data["rest_history"].append({
        "type": "long",
        "day": current_day,
        "characters": names,
    })
    # Keep last 20 entries
    data["rest_history"] = data["rest_history"][-20:]

    _save(data)
    return "\n".join(lines)


def rest_short(
    character_names: str = "",
    resources: dict = None,
    config=None
) -> str:
    """
    Begin a short rest (1 hour). Characters can spend Hit Dice to
    recover HP, and some class resources reset.

    Args:
        character_names: Comma-separated list of character names resting
        resources: Optional dict of {character_name: {resource_name: current_value}}

    Returns:
        Short rest summary.
    """
    if not character_names:
        return "ERROR: character_names is required (comma-separated list)."

    names = [n.strip() for n in character_names.split(",") if n.strip()]
    data = _load()

    lines = ["⏸️ Short Rest"]

    for name in names:
        key = name.strip().lower().replace(" ", "_")

        # Increment short rest count
        if "short_rest_today" not in data:
            data["short_rest_today"] = {}
        data["short_rest_today"][key] = data["short_rest_today"].get(key, 0) + 1

        char_lines = [f"  ⏸️ {name}:"]

        # Short rest resources
        if resources and name in resources:
            char_res = resources[name]
            short_resets = [r.strip() for r in SHORT_REST_RESETS if r.strip() in char_res]
            if short_resets:
                char_lines.append(f"    Resources reset: {', '.join(short_resets)}")
            else:
                char_lines.append(f"    No short-rest resources to reset")
        else:
            char_lines.append(f"    (resource tracking not provided)")

        # Auto-restore short-rest resources via dnd-resources
        try:
            res_result = resource_restore(name, "short", config)
            if res_result and not res_result.startswith("No resources"):
                res_lines = res_result.split("\n")
                if len(res_lines) > 1:
                    for line in res_lines[1:]:
                        if line.strip():
                            char_lines.append(f"    {line.strip()}")
        except Exception:
            pass

        char_lines.append(f"    HP: spend Hit Dice to recover (roll each die + CON mod)")

        lines.append("\n".join(char_lines))

    _save(data)
    return "\n".join(lines)


def rest_spend_hit_dice(
    character_name: str,
    dice_count: int = 1,
    con_modifier: int = 0,
    current_hd: int = None,
    max_hd: int = None
) -> str:
    """
    Record hit dice spent during a short rest to recover HP.

    Args:
        character_name: Character spending dice
        dice_count: Number of Hit Dice to spend. Default: 1
        con_modifier: Constitution modifier added to each die. Default: 0
        current_hd: Current hit dice available. Default: from state
        max_hd: Maximum hit dice (for display). Default: from state

    Returns:
        HP recovered and remaining HD.
    """
    data = _load()
    key = character_name.strip().lower().replace(" ", "_")

    if "hit_dice_expended" not in data:
        data["hit_dice_expended"] = {}

    # Track expended (used) HD
    expended = data["hit_dice_expended"].get(key, 0)
    available = (max_hd or 0) - expended

    if dice_count > available:
        return f"❌ {character_name} only has {available} Hit Dice available ({max_hd or '?'} max, {expended} already expended)."

    # Calculate HP recovered
    import random
    hp_recovered = sum(random.randint(1, 10) + con_modifier for _ in range(dice_count))

    data["hit_dice_expended"][key] = expended + dice_count
    remaining_hd = (max_hd or 0) - data["hit_dice_expended"][key]

    _save(data)

    mod_str = f"+{con_modifier}" if con_modifier >= 0 else str(con_modifier)
    return (
        f"🎲 {character_name} spent {dice_count} Hit Dice (1d10{mod_str} each)\n"
        f"   HP recovered: {hp_recovered} | Remaining HD: {remaining_hd}/{max_hd or '?'}"
    )


def rest_has_long_rested(character_name: str) -> str:
    """
    Check whether a character has already taken a long rest today.

    Args:
        character_name: Character to check

    Returns:
        Yes/no with context.
    """
    data = _load()
    key = character_name.strip().lower().replace(" ", "_")

    has_rested = data.get("long_rest_today", {}).get(key, False)
    short_rests = data.get("short_rest_today", {}).get(key, 0)
    current_day = data.get("current_day", 0)

    if has_rested:
        return f"✅ {character_name} has already long-rested today (day {current_day}). Another long rest requires a new day."
    return f"⏳ {character_name} has not long-rested today (day {current_day}). {short_rests} short rest(s) taken."


def rest_reset_day(day: int = None) -> str:
    """
    Reset rest tracking for a new day. Call this when the in-game day changes.

    Args:
        day: The new day number. Default: increments from current

    Returns:
        Confirmation.
    """
    data = _load()
    new_day = day if day is not None else data.get("current_day", 0) + 1

    # Clear long rest flags (they expire each day)
    data["long_rest_today"] = {}
    # Short rests DO carry over in some editions but we'll reset them too per RAW
    data["short_rest_today"] = {}
    data["current_day"] = new_day

    _save(data)
    return f"🔄 Rest tracking reset for day {new_day}."


def rest_history(count: int = 5) -> str:
    """
    Get recent rest history.

    Args:
        count: Number of past rests to show. Default: 5

    Returns:
        Recent rest events.
    """
    data = _load()
    history = data.get("rest_history", [])

    if not history:
        return "No rest history recorded."

    lines = ["📜 Recent Rest History:"]
    for entry in history[-count:]:
        chars = ", ".join(entry.get("characters", []))
        rtype = "🌙 Long" if entry.get("type") == "long" else "⏸️ Short"
        day = entry.get("day", "?")
        lines.append(f"  {rtype} Rest — Day {day}: {chars}")

    return "\n".join(lines)


def rest_status(character_name: str = "") -> str:
    """
    Get rest status for a character, or all tracked characters.

    Args:
        character_name: Optional specific character. If empty, shows all.

    Returns:
        Rest status summary.
    """
    data = _load()
    current_day = data.get("current_day", 0)

    if character_name:
        key = character_name.strip().lower().replace(" ", "_")
        has_long = data.get("long_rest_today", {}).get(key, False)
        short_rests = data.get("short_rest_today", {}).get(key, 0)
        hd_expended = data.get("hit_dice_expended", {}).get(key, 0)

        long_str = "✅ long-rested" if has_long else "⏳ not long-rested"
        return (
            f"🛏️ {character_name} — Day {current_day}\n"
            f"  {long_str} today | {short_rests} short rests | {hd_expended} HD expended"
        )

    # All characters
    all_keys = set(
        list(data.get("long_rest_today", {}).keys()) +
        list(data.get("short_rest_today", {}).keys()) +
        list(data.get("hit_dice_expended", {}).keys())
    )

    if not all_keys:
        return "No rest data tracked yet. Use rest_long or rest_short."

    lines = [f"🛏️ Rest Status — Day {current_day}"]
    for key in sorted(all_keys):
        has_long = data.get("long_rest_today", {}).get(key, False)
        short_rests = data.get("short_rest_today", {}).get(key, 0)
        hd_expended = data.get("hit_dice_expended", {}).get(key, 0)
        long_str = "✅" if has_long else "⏳"
        lines.append(f"  {long_str} {key}: {short_rests} short rests, {hd_expended} HD used")

    return "\n".join(lines)


TOOLS = [
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "rest_long",
            "description": "Begin a long rest (6+ hours). All characters recover HP to max, recover half their max hit dice, and reset most class resources.",
            "parameters": {
                "type": "object",
                "properties": {
                    "character_names": {"type": "string", "description": "Comma-separated list of character names resting"},
                    "day": {"type": "integer", "description": "Current in-game day number (from dnd-time). Default: None"},
                    "recover_hp": {"type": "boolean", "description": "Whether to restore HP to max. Default: True"},
                    "resources": {"type": "object", "description": "Optional dict of {character_name: {resource_name: current_value}} for resource tracking."}
                },
                "required": ["character_names"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "rest_short",
            "description": "Begin a short rest (1 hour). Characters can spend Hit Dice to recover HP and some class resources reset.",
            "parameters": {
                "type": "object",
                "properties": {
                    "character_names": {"type": "string", "description": "Comma-separated list of character names resting"},
                    "resources": {"type": "object", "description": "Optional dict of {character_name: {resource_name: current_value}} for resource tracking."}
                },
                "required": ["character_names"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "rest_spend_hit_dice",
            "description": "Record hit dice spent during a short rest to recover HP. Simulates rolling HD.",
            "parameters": {
                "type": "object",
                "properties": {
                    "character_name": {"type": "string", "description": "Character spending dice"},
                    "dice_count": {"type": "integer", "description": "Number of Hit Dice to spend. Default: 1"},
                    "con_modifier": {"type": "integer", "description": "Constitution modifier added to each die. Default: 0"},
                    "current_hd": {"type": "integer", "description": "Current hit dice available."},
                    "max_hd": {"type": "integer", "description": "Maximum hit dice (for display)."}
                },
                "required": ["character_name"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "rest_has_long_rested",
            "description": "Check whether a character has already taken a long rest today (per RAW: only one long rest per 24-hour period).",
            "parameters": {
                "type": "object",
                "properties": {
                    "character_name": {"type": "string", "description": "Character to check"}
                },
                "required": ["character_name"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "rest_reset_day",
            "description": "Reset rest tracking for a new in-game day. Call this when the day advances in dnd-time.",
            "parameters": {
                "type": "object",
                "properties": {
                    "day": {"type": "integer", "description": "The new day number. Default: increments from current"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "rest_history",
            "description": "Get recent rest history.",
            "parameters": {
                "type": "object",
                "properties": {
                    "count": {"type": "integer", "description": "Number of past rests to show. Default: 5"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "rest_status",
            "description": "Get rest status for a character or all tracked characters — long rest taken today, short rests today, HD expended.",
            "parameters": {
                "type": "object",
                "properties": {
                    "character_name": {"type": "string", "description": "Optional specific character. Default: ''"}
                },
                "required": []
            }
        }
    },
]


def execute(function_name, arguments, config):
    if function_name == 'rest_long':
        return rest_long(
            character_names=arguments.get('character_names', ''),
            day=arguments.get('day'),
            recover_hp=arguments.get('recover_hp', True),
            resources=arguments.get('resources'),
            config=config
        ), True

    if function_name == 'rest_short':
        return rest_short(
            character_names=arguments.get('character_names', ''),
            resources=arguments.get('resources'),
            config=config
        ), True

    if function_name == 'rest_spend_hit_dice':
        return rest_spend_hit_dice(
            character_name=arguments.get('character_name', ''),
            dice_count=arguments.get('dice_count', 1),
            con_modifier=arguments.get('con_modifier', 0),
            current_hd=arguments.get('current_hd'),
            max_hd=arguments.get('max_hd')
        ), True

    if function_name == 'rest_has_long_rested':
        return rest_has_long_rested(character_name=arguments.get('character_name', '')), True

    if function_name == 'rest_reset_day':
        return rest_reset_day(day=arguments.get('day')), True

    if function_name == 'rest_history':
        return rest_history(count=arguments.get('count', 5)), True

    if function_name == 'rest_status':
        return rest_status(character_name=arguments.get('character_name', '')), True

    return f"Unknown function: {function_name}", False
