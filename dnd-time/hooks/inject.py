"""
dnd-time — Prompt Inject Hook

Injects current time into every prompt so the DM never forgets
whether it's morning, afternoon, or night.
"""

def prompt_inject(event):
    try:
        from core.plugin_loader import plugin_loader

        # Check if D&D mode is active before injecting time
        dnd_active = False
        try:
            toggle_state = plugin_loader.get_plugin_state("dnd-toggle")
            if toggle_state:
                dnd_active = toggle_state.get("dnd_active", False)
        except Exception:
            pass  # dnd-toggle not installed

        if not dnd_active:
            return

        state = plugin_loader.get_plugin_state("dnd-time")
        data = state.get("time")

        if not data:
            return

        hour = data.get("hour", 8)
        minute = data.get("minute", 0)
        day = data.get("day", 1)
        time_of_day = data.get("time_of_day", "morning")
        elapsed = data.get("elapsed_minutes", 0)

        # Format time nicely
        if hour == 0:
            time_str = "12:00 AM (midnight)"
        elif hour == 12:
            time_str = "12:00 PM (noon)"
        elif hour < 12:
            time_str = f"{hour}:{minute:02d} AM"
        else:
            time_str = f"{hour-12}:{minute:02d} PM"

        hours_elapsed = elapsed // 60
        mins_elapsed = elapsed % 60

        lines = [
            "[GAME TIME]",
            f"  It is {time_str} — {time_of_day}.",
            f"  Day {day}.",
            f"  {hours_elapsed}h {mins_elapsed}m has passed this session.",
            "",
            "IMPORTANT: Remember this time. Do not contradict it in your narration.",
            "If the party just woke up in the morning, don't later say it's night",
            "unless time has explicitly advanced with time_advance()."
        ]

        event.context_parts.append("\n".join(lines))

    except Exception:
        pass
