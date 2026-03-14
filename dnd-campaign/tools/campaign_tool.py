"""
Campaign Management Tool

Lets the LLM (or player) set and update the campaign state that
gets injected into every system prompt by the context hook.
"""

ENABLED = True
EMOJI = '🗺️'
AVAILABLE_FUNCTIONS = ['campaign_set', 'campaign_get', 'campaign_quest', 'campaign_set_mode']

TOOLS = [
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "campaign_set",
            "description": "Set or update the campaign's world state. Use at session start, when the party moves locations, or when the chapter changes. This context is injected into every system prompt.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name":         {"type": "string", "description": "Campaign name, e.g. 'Curse of Strahd'"},
                    "chapter":      {"type": "string", "description": "Current chapter or arc, e.g. 'Chapter 3: The Amber Temple'"},
                    "location":     {"type": "string", "description": "Current location, e.g. 'The village of Barovia, near the eastern gate'"},
                    "time":         {"type": "string", "description": "In-world time/date, e.g. 'Nightfall, 3rd day of the Harvest Moon'"},
                    "last_session": {"type": "string", "description": "Summary of what happened last session"},
                    "world_notes":  {"type": "string", "description": "Key lore or world-state notes for the DM to keep in mind"},
                    "factions":     {"type": "string", "description": "Key factions and their current disposition, e.g. 'The City Guard: hostile. The Thieves Guild: neutral.'"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "campaign_get",
            "description": "Get the current campaign state — location, active quests, recent summary.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "campaign_quest",
            "description": "Add, update, or complete a quest in the campaign log.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name":        {"type": "string", "description": "Quest name"},
                    "description": {"type": "string", "description": "Brief quest description or current objective"},
                    "status":      {"type": "string", "description": "active, completed, or failed"},
                    "urgent":      {"type": "boolean", "description": "Mark as urgent/time-sensitive"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "campaign_set_mode",
            "description": "Switch between DM modes: in_character (normal play), paused (out-of-character discussion).",
            "parameters": {
                "type": "object",
                "properties": {
                    "mode": {"type": "string", "description": "'in_character' for normal play, 'paused' to break the fourth wall"}
                },
                "required": ["mode"]
            }
        }
    }
]


def _get_state():
    from core.plugin_loader import plugin_loader
    return plugin_loader.get_plugin_state("dnd-campaign")

def _load() -> dict:
    return _get_state().get("campaign") or {}

def _save(campaign: dict):
    _get_state().save("campaign", campaign)


def execute(function_name, arguments, config):

    if function_name == "campaign_set":
        campaign = _load()
        fields = ["name", "chapter", "location", "time", "last_session", "world_notes", "factions"]
        updated = []
        for field in fields:
            if field in arguments and arguments[field]:
                campaign[field] = arguments[field]
                updated.append(field)
        if not updated:
            return "No campaign fields provided to update.", False
        _save(campaign)

        lines = [f"🗺️ **Campaign Updated:** {', '.join(updated)}"]
        if campaign.get("name"):      lines.append(f"Campaign: {campaign['name']}")
        if campaign.get("chapter"):   lines.append(f"Chapter: {campaign['chapter']}")
        if campaign.get("location"):  lines.append(f"Location: {campaign['location']}")
        return "\n".join(lines), True

    elif function_name == "campaign_get":
        campaign = _load()
        if not campaign:
            return "No campaign loaded yet. Use campaign_set to start.", True

        lines = [f"🗺️ **Campaign: {campaign.get('name', 'Unnamed')}**"]
        if campaign.get("chapter"):      lines.append(f"Chapter: {campaign['chapter']}")
        if campaign.get("location"):     lines.append(f"Location: {campaign['location']}")
        if campaign.get("time"):         lines.append(f"Time: {campaign['time']}")
        if campaign.get("dm_mode"):      lines.append(f"DM Mode: {campaign['dm_mode']}")

        quests = campaign.get("quests", [])
        active = [q for q in quests if q.get("status") == "active"]
        if active:
            lines.append("\n**Active Quests:**")
            for q in active:
                urg = " 🔴 URGENT" if q.get("urgent") else ""
                lines.append(f"  • {q['name']}{urg}: {q.get('description','')}")

        if campaign.get("last_session"):
            lines.append(f"\n**Last Session:** {campaign['last_session']}")
        if campaign.get("world_notes"):
            lines.append(f"\n**World Notes:** {campaign['world_notes']}")
        return "\n".join(lines), True

    elif function_name == "campaign_quest":
        name   = arguments.get("name", "").strip()
        if not name:
            return "Quest name is required.", False
        campaign = _load()
        quests   = campaign.get("quests", [])

        # Find existing quest
        existing = next((q for q in quests if q["name"].lower() == name.lower()), None)
        status = arguments.get("status", "active")

        if existing:
            if "description" in arguments: existing["description"] = arguments["description"]
            if "status" in arguments:      existing["status"]      = arguments["status"]
            if "urgent" in arguments:      existing["urgent"]      = arguments["urgent"]
            msg = f"📜 Quest updated: **{name}** ({existing['status']})"
        else:
            new_quest = {
                "name":        name,
                "description": arguments.get("description", ""),
                "status":      status,
                "urgent":      arguments.get("urgent", False),
            }
            quests.append(new_quest)
            msg = f"📜 New quest added: **{name}** ({status})"

        campaign["quests"] = quests
        _save(campaign)
        return msg, True

    elif function_name == "campaign_set_mode":
        mode = arguments.get("mode", "in_character")
        if mode not in ("in_character", "paused"):
            return "Mode must be 'in_character' or 'paused'.", False
        campaign = _load()
        campaign["dm_mode"] = mode
        _save(campaign)
        if mode == "paused":
            return "⏸️ Game paused. Speaking out-of-character.", True
        else:
            return "▶️ Game resumed. Back in character as DM.", True

    return f"Unknown function: {function_name}", False
