"""
dnd-resources — Class Resource Tracker

Tracks per-rest consumable resources so Remmi never loses count:
  - Rage (Barbarian)
  - Second Wind / Action Surge / Indomitable (Fighter)
  - Ki points (Monk)
  - Bardic Inspiration (Bard)
  - Channel Divinity (Cleric, Paladin)
  - Wild Shape (Druid)
  - Sorcery Points (Sorcerer)
  - Pact Magic slots (Warlock — tracked separately from spell slots)
  - Lay on Hands pool (Paladin)
  - Divine Sense (Paladin)
  - Sneak Attack reminder (Rogue — doesn't deplete but reminds)
  - Custom resources for any class/subclass

Resources are injected into every prompt so the model always knows
what's available without having to remember or calculate.
"""

ENABLED = True
EMOJI = '⚡'
AVAILABLE_FUNCTIONS = [
    'resource_setup', 'resource_use', 'resource_restore',
    'resource_get', 'resource_list', 'resource_set_max'
]

# ── Default resources by class/level ─────────────────────────────────────────
def _default_resources(class_name, level):
    """Return list of (name, max, recharge) tuples for a class at given level."""
    cn = class_name.lower().strip()
    resources = []

    if cn == "barbarian":
        rages = 2
        if level >= 3:  rages = 3
        if level >= 6:  rages = 4
        if level >= 12: rages = 5
        if level >= 17: rages = 6
        if level >= 20: rages = 999  # unlimited
        rage_dmg = 2 if level < 9 else (3 if level < 16 else 4)
        resources.append(("Rage", rages, "long", f"+{rage_dmg} damage, resistance to physical damage"))

    elif cn == "bard":
        insp = max(1, (lambda c: c)(10) if level < 5 else 999)
        # Bardic Inspiration = CHA mod uses (we can't know CHA mod, so store as "CHA mod")
        recharge = "short" if level >= 5 else "long"
        die = "d6" if level < 5 else ("d8" if level < 10 else ("d10" if level < 15 else "d12"))
        resources.append(("Bardic Inspiration", "CHA mod", recharge, f"{die} bonus to roll"))

    elif cn == "cleric":
        cd = 1 if level < 6 else (2 if level < 18 else 3)
        resources.append(("Channel Divinity", cd, "short", "Turn Undead or domain option"))

    elif cn == "druid":
        ws = 2  # always 2 until 20
        if level >= 20: ws = 999
        resources.append(("Wild Shape", ws, "short", f"CR up to {_wild_shape_cr(level)}"))

    elif cn == "fighter":
        resources.append(("Second Wind", 1, "short", "Heal 1d10 + level HP as bonus action"))
        as_uses = 1 if level < 17 else 2
        resources.append(("Action Surge", as_uses, "short", "Extra action"))
        if level >= 9:
            ind = 1 if level < 13 else (2 if level < 17 else 3)
            resources.append(("Indomitable", ind, "long", "Reroll failed saving throw"))

    elif cn == "monk":
        resources.append(("Ki Points", level, "short", "Flurry/Patient Defense/Step of Wind/Stunning Strike"))
        if level >= 3:
            resources.append(("Deflect Missiles", 1, "reaction", "Reduce ranged damage by 1d10+DEX+level"))

    elif cn == "paladin":
        loh = level * 5
        resources.append(("Lay on Hands", loh, "long", f"{loh} HP pool — heal or cure disease/poison (5 HP)"))
        divine_sense = max(1, 1)  # 1 + CHA mod — store as note
        resources.append(("Divine Sense", "1+CHA mod", "long", "Detect celestials/fiends/undead within 60 ft"))
        cd = 1 if level < 3 else 1  # paladin gets 1 CD use per short rest from L3
        if level >= 3:
            resources.append(("Channel Divinity", 1, "short", "Sacred Weapon or Turn the Unholy (subclass)"))

    elif cn == "ranger":
        pass  # Rangers don't have many tracked resources beyond spells

    elif cn == "rogue":
        resources.append(("Uncanny Dodge", "reaction", "passive", "Halve damage from one attack per round — reaction"))
        if level >= 7:
            resources.append(("Evasion", "passive", "passive", "DEX save: no damage on success, half on fail"))

    elif cn == "sorcerer":
        sp = level
        resources.append(("Sorcery Points", sp, "long", "Fuel Metamagic or convert to/from spell slots"))

    elif cn == "warlock":
        slots, slot_level = _warlock_slots(level)
        resources.append(("Pact Magic Slots", slots, "short", f"All at {slot_level}th spell level — regain on short rest"))
        if level >= 11:
            arcana_count = min(4, (level - 9) // 2)
            resources.append(("Mystic Arcanum", arcana_count, "long", f"One 6th-9th level spell per slot, no slot needed"))

    elif cn == "wizard":
        # Arcane Recovery
        recovery_levels = (level + 1) // 2
        resources.append(("Arcane Recovery", 1, "short", f"Regain up to {recovery_levels} levels of spell slots (max 5th level)"))

    elif cn == "artificer":
        resources.append(("Arcane Firearm/Steel Defender", 1, "long", "Subclass-dependent combat resource"))

    return resources


def _wild_shape_cr(level):
    if level >= 18: return "any"
    if level >= 8:  return "2"
    if level >= 4:  return "1"
    return "1/2"


def _warlock_slots(level):
    table = {
        1:(1,1), 2:(2,1), 3:(2,2), 4:(2,2), 5:(2,3),
        6:(2,3), 7:(2,4), 8:(2,4), 9:(2,5), 10:(2,5),
        11:(3,5), 12:(3,5), 13:(3,5), 14:(3,5), 15:(3,5),
        16:(3,5), 17:(4,5), 18:(4,5), 19:(4,5), 20:(4,5),
    }
    return table.get(level, (2, 1))


TOOLS = [
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "resource_setup",
            "description": (
                "Set up tracked resources for a character based on their class and level. "
                "Call this when a character is created or levels up. "
                "Automatically populates the correct resources for their class."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Character name"},
                    "class_name": {"type": "string", "description": "Character's class"},
                    "level": {"type": "integer", "description": "Character's current level"}
                },
                "required": ["name", "class_name", "level"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "resource_use",
            "description": (
                "REQUIRED — Mark one or more uses of a class resource as spent. "
                "Call this EVERY TIME the narrative describes a character using any limited-use class feature. "
                "If you wrote 'Grog activates Rage', 'Zara spends 3 Ki points', 'he uses Bardic Inspiration on the roll', "
                "'she uses Channel Divinity', 'the druid Wild Shapes', 'he uses Second Wind', 'she activates Flurry of Blows', "
                "or 'the warlock uses Mystic Arcanum' — you MUST call resource_use NOW. "
                "Do NOT wait until after the effect resolves. Track: Rage, Ki Points, Bardic Inspiration, Channel Divinity, "
                "Wild Shape, Second Wind, Action Surge, Lay on Hands, Sorcery Points, Pact Magic Slots, and any other limited-use class resources."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Character name"},
                    "resource": {"type": "string", "description": "Resource name (e.g. 'Rage', 'Ki Points', 'Bardic Inspiration')"},
                    "amount": {"type": "integer", "description": "How many uses spent. Default 1."}
                },
                "required": ["name", "resource"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "resource_restore",
            "description": (
                "Restore resources after a rest. "
                "rest_type='short' restores short-rest resources (Ki, Second Wind, Action Surge, Warlock slots, Channel Divinity). "
                "rest_type='long' restores everything."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Character name, or omit to restore for whole party"},
                    "rest_type": {"type": "string", "description": "'short' or 'long'"}
                },
                "required": ["rest_type"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "resource_get",
            "description": "Get current resource status for a character — what's available and what's spent.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Character name"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "resource_list",
            "description": "Get resource status for all party members at a glance.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "resource_set_max",
            "description": "Add or update a resource manually — useful for subclass features, magic items, or anything not auto-populated.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Character name"},
                    "resource": {"type": "string", "description": "Resource name"},
                    "max": {"type": "string", "description": "Maximum uses (integer or string like 'CHA mod')"},
                    "recharge": {"type": "string", "description": "When it recharges: 'short', 'long', 'dawn', 'reaction', 'passive'"},
                    "note": {"type": "string", "description": "Optional description of what it does"}
                },
                "required": ["name", "resource", "max", "recharge"]
            }
        }
    }
]

DEFAULT_CAMPAIGN_ID = "default"


def _get_campaign_id(config=None) -> str:
    from core.plugin_loader import plugin_loader
    try:
        campaign_state = plugin_loader.get_plugin_state("dnd-campaign")
        return campaign_state.get("active_campaign", DEFAULT_CAMPAIGN_ID)
    except Exception:
        return DEFAULT_CAMPAIGN_ID


def _get_state():
    from core.plugin_loader import plugin_loader
    return plugin_loader.get_plugin_state("dnd-scaffold")


def _migrate_if_needed(campaign_id: str):
    state = _get_state()
    migration_key = f"_legacy_migrated_{campaign_id}"
    if state.get(migration_key):
        return
    legacy = state.get("resources")
    if legacy:
        state.save(f"resources:{campaign_id}", legacy)
        state.save(migration_key, True)


def _load(config=None):
    campaign_id = _get_campaign_id(config)
    state = _get_state()
    _migrate_if_needed(campaign_id)
    campaign_resources = state.get(f"resources:{campaign_id}")
    if campaign_resources:
        return campaign_resources
    return state.get("resources") or {}


def _save(data, config=None):
    campaign_id = _get_campaign_id(config)
    _get_state().save(f"resources:{campaign_id}", data)


def _find_resource(char_resources, resource_name):
    """Case-insensitive resource lookup."""
    rn = resource_name.lower()
    for r in char_resources:
        if r["name"].lower() == rn or r["name"].lower().startswith(rn):
            return r
    return None


def _resource_display(r):
    current = r.get("current", r.get("max", 0))
    maximum = r.get("max", "?")
    recharge = r.get("recharge", "")
    note    = r.get("note", "")
    if recharge in ("passive", "reaction"):
        tag = f"[{recharge}]"
    else:
        tag = f"[{recharge} rest]" if recharge else ""
    depleted = ""
    try:
        if isinstance(current, int) and isinstance(maximum, int):
            if current == 0:
                depleted = " SPENT"
            elif current < maximum:
                depleted = f" ({maximum - current} spent)"
    except Exception:
        pass
    line = f"  {r['name']}: {current}/{maximum}{depleted} {tag}"
    if note:
        line += f" — {note}"
    return line


# Standalone resource_restore for use by other tools (e.g. rest.py)
def resource_restore(name: str = "", rest_type: str = "long", config=None) -> str:
    """Restore resources for a character after a rest. Exposed for cross-tool use."""
    rest_type = rest_type.strip().lower()
    data = _load(config)

    targets = [name] if name else list(data.keys())
    if not targets:
        return "No resources set up for any characters."

    SHORT_REST = {"short", "short rest"}
    lines = [f"{'Short' if rest_type == 'short' else 'Long'} rest — resources restored:"]

    for target in targets:
        char_data = data.get(target)
        if not char_data:
            continue
        restored = []
        for r in char_data.get("resources", []):
            rc = r.get("recharge", "long")
            should_restore = (rest_type == "long") or (rc == "short")
            if should_restore and rc not in ("passive", "reaction", "dawn"):
                old = r.get("current", 0)
                r["current"] = r["max"]
                if old != r["max"]:
                    restored.append(r["name"])
        if restored:
            lines.append(f"  {target}: {', '.join(restored)}")

    _save(data)
    return "\n".join(lines) if len(lines) > 1 else f"No resources needed restoring."


def execute(function_name, arguments, config):

    if function_name == "resource_setup":
        name       = arguments.get("name", "").strip()
        class_name = arguments.get("class_name", "").strip()
        level      = int(arguments.get("level", 1))

        if not name or not class_name:
            return "Error: name and class_name required.", False

        defaults   = _default_resources(class_name, level)
        data       = _load(config)
        char_res   = data.get(name, {})
        new_res    = []

        for rname, rmax, recharge, note in defaults:
            existing = _find_resource(char_res.get("resources", []), rname)
            if existing:
                existing["max"] = rmax
                if isinstance(rmax, int) and isinstance(existing.get("current"), int):
                    existing["current"] = min(existing["current"], rmax)
                new_res.append(existing)
            else:
                new_res.append({
                    "name":     rname,
                    "max":      rmax,
                    "current":  rmax,
                    "recharge": recharge,
                    "note":     note
                })

        data[name] = {"class": class_name, "level": level, "resources": new_res}
        _save(data)

        lines = [f"Resources configured for {name} (L{level} {class_name}):"]
        for r in new_res:
            lines.append(_resource_display(r))

        if not new_res:
            lines.append("  (No tracked class resources at this level — spell slots are tracked by dnd-characters)")

        return "\n".join(lines), True

    elif function_name == "resource_use":
        name     = arguments.get("name", "").strip()
        resource = arguments.get("resource", "").strip()
        amount   = int(arguments.get("amount", 1))

        data      = _load()
        char_data = data.get(name)
        if not char_data:
            return f"No resources set up for {name}. Call resource_setup first.", False

        r = _find_resource(char_data["resources"], resource)
        if not r:
            return f"No resource named '{resource}' for {name}.", False

        if r.get("recharge") in ("passive", "reaction"):
            return f"{r['name']} is a passive ability — nothing to track.", True

        current = r.get("current", 0)
        if isinstance(current, int):
            if current <= 0:
                return f"⚠️ {name} has no {r['name']} remaining! (0/{r['max']})", False
            if current < amount:
                return f"⚠️ {name} only has {current} {r['name']} remaining, can't spend {amount}.", False
            r["current"] = current - amount
        else:
            # String max (e.g. "CHA mod") — just track as note
            r["current"] = f"used {amount}"

        _save(data)
        remaining = r.get("current", "?")
        return f"{name} used {amount}× {r['name']}. Remaining: {remaining}/{r['max']}", True

    elif function_name == "resource_restore":
        result = resource_restore(
            name=arguments.get("name", "").strip(),
            rest_type=arguments.get("rest_type", "long").strip().lower(),
            config=config
        )
        return result, True

    elif function_name == "resource_get":
        name      = arguments.get("name", "").strip()
        data      = _load()
        char_data = data.get(name)

        if not char_data:
            return f"No resources set up for {name}. Call resource_setup first.", False

        lines = [f"{name} — Resources (L{char_data.get('level', '?')} {char_data.get('class', '?')}):"]
        for r in char_data["resources"]:
            lines.append(_resource_display(r))

        return "\n".join(lines), True

    elif function_name == "resource_list":
        data  = _load()
        # Get full character roster from dnd-scaffold so we show all campaign members
        # (resource_setup may not have been called for all of them yet)
        try:
            from core.plugin_loader import plugin_loader
            campaign_id = _get_campaign_id(config)
            char_state = plugin_loader.get_plugin_state("dnd-scaffold")
            all_chars = char_state.get(f"characters:{campaign_id}") or char_state.get("characters") or {}
        except Exception:
            all_chars = {}

        lines = ["PARTY RESOURCES:"]
        shown = False
        for name, char_data in all_chars.items():
            class_  = char_data.get("class_name", char_data.get("class", "?"))
            level   = char_data.get("level", "?")
            if name in data and data[name].get("resources"):
                shown = True
                lines.append(f"\n{name} (L{level} {class_}):")
                for r in data[name].get("resources", []):
                    lines.append(_resource_display(r))
            else:
                lines.append(f"\n{name} (L{level} {class_}):")
                lines.append("  (no resources tracked — call resource_setup to configure)")

        if not shown and not all_chars:
            return "No resources set up. Call resource_setup for each character.", True

        return "\n".join(lines), True

    elif function_name == "resource_set_max":
        name     = arguments.get("name", "").strip()
        resource = arguments.get("resource", "").strip()
        max_val  = arguments.get("max")
        recharge = arguments.get("recharge", "long").strip()
        note     = arguments.get("note", "").strip()

        data      = _load()
        char_data = data.setdefault(name, {"resources": [], "class": "custom", "level": 1})
        resources = char_data.setdefault("resources", [])

        existing = _find_resource(resources, resource)
        try:
            max_int = int(max_val)
        except (ValueError, TypeError):
            max_int = max_val

        if existing:
            existing["max"]      = max_int
            existing["recharge"] = recharge
            if note: existing["note"] = note
            action = "Updated"
        else:
            resources.append({
                "name":     resource,
                "max":      max_int,
                "current":  max_int,
                "recharge": recharge,
                "note":     note
            })
            action = "Added"

        _save(data)
        return f"{action} resource '{resource}' for {name}: {max_int} uses, recharges on {recharge} rest.", True

    return f"Unknown function: {function_name}", False
