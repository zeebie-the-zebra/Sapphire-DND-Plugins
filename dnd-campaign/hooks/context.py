"""
Campaign Context Injector

Silently injects the current campaign state into every system prompt.
This ensures the DM AI always knows:
  - Campaign name and current chapter/arc
  - Current location
  - Active quests
  - Party members (from character sheets if available)
  - Recent session summary
  - World notes / lore
  - DM mode (in-character vs out-of-character)

This fires at the prompt_inject hook stage, so the player never sees it
and it doesn't cost context window on every message — it's part of
the system prompt, built fresh each turn.

Supports multiple campaigns - loads data for the active campaign.
"""


DEFAULT_CAMPAIGN_ID = "default"


def _get_campaign_id(guild_id=None):
    """Get the active campaign ID for this context."""
    from core.plugin_loader import plugin_loader
    state = plugin_loader.get_plugin_state("dnd-campaign")

    if guild_id:
        return state.get(f"active_campaign:{guild_id}", DEFAULT_CAMPAIGN_ID)
    return state.get("active_campaign", DEFAULT_CAMPAIGN_ID)


def _load_campaign(guild_id=None):
    """Load campaign data for the active campaign."""
    from core.plugin_loader import plugin_loader
    state = plugin_loader.get_plugin_state("dnd-campaign")

    campaign_id = _get_campaign_id(guild_id)

    # Check for legacy data and migrate if needed
    if not state.get("_legacy_migrated"):
        legacy = state.get("campaign")
        if legacy:
            state.save(f"campaign:{DEFAULT_CAMPAIGN_ID}", legacy)
            state.save("campaign", None)
        state.save("_legacy_migrated", True)

    return state.get(f"campaign:{campaign_id}") or {}


def prompt_inject(event):
    try:
        from core.plugin_loader import plugin_loader

        # Check if D&D mode is active before injecting campaign context
        dnd_active = False
        try:
            toggle_state = plugin_loader.get_plugin_state("dnd-toggle")
            if toggle_state:
                dnd_active = toggle_state.get("dnd_active", False)
        except Exception:
            pass  # dnd-toggle not installed

        if not dnd_active:
            return

        # Get guild_id from event if available
        guild_id = getattr(event, 'guild_id', None)

        campaign = _load_campaign(guild_id)

        if not campaign:
            # No campaign set up yet — inject a minimal reminder
            event.context_parts.append(
                "[DM SYSTEM] No campaign is currently loaded. "
                "Use the campaign_create tool to establish a new campaign, "
                "or campaign_set to continue with legacy data."
            )
            return

        # Check DM mode
        dm_mode = campaign.get("dm_mode", "in_character")
        if dm_mode == "paused":
            event.context_parts.append(
                "[DM SYSTEM] The game is currently PAUSED. "
                "You are speaking as yourself (the AI assistant), not as the DM. "
                "Answer questions out-of-character. Use 'resume' voice command or campaign_set to resume."
            )
            return

        campaign_id = _get_campaign_id(guild_id)
        parts = [f"[CAMPAIGN STATE — DM REFERENCE (Campaign: {campaign_id})]"]

        name = campaign.get("name", "Unnamed Campaign")
        parts.append(f"Campaign: {name}")

        if campaign.get("chapter"):
            parts.append(f"Current Chapter/Arc: {campaign['chapter']}")

        if campaign.get("location"):
            parts.append(f"Current Location: {campaign['location']}")

        if campaign.get("time"):
            parts.append(f"In-World Time: {campaign['time']}")

        # Active quests
        quests = campaign.get("quests", [])
        active = [q for q in quests if q.get("status") == "active"]
        completed = [q for q in quests if q.get("status") == "completed"]
        if active:
            parts.append("Active Quests:")
            for q in active:
                urgency = f" [URGENT]" if q.get("urgent") else ""
                parts.append(f"  • {q['name']}{urgency}: {q.get('description','')}")
        if completed:
            parts.append(f"Recently Completed: {', '.join(q['name'] for q in completed[-3:])}")

        # Party - filtered by campaign
        try:
            char_state = plugin_loader.get_plugin_state("dnd-characters")
            chars = char_state.get(f"characters:{campaign_id}") or {}
            if not chars:
                # Check for legacy character data
                legacy_chars = char_state.get("characters")
                if legacy_chars and not char_state.get(f"_legacy_migrated_{campaign_id}"):
                    chars = legacy_chars
                    # Migrate to campaign scope
                    char_state.save(f"characters:{campaign_id}", chars)
                    char_state.save(f"_legacy_migrated_{campaign_id}", True)

            if chars:
                parts.append("Party:")
                for c in chars.values():
                    hp = c.get("hp_current", "?")
                    hp_max = c.get("hp_max", "?")
                    conds = f" [{','.join(c.get('conditions',[]))}]" if c.get("conditions") else ""
                    parts.append(f"  • {c['name']} — {c['race']} {c['class_name']} Lv{c.get('level',1)} | HP {hp}/{hp_max}{conds}")
        except Exception:
            pass

        # Factions / world state
        if campaign.get("factions"):
            parts.append(f"Key Factions: {campaign['factions']}")

        # Recent events (last session summary)
        if campaign.get("last_session"):
            parts.append(f"Last Session Summary: {campaign['last_session']}")

        # World notes / lore
        if campaign.get("world_notes"):
            parts.append(f"World Notes: {campaign['world_notes']}")

        # DM persona reminder
        parts.append(
            "You are the Dungeon Master. Narrate in vivid present tense. "
            "Call for dice rolls when appropriate. Track consequences. "
            "Play all NPCs in character. Never break the fourth wall unless paused."
        )

        event.context_parts.append("\n".join(parts))

    except Exception as e:
        # Never crash the pipeline
        pass