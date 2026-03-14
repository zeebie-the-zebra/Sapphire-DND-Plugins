"""
dnd-threads — Open Narrative Threads Tracker

Tracks loose ends, consequences, and unresolved story beats.
High-urgency threads are injected into every prompt so Remmi
weaves them back naturally instead of forgetting them.
"""

from datetime import datetime

ENABLED = True
EMOJI = '🧵'
AVAILABLE_FUNCTIONS = ['thread_add', 'thread_resolve', 'thread_list', 'thread_update_urgency']

URGENCY_ORDER = {"high": 0, "medium": 1, "low": 2}
URGENCY_EMOJI = {"high": "🔴", "medium": "🟡", "low": "🟢"}
TYPE_EMOJI    = {
    "consequence": "⚡",
    "promise":     "🤝",
    "clue":        "🔍",
    "threat":      "⚠️",
    "opportunity": "✨",
    "revelation":  "💡",
}

TOOLS = [
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "thread_add",
            "description": (
                "Add an open narrative thread — a loose end, consequence, promise, clue, "
                "or unresolved story beat. Call whenever something happens that should matter "
                "later: a promise made, a villain who saw the party's faces, an uninvestigated "
                "clue, a building threat. "
                "Example: thread_add('The villain saw the party escape — he knows their faces', type='consequence', urgency='high')"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Full description. Be specific — who is involved, what happened, what it might mean."
                    },
                    "type": {
                        "type": "string",
                        "description": "Thread type: 'consequence', 'promise', 'clue', 'threat', 'opportunity', 'revelation'. Default: 'consequence'"
                    },
                    "urgency": {
                        "type": "string",
                        "description": "How soon to surface: 'high' (this session), 'medium' (soon), 'low' (background). Default: 'medium'"
                    },
                    "tag": {
                        "type": "string",
                        "description": "Optional short tag. e.g. 'coded_letter', 'bribed_cobb'"
                    }
                },
                "required": ["description"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "thread_resolve",
            "description": "Mark a thread as resolved — it has played out or is no longer relevant.",
            "parameters": {
                "type": "object",
                "properties": {
                    "thread_id": {"type": "integer", "description": "ID of the thread to resolve."},
                    "resolution": {"type": "string", "description": "Optional — how it was resolved."}
                },
                "required": ["thread_id"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "thread_list",
            "description": "List all open narrative threads. Call at session start or when deciding what consequences to bring into the current scene.",
            "parameters": {
                "type": "object",
                "properties": {
                    "urgency": {"type": "string", "description": "Optional filter: 'high', 'medium', 'low'"},
                    "type": {"type": "string", "description": "Optional filter by type."},
                    "include_resolved": {"type": "boolean", "description": "Include resolved threads. Default false."}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "thread_update_urgency",
            "description": "Change the urgency of a thread when circumstances change.",
            "parameters": {
                "type": "object",
                "properties": {
                    "thread_id": {"type": "integer", "description": "ID of the thread to update."},
                    "urgency": {"type": "string", "description": "New urgency: 'high', 'medium', or 'low'"}
                },
                "required": ["thread_id", "urgency"]
            }
        }
    }
]


def _get_state():
    from core.plugin_loader import plugin_loader
    return plugin_loader.get_plugin_state("dnd-threads")


def _load():
    return _get_state().get("threads") or {"next_id": 1, "items": []}


def _save(data):
    _get_state().save("threads", data)


def execute(function_name, arguments, config):

    if function_name == "thread_add":
        description = arguments.get("description", "").strip()
        thread_type = arguments.get("type", "consequence").strip().lower()
        urgency     = arguments.get("urgency", "medium").strip().lower()
        tag         = arguments.get("tag", "").strip().lower().replace(" ", "_")

        if not description:
            return "Error: description is required.", False

        if urgency not in URGENCY_ORDER:
            urgency = "medium"
        valid_types = {"consequence", "promise", "clue", "threat", "opportunity", "revelation"}
        if thread_type not in valid_types:
            thread_type = "consequence"

        data      = _load()
        thread_id = data.get("next_id", 1)
        data.setdefault("items", []).append({
            "id":          thread_id,
            "description": description,
            "type":        thread_type,
            "urgency":     urgency,
            "tag":         tag or None,
            "status":      "open",
            "resolution":  None,
            "created":     datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        data["next_id"] = thread_id + 1
        _save(data)

        emoji = TYPE_EMOJI.get(thread_type, "•")
        urg   = URGENCY_EMOJI.get(urgency, "")
        return f"Thread #{thread_id} added {emoji}{urg} [{thread_type.upper()} / {urgency}]: {description}", True

    elif function_name == "thread_resolve":
        thread_id  = arguments.get("thread_id")
        resolution = arguments.get("resolution", "").strip()

        if thread_id is None:
            return "Error: thread_id is required.", False

        data  = _load()
        found = next((t for t in data.get("items", []) if t["id"] == thread_id), None)

        if not found:
            return f"Thread #{thread_id} not found.", False
        if found["status"] == "resolved":
            return f"Thread #{thread_id} is already resolved.", True

        found["status"]      = "resolved"
        found["resolution"]  = resolution or "resolved"
        found["resolved_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        _save(data)

        msg = f"Thread #{thread_id} resolved: {found['description']}"
        if resolution:
            msg += f"\nResolution: {resolution}"
        return msg, True

    elif function_name == "thread_list":
        urgency_filter   = arguments.get("urgency", "").strip().lower()
        type_filter      = arguments.get("type", "").strip().lower()
        include_resolved = arguments.get("include_resolved", False)

        data     = _load()
        filtered = data.get("items", [])

        if not include_resolved:
            filtered = [t for t in filtered if t.get("status") == "open"]
        if urgency_filter:
            filtered = [t for t in filtered if t.get("urgency") == urgency_filter]
        if type_filter:
            filtered = [t for t in filtered if t.get("type") == type_filter]

        if not filtered:
            return "No threads match those filters." if (urgency_filter or type_filter) else "No open threads.", True

        filtered = sorted(filtered, key=lambda t: (URGENCY_ORDER.get(t.get("urgency", "medium"), 1), t.get("id", 0)))

        lines = [f"OPEN THREADS ({len(filtered)}):"]
        for t in filtered:
            urg    = URGENCY_EMOJI.get(t.get("urgency", ""), "")
            emoji  = TYPE_EMOJI.get(t.get("type", ""), "•")
            tag    = f" [{t['tag']}]" if t.get("tag") else ""
            status = " RESOLVED" if t.get("status") == "resolved" else ""
            lines.append(f"  #{t['id']} {emoji}{urg} {t.get('type','').upper()}{tag}{status}: {t['description']}")
            if t.get("resolution") and include_resolved:
                lines.append(f"       → {t['resolution']}")
        return "\n".join(lines), True

    elif function_name == "thread_update_urgency":
        thread_id = arguments.get("thread_id")
        urgency   = arguments.get("urgency", "").strip().lower()

        if thread_id is None:
            return "Error: thread_id is required.", False
        if urgency not in URGENCY_ORDER:
            return f"Invalid urgency. Use: high, medium, low", False

        data = _load()
        for t in data.get("items", []):
            if t["id"] == thread_id:
                old = t["urgency"]
                t["urgency"] = urgency
                _save(data)
                return f"Thread #{thread_id} urgency: {old} → {urgency}: {t['description']}", True

        return f"Thread #{thread_id} not found.", False

    return f"Unknown function: {function_name}", False
