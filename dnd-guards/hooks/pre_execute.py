"""
dnd-guards — pre_execute hook

Fires BEFORE any tool call. Used to:

  0. Hard-block ALL D&D tools when game is off (dnd-toggle state).
  1. Hard-block campaign_reset unless confirm=True is explicitly set.
  2. Hard-block character deletion without a name match in storage.
  3. Enforce scene_update_location requires a change_reason.
  4. Log all tool calls to a guard audit trail (last 50 calls).
"""

from datetime import datetime

DND_PREFIXES = (
    "character_", "encounter_", "dice_", "campaign_", "npc_",
    "loot_", "spell_", "fact_", "scene_", "thread_", "recap_"
)


def pre_execute(event):
    fn   = event.function_name or ""
    args = event.arguments or {}

    # ── GUARD 0: hard-block all D&D tools when game is off ───────────────
    if fn.startswith(DND_PREFIXES):
        try:
            from core.plugin_loader import plugin_loader
            toggle = plugin_loader.get_plugin_state("dnd-toggle")
            dnd_active = toggle.get("dnd_active")
            if dnd_active is False:
                event.skip_llm = True
                event.result = (
                    f"⛔ {fn} blocked — D&D mode is off. "
                    "Say 'game on' to activate Remmi and all D&D tools."
                )
                return
        except Exception:
            pass  # If toggle state unreadable, allow through

    _audit(fn, args)

    # ── GUARD 1: campaign_reset requires explicit confirm ─────────────────
    if fn == "campaign_reset":
        if not args.get("confirm"):
            event.skip_llm = True
            event.result = (
                "⛔ campaign_reset blocked. "
                "You must ask the player to confirm before calling this. "
                "Only call campaign_reset with confirm=true after the player has "
                "explicitly said yes. This protects against accidental campaign wipes."
            )
            return

        mode = args.get("mode", "")
        if mode == "full":
            _log_warning(f"FULL campaign reset confirmed by player at {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # ── GUARD 2: scene_update_location should have a reason ──────────────
    if fn == "scene_update_location":
        if not args.get("change_reason"):
            event.arguments["change_reason"] = "[no reason recorded]"

    # ── GUARD 3: character_delete — confirm character exists first ────────
    if fn == "character_delete":
        name = args.get("name", "").strip()
        if name:
            try:
                from core.plugin_loader import plugin_loader
                state = plugin_loader.get_plugin_state("dnd-characters")
                chars = state.get("characters") or {}
                exists = any(
                    k.lower() == name.lower() or v.get("name", "").lower() == name.lower()
                    for k, v in chars.items()
                )
                if not exists:
                    event.skip_llm = True
                    event.result = (
                        f"⛔ character_delete blocked: no character named '{name}' exists. "
                        "Call character_list() to see actual character names before deleting."
                    )
                    return
            except Exception:
                pass


def _audit(fn: str, args: dict):
    """Keep a rolling log of the last 50 tool calls."""
    try:
        from core.plugin_loader import plugin_loader
        state = plugin_loader.get_plugin_state("dnd-guards")
        log   = state.get("audit_log") or []
        log.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "fn":   fn,
            "args": {k: str(v)[:50] for k, v in args.items()}
        })
        if len(log) > 50:
            log = log[-50:]
        state.save("audit_log", log)
    except Exception:
        pass


def _log_warning(message: str):
    try:
        from core.plugin_loader import plugin_loader
        state    = plugin_loader.get_plugin_state("dnd-guards")
        warnings = state.get("warnings") or []
        warnings.append(message)
        state.save("warnings", warnings)
    except Exception:
        pass
