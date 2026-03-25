"""
dnd-scene v2 — Scene Tracker with Location Library

Fixes the "returning to a place" problem. Locations are saved on first
visit and automatically reloaded when the party returns, so the kitchen
stays on the north wall and the green door stays green.

  scene_move()            — travel to a location (loads saved layout if known)
  scene_set()             — save the permanent description of current location
  scene_get()             — get current scene state
  scene_add/remove_person — track who is present
  scene_update()          — per-visit changes (mood, lighting, time)
  scene_update_location() — permanent room changes (wall destroyed, etc.)
  scene_list_locations()  — list all known places
"""

from datetime import datetime
from core.plugin_loader import plugin_loader

ENABLED = True
EMOJI = '🗺️'
AVAILABLE_FUNCTIONS = [
    'scene_move', 'scene_set', 'scene_get',
    'scene_add_person', 'scene_remove_person',
    'scene_update', 'scene_update_location', 'scene_list_locations',
    'scene_edit_location', 'scene_delete_location'
]

TOOLS = [
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "scene_move",
            "description": (
                "Move the party to a location. Call this EVERY TIME the party goes somewhere, "
                "before narrating arrival. If the party has been here before, returns the SAVED "
                "layout — use that for your description so the room is consistent. "
                "If it is a new location, tells you to define it with scene_set()."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Exact name of the location. Must be consistent — 'The Rusty Flagon, common room' every time. Check scene_list_locations() if unsure of exact name."
                    },
                    "present": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Who is here on THIS visit. NPCs may differ each visit."
                    },
                    "time": {"type": "string", "description": "Time of day: 'morning', 'evening', 'midnight', etc."},
                    "mood": {"type": "string", "description": "Atmosphere this visit: 'busy and loud', 'eerily quiet', 'tense', etc."}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "scene_set",
            "description": (
                "Save the permanent description of the CURRENT location. Call this after "
                "arriving at a NEW location to lock in its layout. This description loads "
                "automatically on ALL future visits. Focus on fixed details — NOT who is present."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Permanent layout and sensory details. Where things are, architecture, smells, fixed objects. E.g.: 'Bar on north wall with boar head above, kitchen door behind bar, four round tables, sawdust floor, smells of stale beer, green front door.'"
                    },
                    "lighting_default": {"type": "string", "description": "Typical lighting: 'dim candlelight', 'bright daylight', 'torchlit'."},
                    "notes": {"type": "string", "description": "Permanent DM notes: hidden rooms, secrets, hazards, history."}
                },
                "required": ["description"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "scene_get",
            "description": "Get the current scene — location layout, who is present, known/new status.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "scene_add_person",
            "description": "Add a person to the current scene (they entered).",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of person entering."},
                    "note": {"type": "string", "description": "Optional — how they entered or current state."}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "scene_remove_person",
            "description": "Remove a person from the current scene (they left, fled, or died).",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of person leaving."},
                    "reason": {"type": "string", "description": "Optional — why they left."}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "scene_update",
            "description": (
                "Update a per-visit detail: mood, lighting, time, or visit notes. "
                "Does NOT permanently change the room. For permanent changes use scene_update_location."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "field": {"type": "string", "description": "Field to change: 'mood', 'lighting', 'time', 'visit_notes'"},
                    "value": {"type": "string", "description": "New value."}
                },
                "required": ["field", "value"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "scene_update_location",
            "description": (
                "PERMANENTLY change the saved layout of the current location. "
                "Use ONLY when the place itself changes forever: wall destroyed, secret door found, fire, etc. "
                "Affects ALL future visits."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "field": {"type": "string", "description": "Field to permanently change: 'description', 'lighting_default', 'notes'"},
                    "value": {"type": "string", "description": "New permanent value."},
                    "change_reason": {"type": "string", "description": "What caused this change. Stored in location history."}
                },
                "required": ["field", "value"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "scene_list_locations",
            "description": "List all locations the party has visited with saved descriptions. Check this before scene_move to get the exact saved name.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "scene_edit_location",
            "description": (
                "Edit a saved location in the library by name. You don't need to be there. "
                "Use this to fix typos, update descriptions, or change notes for locations you've already saved. "
                "For permanent changes to the room itself (wall destroyed, etc.), the change is logged automatically."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Exact name of the location to edit (from scene_list_locations)."},
                    "field": {"type": "string", "description": "Field to change: 'description', 'lighting_default', 'notes'"},
                    "value": {"type": "string", "description": "New value for the field."}
                },
                "required": ["name", "field", "value"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "scene_delete_location",
            "description": (
                "Delete a location from the library. The party can still 'move' there — "
                "it will be treated as a NEW location and require scene_set() to save again. "
                "Use with caution; this erases all saved layout, notes, and visit history."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Exact name of the location to delete (from scene_list_locations)."},
                    "confirm": {"type": "boolean", "description": "Must be true to proceed. Always ask the user to confirm before passing true."}
                },
                "required": ["name", "confirm"]
            }
        }
    }
]


DEFAULT_CAMPAIGN_ID = "default"


def _get_state():
    from core.plugin_loader import plugin_loader
    return plugin_loader.get_plugin_state("dnd-scaffold")


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
    """Migrate legacy scene data to campaign scope if needed."""
    state = _get_state()
    migration_key = f"_legacy_migrated_{campaign_id}"

    if state.get(migration_key):
        return

    legacy = state.get("scene")
    if legacy:
        state.save(f"scene:{campaign_id}", legacy)
        state.save(migration_key, True)


def _load(config=None):
    """Load scene data for the current campaign."""
    campaign_id = _get_campaign_id(config)
    state = _get_state()

    _migrate_if_needed(campaign_id)

    campaign_scene = state.get(f"scene:{campaign_id}")
    if campaign_scene:
        return campaign_scene

    return state.get("scene") or {"current": {}, "library": {}}


def _save(data, config=None):
    """Save scene data to the current campaign's storage."""
    campaign_id = _get_campaign_id(config)
    _get_state().save(f"scene:{campaign_id}", data)


def _loc_key(name):
    return name.strip().lower()


def _scene_summary(data):
    current = data.get("current", {})
    library = data.get("library", {})

    if not current:
        return "No current scene. Call scene_move() to go somewhere."

    name   = current.get("name", "Unknown")
    key    = _loc_key(name)
    is_new = current.get("is_new", True)
    saved  = library.get(key, {})

    lines = [f"Location: {name}  [{'NEW' if is_new else 'KNOWN — ' + str(saved.get('visit_count', 1)) + ' visit(s)'}]"]

    time     = current.get("time", "")
    lighting = current.get("lighting") or saved.get("lighting_default", "")
    mood     = current.get("mood", "")

    if time:     lines.append(f"Time: {time}")
    if lighting: lines.append(f"Lighting: {lighting}")
    if mood:     lines.append(f"Mood: {mood}")

    if saved.get("description"):
        lines.append(f"Layout: {saved['description']}")
    elif is_new:
        lines.append("Layout: (new — call scene_set() to lock in the permanent description)")

    if saved.get("notes"):
        lines.append(f"Notes: {saved['notes']}")

    present = current.get("present", [])
    lines.append(f"Present: {', '.join(present) if present else '(nobody)'}")

    if current.get("visit_notes"):
        lines.append(f"This visit: {current['visit_notes']}")

    return "\n".join(lines)


def execute(function_name, arguments, config):
    # Campaign-scoped helpers
    data = _load(config)

    if function_name == "scene_move":
        name    = arguments.get("name", "").strip()
        present = arguments.get("present", [])
        time    = arguments.get("time", "").strip()
        mood    = arguments.get("mood", "").strip()

        if not name:
            return "Error: location name is required.", False

        # Validate present names against character roster AND NPC roster
        if present:
            campaign_id = _get_campaign_id(config)
            valid_names = set()
            try:
                char_state = plugin_loader.get_plugin_state("dnd-scaffold")
                chars = char_state.get(f"characters:{campaign_id}") or char_state.get("characters") or {}
                for c in chars.values() if isinstance(chars, dict) else []:
                    if c.get("name"):
                        valid_names.add(c["name"].lower())
            except Exception:
                pass
            try:
                npc_state = plugin_loader.get_plugin_state("dnd-scaffold")
                npcs = npc_state.get(f"npcs:{campaign_id}") or npc_state.get("npcs") or {}
                for npc in npcs.values() if isinstance(npcs, dict) else []:
                    if npc.get("name"):
                        valid_names.add(npc["name"].lower())
            except Exception:
                pass
            unknown = [p for p in present if p.lower() not in valid_names]
            if unknown:
                return f"ERROR: Unknown name(s): {', '.join(unknown)}. Valid characters & NPCs: {', '.join(sorted(v for v in valid_names)) or '(none registered)'}", False

        data = _load(config)
        library = data.get("library", {})
        key     = _loc_key(name)
        known   = key in library
        saved   = library.get(key, {})

        if known:
            library[key]["visit_count"] = saved.get("visit_count", 1) + 1

        data["current"] = {
            "name": name, "present": present, "time": time,
            "mood": mood, "lighting": "", "visit_notes": "", "is_new": not known
        }
        data["library"] = library
        _save(data, config)

        if known:
            visits = library[key]["visit_count"]
            lines  = [f"Returning to KNOWN location: {name} (visit #{visits})"]
            if saved.get("description"):
                lines.append(f"\nSAVED LAYOUT — use this for your description:\n  {saved['description']}")
            if saved.get("lighting_default"):
                lines.append(f"Default lighting: {saved['lighting_default']}")
            if saved.get("notes"):
                lines.append(f"Notes: {saved['notes']}")
            if saved.get("change_log"):
                lines.append(f"Changes: {' | '.join(saved['change_log'])}")
            lines.append(f"\nPresent this visit: {', '.join(present) if present else '(nobody yet)'}")
            return "\n".join(lines), True
        else:
            return (
                f"NEW location: {name}\n"
                "First visit — describe it now, then call scene_set() to save the permanent layout.\n"
                "Once saved, this layout will load automatically every time you return here."
            ), True

    elif function_name == "scene_set":
        description      = arguments.get("description", "").strip()
        lighting_default = arguments.get("lighting_default", "").strip()
        notes            = arguments.get("notes", "").strip()

        if not description:
            return "Error: description is required.", False

        data = _load(config)
        current = data.get("current", {})

        if not current.get("name"):
            return "No current location. Call scene_move() first.", False

        key     = _loc_key(current["name"])
        library = data.get("library", {})
        exist   = library.get(key, {})

        library[key] = {
            "name":             current["name"],
            "description":      description,
            "lighting_default": lighting_default or exist.get("lighting_default", ""),
            "notes":            notes or exist.get("notes", ""),
            "first_visited":    exist.get("first_visited", datetime.now().strftime("%Y-%m-%d %H:%M")),
            "visit_count":      exist.get("visit_count", 1),
            "change_log":       exist.get("change_log", [])
        }

        current["is_new"] = False
        data["library"]   = library
        data["current"]   = current
        _save(data, config)

        return (
            f"'{current['name']}' saved to location library.\n"
            f"Layout locked in: {description}\n"
            f"This will load automatically on all future visits."
        ), True

    elif function_name == "scene_get":
        return _scene_summary(_load(config)), True

    elif function_name == "scene_add_person":
        name = arguments.get("name", "").strip()
        note = arguments.get("note", "").strip()
        if not name:
            return "Error: name is required.", False

        # Validate against character roster AND NPC roster
        campaign_id = _get_campaign_id(config)
        valid_names = set()
        try:
            char_state = plugin_loader.get_plugin_state("dnd-scaffold")
            chars = char_state.get(f"characters:{campaign_id}") or char_state.get("characters") or {}
            for c in chars.values() if isinstance(chars, dict) else []:
                if c.get("name"):
                    valid_names.add(c["name"].lower())
        except Exception:
            pass
        try:
            npc_state = plugin_loader.get_plugin_state("dnd-scaffold")
            npcs = npc_state.get(f"npcs:{campaign_id}") or npc_state.get("npcs") or {}
            for npc in npcs.values() if isinstance(npcs, dict) else []:
                if npc.get("name"):
                    valid_names.add(npc["name"].lower())
        except Exception:
            pass
        if name.lower() not in valid_names:
            valid = ', '.join(sorted(v for v in valid_names)) or '(none registered)'
            return f"ERROR: '{name}' is not in the campaign roster. Valid names: {valid}", False

        data = _load(config)

        current = data.get("current", {})
        if not current:
            return "No scene set.", False

        present = current.get("present", [])
        if name in present:
            return f"{name} is already in the scene.", True

        present.append(name)
        current["present"] = present
        data["current"] = current
        _save(data, config)
        msg = f"{name} added to scene" + (f" ({note})" if note else "")
        return msg, True

    elif function_name == "scene_remove_person":
        name   = arguments.get("name", "").strip()
        reason = arguments.get("reason", "").strip()
        if not name:
            return "Error: name is required.", False

        data = _load(config)
        current = data.get("current", {})
        if not current:
            return "No scene set.", False

        present     = current.get("present", [])
        new_present = [p for p in present if not p.lower().startswith(name.lower())]
        if len(new_present) == len(present):
            return f"{name} was not in the scene.", False

        current["present"] = new_present
        data["current"]    = current
        _save(data, config)
        msg = f"{name} removed" + (f" ({reason})" if reason else "")
        msg += f". Remaining: {', '.join(new_present) if new_present else 'nobody'}"
        return msg, True

    elif function_name == "scene_update":
        field = arguments.get("field", "").strip().lower()
        value = arguments.get("value", "").strip()

        VISIT_FIELDS = {"mood", "lighting", "time", "visit_notes"}
        if field not in VISIT_FIELDS:
            return (
                f"'{field}' is not a per-visit field. "
                f"To permanently change the room use scene_update_location(). "
                f"Per-visit fields: {', '.join(sorted(VISIT_FIELDS))}"
            ), False

        data = _load(config)
        current = data.get("current", {})
        if not current:
            return "No current scene. Call scene_move() first.", False

        current[field] = value
        data["current"] = current
        _save(data, config)
        return f"Scene {field} → {value}  (this visit only)", True

    elif function_name == "scene_update_location":
        field         = arguments.get("field", "").strip().lower()
        value         = arguments.get("value", "").strip()
        change_reason = arguments.get("change_reason", "").strip()

        LOCATION_FIELDS = {"description", "lighting_default", "notes"}
        if field not in LOCATION_FIELDS:
            return f"Invalid field. Use: {', '.join(sorted(LOCATION_FIELDS))}", False

        data = _load(config)
        current = data.get("current", {})
        if not current.get("name"):
            return "No current location. Call scene_move() first.", False

        key     = _loc_key(current["name"])
        library = data.get("library", {})
        if key not in library:
            return f"'{current['name']}' not in library. Call scene_set() first.", False

        old_val = library[key].get(field, "")
        library[key][field] = value

        if change_reason:
            entry = f"{datetime.now().strftime('%Y-%m-%d')}: {field} — {change_reason}"
            library[key].setdefault("change_log", []).append(entry)

        data["library"] = library
        _save(data, config)
        return (
            f"PERMANENT change to '{current['name']}':\n"
            f"  {field}: was '{old_val[:60]}'\n"
            f"  now: '{value[:60]}'\n"
            + (f"  Reason: {change_reason}" if change_reason else "")
            + "\nThis change will appear on all future visits."
        ), True

    elif function_name == "scene_list_locations":
        data = _load(config)
        library     = data.get("library", {})
        current_key = _loc_key(data.get("current", {}).get("name", ""))

        if not library:
            return "No locations saved yet. Visit places and use scene_set() to save them.", True

        lines = [f"KNOWN LOCATIONS ({len(library)}):"]
        for key, loc in sorted(library.items()):
            here    = " ← YOU ARE HERE" if key == current_key else ""
            visits  = loc.get("visit_count", 1)
            name    = loc.get("name", key)
            desc    = loc.get("description", "(no description)")
            preview = desc[:80] + ("..." if len(desc) > 80 else "")
            lines.append(f"\n  {name}{here}  ({visits} visit{'s' if visits != 1 else ''})")
            lines.append(f"     {preview}")
        return "\n".join(lines), True

    elif function_name == "scene_edit_location":
        name  = arguments.get("name", "").strip()
        field = arguments.get("field", "").strip().lower()
        value = arguments.get("value", "").strip()

        if not name:
            return "Error: location name is required.", False

        LOCATION_FIELDS = {"description", "lighting_default", "notes"}
        if field not in LOCATION_FIELDS:
            return f"Invalid field. Use: {', '.join(sorted(LOCATION_FIELDS))}", False

        data = _load(config)
        library = data.get("library", {})
        key     = _loc_key(name)

        if key not in library:
            return f"'{name}' not in library. Use scene_list_locations() to see saved locations.", False

        old_val = library[key].get(field, "")
        library[key][field] = value

        entry = f"{datetime.now().strftime('%Y-%m-%d')}: {field} — edited"
        library[key].setdefault("change_log", []).append(entry)

        data["library"] = library
        _save(data, config)
        return (
            f"Edited '{name}':\n"
            f"  {field}: was '{old_val[:60]}'\n"
            f"  now: '{value[:60]}'\n"
            "Change logged."
        ), True

    elif function_name == "scene_delete_location":
        name    = arguments.get("name", "").strip()
        confirm = arguments.get("confirm", False)

        if not name:
            return "Error: location name is required.", False

        if not confirm:
            return (
                f"⚠️ Delete '{name}'? This will erase the saved layout, notes, and all visit history. "
                "The party can return but it will be treated as a NEW location. "
                "Ask the user to confirm before passing confirm=true."
            ), False

        data = _load(config)
        library = data.get("library", {})
        key     = _loc_key(name)

        if key not in library:
            return f"'{name}' not in library. Use scene_list_locations() to see saved locations.", False

        deleted = library.pop(key)
        data["library"] = library

        current = data.get("current", {})
        if _loc_key(current.get("name", "")) == key:
            current["is_new"] = True

        _save(data, config)
        return (
            f"Deleted '{name}' from library.\n"
            "The party can still travel there but it will require scene_set() to save again."
        ), True

    return f"Unknown function: {function_name}", False
