"""
D&D Campaign Reset Tool

Clears all plugin state across the entire D&D suite so you can start
a fresh campaign without leftover characters, NPCs, encounters, logs,
or campaign data bleeding in.

Has two modes:
  - full:    Wipes everything — characters, NPCs, campaign, encounters,
             dice history, spell/loot state, session logs, checkpoints.
  - partial: Wipes combat/encounter state and session logs only.
             Keeps characters, NPCs, and campaign world data intact.
             Useful for starting a new session within the same campaign.
"""

ENABLED = True
EMOJI = '🗑️'
AVAILABLE_FUNCTIONS = ['campaign_reset']

PLUGINS_FULL = [
    ("dnd-characters", ["characters"]),
    ("dnd-npcs",       ["npcs"]),
    ("dnd-campaign",   ["campaign"]),
    ("dnd-encounters", ["combat"]),
    ("dnd-logger",     ["session_log", "journal", "turn_count", "session_num", "last_date", "checkpoints"]),
    ("dnd-dice-roller",["history"]),
    ("dnd-scene",      ["scene"]),
    ("dnd-time",       ["time"]),
    ("dnd-facts",      ["facts"]),
    ("dnd-threads",    ["threads"]),
    ("dnd-recap",      ["recap", "turn_count"]),
]

PLUGINS_SESSION = [
    ("dnd-encounters", ["combat"]),
    ("dnd-logger",     ["session_log", "turn_count"]),
    ("dnd-scene",      ["scene"]),
    ("dnd-time",       ["time"]),
    # Wipe recap each session so history stays fresh;
    # keep facts + threads since world knowledge carries over between sessions
    ("dnd-recap",      ["recap", "turn_count"]),
]

TOOLS = [
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "campaign_reset",
            "description": (
                "Reset the D&D campaign state. Use 'full' to wipe everything for a brand new campaign "
                "(characters, NPCs, campaign world, scenes/locations, time, encounters, logs). Use 'session' to clear only "
                "combat, scenes, and session logs while keeping characters, NPCs and campaign data — useful "
                "at the start of a new session in the same campaign. Always confirm with the user "
                "before calling this, especially for a full reset."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "description": "'full' to wipe everything for a new campaign, 'session' to clear only combat and logs for a new session"
                    },
                    "confirm": {
                        "type": "boolean",
                        "description": "Must be true to proceed. Always ask the user to confirm before passing true."
                    }
                },
                "required": ["mode", "confirm"]
            }
        }
    }
]


def execute(function_name, arguments, config):

    if function_name != "campaign_reset":
        return f"Unknown function: {function_name}", False

    if not arguments.get("confirm", False):
        return (
            "⚠️ Reset cancelled — confirmation required. "
            "Ask the user to confirm before proceeding."
        ), False

    mode = arguments.get("mode", "full").lower().strip()
    if mode not in ("full", "session"):
        return f"Unknown mode '{mode}'. Use 'full' or 'session'.", False

    from core.plugin_loader import plugin_loader

    targets = PLUGINS_FULL if mode == "full" else PLUGINS_SESSION
    cleared = []
    errors  = []

    for plugin_name, keys in targets:
        try:
            state = plugin_loader.get_plugin_state(plugin_name)
            for key in keys:
                try:
                    state.delete(key)
                except Exception:
                    # Some implementations use save(key, None) instead of delete
                    try:
                        state.save(key, None)
                    except Exception:
                        pass
            cleared.append(plugin_name)
        except Exception as e:
            errors.append(f"{plugin_name}: {e}")

    if mode == "full":
        lines = [
            "✅ **Full campaign reset complete.**",
            "",
            "The following have been wiped:",
            "  • All player characters",
            "  • All NPCs",
            "  • Campaign world state (location, quests, notes)",
            "  • All scenes and saved locations",
            "  • Time and day tracker",
            "  • Active combat / encounter tracker",
            "  • Session logs and journal entries",
            "  • Dice roll history",
            "",
            "Start fresh with:",
            "  1. `campaign_set` — name your campaign, set location",
            "  2. `character_create` — build your party",
            "  3. `npc_generate` — populate the world",
        ]
    else:
        lines = [
            "✅ **New session ready.**",
            "",
            "Cleared:",
            "  • Active combat tracker",
            "  • Current scene and saved locations",
            "  • Time tracker",
            "  • Session log (journal entries preserved)",
            "",
            "Kept intact:",
            "  • All characters (HP, inventory, spell slots)",
            "  • NPC roster",
            "  • Campaign world state and quests",
            "",
            "Tip: use `character_heal` with is_rest='long' to restore the party before starting.",
        ]

    if errors:
        lines.append(f"\n⚠️ Some plugins could not be cleared: {'; '.join(errors)}")

    return "\n".join(lines), True
