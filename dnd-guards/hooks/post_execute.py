"""
dnd-guards — post_execute hook

Fires AFTER a tool call completes. Used to:

  1. DEATH SAVE DETECTION
     Watches character_damage results. If a character drops to 0 HP,
     automatically announces it in the response and logs it as a
     high-urgency thread so Remmi tracks death saves.

  2. AUTO RECAP LOGGING
     After significant tool calls (combat end, scene moves, NPC saves),
     auto-logs a brief note to the recap without Remmi having to think about it.

  3. COMBAT END XP
     When encounter_end_combat fires, logs XP earned to recap.

  4. SCENE MOVE LOGGING
     When the party moves somewhere, logs it to recap automatically.
"""


def post_execute(event):
    fn     = event.function_name or ""
    result = event.result or ""

    # ── 1. DEATH SAVE DETECTION ───────────────────────────────────────────
    if fn == "character_damage":
        _check_death_save(event, result)

    # ── 2. COMBAT END — log XP to recap ──────────────────────────────────
    elif fn == "encounter_end_combat":
        _log_to_recap(f"Combat ended. {result[:150]}")

    # ── 3. SCENE MOVE — log to recap ─────────────────────────────────────
    elif fn == "scene_move":
        args = event.arguments or {}
        name = args.get("name", "unknown location")
        _log_to_recap(f"Party moved to {name}.")

    # ── 4. QUEST CHANGES — log to recap ──────────────────────────────────
    elif fn == "campaign_quest":
        args   = event.arguments or {}
        action = args.get("action", "")
        quest  = args.get("quest", "")
        if action and quest:
            _log_to_recap(f"Quest {action}: {quest}")

    # ── 5. NPC SAVED — log to recap ──────────────────────────────────────
    elif fn == "npc_save":
        args = event.arguments or {}
        npc  = args.get("npc", {})
        name = npc.get("name", "") if isinstance(npc, dict) else ""
        if name:
            _log_to_recap(f"New NPC encountered and saved: {name}.")

    # ── 6. FACT SET — log important facts to recap ────────────────────────
    elif fn == "fact_set":
        args = event.arguments or {}
        key  = args.get("key", "")
        val  = args.get("value", "")
        cat  = args.get("category", "general")
        if cat in ("secrets", "clues") and key and val:
            _log_to_recap(f"[{cat.upper()}] {key}: {val[:100]}")


def _check_death_save(event, result: str):
    """
    If a character_damage call results in 0 HP, add a high-urgency
    thread and announce it so Remmi handles death saves immediately.
    """
    try:
        result_lower = result.lower()

        # Look for 0 HP indicators in the tool result
        if "0 hp" not in result_lower and "hp: 0" not in result_lower:
            return

        # Extract character name from arguments
        args      = event.arguments or {}
        char_name = args.get("name", "A character")

        # Add a high-urgency death save thread
        try:
            from core.plugin_loader import plugin_loader
            state = plugin_loader.get_plugin_state("dnd-threads")
            data  = state.get("threads") or {"next_id": 1, "items": []}

            thread_id = data.get("next_id", 1)
            data.setdefault("items", []).append({
                "id":          thread_id,
                "description": f"{char_name} is at 0 HP — death saving throws required each turn (3 successes = stable, 3 failures = dead)",
                "type":        "threat",
                "urgency":     "high",
                "tag":         f"death_save_{char_name.lower().replace(' ', '_')}",
                "status":      "open",
                "resolution":  None,
                "created":     _now()
            })
            data["next_id"] = thread_id + 1
            state.save("threads", data)
        except Exception:
            pass

        # Also log to recap
        _log_to_recap(f"⚠️ {char_name} dropped to 0 HP — death saving throws begun.")

    except Exception:
        pass


def _log_to_recap(note: str):
    """Append a brief note to the recap raw events."""
    try:
        from core.plugin_loader import plugin_loader
        state = plugin_loader.get_plugin_state("dnd-recap")
        data  = state.get("recap") or {
            "summaries": [], "raw_events": [], "last_session": None
        }
        data.setdefault("raw_events", []).append(f"[tool] {note}")

        # Auto-compress if needed
        COMPRESS_EVERY = 6
        KEEP_RAW       = 4
        raw = data["raw_events"]
        if len(raw) >= COMPRESS_EVERY + KEEP_RAW:
            to_compress        = raw[:-KEEP_RAW]
            data["raw_events"] = raw[-KEEP_RAW:]
            summary = " ".join(e.replace("[tool] ", "").replace("[auto] ", "") for e in to_compress)
            if summary:
                data.setdefault("summaries", []).append(summary)

        state.save("recap", data)
    except Exception:
        pass


def _now() -> str:
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M")
