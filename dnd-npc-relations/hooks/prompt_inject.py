"""
dnd-npc-relations — prompt_inject hook

Injects relevant NPC/faction attitudes into every prompt.

Injection strategy:
- Non-neutral NPCs tagged to the current scene location are always injected
- All hostile/unfriendly entities are always injected (regardless of scene tags)
- Friendly/ally entities with scene tags matching the current location are injected
- Neutral entries are NOT injected (they don't need reminding)

Current location is read from dnd-scene plugin state (key: "current_location_name").
If unavailable, falls back to dnd-campaign state (key: "location").
"""

from core.plugin_loader import plugin_loader
import json
import logging

logger = logging.getLogger("dnd-npc-relations")


def _get_current_location_tag() -> str:
    """Get a normalised location key for tag matching."""
    try:
        scene_state = plugin_loader.get_plugin_state("dnd-scene")
        loc = scene_state.get("current_location_name")
        if loc:
            return loc.strip().lower().replace(" ", "_")
    except Exception:
        pass

    try:
        camp_state = plugin_loader.get_plugin_state("dnd-campaign")
        loc = camp_state.get("location")
        if loc:
            return loc.strip().lower().replace(" ", "_")
    except Exception:
        pass

    return ""


def _load_all():
    raw = plugin_loader.get_plugin_state("dnd-npc-relations").get("relations_index")
    if not raw:
        return {}
    try:
        return json.loads(raw) if isinstance(raw, str) else raw
    except Exception:
        return {}


def prompt_inject(event):
    all_data = _load_all()
    if not all_data:
        return

    current_loc = _get_current_location_tag()
    entries = list(all_data.values())

    to_inject = []

    for e in entries:
        score = e.get("attitude_score", 0)
        tags = e.get("tags", [])

        # Always inject hostile and unfriendly — they're a risk everywhere
        if score <= -1:
            to_inject.append(e)
            continue

        # Always inject non-neutral untagged entries (global NPCs)
        if score != 0 and not tags:
            to_inject.append(e)
            continue

        # Inject scene-tagged non-neutral if we match the current location
        if score != 0 and current_loc and any(current_loc in t for t in tags):
            to_inject.append(e)

    if not to_inject:
        return

    # Sort: hostile first, then unfriendly, then friendly, then ally
    to_inject.sort(key=lambda e: e.get("attitude_score", 0))

    lines = ["🧭 NPC/FACTION ATTITUDES (do not reset these to neutral):"]
    for e in to_inject:
        name = e["name"]
        attitude = e["attitude"].upper()
        etype = e["entity_type"]
        notes = e.get("notes", "")
        note_str = f" — {notes}" if notes else ""
        lines.append(f"  {name} ({etype}): {attitude}{note_str}")

    event.context_parts.append("\n".join(lines))
