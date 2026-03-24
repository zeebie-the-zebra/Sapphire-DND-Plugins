"""
dnd-scaffold — tools/mystery.py

Wrapped from dnd-mystery. Pre-execute signature changed from:
  def execute(function_name, arguments, config)
to:
  def execute(event)

Each mystery has a name and its own set of clues, suspects, and status.
Stored under "mystery:{mystery_id}:{campaign_id}".
"""

from core.plugin_loader import plugin_loader
import json
import logging

logger = logging.getLogger("dnd-scaffold")

DEFAULT_CAMPAIGN_ID = "default"


def _get_campaign_id(config=None) -> str:
    try:
        campaign_state = plugin_loader.get_plugin_state("dnd-campaign")
        return campaign_state.get("active_campaign", DEFAULT_CAMPAIGN_ID)
    except Exception:
        return DEFAULT_CAMPAIGN_ID


def _state():
    return plugin_loader.get_plugin_state("dnd-scaffold")


def _load_mystery(mystery_id: str, config=None):
    campaign_id = _get_campaign_id(config)
    raw = _state().get(f"mystery:{mystery_id}:{campaign_id}")
    if not raw:
        return None
    return json.loads(raw) if isinstance(raw, str) else raw


def _save_mystery(mystery_id: str, data: dict, config=None):
    campaign_id = _get_campaign_id(config)
    _state().save(f"mystery:{mystery_id}:{campaign_id}", json.dumps(data))


def _load_index(config=None):
    campaign_id = _get_campaign_id(config)
    raw = _state().get(f"mystery_index:{campaign_id}")
    if not raw:
        return []
    return json.loads(raw) if isinstance(raw, str) else raw


def _save_index(index: list, config=None):
    campaign_id = _get_campaign_id(config)
    _state().save(f"mystery_index:{campaign_id}", json.dumps(index))


def mystery_create(
    name: str,
    description: str = "",
    is_active: bool = True
) -> str:
    mystery_id = name.strip().lower().replace(" ", "_")
    if not mystery_id:
        return "ERROR: mystery name cannot be empty."

    existing = _load_mystery(mystery_id)
    if existing:
        return f"Mystery '{mystery_id}' already exists. Use mystery_update to modify it."

    data = {
        "name": name,
        "description": description,
        "is_active": is_active,
        "status": "open",
        "clues": {},
        "red_herrings": {},
        "connections": {},
        "suspects": {},
        "notes": "",
        "created_session": "",
    }

    _save_mystery(mystery_id, data)

    index = _load_index()
    if mystery_id not in index:
        index.append(mystery_id)
        _save_index(index)

    status_str = "Active" if is_active else "On hold"
    return f"🔍 Mystery '{mystery_id}' created. {status_str}: {description or '(no description)'}"


def clue_add(
    mystery_id: str,
    clue_name: str,
    clue_text: str,
    clue_type: str = "physical",
    discovered_by: str = "",
    location: str = "",
    significance: str = "minor"
) -> str:
    data = _load_mystery(mystery_id)
    if not data:
        return f"Mystery '{mystery_id}' not found. Use mystery_create first."

    clue_id = clue_name.strip().lower().replace(" ", "_")

    if clue_id in data["clues"]:
        return f"Clue '{clue_id}' already exists in this mystery. Use clue_update to modify it."

    data["clues"][clue_id] = {
        "name": clue_name,
        "text": clue_text,
        "type": clue_type,
        "discovered_by": discovered_by,
        "location": location,
        "significance": significance,
        "discovered": True,
        "revealed_to_party": False,
    }

    _save_mystery(mystery_id, data)

    sig_emoji = {"critical": "🔴", "key": "🟡", "minor": "⚪"}.get(significance, "⚪")
    loc_str = f" at {location}" if location else ""
    return f"{sig_emoji} Clue '{clue_id}' added to {mystery_id}{loc_str}: {clue_text[:80]}{'...' if len(clue_text) > 80 else ''}"


def clue_reveal(mystery_id: str, clue_name: str) -> str:
    data = _load_mystery(mystery_id)
    if not data:
        return f"Mystery '{mystery_id}' not found."

    clue_id = clue_name.strip().lower().replace(" ", "_")
    if clue_id not in data["clues"]:
        return f"Clue '{clue_id}' not found in mystery '{mystery_id}'."

    data["clues"][clue_id]["revealed_to_party"] = True
    _save_mystery(mystery_id, data)
    return f"👁️ {clue_id} is now known to the party."


def clue_connect(
    mystery_id: str,
    clue_a: str,
    clue_b: str,
    connection_note: str = ""
) -> str:
    data = _load_mystery(mystery_id)
    if not data:
        return f"Mystery '{mystery_id}' not found."

    a_id = clue_a.strip().lower().replace(" ", "_")
    b_id = clue_b.strip().lower().replace(" ", "_")

    if a_id not in data["clues"]:
        return f"Clue '{a_id}' not found."
    if b_id not in data["clues"]:
        return f"Clue '{b_id}' not found."

    if "connections" not in data:
        data["connections"] = {}

    if a_id not in data["connections"]:
        data["connections"][a_id] = []
    if b_id not in data["connections"][a_id]:
        data["connections"][a_id].append(b_id)

    if b_id not in data["connections"]:
        data["connections"][b_id] = []
    if a_id not in data["connections"][b_id]:
        data["connections"][b_id].append(a_id)

    note_str = f" — {connection_note}" if connection_note else ""
    _save_mystery(mystery_id, data)
    return f"🔗 {a_id} connected to {b_id}{note_str}"


def red_herring_add(
    mystery_id: str,
    herring_name: str,
    herring_text: str,
    planted_by: str = "",
    revealed_as_herring: bool = False
) -> str:
    data = _load_mystery(mystery_id)
    if not data:
        return f"Mystery '{mystery_id}' not found."

    herring_id = herring_name.strip().lower().replace(" ", "_")

    data["red_herrings"][herring_id] = {
        "name": herring_name,
        "text": herring_text,
        "planted_by": planted_by,
        "revealed_as_herring": revealed_as_herring,
    }
    _save_mystery(mystery_id, data)

    status = "revealed" if revealed_as_herring else "hidden"
    return f"🐟 Red herring '{herring_id}' added to {mystery_id} ({status})."


def red_herring_reveal(mystery_id: str, herring_name: str) -> str:
    data = _load_mystery(mystery_id)
    if not data:
        return f"Mystery '{mystery_id}' not found."

    herring_id = herring_name.strip().lower().replace(" ", "_")
    if herring_id not in data["red_herrings"]:
        return f"Red herring '{herring_id}' not found."

    data["red_herrings"][herring_id]["revealed_as_herring"] = True
    _save_mystery(mystery_id, data)
    return f"🐟 {herring_id} revealed as a red herring."


def suspect_add(
    mystery_id: str,
    suspect_name: str,
    description: str = "",
    alibi: str = "",
    motive: str = "",
    evidence_against: str = ""
) -> str:
    data = _load_mystery(mystery_id)
    if not data:
        return f"Mystery '{mystery_id}' not found."

    suspect_id = suspect_name.strip().lower().replace(" ", "_")

    data["suspects"][suspect_id] = {
        "name": suspect_name,
        "description": description,
        "alibi": alibi,
        "motive": motive,
        "evidence_against": evidence_against,
        "cleared": False,
        "ruled_out": False,
    }
    _save_mystery(mystery_id, data)
    return f"🎭 Suspect '{suspect_id}' added to {mystery_id}."


def suspect_rulout(mystery_id: str, suspect_name: str, reason: str = "") -> str:
    data = _load_mystery(mystery_id)
    if not data:
        return f"Mystery '{mystery_id}' not found."

    suspect_id = suspect_name.strip().lower().replace(" ", "_")
    if suspect_id not in data["suspects"]:
        return f"Suspect '{suspect_id}' not found."

    data["suspects"][suspect_id]["ruled_out"] = True
    reason_str = f" ({reason})" if reason else ""
    _save_mystery(mystery_id, data)
    return f"✅ {suspect_id} ruled out{reason_str}."


def mystery_status(mystery_id: str = "") -> str:
    if mystery_id:
        return _mystery_detail(mystery_id)

    index = _load_index()
    if not index:
        return "No mysteries created. Use mystery_create to start one."

    lines = ["🔍 Active Mysteries:"]
    for mid in index:
        data = _load_mystery(mid)
        if not data:
            continue
        status = data.get("status", "open")
        clue_count = len(data.get("clues", {}))
        herring_count = len(data.get("red_herrings", {}))
        suspect_count = len(data.get("suspects", {}))
        active_marker = "▶" if data.get("is_active") else " "
        lines.append(f"  {active_marker} [{status}] {mid}: {data.get('description', '(no description)')[:50]}")
        lines.append(f"     Clues: {clue_count} | Suspects: {suspect_count} | Red Herrings: {herring_count}")

    return "\n".join(lines)


def _mystery_detail(mystery_id: str) -> str:
    data = _load_mystery(mystery_id)
    if not data:
        return f"Mystery '{mystery_id}' not found."

    status = data.get("status", "open")
    desc = data.get("description", "")

    lines = [
        f"🔍 Mystery: {mystery_id}",
        f"   Status: {status} | {desc}"
    ]

    clues = data.get("clues", {})
    revealed = {k: v for k, v in clues.items() if v.get("revealed_to_party")}
    hidden = {k: v for k, v in clues.items() if not v.get("revealed_to_party")}

    if revealed:
        lines.append(f"\n   📋 REVEALED CLUES ({len(revealed)}):")
        for cid, c in revealed.items():
            sig = c.get("significance", "minor")
            sig_mark = {"critical": "🔴", "key": "🟡", "minor": "⚪"}.get(sig, "⚪")
            loc = f" @ {c['location']}" if c.get("location") else ""
            lines.append(f"     {sig_mark} {cid}{loc}: {c['text'][:100]}")

    if hidden:
        lines.append(f"\n   🔒 UNREVEALED CLUES ({len(hidden)}):")
        for cid, c in hidden.items():
            sig = c.get("significance", "minor")
            sig_mark = {"critical": "🔴", "key": "🟡", "minor": "⚪"}.get(sig, "⚪")
            lines.append(f"     {sig_mark} {cid}: [hidden — {c['text'][:60]}...]")

    herrings = data.get("red_herrings", {})
    active_herrings = [h for h in herrings.values() if not h.get("revealed_as_herring")]
    revealed_herrings = [h for h in herrings.values() if h.get("revealed_as_herring")]

    if active_herrings:
        lines.append(f"\n   🐟 HIDDEN RED HERRINGS ({len(active_herrings)}):")
        for h in active_herrings:
            planted = f" (planted by {h['planted_by']})" if h.get("planted_by") else ""
            lines.append(f"     {h['name']}: {h['text'][:80]}{planted}")

    if revealed_herrings:
        lines.append(f"\n   ✅ REVEALED RED HERRINGS ({len(revealed_herrings)}):")
        for h in revealed_herrings:
            lines.append(f"     ~~{h['name']}: {h['text'][:80]}~~")

    suspects = data.get("suspects", {})
    active = [s for s in suspects.values() if not s.get("ruled_out")]
    ruled_out = [s for s in suspects.values() if s.get("ruled_out")]

    if active:
        lines.append(f"\n   🎭 SUSPECTS ({len(active)}):")
        for s in active:
            ev = f" evidence: {s['evidence_against'][:60]}" if s.get("evidence_against") else ""
            lines.append(f"     • {s['name']}: {s.get('description', '')}{ev}")

    if ruled_out:
        lines.append(f"\n   ✅ CLEARED SUSPECTS ({len(ruled_out)}):")
        for s in ruled_out:
            lines.append(f"     • {s['name']} (ruled out)")

    connections = data.get("connections", {})
    if connections:
        lines.append(f"\n   🔗 CLUE CONNECTIONS ({len(connections)} links):")
        for a_id, b_list in connections.items():
            for b_id in b_list:
                if a_id < b_id:
                    lines.append(f"     {a_id} ↔ {b_id}")

    return "\n".join(lines)


def mystery_solve(mystery_id: str, resolution: str = "") -> str:
    data = _load_mystery(mystery_id)
    if not data:
        return f"Mystery '{mystery_id}' not found."

    data["status"] = "solved"
    data["resolution"] = resolution
    _save_mystery(mystery_id, data)

    return f"🏆 Mystery '{mystery_id}' SOLVED! Resolution: {resolution or '(not recorded)'}"


def mystery_delete(mystery_id: str) -> str:
    data = _load_mystery(mystery_id)
    if not data:
        return f"Mystery '{mystery_id}' not found."

    campaign_id = _get_campaign_id()
    _state().save(f"mystery:{mystery_id}:{campaign_id}", None)

    index = _load_index()
    if mystery_id in index:
        index.remove(mystery_id)
        _save_index(index)

    return f"🗑️ Mystery '{mystery_id}' deleted."


TOOLS = [
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "mystery_create",
            "description": "Create a new mystery or investigative thread. Give it a short internal name (underscores, no spaces) and a description of what the party is trying to uncover.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Internal ID for this mystery (e.g. 'murder_at_the_inn'). Use underscores, no spaces."},
                    "description": {"type": "string", "description": "What the party is trying to uncover. Default: ''"},
                    "is_active": {"type": "boolean", "description": "Set as the current active mystery. Default: True"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "clue_add",
            "description": "Add a clue to a mystery when the party discovers or learns something.",
            "parameters": {
                "type": "object",
                "properties": {
                    "mystery_id": {"type": "string", "description": "The mystery this clue belongs to"},
                    "clue_name": {"type": "string", "description": "Short identifier for this clue (e.g. 'bloody_letter', 'witness_statement_1')"},
                    "clue_text": {"type": "string", "description": "Full description of what the clue shows"},
                    "clue_type": {"type": "string", "description": "Type: physical | testimony | document | circumstantial | environmental. Default: physical"},
                    "discovered_by": {"type": "string", "description": "Who found it. Default: ''"},
                    "location": {"type": "string", "description": "Where it was found. Default: ''"},
                    "significance": {"type": "string", "description": "Importance: minor | key | critical. Default: minor"}
                },
                "required": ["mystery_id", "clue_name", "clue_text"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "clue_reveal",
            "description": "Mark a clue as revealed to the party (they've learned about it in play, even if found off-screen).",
            "parameters": {
                "type": "object",
                "properties": {
                    "mystery_id": {"type": "string", "description": "The mystery"},
                    "clue_name": {"type": "string", "description": "The clue ID to reveal"}
                },
                "required": ["mystery_id", "clue_name"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "clue_connect",
            "description": "Create a logical connection between two clues. Helps track how pieces of evidence link together.",
            "parameters": {
                "type": "object",
                "properties": {
                    "mystery_id": {"type": "string", "description": "The mystery"},
                    "clue_a": {"type": "string", "description": "First clue ID"},
                    "clue_b": {"type": "string", "description": "Second clue ID"},
                    "connection_note": {"type": "string", "description": "What the connection is. Default: ''"}
                },
                "required": ["mystery_id", "clue_a", "clue_b"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "red_herring_add",
            "description": "Add a red herring — a clue that seems important but isn't connected to the truth.",
            "parameters": {
                "type": "object",
                "properties": {
                    "mystery_id": {"type": "string", "description": "The mystery"},
                    "herring_name": {"type": "string", "description": "Short identifier"},
                    "herring_text": {"type": "string", "description": "What the false lead appears to show"},
                    "planted_by": {"type": "string", "description": "Who planted it (NPC name). Default: ''"},
                    "revealed_as_herring": {"type": "boolean", "description": "Whether the party already knows it's a false lead. Default: False"}
                },
                "required": ["mystery_id", "herring_name", "herring_text"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "red_herring_reveal",
            "description": "Mark a red herring as revealed — the party has learned it's a false lead.",
            "parameters": {
                "type": "object",
                "properties": {
                    "mystery_id": {"type": "string", "description": "The mystery"},
                    "herring_name": {"type": "string", "description": "The herring ID"}
                },
                "required": ["mystery_id", "herring_name"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "suspect_add",
            "description": "Add a suspect to a mystery with their description, alibi, motive, and evidence against them.",
            "parameters": {
                "type": "object",
                "properties": {
                    "mystery_id": {"type": "string", "description": "The mystery"},
                    "suspect_name": {"type": "string", "description": "NPC name (used as ID)"},
                    "description": {"type": "string", "description": "Brief description. Default: ''"},
                    "alibi": {"type": "string", "description": "Their stated alibi. Default: ''"},
                    "motive": {"type": "string", "description": "Possible motive. Default: ''"},
                    "evidence_against": {"type": "string", "description": "What evidence points to them. Default: ''"}
                },
                "required": ["mystery_id", "suspect_name"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "suspect_rulout",
            "description": "Rule a suspect out (cleared or eliminated from the mystery).",
            "parameters": {
                "type": "object",
                "properties": {
                    "mystery_id": {"type": "string", "description": "The mystery"},
                    "suspect_name": {"type": "string", "description": "Suspect ID to rule out"},
                    "reason": {"type": "string", "description": "Why they were cleared. Default: ''"}
                },
                "required": ["mystery_id", "suspect_name"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "mystery_status",
            "description": "Get full status of a mystery — all clues (revealed and hidden), suspects, red herrings, and connections. Or list all mysteries if no ID given.",
            "parameters": {
                "type": "object",
                "properties": {
                    "mystery_id": {"type": "string", "description": "Mystery to check. If empty, shows all mysteries. Default: ''"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "mystery_solve",
            "description": "Mark a mystery as solved, with a resolution summary.",
            "parameters": {
                "type": "object",
                "properties": {
                    "mystery_id": {"type": "string", "description": "The mystery to close"},
                    "resolution": {"type": "string", "description": "What the party discovered / the truth. Default: ''"}
                },
                "required": ["mystery_id"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "mystery_delete",
            "description": "Delete a mystery and all its data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "mystery_id": {"type": "string", "description": "The mystery to delete"}
                },
                "required": ["mystery_id"]
            }
        }
    },
]


def execute(function_name, arguments, config):

    if function_name == 'mystery_create':
        return mystery_create(
            name=arguments.get('name', ''),
            description=arguments.get('description', ''),
            is_active=arguments.get('is_active', True)
        ), True

    if function_name == 'clue_add':
        return clue_add(
            mystery_id=arguments.get('mystery_id', ''),
            clue_name=arguments.get('clue_name', ''),
            clue_text=arguments.get('clue_text', ''),
            clue_type=arguments.get('clue_type', 'physical'),
            discovered_by=arguments.get('discovered_by', ''),
            location=arguments.get('location', ''),
            significance=arguments.get('significance', 'minor')
        ), True

    if function_name == 'clue_reveal':
        return clue_reveal(
            mystery_id=arguments.get('mystery_id', ''),
            clue_name=arguments.get('clue_name', '')
        ), True

    if function_name == 'clue_connect':
        return clue_connect(
            mystery_id=arguments.get('mystery_id', ''),
            clue_a=arguments.get('clue_a', ''),
            clue_b=arguments.get('clue_b', ''),
            connection_note=arguments.get('connection_note', '')
        ), True

    if function_name == 'red_herring_add':
        return red_herring_add(
            mystery_id=arguments.get('mystery_id', ''),
            herring_name=arguments.get('herring_name', ''),
            herring_text=arguments.get('herring_text', ''),
            planted_by=arguments.get('planted_by', ''),
            revealed_as_herring=arguments.get('revealed_as_herring', False)
        ), True

    if function_name == 'red_herring_reveal':
        return red_herring_reveal(
            mystery_id=arguments.get('mystery_id', ''),
            herring_name=arguments.get('herring_name', '')
        ), True

    if function_name == 'suspect_add':
        return suspect_add(
            mystery_id=arguments.get('mystery_id', ''),
            suspect_name=arguments.get('suspect_name', ''),
            description=arguments.get('description', ''),
            alibi=arguments.get('alibi', ''),
            motive=arguments.get('motive', ''),
            evidence_against=arguments.get('evidence_against', '')
        ), True

    if function_name == 'suspect_rulout':
        return suspect_rulout(
            mystery_id=arguments.get('mystery_id', ''),
            suspect_name=arguments.get('suspect_name', ''),
            reason=arguments.get('reason', '')
        ), True

    if function_name == 'mystery_status':
        return mystery_status(mystery_id=arguments.get('mystery_id', '')), True

    if function_name == 'mystery_solve':
        return mystery_solve(
            mystery_id=arguments.get('mystery_id', ''),
            resolution=arguments.get('resolution', '')
        ), True

    if function_name == 'mystery_delete':
        return mystery_delete(mystery_id=arguments.get('mystery_id', '')), True

    return f"Unknown function: {function_name}", False
