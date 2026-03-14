"""
dnd-recap — Auto Log Hook (post_chat)

Fires after every exchange. Logs a brief note of what just happened.

This hook only LOGS — it does not compress.
Compression is handled by schedule/compress.py (runs every 5 min)
which safely calls the local LLM outside of any chat turn.

WHY NO LLM CALL HERE:
Calling system.llm_chat.chat() from post_chat injects the prompt into
conversation history as a user message, causing an iteration loop.
"""

AUTO_LOG_EVERY = 3    # log a note every N turns
MAX_EVENT_LEN  = 150  # hard cap per event


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

        # Skip logging if D&D mode is off
        if not dnd_active:
            return

        response = getattr(event, "response", "") or ""
        if not response or len(response) < 50:
            return

        state = plugin_loader.get_plugin_state("dnd-recap")

        # ── Turn counter ──────────────────────────────────────────────
        turn_count = (state.get("turn_count") or 0) + 1
        state.save("turn_count", turn_count)

        if turn_count % AUTO_LOG_EVERY != 0:
            return

        # ── Extract first meaningful sentence ─────────────────────────
        sentences = [
            s.strip()
            for s in response.replace("\n", " ").split(".")
            if len(s.strip()) > 30
        ]
        if not sentences:
            return

        note = sentences[0][:MAX_EVENT_LEN]
        if not note:
            return

        # ── Append — no compression here, schedule handles that ───────
        data = state.get("recap") or {
            "summaries": [], "raw_events": [], "last_session": None
        }
        data.setdefault("raw_events", []).append(f"[auto] {note}")
        state.save("recap", data)

    except Exception:
        pass
