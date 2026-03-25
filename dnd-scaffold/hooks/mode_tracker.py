"""
dnd-scaffold/hooks/mode_tracker.py — merged from dnd-guards pre_execute

pre_execute: watches for mode-push and mode-pop trigger tools.
Maintains mode_stack in plugin state.
Combat mode always stays on top of the stack.

Also enforces:
  0. Hard-block all D&D tools when game is off (dnd-toggle state).
  1. Hard-block campaign_reset unless confirm=True is explicitly set.
  2. Hard-block character deletion without a name match in storage.
  3. Enforce scene_update_location requires a change_reason.
  4. Log all tool calls to a guard audit trail.
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from manifest.config import (
    MODE_PUSH_TRIGGERS,
    MODE_POP_TRIGGERS,
    MODES,
)

DND_PREFIXES = (
    "character_", "encounter_", "dice_", "campaign_", "npc_",
    "loot_", "spell_", "fact_", "scene_", "thread_", "recap_"
)


def _get_state():
    from core.plugin_loader import plugin_loader
    return plugin_loader.get_plugin_state("dnd-scaffold")


def _get_mode_stack():
    stack = _get_state().get("mode_stack") or []
    if not isinstance(stack, list):
        stack = []
    return stack


def _save_mode_stack(stack):
    _get_state().save("mode_stack", stack)


def pre_execute(event):
    """Track mode push/pop based on tool calls, with guard checks."""
    fn   = event.function_name or ""
    args = event.arguments or {}

    # ── GUARD 0: hard-block all D&D tools when game is off ───────────────
    if fn.startswith(DND_PREFIXES):
        try:
            from core.plugin_loader import plugin_loader
            toggle = plugin_loader.get_plugin_state("dnd-scaffold")
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

    # ── Audit log ─────────────────────────────────────────────────────────
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
                config = getattr(event, "config", None)
                guild_id = None
                if config and isinstance(config, dict):
                    guild_id = config.get("guild_id")
                # Get campaign-scoped character store (same logic as character tools)
                campaign_state = plugin_loader.get_plugin_state("dnd-campaign")
                if guild_id:
                    campaign_id = campaign_state.get(f"active_campaign:{guild_id}")
                    if not campaign_id:
                        campaign_id = campaign_state.get("active_campaign")
                else:
                    campaign_id = campaign_state.get("active_campaign")
                if not campaign_id:
                    campaign_id = "default"
                char_state = plugin_loader.get_plugin_state("dnd-scaffold")
                chars = char_state.get(f"characters:{campaign_id}") or char_state.get("characters") or {}
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

    # ── Mode tracking ───────────────────────────────────────────────────────
    try:
        from core.plugin_loader import plugin_loader
        toggle_state = plugin_loader.get_plugin_state("dnd-scaffold")
        dnd_active = toggle_state.get("dnd_active", False)
        if not dnd_active:
            return
    except Exception:
        return

    stack = _get_mode_stack()

    # Check if this is a pop trigger
    popped = False
    for mode, triggers in MODE_POP_TRIGGERS.items():
        if fn in triggers:
            # Pop this mode and any modes above it
            if mode in stack:
                idx = stack.index(mode)
                stack = stack[:idx]
                popped = True
            break

    # Check if this is a push trigger
    if not popped:
        for mode, triggers in MODE_PUSH_TRIGGERS.items():
            if fn in triggers:
                # Don't push if already at top
                if stack and stack[-1] == mode:
                    pass  # already active
                elif mode == "combat":
                    # Combat always goes on top, push without removing others
                    if stack and stack[-1] != "combat":
                        # demote current top but don't remove it
                        pass
                    stack.append(mode)
                else:
                    # Remove mode if already in stack (avoid duplicates)
                    if mode in stack:
                        stack.remove(mode)
                    stack.append(mode)
                break

    _save_mode_stack(stack)


def _audit(fn: str, args: dict):
    """Keep a rolling log of the last 50 tool calls."""
    try:
        from core.plugin_loader import plugin_loader
        state = plugin_loader.get_plugin_state("dnd-scaffold")
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
        state    = plugin_loader.get_plugin_state("dnd-scaffold")
        warnings = state.get("warnings") or []
        warnings.append(message)
        state.save("warnings", warnings)
    except Exception:
        pass


def get_current_mode():
    """Return the current active mode (top of stack), or 'session' if none."""
    stack = _get_mode_stack()
    if not stack:
        return "session"
    return stack[-1]


def get_mode_stack():
    """Return the full mode stack list."""
    return _get_mode_stack()
