"""
dnd-weather — tools

Persistent in-game weather tracker. Set it manually or generate
weather based on climate and season. Injects current conditions
into every prompt via the prompt_inject hook.

Supports:
- Multi-location weather (different areas can have different weather)
- Weather forecasting for travel planning
- Auto-advance integration with dnd-time

Stored in plugin state under key "weather_state".
"""

from core.plugin_loader import plugin_loader
import json
import random

# Climate presets: maps to weighted weather pools
CLIMATE_PRESETS = {
    "temperate": [
        ("clear", 25), ("overcast", 20), ("light_rain", 20),
        ("heavy_rain", 10), ("fog", 10), ("windy", 10), ("snow", 5),
    ],
    "arctic": [
        ("blizzard", 20), ("snow", 30), ("overcast", 20),
        ("clear_cold", 20), ("fog", 10),
    ],
    "desert": [
        ("clear_hot", 40), ("windy_sand", 25), ("overcast", 15),
        ("clear", 15), ("rare_rain", 5),
    ],
    "tropical": [
        ("heavy_rain", 25), ("thunderstorm", 20), ("humid_overcast", 20),
        ("clear_humid", 25), ("fog", 10),
    ],
    "coastal": [
        ("clear", 20), ("sea_fog", 20), ("strong_wind", 20),
        ("light_rain", 20), ("overcast", 15), ("storm", 5),
    ],
    "mountain": [
        ("clear", 20), ("clear_cold", 20), ("fog", 15), ("windy", 15),
        ("snow", 15), ("blizzard", 10), ("overcast", 5),
    ],
    "swamp": [
        ("humid_overcast", 25), ("fog", 25), ("light_rain", 20),
        ("clear_humid", 15), ("heavy_rain", 10), ("clear", 5),
    ],
}

# Human-readable descriptions for each weather type
WEATHER_DESCRIPTIONS = {
    "clear":          "Clear skies. Comfortable temperature. Good visibility.",
    "overcast":       "Heavy cloud cover. No direct sun. Feels close.",
    "light_rain":     "Light rain. Ground damp. Hoods up, travel slowed slightly.",
    "heavy_rain":     "Heavy downpour. Visibility reduced. Roads turning to mud. Fires hard to light.",
    "fog":            "Dense fog. Visibility reduced to 60ft. Sound carries strangely.",
    "windy":          "Strong wind. Riding is harder. Ranged attacks at disadvantage outdoors.",
    "snow":           "Light snowfall. Tracks covered within hours. Cold but manageable.",
    "blizzard":       "Blizzard. Travel dangerous without shelter. Visibility near zero. Exhaustion risk.",
    "clear_cold":     "Clear and bitterly cold. Ice on surfaces. Every breath visible.",
    "clear_hot":      "Clear and scorching. Unshaded travel risks exhaustion. Water important.",
    "windy_sand":     "Hot sandstorm. Visibility reduced. Unprotected skin stings. Eyes need covering.",
    "rare_rain":      "Sudden brief downpour. Locals stare. Gone within the hour.",
    "thunderstorm":   "Thunderstorm. Lightning strikes nearby high points. Loud, dramatic, dangerous.",
    "humid_overcast": "Humid and overcast. Everything feels damp. Morale subtly affected.",
    "clear_humid":    "Bright but oppressively humid. Armour chafes. Short rests feel wasted.",
    "sea_fog":        "Sea fog rolling in from the water. Navigation harder. Eerie silence.",
    "strong_wind":    "Strong coastal wind. Voices lost in it. Ranged attacks penalised.",
    "storm":          "Coastal storm. Boats grounded. Visibility zero at sea. Shelter essential.",
}

# Travel/mechanical impact notes
WEATHER_MECHANICS = {
    "blizzard":       "⚠️ Overland travel requires CON save DC 12 each hour or gain 1 exhaustion level.",
    "heavy_rain":     "⚠️ Disadvantage on Perception checks relying on sight or sound.",
    "fog":            "⚠️ Heavily obscured beyond 60ft. Disadvantage on attacks against targets in fog.",
    "thunderstorm":   "⚠️ Disadvantage on Perception. Lightning: 1-in-20 chance per hour outside to strike a tall object.",
    "windy":          "⚠️ Ranged weapon attacks beyond normal range have disadvantage.",
    "strong_wind":    "⚠️ Ranged weapon attacks beyond normal range have disadvantage.",
    "windy_sand":     "⚠️ Ranged attacks at disadvantage. Unprotected eyes: disadvantage on Perception.",
    "clear_hot":      "⚠️ Unshaded travel beyond 2 hours: CON save DC 10 or 1 exhaustion level.",
    "snow":           "⚠️ Difficult terrain in open areas. Tracks visible for 4 hours.",
}

# Spell interaction notes (optional, for reference)
WEATHER_SPELL_EFFECTS = {
    "fireball": "Rain/heavy_rain: fires struggle to light, Fireball damage reduced if target is wet",
    "lightning": "thunderstorm: advantage on lightning attacks, +1 damage per die",
    "fog_cloud": "fog: spell fog blends with natural fog, visibility chaotic",
    "call-lightning": "thunderstorm: always works, +2 damage per hit",
    "wind-wall": "windy/strong_wind: spell resists strong wind but is strain on caster",
}


def _state():
    return plugin_loader.get_plugin_state("dnd-weather")


def _load():
    raw = _state().get("weather_state")
    if not raw:
        return {"default": {}, "locations": {}}
    data = json.loads(raw) if isinstance(raw, str) else raw
    # Ensure backward compatibility with old format
    if "default" not in data:
        old_default = {k: v for k, v in data.items() if k != "locations"}
        return {"default": old_default, "locations": data.get("locations", {})}
    return data


def _save(data: dict):
    _state().save("weather_state", json.dumps(data))


def _get_weather(location: str = None):
    """Get weather for a specific location or default."""
    data = _load()
    if location and location in data.get("locations", {}):
        return data["locations"][location]
    return data.get("default", {})


def _set_weather(weather: dict, location: str = None):
    """Set weather for a specific location or default."""
    data = _load()
    if location:
        if "locations" not in data:
            data["locations"] = {}
        data["locations"][location] = weather
    else:
        data["default"] = weather
    _save(data)


def _weighted_choice(pairs):
    """Choose from list of (value, weight) pairs."""
    total = sum(w for _, w in pairs)
    r = random.randint(1, total)
    cumulative = 0
    for value, weight in pairs:
        cumulative += weight
        if r <= cumulative:
            return value
    return pairs[-1][0]


def weather_set(
    condition: str,
    temperature: str = "",
    wind: str = "",
    notes: str = "",
    day: int = None,
    location: str = None
) -> str:
    """
    Manually set the current weather.

    Args:
        condition: Weather condition. Common values: clear, overcast, light_rain,
                   heavy_rain, fog, windy, snow, blizzard, thunderstorm.
                   Use any descriptive string — it will be stored and injected as-is.
        temperature: Temperature description (e.g. "bitterly cold", "warm", "sweltering")
        wind: Wind description (e.g. "still", "light breeze", "gale force")
        notes: Any additional weather notes (e.g. "smells of rain", "frost on the ground")
        day: Current in-game day number (for change tracking)
        location: Optional location name. If omitted, sets global default weather.

    Returns:
        Confirmation of new weather.
    """
    description = WEATHER_DESCRIPTIONS.get(condition, condition)
    mechanics = WEATHER_MECHANICS.get(condition, "")

    weather = {
        "condition": condition,
        "description": description,
        "temperature": temperature,
        "wind": wind,
        "notes": notes,
        "mechanics": mechanics,
        "set_on_day": day,
    }
    _set_weather(weather, location)

    loc_str = f" [{location}]" if location else ""
    result = f"🌤️ Weather set{loc_str}: {condition}"
    if temperature:
        result += f" | {temperature}"
    if wind:
        result += f" | Wind: {wind}"
    result += f"\n  {description}"
    if mechanics:
        result += f"\n  {mechanics}"
    return result


def weather_generate(climate: str = "temperate", season: str = "", day: int = None, location: str = None) -> str:
    """
    Randomly generate weather appropriate to a climate and season.
    Sets the result as the current weather.

    Args:
        climate: Climate preset — temperate | arctic | desert | tropical | coastal | mountain | swamp
        season: Optional season modifier — spring | summer | autumn | winter.
                Shifts probability toward seasonal extremes (e.g. winter → more snow).
        day: Current in-game day number
        location: Optional location name. If omitted, sets global default weather.

    Returns:
        Generated weather description.
    """
    if climate not in CLIMATE_PRESETS:
        return f"ERROR: climate must be one of: {', '.join(CLIMATE_PRESETS.keys())}"

    pairs = list(CLIMATE_PRESETS[climate])

    # Apply mild season shifts
    if season == "winter":
        pairs = [(c, w * 2) if "snow" in c or "cold" in c or "blizzard" in c else (c, w) for c, w in pairs]
    elif season == "summer":
        pairs = [(c, w * 2) if "hot" in c or "clear" in c else (c, w) for c, w in pairs]

    condition = _weighted_choice(pairs)
    description = WEATHER_DESCRIPTIONS.get(condition, condition)
    mechanics = WEATHER_MECHANICS.get(condition, "")

    weather = {
        "condition": condition,
        "description": description,
        "temperature": "",
        "wind": "",
        "notes": f"Generated for {climate} climate" + (f", {season}" if season else ""),
        "mechanics": mechanics,
        "set_on_day": day,
    }
    _set_weather(weather, location)

    loc_str = f" [{location}]" if location else ""
    result = f"🌤️ Generated weather ({climate}){loc_str}: {condition}\n  {description}"
    if mechanics:
        result += f"\n  {mechanics}"
    return result


def weather_get(location: str = None) -> str:
    """
    Get the current weather state.

    Args:
        location: Optional location name. If omitted, returns default/global weather.

    Returns:
        Current weather description with any mechanical effects.
    """
    data = _load()

    # If location specified, get that specific weather
    if location:
        weather = data.get("locations", {}).get(location, {})
        if not weather:
            return f"No weather set for {location}. Call weather_set(location=\"{location}\", ...) or weather_generate(location=\"{location}\", ...)."
    else:
        weather = data.get("default", {})

    if not weather:
        return "No weather set. Call weather_set or weather_generate."

    cond = weather.get("condition", "unknown")
    desc = weather.get("description", "")
    temp = weather.get("temperature", "")
    wind = weather.get("wind", "")
    notes = weather.get("notes", "")
    mechanics = weather.get("mechanics", "")
    day = weather.get("set_on_day")

    loc_str = f" [{location}]" if location else ""
    lines = [f"🌤️ Current weather{loc_str}: {cond}"]
    if temp:
        lines.append(f"  Temperature: {temp}")
    if wind:
        lines.append(f"  Wind: {wind}")
    if desc:
        lines.append(f"  Conditions: {desc}")
    if notes:
        lines.append(f"  Notes: {notes}")
    if mechanics:
        lines.append(f"  {mechanics}")
    if day is not None:
        lines.append(f"  (Set on day {day})")

    return "\n".join(lines)


def weather_advance(hours_passed: int = 8, climate: str = "temperate", location: str = None) -> str:
    """
    Advance weather after significant time has passed (rest, long travel).
    Has a chance to shift conditions based on how much time has elapsed.

    Args:
        hours_passed: In-game hours elapsed since last weather check
        climate: Current climate for any generated new weather
        location: Optional location name. If omitted, advances default/global weather.

    Returns:
        Whether weather changed and the new conditions.
    """
    # Get current weather for the location
    if location:
        data = _load()
        current = data.get("locations", {}).get(location, {})
    else:
        current = _load().get("default", {})

    # Probability of change scales with time elapsed
    change_chance = min(90, int(hours_passed * 5))
    if random.randint(1, 100) > change_chance:
        condition = current.get("condition", "unknown")
        loc_str = f" [{location}]" if location else ""
        return f"🌤️ Weather holds{loc_str}: {condition}. No significant change after {hours_passed} hours."

    # Generate new weather
    return weather_generate(climate=climate, location=location)


def weather_forecast(climate: str = "temperate", days: int = 3, location: str = None) -> str:
    """
    Generate a weather forecast for upcoming days. Useful for travel planning.

    Args:
        climate: Climate preset — temperate | arctic | desert | tropical | coastal | mountain | swamp
        days: Number of days to forecast (1-7)
        location: Optional location name. If set, stores the forecast for that location.

    Returns:
        Day-by-day weather forecast with travel warnings.
    """
    if days < 1 or days > 7:
        return "Forecast limited to 1-7 days."

    forecast = []
    current_condition = None

    for day in range(1, days + 1):
        pairs = list(CLIMATE_PRESETS.get(climate, CLIMATE_PRESETS["temperate"]))

        # Slight carryover chance from previous day
        if current_condition and random.randint(1, 100) <= 40:
            condition = current_condition
        else:
            condition = _weighted_choice(pairs)

        current_condition = condition
        desc = WEATHER_DESCRIPTIONS.get(condition, condition)
        mechanics = WEATHER_MECHANICS.get(condition, "")

        day_line = f"Day {day}: {condition}"
        if mechanics:
            day_line += f" {mechanics}"
        forecast.append(day_line)

    result = f"📅 {days}-Day Weather Forecast ({climate}):\n" + "\n".join(f"  {f}" for f in forecast)

    # Optionally store as "planned" weather for a location
    if location:
        data = _load()
        if "forecasts" not in data:
            data["forecasts"] = {}
        data["forecasts"][location] = {
            "climate": climate,
            "days": days,
            "forecast": forecast,
        }
        _save(data)
        result += f"\n  (Saved to {location})"

    return result


def weather_list_locations() -> str:
    """
    List all locations with weather data.

    Returns:
        List of all tracked weather locations.
    """
    data = _load()
    locations = data.get("locations", {})
    default = data.get("default", {})

    lines = ["📍 Weather-tracked locations:"]

    if default:
        lines.append(f"  • [Default]: {default.get('condition', 'unknown')}")

    for loc, weather in locations.items():
        lines.append(f"  • {loc}: {weather.get('condition', 'unknown')}")

    if not locations and not default:
        return "No weather data. Call weather_set or weather_generate first."

    return "\n".join(lines)


def weather_delete_location(location: str = None) -> str:
    """
    Delete weather data for a location, or clear all default weather.

    Args:
        location: Optional location name. If omitted, clears default/global weather.

    Returns:
        Confirmation of deletion.
    """
    data = _load()

    if location:
        if location in data.get("locations", {}):
            del data["locations"][location]
            _save(data)
            return f"🌤️ Weather deleted for {location}."
        else:
            return f"No weather data found for {location}."
    else:
        data["default"] = {}
        _save(data)
        return "🌤️ Default weather cleared."


def weather_auto_advance(enabled: bool = True, climate: str = "temperate") -> str:
    """
    Enable or disable automatic weather advancement when time advances.

    When enabled, weather will automatically change when dnd-time's
    time_advance is called with >4 hours.

    Args:
        enabled: True to enable auto-advance, False to disable
        climate: Default climate for auto-generated weather

    Returns:
        Confirmation message
    """
    state = _state()
    state.save("auto_advance", enabled)
    state.save("default_climate", climate)

    status = "enabled" if enabled else "disabled"
    return f"🌤️ Auto-weather {status} (climate: {climate})"


TOOLS = [
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "weather_set",
            "description": "Manually set the current weather.",
            "parameters": {
                "type": "object",
                "properties": {
                    "condition": {"type": "string", "description": "Weather condition: clear, overcast, light_rain, heavy_rain, fog, windy, snow, blizzard, thunderstorm, etc."},
                    "temperature": {"type": "string", "description": "Temperature description (e.g. 'bitterly cold', 'warm', 'sweltering'). Default: ''"},
                    "wind": {"type": "string", "description": "Wind description (e.g. 'still', 'light breeze', 'gale force'). Default: ''"},
                    "notes": {"type": "string", "description": "Additional weather notes. Default: ''"},
                    "day": {"type": "integer", "description": "Current in-game day number. Default: None"},
                    "location": {"type": "string", "description": "Optional location name. If omitted, sets global default weather. Default: None"}
                },
                "required": ["condition"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "weather_generate",
            "description": "Randomly generate weather appropriate to a climate and season, and set it as current.",
            "parameters": {
                "type": "object",
                "properties": {
                    "climate": {"type": "string", "description": "Climate preset: temperate | arctic | desert | tropical | coastal | mountain | swamp. Default: temperate"},
                    "season": {"type": "string", "description": "Optional season modifier: spring | summer | autumn | winter. Default: ''"},
                    "day": {"type": "integer", "description": "Current in-game day number. Default: None"},
                    "location": {"type": "string", "description": "Optional location name. Default: None"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "weather_get",
            "description": "Get the current weather state.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "Optional location name. If omitted, returns default/global weather. Default: None"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "weather_advance",
            "description": "Advance weather after significant time has passed (rest, long travel). Has a chance to shift conditions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "hours_passed": {"type": "integer", "description": "In-game hours elapsed since last weather check. Default: 8"},
                    "climate": {"type": "string", "description": "Current climate for any generated new weather. Default: temperate"},
                    "location": {"type": "string", "description": "Optional location name. Default: None"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "weather_forecast",
            "description": "Generate a weather forecast for upcoming days. Useful for travel planning.",
            "parameters": {
                "type": "object",
                "properties": {
                    "climate": {"type": "string", "description": "Climate preset: temperate | arctic | desert | tropical | coastal | mountain | swamp. Default: temperate"},
                    "days": {"type": "integer", "description": "Number of days to forecast (1-7). Default: 3"},
                    "location": {"type": "string", "description": "Optional location name. Default: None"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "weather_list_locations",
            "description": "List all locations with weather data.",
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
            "name": "weather_delete_location",
            "description": "Delete weather data for a location, or clear all default weather.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "Optional location name. If omitted, clears default/global weather. Default: None"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "weather_auto_advance",
            "description": "Enable or disable automatic weather advancement when time advances.",
            "parameters": {
                "type": "object",
                "properties": {
                    "enabled": {"type": "boolean", "description": "True to enable auto-advance, False to disable. Default: True"},
                    "climate": {"type": "string", "description": "Default climate for auto-generated weather. Default: temperate"}
                },
                "required": []
            }
        }
    },
]


def execute(function_name, arguments, config):
    if function_name == 'weather_set':
        return weather_set(
            condition=arguments.get('condition', ''),
            temperature=arguments.get('temperature', ''),
            wind=arguments.get('wind', ''),
            notes=arguments.get('notes', ''),
            day=arguments.get('day'),
            location=arguments.get('location')
        ), True

    if function_name == 'weather_generate':
        return weather_generate(
            climate=arguments.get('climate', 'temperate'),
            season=arguments.get('season', ''),
            day=arguments.get('day'),
            location=arguments.get('location')
        ), True

    if function_name == 'weather_get':
        return weather_get(location=arguments.get('location')), True

    if function_name == 'weather_advance':
        return weather_advance(
            hours_passed=arguments.get('hours_passed', 8),
            climate=arguments.get('climate', 'temperate'),
            location=arguments.get('location')
        ), True

    if function_name == 'weather_forecast':
        return weather_forecast(
            climate=arguments.get('climate', 'temperate'),
            days=arguments.get('days', 3),
            location=arguments.get('location')
        ), True

    if function_name == 'weather_list_locations':
        return weather_list_locations(), True

    if function_name == 'weather_delete_location':
        return weather_delete_location(location=arguments.get('location')), True

    if function_name == 'weather_auto_advance':
        return weather_auto_advance(
            enabled=arguments.get('enabled', True),
            climate=arguments.get('climate', 'temperate')
        ), True

    return f"Unknown function: {function_name}", False
