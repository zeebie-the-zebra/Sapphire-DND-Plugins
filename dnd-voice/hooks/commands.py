"""
D&D Voice Command Handlers

Handles all voice commands registered in plugin.json.
Each handler checks the input to dispatch to the right action.
"""

from datetime import datetime


def pre_chat(event):
    from core.plugin_loader import plugin_loader

    # Check if D&D mode is active
    dnd_active = False
    try:
        toggle_state = plugin_loader.get_plugin_state("dnd-toggle")
        if toggle_state:
            dnd_active = toggle_state.get("dnd_active", False)
    except Exception:
        pass  # dnd-toggle not installed

    inp = (event.input or "").lower().strip()

    # If D&D mode is off, skip all D&D voice commands
    if not dnd_active:
        return

    # ── PAUSE GAME ──
    if any(t in inp for t in ["pause game", "pause the game", "out of character", "ooc"]):
        _pause_game(event)

    # ── RESUME GAME ──
    elif any(t in inp for t in ["resume game", "resume the game", "in character", "back to the game"]) or inp == "resume":
        _resume_game(event)

    # ── SAVE GAME ──
    elif any(t in inp for t in ["save game", "save session", "save progress"]):
        _save_game(event)

    # ── PARTY STATUS ──
    elif any(t in inp for t in ["party status", "show party", "check party", "party stats"]):
        _party_status(event)

    # ── END SESSION ──
    elif any(t in inp for t in ["end session", "end the session", "session over"]):
        _end_session(event)

    # ── RECAP — let through to LLM but prime it ──
    elif any(t in inp for t in ["recap", "what happened", "story so far", "session recap"]):
        _recap_prime(event)


def _pause_game(event):
    """Pause the game — switch to out-of-character mode."""
    try:
        from core.plugin_loader import plugin_loader
        state    = plugin_loader.get_plugin_state("dnd-campaign")
        campaign = state.get("campaign") or {}
        campaign["dm_mode"] = "paused"
        state.save("campaign", campaign)
    except Exception:
        pass

    system = event.metadata.get("system")
    if system and hasattr(system, "tts") and system.tts:
        system.tts.set_speed(1.0)

    event.skip_llm = True
    event.ephemeral = False
    event.response = "⏸️ Game paused. Out-of-character mode. Ask me anything — rules questions, planning, or lore checks. Say 'resume' to return to the story."
    event.stop_propagation = True


def _resume_game(event):
    """Resume the game — switch back to in-character DM mode."""
    try:
        from core.plugin_loader import plugin_loader
        state    = plugin_loader.get_plugin_state("dnd-campaign")
        campaign = state.get("campaign") or {}
        campaign["dm_mode"] = "in_character"
        location = campaign.get("location", "your current location")
        state.save("campaign", campaign)
    except Exception:
        location = "your current location"

    system = event.metadata.get("system")
    if system and hasattr(system, "tts") and system.tts:
        system.tts.set_speed(1.0)

    event.skip_llm = True
    event.ephemeral = False
    event.response = f"▶️ Game resumed. You are at {location}. I'm your Dungeon Master. What do you do?"
    event.stop_propagation = True


def _save_game(event):
    """Save a session checkpoint to plugin state."""
    try:
        from core.plugin_loader import plugin_loader

        # Snapshot campaign state
        cam_state  = plugin_loader.get_plugin_state("dnd-campaign")
        campaign   = cam_state.get("campaign") or {}

        # Snapshot characters
        char_state = plugin_loader.get_plugin_state("dnd-characters")
        characters = char_state.get("characters") or {}

        # Snapshot NPCs
        npc_state  = plugin_loader.get_plugin_state("dnd-npcs")
        npcs       = npc_state.get("npcs") or {}

        # Save checkpoint
        log_state  = plugin_loader.get_plugin_state("dnd-logger")
        checkpoints = log_state.get("checkpoints") or []
        checkpoints.append({
            "timestamp":  datetime.now().strftime("%Y-%m-%d %H:%M"),
            "campaign":   campaign,
            "characters": characters,
            "npcs":       npcs,
        })
        log_state.save("checkpoints", checkpoints[-10:])  # keep last 10

        loc = campaign.get("location", "unknown location")
        msg = f"💾 Game saved! Checkpoint recorded at {loc}."
    except Exception as e:
        msg = f"💾 Save attempted (some data may not have persisted: {e})"

    event.skip_llm = True
    event.ephemeral = True
    event.response = msg
    event.stop_propagation = True


def _party_status(event):
    """Quick party HP and status readout."""
    try:
        from core.plugin_loader import plugin_loader
        state = plugin_loader.get_plugin_state("dnd-characters")
        chars = state.get("characters") or {}

        if not chars:
            msg = "No characters saved. Use character_create to add your party."
        else:
            lines = ["⚔️ **Party Status:**"]
            for c in chars.values():
                hp     = c.get("hp_current", "?")
                hp_max = c.get("hp_max", "?")
                pct    = int((hp / hp_max) * 100) if isinstance(hp, int) and hp_max else 0
                bar    = "█" * (pct // 10) + "░" * (10 - pct // 10)
                conds  = f" ⚠️ {', '.join(c.get('conditions', []))}" if c.get("conditions") else ""
                lines.append(f"• **{c['name']}** [{bar}] {hp}/{hp_max} HP{conds}")

            # Check if any combat is active
            enc_state = plugin_loader.get_plugin_state("dnd-encounters")
            combat = enc_state.get("combat") or {}
            if combat:
                rnd = combat.get("round", 1)
                current = combat.get("current_turn", 0)
                combatants = combat.get("combatants", [])
                if combatants:
                    active_name = combatants[current]["name"] if current < len(combatants) else "?"
                    lines.append(f"\n🎲 **In Combat** — Round {rnd} | {active_name}'s turn")

            msg = "\n".join(lines)
    except Exception as e:
        msg = f"Couldn't load party status: {e}"

    event.skip_llm = True
    event.ephemeral = True
    event.response = msg
    event.stop_propagation = True


def _end_session(event):
    """End the session — prompt for summary."""
    try:
        from core.plugin_loader import plugin_loader
        state     = plugin_loader.get_plugin_state("dnd-logger")
        turns     = state.get("turn_count") or 0
        session   = state.get("session_num") or 1

        # Increment session counter for next time
        state.save("session_num", session + 1)
        state.save("turn_count", 0)

        msg = (
            f"📕 **Session {session} ended.** ({turns} exchanges recorded)\n\n"
            f"The session log has been saved. A journal summary will be generated automatically.\n"
            f"Say 'resume' or start a new message to begin Session {session + 1}."
        )
    except Exception:
        msg = "📕 Session ended. Start a new message to begin your next session."

    event.skip_llm = True
    event.ephemeral = False
    event.response = msg
    event.stop_propagation = True


def _recap_prime(event):
    """
    Recap request — let this through to the LLM, but prime the input
    so the DM gives a proper in-world story summary.
    """
    try:
        from core.plugin_loader import plugin_loader
        log_state = plugin_loader.get_plugin_state("dnd-logger")
        log       = log_state.get("session_log") or []
        journal   = log_state.get("journal") or []

        cam_state = plugin_loader.get_plugin_state("dnd-campaign")
        campaign  = cam_state.get("campaign") or {}

        # Pull most recent journal entry if available
        if journal:
            last = journal[-1]
            context = f"[Most recent journal entry: {last['summary'][:500]}]"
        elif log:
            recent = log[-10:]
            context = "[Recent events: " + " | ".join(
                f"Player: {t['player'][:100]}" for t in recent
            ) + "]"
        else:
            context = ""

        # Rewrite the input to prime the DM voice
        if context:
            event.input = (
                f"Give the party a dramatic in-character recap of what has happened so far "
                f"in the campaign. Speak as the Dungeon Master, in the style of a bard retelling "
                f"great deeds. Be vivid and specific. {context}"
            )
        # Let it fall through to the LLM (don't set skip_llm)
    except Exception:
        pass
