"""
dnd-characters — Prompt Inject Hook

Injects party composition and user control information into every prompt
to prevent the DM from narrating user character actions without input.
"""

def prompt_inject(event):
    try:
        from core.plugin_loader import plugin_loader

        # Check if D&D mode is active before injecting party info
        dnd_active = False
        try:
            toggle_state = plugin_loader.get_plugin_state("dnd-toggle")
            if toggle_state:
                dnd_active = toggle_state.get("dnd_active", False)
        except Exception:
            pass  # dnd-toggle not installed

        if not dnd_active:
            return

        state = plugin_loader.get_plugin_state("dnd-characters")
        chars = state.get("characters") or {}

        if not chars:
            return

        # Find user-controlled characters
        user_chars = []
        dm_chars = []

        for name, char in chars.items():
            if char.get("user_controlled", False):
                user_chars.append(char.get("name", name))
            else:
                dm_chars.append(char.get("name", name))

        if not user_chars:
            # No user-controlled flag set yet - assume first character or all are potential
            return

        lines = ["[PARTY]"]

        # User-controlled characters
        if user_chars:
            lines.append(f"  USER-CONTROLLED (act only when user directs): {', '.join(user_chars)}")

        # DM-controlled party members
        if dm_chars:
            lines.append(f"  DM-CONTROLLED party members: {', '.join(dm_chars)}")

        lines.append("")
        lines.append("IMPORTANT: Only describe actions for user-controlled characters WHEN THE USER INPUT DIRECTLY SPECIFICALLY ASKS FOR IT.")
        lines.append("Do NOT narrate what user characters do on your own.")
        lines.append("For DM-controlled party members, you may describe their actions as needed.")

        event.context_parts.append("\n".join(lines))

    except Exception:
        pass
