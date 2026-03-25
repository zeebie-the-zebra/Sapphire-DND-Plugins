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
    Iterates over all campaigns to compress each one's recap.
    Safe LLM call — runs outside of any chat turn.
    """
    try:
        from core.plugin_loader import plugin_loader
        state = plugin_loader.get_plugin_state("dnd-scaffold")
        campaign_state = plugin_loader.get_plugin_state("dnd-campaign")

        # Get all known campaign IDs
        campaigns = campaign_state.get("campaigns") or {}
        all_campaign_ids = list(campaigns.keys()) or ["default"]
        if "default" not in all_campaign_ids:
            all_campaign_ids.append("default")

        for campaign_id in all_campaign_ids:
            try:
                key = f"recap:{campaign_id}"
                data = state.get(key)
                if not data:
                    continue

                raw = data.get("raw_events", [])
                if len(raw) < COMPRESS_EVERY + KEEP_RAW:
                    continue

                to_compress = raw[:-KEEP_RAW]
                data["raw_events"] = raw[-KEEP_RAW:]

                summary_text = " ".join(
                    e.replace("[tool] ", "").replace("[auto] ", "")
                    for e in to_compress
                )

                if summary_text:
                    data.setdefault("summaries", []).append(summary_text)
                    state.save(key, data)
                    logger.info(f"[compress] Compressed {len(to_compress)} events for campaign '{campaign_id}'")
            except Exception as e:
                logger.debug(f"[compress] Failed for campaign '{campaign_id}': {e}")

    except Exception as e:
        logger.error(f"[compress] Compression failed: {e}")


# Alias for schedule hook compatibility
def schedule_handler(event=None):
    run_compress()
