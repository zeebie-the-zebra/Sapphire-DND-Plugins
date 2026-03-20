"""
dnd-weather — post_execute hook

Optional integration with dnd-time. When time_advance is called with
significant hours (>4), this hook can automatically advance weather.

This is disabled by default to avoid unexpected weather changes.
Enable by setting auto_advance=true in plugin state.
"""

from core.plugin_loader import plugin_loader
import json
import logging
import random

logger = logging.getLogger("dnd-weather")


def post_execute(event):
    """
    Auto-advance weather when significant time passes.

    Looks for dnd-time's time_advance tool calls and optionally
    advances weather accordingly.
    """
    try:
        # Check if auto-advance is enabled
        state = plugin_loader.get_plugin_state("dnd-weather")
        auto_enabled = state.get("auto_advance", False)

        if not auto_enabled:
            return

        # Check if this was a time_advance call from dnd-time
        tool_name = event.tool_name
        if tool_name != "time_advance":
            return

        # Get hours passed from the tool call
        hours = 8  # default
        if hasattr(event, "tool_args") and event.tool_args:
            args = event.tool_args
            hours = args.get("hours_passed", args.get("hours", 8))

        # Only auto-advance for significant time (>4 hours)
        if hours <= 4:
            return

        # Import the weather tools to use their logic
        from tools.weather import _load, _save, _weighted_choice, CLIMATE_PRESETS, WEATHER_DESCRIPTIONS, WEATHER_MECHANICS

        data = _load()
        climate = state.get("default_climate", "temperate")
        locations = list(data.get("locations", {}).keys()) if data.get("locations") else []

        # Decide if weather changes (same logic as weather_advance)
        change_chance = min(90, int(hours * 5))
        if random.randint(1, 100) > change_chance:
            logger.debug(f"[dnd-weather] Weather holds after {hours} hours")
            return

        # Advance default weather
        pairs = list(CLIMATE_PRESETS.get(climate, CLIMATE_PRESETS["temperate"]))
        condition = _weighted_choice(pairs)
        description = WEATHER_DESCRIPTIONS.get(condition, condition)
        mechanics = WEATHER_MECHANICS.get(condition, "")

        weather = {
            "condition": condition,
            "description": description,
            "mechanics": mechanics,
            "notes": f"Auto-advanced after {hours} hours",
        }

        data["default"] = weather

        # Optionally advance location-specific weather too
        for loc in locations:
            loc_weather = data["locations"].get(loc, {})
            if random.randint(1, 100) <= change_chance:
                loc_condition = _weighted_choice(pairs)
                data["locations"][loc] = {
                    "condition": loc_condition,
                    "description": WEATHER_DESCRIPTIONS.get(loc_condition, loc_condition),
                    "mechanics": WEATHER_MECHANICS.get(loc_condition, ""),
                    "notes": f"Auto-advanced after {hours} hours",
                }

        _save(data)
        logger.debug(f"[dnd-weather] Auto-advanced weather: {condition}")

    except Exception as e:
        logger.debug(f"[dnd-weather] auto-advance failed: {e}")


def set_auto_advance(enabled: bool = True, climate: str = "temperate") -> str:
    """
    Enable or disable automatic weather advancement when time advances.

    Args:
        enabled: True to enable auto-advance, False to disable
        climate: Default climate for auto-generated weather

    Returns:
        Confirmation message
    """
    state = plugin_loader.get_plugin_state("dnd-weather")
    state.save("auto_advance", enabled)
    state.save("default_climate", climate)

    status = "enabled" if enabled else "disabled"
    return f"🌤️ Auto-weather {status} (climate: {climate})"


# Note: This requires adding set_auto_advance to the tools list in __init__.py
# or exposing it via the plugin system