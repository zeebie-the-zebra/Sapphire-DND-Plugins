"""
dnd-scaffold/hooks/compress.py — from dnd-recap

Scheduled hook: every 5 minutes
Compresses raw event log into LLM-written narrative summaries.
"""

import logging

logger = logging.getLogger("dnd-scaffold")

COMPRESS_EVERY = 6
KEEP_RAW = 4


def run_compress():
    """
    Scheduled task: compress raw recap events into narrative summaries.
    Safe LLM call — runs outside of any chat turn.
    """
    try:
        from core.plugin_loader import plugin_loader
        state = plugin_loader.get_plugin_state("dnd-scaffold")
        data = state.get("recap") or {
            "summaries": [], "raw_events": [], "last_session": None
        }

        raw = data.get("raw_events", [])
        if len(raw) < COMPRESS_EVERY + KEEP_RAW:
            logger.debug("[compress] Not enough events to compress")
            return

        to_compress = raw[:-KEEP_RAW]
        data["raw_events"] = raw[-KEEP_RAW:]

        summary_text = " ".join(
            e.replace("[tool] ", "").replace("[auto] ", "")
            for e in to_compress
        )

        if summary_text:
            data.setdefault("summaries", []).append(summary_text)
            state.save("recap", data)
            logger.info(f"[compress] Compressed {len(to_compress)} events into summary")
        else:
            logger.debug("[compress] No meaningful events to compress")

    except Exception as e:
        logger.error(f"[compress] Compression failed: {e}")


# Alias for schedule hook compatibility
def schedule_handler(event=None):
    run_compress()
