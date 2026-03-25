"""
dnd-travel — tools

Overland travel logistics. Tracks march pace, exhaustion accumulation
over days, ration tracking, terrain-based travel times, and passage
through multiple terrain types. Complements dnd-weather and dnd-time.

Stored in plugin state under "travel_state:{campaign_id}".
"""

from core.plugin_loader import plugin_loader
import json
import logging

logger = logging.getLogger("dnd-travel")

DEFAULT_CAMPAIGN_ID = "default"

# Travel pace in miles per day at each setting, per PHB
# Format: {terrain: {pace: miles_per_day}}
TERRAIN_TRAVEL = {
    "road":      {"slow": 24, "normal": 30, "fast": 36},
    "grassland": {"slow": 24, "normal": 30, "fast": 36},
    "forest":    {"slow": 16, "normal": 24, "fast": 32},
    "hills":      {"slow": 20, "normal": 24, "fast": 30},
    "mountain":  {"slow": 12, "normal": 20, "fast": 24},
    "swamp":      {"slow": 12, "normal": 16, "fast": 20},
    "desert":     {"slow": 16, "normal": 20, "fast": 30},
    "arctic":     {"slow": 12, "normal": 16, "fast": 20},
    "coastal":    {"slow": 16, "normal": 20, "fast": 24},
    "underdark":  {"slow": 12, "normal": 16, "fast": 20},
    "water":      {"slow": 16, "normal": 24, "fast": 30},  # by boat
}

# Foraging success chance (percentage) by terrain, per PHB
FORAGE_CHANCE = {
    "forest":    50,
    "grassland": 40,
    "hills":     35,
    "swamp":     30,
    "desert":    10,
    "arctic":    5,
    "mountain":  20,
    "coastal":   20,
    "road":      60,
    "underdark": 0,
}

# Rations consumed per day per person
RATIONS_PER_DAY = 1

# Exhaustion levels and their effects
EXHAUSTION_EFFECTS = {
    1: "Disadvantage on ability checks",
    2: "Half speed",
    3: "Disadvantage on attack rolls and saving throws",
    4: "Max HP halved",
    5: "Speed reduced to 0",
    6: "Death",
}


def _get_campaign_id(config=None) -> str:
    try:
        campaign_state = plugin_loader.get_plugin_state("dnd-campaign")
        return campaign_state.get("active_campaign", DEFAULT_CAMPAIGN_ID)
    except Exception:
        return DEFAULT_CAMPAIGN_ID


def _state():
    return plugin_loader.get_plugin_state("dnd-scaffold")


def _load(config=None):
    campaign_id = _get_campaign_id(config)
    raw = _state().get(f"travel_state:{campaign_id}")
    if not raw:
        return _default_state()
    return json.loads(raw) if isinstance(raw, str) else raw


def _save(data: dict, config=None):
    campaign_id = _get_campaign_id(config)
    _state().save(f"travel_state:{campaign_id}", json.dumps(data))


def _default_state():
    return {
        "active_journey": None,
        "rations_used": {},
        "exhaustion": {},  # character_name -> exhaustion level
        "total_exhaustion_days": {},  # accumulated days at each level
        "last_travel_day": 0,
    }


def _pace_to_mph(pace: str) -> int:
    return {"slow": 0, "normal": 1, "fast": 2}.get(pace, 1)


def travel_start(
    destination: str,
    distance_miles: float,
    terrain: str = "road",
    pace: str = "normal",
    party_size: int = 4,
    days_per_rations: int = 1,
    current_day: int = None
) -> str:
    """
    Begin a new travel journey.

    Args:
        destination: Where the party is traveling to
        distance_miles: Total distance to destination
        terrain: Primary terrain type — road, grassland, forest, hills, mountain,
                 swamp, desert, arctic, coastal, underdark. Default: road
        pace: Travel pace — slow, normal, fast. Default: normal
        party_size: Number of party members consuming rations. Default: 4
        days_per_rations: How many days per ration unit each person. Default: 1
        current_day: Current in-game day number (from dnd-time). Default: 0

    Returns:
        Journey summary and expected arrival.
    """
    terrain = terrain.lower()
    pace = pace.lower()

    if terrain not in TERRAIN_TRAVEL:
        return f"ERROR: terrain must be one of: {', '.join(TERRAIN_TRAVEL.keys())}"
    if pace not in TERRAIN_TRAVEL[terrain]:
        return f"ERROR: pace must be one of: slow, normal, fast"

    miles_per_day = TERRAIN_TRAVEL[terrain][pace]
    days_needed = distance_miles / miles_per_day
    days_rounded = __import__("math").ceil(days_needed)

    rations_total = days_rounded * party_size * days_per_rations

    # Exhaustion risk at fast pace
    exhaustion_risk = ""
    if pace == "fast":
        days_until_exhaustion = int(10 / party_size) if party_size > 0 else 10
        exhaustion_risk = f" ⚠️ Fast pace: each party member gains 1 exhaustion after {max(1, days_until_exhaustion)} days."

    # Foraging info
    forage_pct = FORAGE_CHANCE.get(terrain, 0)
    forage_str = f" Foraging success: {forage_pct}% per day." if forage_pct > 0 else " No foraging possible."

    data = _load()
    data["active_journey"] = {
        "destination": destination,
        "distance_miles": distance_miles,
        "terrain": terrain,
        "pace": pace,
        "party_size": party_size,
        "days_per_rations": days_per_rations,
        "miles_per_day": miles_per_day,
        "days_needed": days_needed,
        "days_rounded": days_rounded,
        "rations_total": rations_total,
        "rations_used": 0,
        "days_traveled": 0,
        "start_day": current_day or 0,
    }
    _save(data)

    return (
        f"🗺️ Journey started: {destination}\n"
        f"  Distance: {distance_miles} miles | Terrain: {terrain} | Pace: {pace}\n"
        f"  Miles/day: {miles_per_day} | Days needed: ~{days_needed:.1f} ({days_rounded} days)\n"
        f"  Party size: {party_size} | Rations needed: {rations_total}\n"
        f"  Estimated arrival: day {(current_day or 0) + days_rounded}{exhaustion_risk}{forage_str}"
    )


def travel_advance(days: int = 1, rations_available: int = None) -> str:
    """
    Advance travel by a number of days. Consumes rations and may add exhaustion.

    Args:
        days: Number of days to advance. Default: 1
        rations_available: Total rations the party has. If provided, warns if running low.

    Returns:
        Progress update, rations consumed, exhaustion checks.
    """
    data = _load()
    journey = data.get("active_journey")

    if not journey:
        return "No active journey. Use travel_start first."

    party_size = journey.get("party_size", 4)
    terrain = journey.get("terrain", "road")
    pace = journey.get("pace", "normal")
    days_per_rations = journey.get("days_per_rations", 1)
    miles_per_day = journey.get("miles_per_day", 24)
    days_traveled = journey.get("days_traveled", 0)

    rations_consumed = days * party_size * days_per_rations
    miles_covered = days * miles_per_day
    new_days_traveled = days_traveled + days

    remaining_distance = journey["distance_miles"] - (days_traveled * miles_per_day)
    distance_after = max(0, remaining_distance - miles_covered)

    # Check for exhaustion on fast pace
    exhaustion_msgs = []
    new_exhaustion = {}

    if pace == "fast":
        for char_key, level in data.get("exhaustion", {}).items():
            if level < 6:
                new_level = min(6, level + 1)
                new_exhaustion[char_key] = new_level
                exhaustion_msgs.append(f"  ⚠️ {char_key} gained 1 exhaustion (now level {new_level}): {EXHAUSTION_EFFECTS.get(new_level, '')}")

    # If no active tracking yet, initialize
    if "exhaustion" not in data:
        data["exhaustion"] = {}

    for char_key, level in new_exhaustion.items():
        data["exhaustion"][char_key] = level

    journey["days_traveled"] = new_days_traveled
    journey["rations_used"] = journey.get("rations_used", 0) + rations_consumed

    # Check arrival
    arrived = distance_after <= 0
    if arrived:
        data["active_journey"] = None
        result = f"✅ Arrived at {journey['destination']} after {new_days_traveled} days!"
    else:
        remaining_days = remaining_distance / miles_per_day
        result = (
            f"🌄 Traveled {miles_covered} miles ({days} day{'s' if days > 1 else ''})\n"
            f"  {distance_after:.1f} miles remaining (~{remaining_days:.1f} days)\n"
            f"  Rations used: {journey['rations_used']}/{journey['rations_total']}"
        )

    # Ration warning
    if rations_available is not None:
        remaining_rations = rations_available - journey["rations_used"]
        if remaining_rations <= party_size * 2:
            exhaustion_msgs.insert(0, f"  ⚠️ Rations running low: only {remaining_rations} remaining ({party_size} needed/day)")

    if exhaustion_msgs:
        result += "\n" + "\n".join(exhaustion_msgs)

    _save(data)
    return result


def travel_add_exhaustion(character_name: str, levels: int = 1) -> str:
    """
    Manually add exhaustion levels to a character during travel.

    Args:
        character_name: Character affected
        levels: Number of levels to add. Default: 1

    Returns:
        Updated exhaustion state.
    """
    data = _load()
    key = character_name.strip().lower().replace(" ", "_")

    if "exhaustion" not in data:
        data["exhaustion"] = {}

    current = data["exhaustion"].get(key, 0)
    new_level = min(6, current + levels)
    data["exhaustion"][key] = new_level
    _save(data)

    if new_level >= 6:
        return f"☠️ {character_name} has reached exhaustion level 6 and is dead."
    if new_level >= 5:
        return f"🛑 {character_name} is at exhaustion level {new_level} — speed reduced to 0. {EXHAUSTION_EFFECTS[new_level]}"
    return f"😓 {character_name} exhaustion: {new_level}/6. {EXHAUSTION_EFFECTS.get(new_level, '')}"


def travel_remove_exhaustion(character_name: str, levels: int = 1) -> str:
    """
    Remove exhaustion levels (after a long rest).

    Args:
        character_name: Character recovering
        levels: Number of levels to remove. Default: 1

    Returns:
        Updated exhaustion state.
    """
    data = _load()
    key = character_name.strip().lower().replace(" ", "_")

    if "exhaustion" not in data:
        data["exhaustion"] = {}

    current = data["exhaustion"].get(key, 0)
    new_level = max(0, current - levels)
    data["exhaustion"][key] = new_level
    _save(data)

    if new_level == 0:
        return f"✅ {character_name} has no exhaustion."
    return f"😌 {character_name} exhaustion: {new_level}/6. {EXHAUSTION_EFFECTS.get(new_level, '')}"


def travel_get() -> str:
    """
    Get the current travel state — active journey progress and party exhaustion.

    Returns:
        Full travel status.
    """
    data = _load()
    journey = data.get("active_journey")

    if not journey:
        return "No active journey. Use travel_start to begin one."

    remaining_dist = journey["distance_miles"] - (journey["days_traveled"] * journey["miles_per_day"])
    remaining_days = remaining_dist / journey["miles_per_day"] if journey["miles_per_day"] > 0 else 0
    rations_remaining = journey["rations_total"] - journey.get("rations_used", 0)

    lines = [
        f"🗺️  Journey: {journey['destination']}",
        f"  Distance: {remaining_dist:.1f} miles remaining (~{remaining_days:.1f} days)",
        f"  Terrain: {journey['terrain']} | Pace: {journey['pace']} ({journey['miles_per_day']} mi/day)",
        f"  Days traveled: {journey['days_traveled']}/{journey['days_rounded']} | Rations: {journey.get('rations_used', 0)}/{journey['rations_total']}",
    ]

    exhaustion = data.get("exhaustion", {})
    if exhaustion:
        lines.append("  😓 Party exhaustion:")
        for char, level in exhaustion.items():
            if level > 0:
                lines.append(f"    {char}: level {level} — {EXHAUSTION_EFFECTS.get(level, '')}")
    else:
        lines.append("  😴 No one has exhaustion.")

    return "\n".join(lines)


def travel_cancel() -> str:
    """
    Cancel the current journey without arriving.

    Returns:
        Confirmation.
    """
    data = _load()
    data["active_journey"] = None
    _save(data)
    return "🛑 Journey cancelled."


def travel_forage(
    terrain: str,
    party_size: int = 4,
    days_needed: int = 1,
    survival_modifier: int = 0
) -> str:
    """
    Simulate foraging attempts over a travel day. Each party member with
    a Survival modifier makes a check; DC based on terrain.

    Args:
        terrain: Terrain type for foraging
        party_size: Number of people needing food. Default: 4
        days_needed: Number of days to cover with foraging. Default: 1
        survival_modifier: Party's collective survival bonus. Default: 0

    Returns:
        Foraging results and ration math.
    """
    terrain = terrain.lower()
    if terrain not in FORAGE_CHANCE:
        return f"ERROR: terrain must be one of: {', '.join(FORAGE_CHANCE.keys())}"

    DC = 10 + (10 - FORAGE_CHANCE.get(terrain, 20)) // 5  # harder terrain = higher DC
    success_chance = FORAGE_CHANCE.get(terrain, 0)

    total_food_needed = party_size * days_needed
    expected_success = (success_chance / 100) * party_size
    food_from_foraging = int(expected_success)

    result = (
        f"🌿 Foraging in {terrain} (DC ~{DC}, {success_chance}% per person)\n"
        f"  Food needed: {total_food_needed} rations | Expected from foraging: ~{food_from_foraging}\n"
    )

    if food_from_foraging >= total_food_needed:
        result += "  ✅ Foraging should cover all ration needs."
    elif food_from_foraging > 0:
        shortfall = total_food_needed - food_from_foraging
        result += f"  ⚠️ Shortfall of ~{shortfall} rations. Party should hunt or use supplies."
    else:
        result += f"  ❌ No reliable food in {terrain}. Party must bring all rations."

    return result


def travel_prompt() -> str:
    """
    Return travel state for prompt injection.

    Returns:
        One-line travel status, or empty string if not traveling.
    """
    data = _load()
    journey = data.get("active_journey")

    if not journey:
        return ""

    remaining_dist = journey["distance_miles"] - (journey["days_traveled"] * journey["miles_per_day"])
    return (
        f"🗺️ Traveling to {journey['destination']} — "
        f"{remaining_dist:.0f} miles remaining, {journey['terrain']} terrain, "
        f"{journey['pace']} pace. "
        f"Rations: {journey.get('rations_used', 0)}/{journey['rations_total']} used."
    )


TOOLS = [
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "travel_start",
            "description": "Begin a new overland travel journey. Calculates days needed, ration requirements, and exhaustion risk based on terrain and pace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "destination": {"type": "string", "description": "Where the party is traveling to"},
                    "distance_miles": {"type": "number", "description": "Total distance to destination in miles"},
                    "terrain": {"type": "string", "description": "Primary terrain: road, grassland, forest, hills, mountain, swamp, desert, arctic, coastal, underdark. Default: road"},
                    "pace": {"type": "string", "description": "Travel pace: slow, normal, fast. Default: normal"},
                    "party_size": {"type": "integer", "description": "Number of party members consuming rations. Default: 4"},
                    "days_per_rations": {"type": "integer", "description": "How many days each ration lasts per person. Default: 1"},
                    "current_day": {"type": "integer", "description": "Current in-game day number (from dnd-time). Default: 0"}
                },
                "required": ["destination", "distance_miles"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "travel_advance",
            "description": "Advance travel by a number of days. Consumes rations, may apply exhaustion at fast pace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "days": {"type": "integer", "description": "Number of days to advance. Default: 1"},
                    "rations_available": {"type": "integer", "description": "Total rations the party has. If provided, warns if running low."}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "travel_add_exhaustion",
            "description": "Manually add exhaustion levels to a character during travel (e.g. from extreme weather, hard pace, deprivation).",
            "parameters": {
                "type": "object",
                "properties": {
                    "character_name": {"type": "string", "description": "Name of the character affected"},
                    "levels": {"type": "integer", "description": "Number of exhaustion levels to add. Default: 1"}
                },
                "required": ["character_name"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "travel_remove_exhaustion",
            "description": "Remove exhaustion levels from a character (granted by long rest — 1 level removed per long rest).",
            "parameters": {
                "type": "object",
                "properties": {
                    "character_name": {"type": "string", "description": "Name of the character recovering"},
                    "levels": {"type": "integer", "description": "Number of levels to remove. Default: 1"}
                },
                "required": ["character_name"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "travel_get",
            "description": "Get the current travel state — active journey progress, rations used, and party exhaustion levels.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "travel_cancel",
            "description": "Cancel the current journey without arriving at the destination.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "travel_forage",
            "description": "Simulate foraging results over a travel day. Estimates food gathered vs needed based on terrain and party survival skill.",
            "parameters": {
                "type": "object",
                "properties": {
                    "terrain": {"type": "string", "description": "Terrain type for foraging chance"},
                    "party_size": {"type": "integer", "description": "Number of people needing food. Default: 4"},
                    "days_needed": {"type": "integer", "description": "Number of days to cover with foraging. Default: 1"},
                    "survival_modifier": {"type": "integer", "description": "Party survival bonus. Default: 0"}
                },
                "required": ["terrain"]
            }
        }
    },
]


def execute(function_name, arguments, config):
    if function_name == 'travel_start':
        return travel_start(
            destination=arguments.get('destination', ''),
            distance_miles=arguments.get('distance_miles', 0),
            terrain=arguments.get('terrain', 'road'),
            pace=arguments.get('pace', 'normal'),
            party_size=arguments.get('party_size', 4),
            days_per_rations=arguments.get('days_per_rations', 1),
            current_day=arguments.get('current_day')
        ), True

    if function_name == 'travel_advance':
        return travel_advance(
            days=arguments.get('days', 1),
            rations_available=arguments.get('rations_available')
        ), True

    if function_name == 'travel_add_exhaustion':
        return travel_add_exhaustion(
            character_name=arguments.get('character_name', ''),
            levels=arguments.get('levels', 1)
        ), True

    if function_name == 'travel_remove_exhaustion':
        return travel_remove_exhaustion(
            character_name=arguments.get('character_name', ''),
            levels=arguments.get('levels', 1)
        ), True

    if function_name == 'travel_get':
        return travel_get(), True

    if function_name == 'travel_cancel':
        return travel_cancel(), True

    if function_name == 'travel_forage':
        return travel_forage(
            terrain=arguments.get('terrain', ''),
            party_size=arguments.get('party_size', 4),
            days_needed=arguments.get('days_needed', 1),
            survival_modifier=arguments.get('survival_modifier', 0)
        ), True

    return f"Unknown function: {function_name}", False
