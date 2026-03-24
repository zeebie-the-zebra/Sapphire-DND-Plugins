"""
dnd-scaffold/hooks/context_inject.py — merged from dnd-toggle (prompt_inject)
+ dnd-context-budget

prompt_inject at priority 45: reads mode stack, loads relevant mode context
files, trims to fit within context_budget setting.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def prompt_inject(event):
    """
    Fires at priority 45 — after most other D&D plugins have injected,
    but before context_budget trims.

    Injects:
    1. Current mode reminder (from mode_stack)
    2. Relevant mode context file content
    3. Context budget enforcement (from dnd-context-budget)
    """
    try:
        from core.plugin_loader import plugin_loader

        # Check if D&D mode is active
        dnd_active = False
        try:
            toggle_state = plugin_loader.get_plugin_state("dnd-scaffold")
            if toggle_state:
                dnd_active = toggle_state.get("dnd_active", False)
        except Exception:
            pass

        if not dnd_active:
            return

        # Get config for settings
        config = getattr(event, "config", None) or {}

        # Read context budget settings
        try:
            char_budget = int(getattr(config, "dnd_context_budget_char_budget", 6000))
            warn_at_percent = int(getattr(config, "dnd_context_budget_warn_at_percent", 80))
        except Exception:
            char_budget = 6000
            warn_at_percent = 80

        # Get current mode from mode_tracker
        try:
            from hooks.mode_tracker import get_current_mode
            current_mode = get_current_mode()
        except Exception:
            current_mode = "session"

        # Build mode injection
        mode_parts = []

        # Add mode context from file
        try:
            from manifest.config import MODE_CONTEXTS
            mode_file = MODE_CONTEXTS.get(current_mode)
            if mode_file:
                # Resolve relative to plugin directory
                plugin_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                mode_path = os.path.join(plugin_dir, mode_file)
                if os.path.exists(mode_path):
                    with open(mode_path, "r") as f:
                        content = f.read().strip()
                    if content:
                        mode_parts.append(f"[MODE: {current_mode.upper()}]\n{content}")
        except Exception:
            pass

        # Add mode reminder
        mode_parts.append(
            f"[Game Mode: {current_mode}] — "
            f"Use tools appropriate for {current_mode} mode. "
            f"Combat overrides all other modes when active."
        )

        if mode_parts:
            event.context_parts.append("\n\n".join(mode_parts))

        # ── Context budget trimming ─────────────────────────────────────────
        parts = event.context_parts
        if not parts:
            return

        total_chars = sum(len(p) for p in parts)
        warn_threshold = int(char_budget * (warn_at_percent / 100))
        MIN_PARTS = 3

        if total_chars <= warn_threshold:
            return

        if total_chars <= char_budget:
            # Over warn threshold but under hard limit — log only
            import logging
            logger = logging.getLogger("dnd-scaffold")
            logger.warning(
                f"[context-budget] Injected context at {total_chars} chars "
                f"({round(total_chars/char_budget*100)}% of {char_budget} budget)."
            )
            return

        # Over hard budget — trim from the tail
        trimmed_count = 0
        trimmed_chars = 0

        while sum(len(p) for p in parts) > char_budget and len(parts) > MIN_PARTS:
            removed = parts.pop()
            trimmed_count += 1
            trimmed_chars += len(removed)

        final_total = sum(len(p) for p in parts)

        import logging
        logger = logging.getLogger("dnd-scaffold")
        logger.warning(
            f"[context-budget] TRIMMED {trimmed_count} context section(s) "
            f"({trimmed_chars} chars removed). "
            f"Final: {final_total}/{char_budget} chars."
        )

        parts.append(
            f"[context-budget] ⚠️ {trimmed_count} lower-priority context section(s) were "
            f"omitted to stay within the {char_budget}-char injection budget."
        )

        event.context_parts = parts

    except Exception:
        pass
