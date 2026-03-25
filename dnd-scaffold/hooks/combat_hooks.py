"""
dnd-scaffold/hooks/combat_hooks.py — merged from dnd-guards + dnd-weather + shadow_state

post_execute: watches for combat events, guards, travel, weather, and
validates state-change tool calls against the narrative.
"""

import re
from datetime import datetime


# ── Shadow state validation ───────────────────────────────────────────────────

SHADOW_TRACKED_TOOLS = {
    "character_add_item",
    "character_remove_item",
    "character_damage",
    "character_heal",
    "character_set_condition",
    "resource_use",
    "character_use_spell_slot",
    "xp_add",
}


def _shadow_get_state():
    from core.plugin_loader import plugin_loader
    return plugin_loader.get_plugin_state("dnd-scaffold")


def _recap_key(event=None):
    """Get the campaign-scoped recap key for the current context."""
    try:
        from core.plugin_loader import plugin_loader
        campaign_state = plugin_loader.get_plugin_state("dnd-campaign")
        campaign_id = campaign_state.get("active_campaign", "default")
        if event and hasattr(event, "config") and event.config:
            guild_id = event.config.get("guild_id") if isinstance(event.config, dict) else None
            if guild_id:
                val = campaign_state.get(f"active_campaign:{guild_id}")
                if val:
                    campaign_id = val
        return f"recap:{campaign_id}"
    except Exception:
        return "recap:default"


def _shadow_get_recent_narrative(event, lookback=4):
    """
    Get recent narrative text from chat history.
    Looks back 'lookback' messages to find the DM's last narrative response.
    """
    try:
        system = event.metadata.get("system")
        if not system or not hasattr(system, "llm_chat"):
            return ""
        if not hasattr(system.llm_chat, "session_manager"):
            return ""
        messages = system.llm_chat.session_manager.get_messages()
        if not messages:
            return ""
        narrative_parts = []
        for m in messages[-lookback:]:
            content = m.get("content", "")
            if isinstance(content, str) and len(content) > 10:
                narrative_parts.append(content)
        return " ".join(narrative_parts)
    except Exception:
        return ""


def _shadow_flag_discrepancy(state, tool, args, message, raw_context=""):
    """Log a shadow state discrepancy to state."""
    try:
        discrepancies = state.get("shadow_discrepancies") or []
        discrepancies.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tool": tool,
            "args": {k: str(v)[:80] for k, v in args.items()},
            "message": message,
            "context_preview": raw_context[:200] if raw_context else "",
        })
        if len(discrepancies) > 30:
            discrepancies = discrepancies[-30:]
        state.save("shadow_discrepancies", discrepancies)

        try:
            recap_data = state.get(_recap_key(event)) or {"raw_events": []}
            recap_data.setdefault("raw_events", []).append(
                f"[SHADOW] {message}"
            )
            state.save(_recap_key(event), recap_data)
        except Exception:
            pass
    except Exception:
        pass  # Never crash on shadow checks


def _shadow_validate_tool(event, fn, args, result, narrative, narrative_lower, state):
    """Run per-tool shadow validation. Returns True if a discrepancy was flagged."""
    item_keywords = []
    char_lower = ""

    if fn == "character_add_item":
        item = (args.get("item") or "").strip().lower()
        char = (args.get("name") or "").strip()
        quantity = args.get("quantity", 1)

        if not item or len(item) < 2:
            return False

        item_keywords = [word for word in item.split() if len(word) > 3]
        item_mentioned = any(kw in narrative_lower for kw in item_keywords) if item_keywords else False

        acquisition_verbs = ["takes", "finds", "picks", "receives", "gets", "grabs", "loots", "obtains", "acquires", "hands"]
        narrative_has_acquisition = any(verb in narrative_lower for verb in acquisition_verbs)

        if not item_mentioned and not narrative_has_acquisition:
            _shadow_flag_discrepancy(
                state, fn, args,
                f"character_add_item called for '{item}' but narrative contains no mention "
                f"of acquiring this item. Tool result: {result[:100]}",
                raw_context=narrative[:300]
            )
            return True

    elif fn == "character_remove_item":
        item = (args.get("item") or "").strip().lower()
        char = (args.get("name") or "").strip()

        if not item or len(item) < 2:
            return False

        item_keywords = [word for word in item.split() if len(word) > 3]
        item_mentioned = any(kw in narrative_lower for kw in item_keywords) if item_keywords else False

        removal_verbs = ["sells", "loses", "drops", "destroys", "consumes", "gives", "stolen", "parts with"]
        narrative_has_removal = any(verb in narrative_lower for verb in removal_verbs)

        if not item_mentioned and not narrative_has_removal:
            _shadow_flag_discrepancy(
                state, fn, args,
                f"character_remove_item called for '{item}' but narrative contains no mention "
                f"of losing, selling, or disposing of this item. Tool result: {result[:100]}",
                raw_context=narrative[:300]
            )
            return True

    elif fn == "character_damage":
        char = (args.get("name") or "").strip()
        amount = args.get("amount", 0)

        if not char:
            return False

        char_lower = char.lower()
        damage_indicators = ["takes", "damage", "hit", "wounds", "strikes", "deals", "suffers"]
        char_mentioned_near_damage = False

        words = narrative_lower.split()
        for i, word in enumerate(words):
            if char_lower in word:
                context = " ".join(words[max(0, i-3):i+4])
                if any(ind in context for ind in damage_indicators):
                    char_mentioned_near_damage = True
                    break

        has_damage_number = any([
            re.search(rf'\b\d+\b.*\b{re.escape(char_lower)}\b', narrative_lower),
            re.search(rf'\b{re.escape(char_lower)}\b.*\b\d+\b.*(?:damage|hit)', narrative_lower),
        ])

        if not char_mentioned_near_damage and not has_damage_number:
            _shadow_flag_discrepancy(
                state, fn, args,
                f"character_damage called for '{char}' ({amount} HP) but narrative contains no "
                f"description of this character taking damage. Tool result: {result[:100]}",
                raw_context=narrative[:300]
            )
            return True

    elif fn == "character_heal":
        char = (args.get("name") or "").strip()
        amount = args.get("amount", 0)

        if not char:
            return False

        char_lower = char.lower()
        heal_indicators = ["heals", "recovers", "restores", "cure", "healing", "potions"]
        char_mentioned_near_heal = False

        words = narrative_lower.split()
        for i, word in enumerate(words):
            if char_lower in word:
                context = " ".join(words[max(0, i-3):i+4])
                if any(ind in context for ind in heal_indicators):
                    char_mentioned_near_heal = True
                    break

        if not char_mentioned_near_heal:
            _shadow_flag_discrepancy(
                state, fn, args,
                f"character_heal called for '{char}' ({amount} HP) but narrative contains no "
                f"description of this character being healed. Tool result: {result[:100]}",
                raw_context=narrative[:300]
            )
            return True

    elif fn == "character_set_condition":
        char = (args.get("name") or "").strip()
        condition = (args.get("condition") or "").strip().lower()
        active = args.get("active", True)
        if isinstance(active, str):
            active = active.strip().lower() not in ("false", "0", "no", "off", "remove", "")

        if not char or not condition:
            return False

        char_lower = char.lower()
        cond_mentioned = condition in narrative_lower

        if not cond_mentioned and active:
            _shadow_flag_discrepancy(
                state, fn, args,
                f"character_set_condition called to apply '{condition}' to '{char}' but narrative "
                f"contains no mention of this condition. Tool result: {result[:100]}",
                raw_context=narrative[:300]
            )
            return True

    elif fn == "resource_use":
        char = (args.get("name") or "").strip()
        resource = (args.get("resource") or "").strip().lower()
        amount = args.get("amount", 1)

        if not char:
            return False

        char_lower = char.lower()
        resource_keywords = resource.split()
        resource_mentioned = any(kw in narrative_lower for kw in resource_keywords if len(kw) > 3)

        use_indicators = ["uses", "activates", "enters", "spends", "casts"]
        char_near_use = any(ind in narrative_lower for ind in use_indicators)

        if not resource_mentioned and not char_near_use:
            _shadow_flag_discrepancy(
                state, fn, args,
                f"resource_use called for '{resource}' ({amount} uses) but narrative contains no "
                f"description of this resource being used. Tool result: {result[:100]}",
                raw_context=narrative[:300]
            )
            return True

    elif fn == "xp_add":
        xp = args.get("xp", 0)
        reason = (args.get("reason") or "").strip().lower()
        char = (args.get("name") or "").strip()

        xp_mentioned = f"{xp} xp" in narrative_lower or f"{xp} experience" in narrative_lower

        if not xp_mentioned and not reason:
            _shadow_flag_discrepancy(
                state, fn, args,
                f"xp_add called for {xp} XP but narrative contains no mention of XP being awarded. "
                f"Tool result: {result[:100]}",
                raw_context=narrative[:300]
            )
            return True

    return False


def post_execute(event):
    """Handle post-execute events: combat, travel, weather."""
    fn = event.function_name or ""
    result = event.result or ""

    # ── 1. Death save detection ────────────────────────────────────────────
    if fn == "character_damage":
        _check_death_save(event, result)

    # ── 2. Combat end — log XP to recap ───────────────────────────────────
    elif fn == "encounter_end_combat":
        _log_to_recap(f"Combat ended. {result[:150]}", event)
        _check_level_ups(event)

    # ── 3. Scene move — log to recap ─────────────────────────────────────
    elif fn == "scene_move":
        args = event.arguments or {}
        name = args.get("name", "unknown location")
        _log_to_recap(f"Party moved to {name}.", event)

    # ── 4. Quest changes — log to recap ──────────────────────────────────
    elif fn == "campaign_quest":
        args = event.arguments or {}
        action = args.get("action", "")
        quest = args.get("quest", "")
        if action and quest:
            _log_to_recap(f"Quest {action}: {quest}", event)

    # ── 5. NPC saved — log to recap ──────────────────────────────────────
    elif fn == "npc_save":
        args = event.arguments or {}
        npc = args.get("npc", {})
        name = npc.get("name", "") if isinstance(npc, dict) else ""
        if name:
            _log_to_recap(f"New NPC encountered and saved: {name}.", event)

    # ── 6. Fact set — log important facts to recap ────────────────────────
    elif fn == "fact_set":
        args = event.arguments or {}
        key = args.get("key", "")
        val = args.get("value", "")
        cat = args.get("category", "general")
        if cat in ("secrets", "clues") and key and val:
            _log_to_recap(f"[{cat.upper()}] {key}: {val[:100]}", event)

    # ── 7. Travel advance — weather shift chance ─────────────────────────
    elif fn == "travel_advance":
        _handle_travel_advance(event)

    # ── 8. Shadow state validation ─────────────────────────────────────────
    if fn in SHADOW_TRACKED_TOOLS:
        _run_shadow_validation(event, fn, result)


def _check_death_save(event, result: str):
    """If a character_damage call results in 0 HP, add a high-urgency thread."""
    try:
        result_lower = result.lower()

        if "0 hp" not in result_lower and "hp: 0" not in result_lower:
            return

        args = event.arguments or {}
        char_name = args.get("name", "A character")

        try:
            from core.plugin_loader import plugin_loader
            state = plugin_loader.get_plugin_state("dnd-scaffold")
            data = state.get("threads") or {"next_id": 1, "items": []}

            thread_id = data.get("next_id", 1)
            data.setdefault("items", []).append({
                "id": thread_id,
                "description": f"{char_name} is at 0 HP — death saving throws required each turn (3 successes = stable, 3 failures = dead)",
                "type": "threat",
                "urgency": "high",
                "tag": f"death_save_{char_name.lower().replace(' ', '_')}",
                "status": "open",
                "resolution": None,
                "created": _now()
            })
            data["next_id"] = thread_id + 1
            state.save("threads", data)
        except Exception:
            pass

        _log_to_recap(f"⚠️ {char_name} dropped to 0 HP — death saving throws begun.", event)

    except Exception:
        pass


def _check_level_ups(event=None):
    """Check if any characters are ready to level up after combat XP awards."""
    try:
        from core.plugin_loader import plugin_loader

        char_state = plugin_loader.get_plugin_state("dnd-scaffold")
        chars = char_state.get("characters") or {}

        try:
            lv_state = plugin_loader.get_plugin_state("dnd-scaffold")
            xp_data = lv_state.get("xp_data") or {}
        except Exception:
            return

        XP_THRESHOLDS = {
            1: 0, 2: 300, 3: 900, 4: 2700, 5: 6500, 6: 14000, 7: 23000, 8: 34000,
            9: 48000, 10: 64000, 11: 85000, 12: 100000, 13: 120000, 14: 140000,
            15: 165000, 16: 195000, 17: 225000, 18: 265000, 19: 305000, 20: 355000
        }

        ready = []
        for key, char in chars.items():
            data = xp_data.get(key, {})
            xp = data.get("xp", 0)
            level = char.get("level", 1)
            # Find current level based on XP
            for lvl, threshold in sorted(XP_THRESHOLDS.items()):
                if xp >= threshold:
                    level = lvl
            next_threshold = XP_THRESHOLDS.get(level + 1)
            if next_threshold and xp >= next_threshold:
                ready.append((char.get("name", key), level + 1))

        if ready:
            names = ", ".join(f"{n} (→ L{lv})" for n, lv in ready)
            _log_to_recap(f"⬆️ LEVEL UP READY after XP award: {names}", event)

    except Exception:
        pass


def _handle_travel_advance(event):
    """Handle weather shift after travel_advance from dnd-weather."""
    try:
        from core.plugin_loader import plugin_loader

        state = plugin_loader.get_plugin_state("dnd-scaffold")
        auto_enabled = state.get("auto_weather_advance", False)

        if not auto_enabled:
            return

        args = event.arguments or {}
        hours = args.get("hours_passed", args.get("hours", 8))

        if hours <= 4:
            return

        # Weather advance is handled by the travel tool itself
        # This hook is for any post-travel bookkeeping

    except Exception:
        pass


def _log_to_recap(note: str, event=None):
    """Append a brief note to the recap raw events (campaign-scoped)."""
    try:
        from core.plugin_loader import plugin_loader
        state = plugin_loader.get_plugin_state("dnd-scaffold")
        key = _recap_key(event) if event else "recap:default"
        data = state.get(key) or {
            "summaries": [], "raw_events": [], "last_session": None
        }
        data.setdefault("raw_events", []).append(f"[tool] {note}")

        # Auto-compress if needed
        COMPRESS_EVERY = 6
        KEEP_RAW = 4
        raw = data["raw_events"]
        if len(raw) >= COMPRESS_EVERY + KEEP_RAW:
            to_compress = raw[:-KEEP_RAW]
            data["raw_events"] = raw[-KEEP_RAW:]
            summary = " ".join(e.replace("[tool] ", "").replace("[auto] ", "") for e in to_compress)
            if summary:
                data.setdefault("summaries", []).append(summary)

        state.save(key, data)
    except Exception:
        pass


def _run_shadow_validation(event, fn, result):
    """Run shadow state validation for state-change tool calls."""
    try:
        state = _shadow_get_state()
    except Exception:
        return

    narrative = _shadow_get_recent_narrative(event, lookback=4)
    narrative_lower = narrative.lower()
    args = event.arguments or {}

    _shadow_validate_tool(event, fn, args, result, narrative, narrative_lower, state)


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")
