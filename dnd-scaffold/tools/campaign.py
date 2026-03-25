"""
dnd-scaffold — tools/campaign.py

Wrapped from dnd-campaign. Pre-execute signature changed from:
  def execute(function_name, arguments, config)
to:
  def execute(event)
"""

ENABLED = True
EMOJI = '🗺️'
AVAILABLE_FUNCTIONS = [
    'campaign_set', 'campaign_get', 'campaign_quest', 'campaign_set_mode',
    'campaign_create', 'campaign_list', 'campaign_switch', 'campaign_delete',
    'campaign_debug', 'campaign_clean_migration'
]

# Default campaign ID for backward compatibility
DEFAULT_CAMPAIGN_ID = "default"


def _get_state():
    from core.plugin_loader import plugin_loader
    return plugin_loader.get_plugin_state("dnd-campaign")


def _get_active_campaign(guild_id: str = None) -> str:
    """Get the active campaign ID for the current context."""
    state = _get_state()
    if guild_id:
        # Check guild-scoped key first; fall back to non-guild key for
        # cross-compatibility when campaign was set without a guild context.
        guild_val = state.get(f"active_campaign:{guild_id}")
        if guild_val:
            return guild_val
        non_guild_val = state.get("active_campaign")
        if non_guild_val:
            return non_guild_val
        return DEFAULT_CAMPAIGN_ID
    return state.get("active_campaign", DEFAULT_CAMPAIGN_ID)


def _set_active_campaign(campaign_id: str, guild_id: str = None):
    """Set the active campaign ID for the current context."""
    state = _get_state()
    import logging
    logger = logging.getLogger("dnd-campaign")
    logger.warning(f"[dnd-campaign] _set_active_campaign: campaign_id={campaign_id}, guild_id={guild_id}")
    if guild_id:
        # Always also store at the non-guild key so plugins that don't read
        # guild-scoped state can still find the active campaign correctly.
        state.save(f"active_campaign:{guild_id}", campaign_id)
        state.save("active_campaign", campaign_id)
        logger.warning(f"[dnd-campaign]   wrote active_campaign:{guild_id} AND active_campaign (both)")
    else:
        state.save("active_campaign", campaign_id)
        logger.warning(f"[dnd-campaign]   wrote active_campaign={campaign_id}")


def _get_campaign_list(guild_id: str = None) -> dict:
    """Get the list of campaigns in this guild."""
    state = _get_state()
    key = f"campaigns:{guild_id}" if guild_id else "campaigns"
    return state.get(key) or {}


def _save_campaign_list(campaigns: dict, guild_id: str = None):
    """Save the campaign list."""
    state = _get_state()
    key = f"campaigns:{guild_id}" if guild_id else "campaigns"
    state.save(key, campaigns)


def _campaign_debug(config=None) -> str:
    """
    Dump raw campaign and character plugin state for debugging.
    Shows all campaign IDs, the active campaign, and what characters
    exist under each campaign key.
    """
    from core.plugin_loader import plugin_loader
    guild_id = _get_guild_id(config)

    lines = ["🔍 Campaign Debug Output:", ""]

    # Show config context
    lines.append(f"config guild_id = {repr(guild_id)}")
    lines.append(f"config = {repr(config)}")

    try:
        camp_state = plugin_loader.get_plugin_state("dnd-campaign")
    except Exception as e:
        return f"Error accessing campaign state: {e}"

    # Active campaign (both keys)
    active_global = camp_state.get("active_campaign", "(not set)")
    lines.append(f"\nactive_campaign (global) = {active_global}")
    if guild_id:
        active_guild = camp_state.get(f"active_campaign:{guild_id}", "(not set)")
        lines.append(f"active_campaign:{guild_id} = {active_guild}")

    # Campaign list
    campaigns = _get_campaign_list(guild_id)
    lines.append(f"\nCampaign list ({len(campaigns)}): {list(campaigns.keys())}")

    # For each known campaign, check if it has character data
    lines.append(f"\nCharacter data per campaign:")
    try:
        char_state = plugin_loader.get_plugin_state("dnd-scaffold")
        all_campaign_ids = list(campaigns.keys())
        if "default" not in all_campaign_ids:
            all_campaign_ids.append("default")
        for cid in all_campaign_ids:
            chars = char_state.get(f"characters:{cid}")
            if chars:
                lines.append(f"  characters:{cid} = {list(chars.keys())}")
            else:
                lines.append(f"  characters:{cid} = (empty)")
        legacy = char_state.get("characters")
        if legacy:
            lines.append(f"  characters (legacy) = {list(legacy.keys())}")
    except Exception as e:
        lines.append(f"  Error reading character state: {e}")

    return "\n".join(lines)


def _migrate_legacy_data():
    """Migrate legacy (non-campaign-scoped) data to default campaign."""
    state = _get_state()
    # Check if legacy data exists and hasn't been migrated
    if state.get("_legacy_migrated"):
        return

    legacy = state.get("campaign")
    if legacy:
        # Migrate to default campaign
        state.save(f"campaign:{DEFAULT_CAMPAIGN_ID}", legacy)
        state.save("campaign", None)  # Clear legacy

    # Mark migration complete
    state.save("_legacy_migrated", True)


def _campaign_clean_migration(config=None) -> str:
    """
    Clean up cross-campaign character contamination caused by the legacy migration bug.

    When _migrate_if_needed ran for a new campaign, it copied ALL legacy characters
    into that campaign. This function:
    1. Initializes any missing campaign:{id} data
    2. Finds characters that appear in multiple campaigns (orphaned migrants)
    3. Removes orphaned characters from campaigns that don't own them

    Characters are kept in the campaign that is currently active (active_campaign).
    Characters that were legitimately created in a campaign stay there.
    Legacy characters are only kept in the 'default' campaign.
    """
    from core.plugin_loader import plugin_loader
    guild_id = _get_guild_id(config)
    state = _get_state()
    char_state = plugin_loader.get_plugin_state("dnd-characters")

    lines = ["🧹 Campaign Migration Cleanup:", ""]
    changed = False

    # Step 1: Initialize any missing campaign:{id} data
    campaigns = _get_campaign_list(guild_id)
    for cid in campaigns:
        campaign_data = state.get(f"campaign:{cid}")
        if not campaign_data:
            name = campaigns[cid].get("name", cid)
            state.save(f"campaign:{cid}", {"name": name})
            lines.append(f"  ✅ Initialized missing campaign:{cid} data")
            changed = True

    # Step 2: Find all character keys across campaigns
    campaign_char_keys = {}
    for cid in campaigns:
        chars = char_state.get(f"characters:{cid}") or {}
        for char_name in chars:
            if char_name not in campaign_char_keys:
                campaign_char_keys[char_name] = []
            campaign_char_keys[char_name].append(cid)

    # Legacy character names (from the original default campaign)
    legacy_chars = char_state.get("characters") or {}
    legacy_char_names = set(legacy_chars.keys())

    # Characters that appear in multiple campaigns = likely migrated orphans
    orphan_chars = {n: cids for n, cids in campaign_char_keys.items() if len(cids) > 1}
    current_active = state.get("active_campaign", DEFAULT_CAMPAIGN_ID)

    if not orphan_chars:
        lines.append("  ✅ No cross-campaign contamination found.")
        if not changed:
            lines.append("  All campaigns properly initialized.")
        return "\n".join(lines)

    lines.append(f"  Found {len(orphan_chars)} characters appearing in multiple campaigns:")
    for char_name, cids in orphan_chars.items():
        is_legacy = char_name in legacy_char_names
        # Determine the "owner" campaign:
        # - Legacy chars: owner is 'default' campaign
        # - Non-legacy: owner is the campaign where they were FIRST created
        # Since we can't know creation order reliably, keep in current active campaign
        # and remove from others
        owner = "default" if is_legacy else current_active
        if owner not in cids:
            owner = cids[0]  # fallback: keep in first campaign found

        keep_in = owner
        remove_from = [c for c in cids if c != keep_in]

        for cid in remove_from:
            chars = char_state.get(f"characters:{cid}") or {}
            if char_name in chars:
                del chars[char_name]
                char_state.save(f"characters:{cid}", chars)
                lines.append(f"  🗑️ Removed '{char_name}' from campaign '{cid}' (owner: '{keep_in}')")
                changed = True

    # Step 3: Ensure legacy characters ONLY exist in 'default' campaign
    if "default" in campaigns:
        default_chars = char_state.get("characters:default") or {}
        for char_name in legacy_char_names:
            if char_name in default_chars:
                continue  # already correctly in default
            # Remove from any non-default campaign
            for cid in campaigns:
                if cid == "default":
                    continue
                chars = char_state.get(f"characters:{cid}") or {}
                if char_name in chars:
                    del chars[char_name]
                    char_state.save(f"characters:{cid}", chars)
                    lines.append(f"  🗑️ Removed legacy char '{char_name}' from '{cid}' (kept in default)")
                    changed = True

    if changed:
        lines.insert(2, f"  Cleaned up cross-campaign contamination.")
    else:
        lines.insert(2, "  No cleanup needed.")

    return "\n".join(lines)


def _load_campaign(campaign_id: str = None) -> dict:
    """Load campaign data by ID, with backward compatibility."""
    # Ensure legacy data is migrated
    _migrate_legacy_data()

    if campaign_id is None:
        campaign_id = _get_active_campaign()

    return _get_state().get(f"campaign:{campaign_id}") or {}


def _save_campaign(campaign: dict, campaign_id: str = None):
    """Save campaign data by ID."""
    if campaign_id is None:
        campaign_id = _get_active_campaign()

    _get_state().save(f"campaign:{campaign_id}", campaign)


def _get_guild_id(config) -> str:
    """Extract guild_id from config if available."""
    if config and isinstance(config, dict):
        return config.get("guild_id")
    return None


# ── Tool Definitions ───────────────────────────────────────────────────────────

TOOLS = [
    # Campaign Management
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "campaign_create",
            "description": "Create a new campaign. Use when starting a new campaign or adventure - each campaign keeps its own characters, NPCs, quests, and progress separate.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name":         {"type": "string", "description": "Campaign name, e.g. 'Curse of Strahd'"},
                    "campaign_id":  {"type": "string", "description": "Unique ID for this campaign (auto-generated from name if omitted)"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "campaign_list",
            "description": "List all campaigns in this server. Shows which campaign is currently active.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "campaign_switch",
            "description": "Switch to a different campaign. This changes which campaign data is being viewed/edited.",
            "parameters": {
                "type": "object",
                "properties": {
                    "campaign_id": {"type": "string", "description": "The campaign ID to switch to"}
                },
                "required": ["campaign_id"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "campaign_delete",
            "description": "Delete a campaign and all its data (characters, NPCs, quests, etc.). This cannot be undone!",
            "parameters": {
                "type": "object",
                "properties": {
                    "campaign_id": {"type": "string", "description": "The campaign ID to delete"},
                    "confirm":     {"type": "boolean", "description": "Must be true to confirm deletion"}
                },
                "required": ["campaign_id", "confirm"]
            }
        }
    },
    # Existing Campaign Functions
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "campaign_set",
            "description": "Set or update the campaign's world state. Use at session start, when the party moves locations, or when the chapter changes.",
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
            "description": "Add, update, or complete (or fail) a quest in the campaign log. To remove a quest entirely, use campaign_quest_delete instead.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name":        {"type": "string", "description": "Quest name"},
                    "description": {"type": "string", "description": "Brief quest description or current objective"},
                    "status":      {"type": "string", "description": "active | completed | failed (use campaign_quest_delete to remove entirely)"},
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
            "name": "campaign_quest_delete",
            "description": "Delete a quest from the campaign log. This removes the quest entirely.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Quest name to delete"}
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
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "campaign_debug",
            "description": "Dump raw campaign and character plugin state for debugging. Shows all campaign IDs, the active campaign, and what characters exist under each campaign key.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "campaign_clean_migration",
            "description": "Clean up cross-campaign character contamination caused by a legacy migration bug. Characters that appeared in multiple campaigns (orphaned migrants) are removed from the wrong campaigns. Run this once to fix campaigns created before the multi-campaign bug was fixed.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    }
]


def execute(function_name, arguments, config):

    guild_id = _get_guild_id(config)

    # ── Campaign Management Functions ─────────────────────────────────────
    if function_name == "campaign_create":
        name = arguments.get("name", "").strip()
        if not name:
            return "Campaign name is required.", False

        campaign_id = arguments.get("campaign_id")
        if not campaign_id:
            # Generate campaign ID from name
            campaign_id = name.lower().replace(" ", "-").replace("'", "")

        # Check if campaign already exists
        campaigns = _get_campaign_list(guild_id)
        if campaign_id in campaigns:
            return f"Campaign '{name}' already exists. Use campaign_switch to switch to it.", False

        # Create campaign
        campaigns[campaign_id] = {"name": name, "created": True}
        _save_campaign_list(campaigns, guild_id)

        # Initialize campaign data so campaign_get works immediately
        state = _get_state()
        state.save(f"campaign:{campaign_id}", {"name": name})

        # Set as active
        _set_active_campaign(campaign_id, guild_id)

        return f"✅ Campaign '{name}' created! (ID: {campaign_id})\nUse campaign_set to add world details.", True

    elif function_name == "campaign_list":
        campaigns = _get_campaign_list(guild_id)
        active = _get_active_campaign(guild_id)

        if not campaigns:
            # Return legacy info if no campaigns exist yet
            campaign = _load_campaign()
            if campaign:
                return f"**Current Campaign:** {campaign.get('name', 'Unnamed')}\n(Migrated from legacy data)", True
            return "No campaigns yet. Use campaign_create to start a new campaign.", True

        lines = ["**Campaigns:**"]
        for cid, info in campaigns.items():
            marker = " 👈 (active)" if cid == active else ""
            lines.append(f"• **{info.get('name', cid)}** (ID: {cid}){marker}")
        lines.append(f"\nUse `campaign_switch` to change campaigns.")
        return "\n".join(lines), True

    elif function_name == "campaign_switch":
        campaign_id = arguments.get("campaign_id", "").strip()
        if not campaign_id:
            return "Campaign ID is required.", False

        campaigns = _get_campaign_list(guild_id)
        if campaign_id not in campaigns and campaign_id != DEFAULT_CAMPAIGN_ID:
            # Check if default campaign has data
            default_data = _get_state().get(f"campaign:{DEFAULT_CAMPAIGN_ID}")
            if not default_data:
                return f"Campaign '{campaign_id}' not found. Use campaign_list to see available campaigns.", False

        _set_active_campaign(campaign_id, guild_id)

        # Ensure campaign data exists — initialize if missing to prevent
        # _load_campaign from falling back to legacy data and causing cross-contamination
        campaign = _get_state().get(f"campaign:{campaign_id}")
        if not campaign:
            state = _get_state()
            state.save(f"campaign:{campaign_id}", {"name": campaign_id})
            campaign = {"name": campaign_id}

        cname = campaign.get("name", campaign_id)
        return f"🔄 Switched to campaign: **{cname}**", True

    elif function_name == "campaign_delete":
        campaign_id = arguments.get("campaign_id", "").strip()
        confirm = arguments.get("confirm", False)

        if not campaign_id:
            return "Campaign ID is required.", False

        if not confirm:
            return f"⚠️ To delete campaign '{campaign_id}', set confirm=true. This will PERMANENTLY DELETE all data!", False

        campaigns = _get_campaign_list(guild_id)
        if campaign_id in campaigns:
            del campaigns[campaign_id]
            _save_campaign_list(campaigns, guild_id)

        # Delete campaign data
        _get_state().save(f"campaign:{campaign_id}", None)

        # Switch to another campaign if we deleted the active one
        if _get_active_campaign(guild_id) == campaign_id:
            remaining = list(campaigns.keys())
            if remaining:
                _set_active_campaign(remaining[0], guild_id)
            else:
                _set_active_campaign(DEFAULT_CAMPAIGN_ID, guild_id)

        return f"🗑️ Campaign '{campaign_id}' and all its data have been deleted.", True

    # ── Existing Campaign Functions ───────────────────────────────────────

    elif function_name == "campaign_set":
        campaign = _load_campaign()
        fields = ["name", "chapter", "location", "time", "last_session", "world_notes", "factions"]
        updated = []
        for field in fields:
            if field in arguments and arguments[field]:
                campaign[field] = arguments[field]
                updated.append(field)
        if not updated:
            return "No campaign fields provided to update.", False
        _save_campaign(campaign)

        lines = [f"🗺️ **Campaign Updated:** {', '.join(updated)}"]
        if campaign.get("name"):      lines.append(f"Campaign: {campaign['name']}")
        if campaign.get("chapter"):   lines.append(f"Chapter: {campaign['chapter']}")
        if campaign.get("location"):  lines.append(f"Location: {campaign['location']}")
        return "\n".join(lines), True

    elif function_name == "campaign_get":
        campaign = _load_campaign()
        if not campaign:
            return "No campaign loaded yet. Use campaign_create or campaign_set to start.", True

        active_id = _get_active_campaign(guild_id)
        lines = [f"🗺️ **Campaign: {campaign.get('name', 'Unnamed')}** (ID: {active_id})"]
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
        campaign = _load_campaign()
        quests   = campaign.get("quests", [])

        # Find existing quest
        existing = next((q for q in quests if q["name"].lower() == name.lower()), None)
        status = arguments.get("status", "active")

        # Validate status value
        if status not in ("active", "completed", "failed"):
            return (
                f"Invalid status '{status}'. Use 'active', 'completed', or 'failed'. "
                "To remove a quest entirely, use campaign_quest_delete.",
                False
            )

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
        _save_campaign(campaign)
        return msg, True

    elif function_name == "campaign_quest_delete":
        name = arguments.get("name", "").strip()
        if not name:
            return "Quest name is required.", False
        campaign = _load_campaign()
        quests = campaign.get("quests", [])
        original_count = len(quests)
        quests = [q for q in quests if q["name"].lower() != name.lower()]
        if len(quests) == original_count:
            return f"No quest named '{name}' found.", False
        campaign["quests"] = quests
        _save_campaign(campaign)
        return f"🗑️ Quest deleted: **{name}**", True

    elif function_name == "campaign_set_mode":
        mode = arguments.get("mode", "in_character")
        if mode not in ("in_character", "paused"):
            return "Mode must be 'in_character' or 'paused'.", False
        campaign = _load_campaign()
        campaign["dm_mode"] = mode
        _save_campaign(campaign)
        if mode == "paused":
            return "⏸️ Game paused. Speaking out-of-character.", True
        else:
            return "▶️ Game resumed. Back in character as DM.", True

    elif function_name == "campaign_debug":
        return _campaign_debug(config), True

    elif function_name == "campaign_clean_migration":
        return _campaign_clean_migration(config), True

    return f"Unknown function: {function_name}", False
