"""
D&D Session Logger

Fires after every AI response. Appends the exchange to a running
session log stored in plugin state. Every 20 turns it also asks the
LLM to write a summary paragraph for the campaign journal.

Logs are stored as:
  - session_log: list of {turn, player, dm, timestamp}
  - journal: list of {session_num, summary, date}
  - session_num: incrementing session counter
  - turn_count: total turns this session
"""

from datetime import datetime


def post_chat(event):
    try:
        from core.plugin_loader import plugin_loader

        # Check if D&D mode is active before logging
        dnd_active = False
        try:
            toggle_state = plugin_loader.get_plugin_state("dnd-toggle")
            if toggle_state:
                dnd_active = toggle_state.get("dnd_active", False)
        except Exception:
            pass  # dnd-toggle not installed

        # Only log if D&D mode is active
        if not dnd_active:
            return

        # Only log if there's an actual player message and DM response
        player_msg = (event.input or "").strip()
        dm_response = (event.response or "").strip()
        if not player_msg or not dm_response:
            return

        state = plugin_loader.get_plugin_state("dnd-logger")

        session_log  = state.get("session_log") or []
        journal      = state.get("journal") or []
        turn_count   = state.get("turn_count") or 0
        session_num  = state.get("session_num") or 1

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        # Append this turn
        session_log.append({
            "turn":      turn_count + 1,
            "player":    player_msg[:500],   # cap to avoid bloat
            "dm":        dm_response[:1000],
            "timestamp": timestamp,
        })
        turn_count += 1

        state.save("session_log", session_log[-200:])  # keep last 200 turns
        state.save("turn_count", turn_count)

        # NOTE: LLM summarization has been disabled in post_chat hooks.
        # The dnd-recap plugin handles compression via its scheduled task (runs every 5 min).
        # Calling system.llm_chat.chat() from post_chat can cause conversation pollution.
        # Summarization is now handled exclusively by dnd-recap's schedule/compress.py

        # Auto-increment session number on first turn of a new day
        last_date = state.get("last_date") or ""
        today = datetime.now().strftime("%Y-%m-%d")
        if last_date and last_date != today and turn_count == 1:
            state.save("session_num", session_num + 1)
        state.save("last_date", today)

    except Exception:
        pass  # never crash the pipeline
