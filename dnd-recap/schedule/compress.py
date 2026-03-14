"""
dnd-recap — Scheduled Compression Handler

Runs every 5 minutes in the background, independent of any conversation.

IMPORTANT: LLM compression has been DISABLED because scheduled LLM calls
appear as user messages in the chat UI. We use fallback compression instead.

What it does:
  - Checks if there are enough raw events to be worth compressing
  - If yes: uses simple text join fallback (no LLM call)
  - If nothing needs compressing: exits silently in ~1ms

The result is that the recap context block stays tight and readable
rather than growing into a slab of joined sentences.
"""

COMPRESS_THRESHOLD = 6   # compress when raw events exceed this
KEEP_RAW           = 3   # always keep last N events verbatim


def run(event):
    state  = event["plugin_state"]
    system = event.get("system")

    # Check if D&D mode is active before compressing
    # If dnd-toggle is installed but game is off, skip compression
    try:
        from core.plugin_loader import plugin_loader
        toggle_state = plugin_loader.get_plugin_state("dnd-toggle")
        if toggle_state:
            dnd_active = toggle_state.get("dnd_active", False)
            if not dnd_active:
                # D&D mode is off - skip compression
                return None
    except Exception:
        pass  # dnd-toggle not installed, continue normally

    data = state.get("recap") or {
        "summaries": [], "raw_events": [], "last_session": None
    }

    raw = data.get("raw_events", [])

    # Nothing to do — exit immediately
    if len(raw) <= COMPRESS_THRESHOLD:
        return None

    to_compress        = raw[:-KEEP_RAW]
    data["raw_events"] = raw[-KEEP_RAW:]

    # Use ONLY fallback compression - LLM calls from scheduled tasks
    # appear as user messages in the chat UI
    summary = _fallback_compress(to_compress)

    if summary:
        data.setdefault("summaries", []).append(summary)
        state.save("recap", data)
        return f"Compressed {len(to_compress)} events ({len(summary)} chars)"

    return None


def _fallback_compress(events):
    """Simple fallback compression without LLM."""
    if not events:
        return ""
    clean = [e.replace("[auto] ", "").replace("[tool] ", "").strip() for e in events]
    joined = " | ".join(e for e in clean if e)
    return joined[:600]
