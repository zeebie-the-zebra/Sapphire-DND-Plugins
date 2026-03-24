"""
dnd-scaffold/hooks/enforcement_gate.py

pre_tts hook: Commit gate — blocks TTS if pending violations exist.
Forces the LLM to make missing state-change tool calls before anything plays.

Does NOT fire on normal non-D&D conversations (checks dnd_active flag).
"""

def pre_tts(event):
    """Block TTS if there are unacknowledged state violations."""
    try:
        from core.plugin_loader import plugin_loader

        # Only enforce in D&D mode
        try:
            state = plugin_loader.get_plugin_state("dnd-scaffold")
            if not state.get("dnd_active", False):
                return
        except Exception:
            return

        # Check for pending violations
        if not state.get("pending_violations", False):
            return

        violations = state.get("violation_details") or []
        if not violations:
            # No actual violations to report, clear flag
            state.save("pending_violations", False)
            return

        # Block TTS
        event.skip_tts = True

        # Mark that we blocked — prompt_inject will pick this up
        state.save("tts_blocked", True)

        # Prepend a visible correction prompt to what TTS would have played
        # The actual text still goes to chat history, just don't speak it
        violation_lines = "\n".join(f"  • {v}" for v in violations[:10])
        block_notice = (
            f"\n\n[STATE VIOLATION — TTS BLOCKED]\n"
            f"The following tool calls were narrated but not executed:\n"
            f"{violation_lines}\n\n"
            f"Fix these NOW. Call the missing tools, then append '✓ State corrected.' "
            f"Do not continue the narrative until all violations are resolved.\n"
        )

        # Inject the correction prompt into the next input context
        # We store it so prompt_inject can pick it up
        state.save("correction_prompt", block_notice)

    except Exception:
        # Never block TTS on errors — fail open
        pass
