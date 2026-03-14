"""
dnd-facts — World Facts Registry

Stores granular, named facts about the world that Remmi must stay
consistent with. Facts are stored by key under optional categories.
The prompt_inject hook stamps all of them into every system prompt.
"""

from datetime import datetime

ENABLED = True
EMOJI = '📚'
AVAILABLE_FUNCTIONS = ['fact_set', 'fact_get', 'fact_list', 'fact_delete']

TOOLS = [
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "fact_set",
            "description": (
                "Save a specific world fact by key so Remmi never forgets or contradicts it. "
                "Use this the moment you establish any named detail — an NPC's appearance, "
                "a location's description, a password, a promise, a secret the party learned. "
                "Examples: fact_set('inn_rusty_flagon', 'Green door, smells of fish, run by Petra (one-armed, red hair)', category='locations') "
                "or fact_set('duke_password', 'silverbell', category='secrets'). "
                "Overwrites existing fact if key already exists."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "Short unique identifier, snake_case. e.g. 'inn_name', 'harbormaster_appearance', 'vault_password'"
                    },
                    "value": {
                        "type": "string",
                        "description": "The full fact to remember. Be specific."
                    },
                    "category": {
                        "type": "string",
                        "description": "Optional grouping: 'npcs', 'locations', 'secrets', 'promises', 'lore', 'clues', 'items'. Defaults to 'general'."
                    }
                },
                "required": ["key", "value"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "fact_get",
            "description": "Retrieve a specific fact by its key. Call this before describing someone or somewhere you have established before.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "The key of the fact to retrieve."}
                },
                "required": ["key"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "fact_list",
            "description": "List all saved facts, optionally filtered by category.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Optional filter: 'npcs', 'locations', 'secrets', 'promises', 'lore', 'clues', 'items', 'general'"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "fact_delete",
            "description": "Delete a fact that is no longer relevant (secret revealed, password changed, etc).",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Key of the fact to delete."}
                },
                "required": ["key"]
            }
        }
    }
]


def _get_state():
    from core.plugin_loader import plugin_loader
    return plugin_loader.get_plugin_state("dnd-facts")


def _load():
    return _get_state().get("facts") or {}


def _save(facts):
    _get_state().save("facts", facts)


def execute(function_name, arguments, config):

    if function_name == "fact_set":
        key      = arguments.get("key", "").strip().lower().replace(" ", "_")
        value    = arguments.get("value", "").strip()
        category = arguments.get("category", "general").strip().lower()

        if not key:
            return "Error: key is required.", False
        if not value:
            return "Error: value is required.", False

        facts   = _load()
        existed = key in facts
        facts[key] = {
            "value":    value,
            "category": category,
            "updated":  datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        _save(facts)
        action = "Updated" if existed else "Saved"
        return f"{action} fact [{key}] ({category}): {value}", True

    elif function_name == "fact_get":
        key   = arguments.get("key", "").strip().lower()
        facts = _load()
        if key not in facts:
            return f"No fact found with key '{key}'.", False
        f = facts[key]
        return f"[{key}] ({f['category']}): {f['value']}", True

    elif function_name == "fact_list":
        category = arguments.get("category", "").strip().lower()
        facts    = _load()

        if not facts:
            return "No facts saved yet.", True

        items = {k: v for k, v in facts.items() if v.get("category") == category} if category else facts
        if not items:
            return f"No facts in category '{category}'.", True

        by_cat = {}
        for k, v in items.items():
            cat = v.get("category", "general")
            by_cat.setdefault(cat, []).append((k, v["value"]))

        lines = ["ESTABLISHED FACTS:"]
        for cat in sorted(by_cat.keys()):
            lines.append(f"\n  [{cat.upper()}]")
            for k, val in sorted(by_cat[cat]):
                lines.append(f"    {k}: {val}")
        return "\n".join(lines), True

    elif function_name == "fact_delete":
        key   = arguments.get("key", "").strip().lower()
        facts = _load()
        if key not in facts:
            return f"No fact found with key '{key}'.", False
        del facts[key]
        _save(facts)
        return f"Deleted fact '{key}'.", True

    return f"Unknown function: {function_name}", False
