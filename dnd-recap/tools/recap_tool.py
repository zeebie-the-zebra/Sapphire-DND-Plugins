"""
dnd-recap — Rolling Session Summary

Maintains a compressed running narrative of the session.
Old events are compressed into dense summaries placed at the top
of context where local models pay most attention.
"""

COMPRESS_EVERY = 6
KEEP_RAW       = 4

ENABLED = True
EMOJI = '📜'
AVAILABLE_FUNCTIONS = ['recap_add_event', 'recap_get', 'recap_compress', 'recap_new_session', 'recap_summarize']

TOOLS = [
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "recap_add_event",
            "description": (
                "Log an important event to the session recap. Call this for any significant "
                "moment: a revelation, major decision, NPC interaction, combat result, discovery. "
                "Be specific — names, outcomes, what changed. "
                "Example: recap_add_event('Party discovered Harbormaster Voss is blackmailed "
                "by the Sea Prince. He gave them the dock manifest for 50gp.')"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "event": {
                        "type": "string",
                        "description": "What happened. Include names, outcomes, discoveries, decisions."
                    }
                },
                "required": ["event"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "recap_get",
            "description": "Get the full session recap — compressed summaries and recent raw events.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "recap_compress",
            "description": "Manually compress old raw events into a summary. Happens automatically but call this if the log is getting long.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "recap_summarize",
            "description": (
                "Generate a narrative-style summary of recent session events using the LLM. "
                "This creates a story-style summary that gets injected into the LLM's context. "
                "Use when you want richer, more narrative summaries of what happened."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "recap_new_session",
            "description": "Archive everything into a 'last session' summary and start fresh. Call at the beginning of a new play session.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    }
]

DEFAULT_CAMPAIGN_ID = "default"


def _get_state():
    from core.plugin_loader import plugin_loader
    return plugin_loader.get_plugin_state("dnd-recap")


def _get_campaign_id(config=None) -> str:
    """Get current campaign ID, defaulting to 'default' for backward compatibility."""
    from core.plugin_loader import plugin_loader

    try:
        campaign_state = plugin_loader.get_plugin_state("dnd-campaign")
        campaign_id = campaign_state.get("active_campaign", DEFAULT_CAMPAIGN_ID)
        if campaign_id:
            return campaign_id
    except Exception:
        pass

    return DEFAULT_CAMPAIGN_ID


def _migrate_if_needed(campaign_id: str):
    """Migrate legacy recap data to campaign scope if needed."""
    state = _get_state()
    migration_key = f"_legacy_migrated_{campaign_id}"

    if state.get(migration_key):
        return

    # Check for legacy data
    legacy = state.get("recap")
    if legacy:
        state.save(f"recap:{campaign_id}", legacy)
        state.save(migration_key, True)


def _load(config=None):
    """Load recap for the current campaign."""
    campaign_id = _get_campaign_id(config)
    state = _get_state()

    # Migrate legacy data if needed
    _migrate_if_needed(campaign_id)

    # Try campaign-scoped data first
    campaign_recap = state.get(f"recap:{campaign_id}")
    if campaign_recap:
        return campaign_recap

    # Fall back to legacy data for backward compatibility
    return state.get("recap") or {
        "summaries": [], "raw_events": [], "last_session": None
    }


def _save(data, config=None):
    """Save recap to the current campaign's storage."""
    campaign_id = _get_campaign_id(config)
    _get_state().save(f"recap:{campaign_id}", data)


def _compress_simple(events):
    """Join events into a dense paragraph. No LLM needed."""
    if not events:
        return ""
    return " ".join(e.replace("[auto] ", "").replace("[tool] ", "") for e in events)


def _maybe_compress(data):
    """Auto-compress if raw events exceed threshold."""
    raw = data.get("raw_events", [])
    if len(raw) >= COMPRESS_EVERY + KEEP_RAW:
        to_compress        = raw[:-KEEP_RAW]
        data["raw_events"] = raw[-KEEP_RAW:]
        summary            = _compress_simple(to_compress)
        if summary:
            data.setdefault("summaries", []).append(summary)
    return data


def execute(function_name, arguments, config):

    # Helper to get campaign-scoped data
    def load():
        return _load(config)

    def save(data):
        _save(data, config)

    if function_name == "recap_add_event":
        event_text = arguments.get("event", "").strip()
        if not event_text:
            return "Error: event text is required.", False

        data = load()
        data.setdefault("raw_events", []).append(event_text)
        data = _maybe_compress(data)
        save(data)
        return (
            f"Event logged. "
            f"({len(data['raw_events'])} recent, "
            f"{len(data.get('summaries', []))} compressed)"
        ), True

    elif function_name == "recap_get":
        data  = _load()
        lines = []

        if data.get("last_session"):
            lines.append(f"PREVIOUS SESSION:\n  {data['last_session']}\n")

        summaries = data.get("summaries", [])
        if summaries:
            lines.append("EARLIER THIS SESSION:")
            for s in summaries:
                lines.append(f"  {s}")
            lines.append("")

        raw = data.get("raw_events", [])
        if raw:
            lines.append("RECENT EVENTS:")
            for e in raw:
                lines.append(f"  • {e}")

        return ("\n".join(lines) if lines else "No session history yet."), True

    elif function_name == "recap_compress":
        data = load()
        raw  = data.get("raw_events", [])

        if len(raw) <= KEEP_RAW:
            return f"Only {len(raw)} raw events — nothing to compress yet.", True

        to_compress        = raw[:-KEEP_RAW]
        data["raw_events"] = raw[-KEEP_RAW:]
        summary            = _compress_simple(to_compress)

        if summary:
            data.setdefault("summaries", []).append(summary)
            save(data)
            return f"Compressed {len(to_compress)} events:\n{summary}", True
        return "Compression produced no output.", False

    elif function_name == "recap_new_session":
        data       = _load()
        all_events = list(data.get("summaries", [])) + list(data.get("raw_events", []))

        if not all_events:
            save({"summaries": [], "raw_events": [], "last_session": None})
            return "New session started. (No previous events to archive.)", True

        full_summary = _compress_simple(all_events)
        save({"summaries": [], "raw_events": [], "last_session": full_summary})
        return f"New session started. Archived:\n{full_summary}", True

    elif function_name == "recap_summarize":
        """Generate narrative-style summary. Ask the LLM directly - say 'can you summarize what happened?' and the LLM will provide a narrative summary based on the injected recap context."""
        data = load()
        raw = data.get("raw_events", [])

        if len(raw) < 2:
            return "Not enough events to summarize yet.", True

        # Use simple compression
        summary = _compress_simple(raw)

        if summary:
            # Save to summaries for LLM context
            data.setdefault("summaries", []).append(summary)
            save(data)
            return (
                f"Summary saved to context. You can also ask me directly: "
                f"'Can you summarize what happened?' and I'll provide a narrative recap based on:\n{summary}"
            ), True

        return "Could not generate summary.", False

    return f"Unknown function: {function_name}", False
