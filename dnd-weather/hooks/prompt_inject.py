"""
dnd-weather — prompt_inject hook

Injects current weather into every prompt as a brief one-liner.
Only injects if weather has been set. Mechanical warnings are
included when present (e.g. ranged attack disadvantage in storms).
Supports multi-location weather.
"""

from core.plugin_loader import plugin_loader
import json
import logging

logger = logging.getLogger("dnd-weather")


def _get_inject_text(weather_data: dict) -> str:
    """Format weather data for injection."""
    if not weather_data:
        return None

    condition = weather_data.get("condition", "")
    description = weather_data.get("description", "")
    mechanics = weather_data.get("mechanics", "")

    if not condition:
        return None

    line = f"🌤️ Weather: {condition}"
    if description:
        line += f" — {description}"
    if mechanics:
        line += f" {mechanics}"

    return line


def prompt_inject(event):
    try:
        raw = plugin_loader.get_plugin_state("dnd-weather").get("weather_state")
        if not raw:
            return

        data = json.loads(raw) if isinstance(raw, str) else raw
        default = data.get("default", {})
        locations = data.get("locations", {})

        # Inject default weather
        inject_text = _get_inject_text(default)
        if inject_text:
            event.context_parts.append(inject_text)

        # Inject weather for any tracked locations (if not too many)
        if locations:
            loc_count = len(locations)
            if loc_count <= 3:
                for loc, weather in locations.items():
                    loc_text = _get_inject_text(weather)
                    if loc_text:
                        event.context_parts.append(f"  [{loc}] {loc_text}")
            else:
                # Too many locations, just list them
                loc_list = ", ".join(locations.keys())
                event.context_parts.append(f"  ({loc_list} have tracked weather)")

    except Exception as e:
        logger.debug(f"[dnd-weather] inject failed: {e}")
