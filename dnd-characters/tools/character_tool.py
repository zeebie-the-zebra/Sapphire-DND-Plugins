"""
D&D Character Sheet Manager

Persistent storage for all player characters. Tracks:
  - Core stats (STR, DEX, CON, INT, WIS, CHA) and modifiers
  - HP (current, max, temp), AC, speed, level, class, race
  - Spell slots (by level, current and max)
  - Inventory and gold
  - Conditions / status effects
  - Death saves
  - Skills, saving throws, proficiencies
  - Notes / backstory
"""

import json
from datetime import datetime

ENABLED = True
EMOJI = '📋'
AVAILABLE_FUNCTIONS = [
    'character_create',
    'character_get',
    'character_update',
    'character_list',
    'character_delete',
    'character_damage',
    'character_heal',
    'character_use_spell_slot',
    'character_restore_spell_slots',
    'character_add_item',
    'character_remove_item',
    'character_set_condition',
    'character_set_user_controlled',
]

TOOLS = [
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "character_create",
            "description": "Create a new D&D player character sheet. Use when a player introduces a new character or starts a new campaign.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name":       {"type": "string",  "description": "Character name"},
                    "player":     {"type": "string",  "description": "Player's real name (optional)"},
                    "race":       {"type": "string",  "description": "Character race, e.g. Human, Elf, Dwarf"},
                    "class_name": {"type": "string",  "description": "Character class, e.g. Fighter, Wizard, Rogue"},
                    "level":      {"type": "integer", "description": "Starting level (default 1)"},
                    "hp_max":     {"type": "integer", "description": "Maximum hit points"},
                    "ac":         {"type": "integer", "description": "Armor class"},
                    "speed":      {"type": "integer", "description": "Speed in feet (default 30)"},
                    "str": {"type": "integer", "description": "Strength score"},
                    "dex": {"type": "integer", "description": "Dexterity score"},
                    "con": {"type": "integer", "description": "Constitution score"},
                    "int": {"type": "integer", "description": "Intelligence score"},
                    "wis": {"type": "integer", "description": "Wisdom score"},
                    "cha": {"type": "integer", "description": "Charisma score"},
                    "proficiency_bonus": {"type": "integer", "description": "Proficiency bonus (default based on level)"},
                    "background":  {"type": "string", "description": "Character background, e.g. Soldier, Noble"},
                    "alignment":   {"type": "string", "description": "Alignment, e.g. Chaotic Good"},
                    "backstory":   {"type": "string", "description": "Brief backstory notes"},
                    "spell_slots": {
                        "type": "object",
                        "description": "Spell slots by level, e.g. {\"1\": 4, \"2\": 3}. Only for spellcasters."
                    },
                    "user_controlled": {
                        "type": "boolean",
                        "description": "True if this is the user's character (acts only on user input). Set to true for player characters."
                    }
                },
                "required": ["name", "class_name", "race", "hp_max"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "character_get",
            "description": "Retrieve a character's full sheet. Use before making decisions about a character's abilities, HP, or resources.",
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
            "name": "character_update",
            "description": "Update any fields on a character sheet. Use for level-ups, stat changes, AC changes, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name":   {"type": "string", "description": "Character name"},
                    "fields": {"type": "object", "description": "Key-value pairs of fields to update, e.g. {\"level\": 5, \"ac\": 16}"}
                },
                "required": ["name", "fields"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "character_list",
            "description": "List all saved characters with a brief summary. Use at session start or when asked who's in the party.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "character_delete",
            "description": "Permanently delete a character sheet.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Character name to delete"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "character_damage",
            "description": "Apply damage to a character. Handles temp HP first, then real HP. Tracks death saves when HP reaches 0.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name":   {"type": "string",  "description": "Character name"},
                    "amount": {"type": "integer", "description": "Damage amount"},
                    "type":   {"type": "string",  "description": "Damage type, e.g. fire, slashing, necrotic (optional)"}
                },
                "required": ["name", "amount"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "character_heal",
            "description": "Heal a character. Can also add temporary HP. Use after healing spells, potions, or short/long rests.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name":    {"type": "string",  "description": "Character name"},
                    "amount":  {"type": "integer", "description": "HP to restore"},
                    "temp":    {"type": "boolean", "description": "If true, adds as temporary HP instead"},
                    "is_rest": {"type": "string",  "description": "'short' or 'long' — long rest restores to max + resets spell slots"}
                },
                "required": ["name", "amount"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "character_use_spell_slot",
            "description": "Expend a spell slot when a character casts a spell.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name":  {"type": "string",  "description": "Character name"},
                    "level": {"type": "integer", "description": "Spell slot level (1-9)"}
                },
                "required": ["name", "level"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "character_restore_spell_slots",
            "description": "Restore spell slots after a long rest or class feature (e.g. Arcane Recovery).",
            "parameters": {
                "type": "object",
                "properties": {
                    "name":   {"type": "string", "description": "Character name"},
                    "levels": {"type": "array",  "items": {"type": "integer"}, "description": "Specific slot levels to restore, or omit to restore all"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "character_add_item",
            "description": "Add an item to a character's inventory. Use when party finds loot or purchases equipment.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name":     {"type": "string",  "description": "Character name"},
                    "item":     {"type": "string",  "description": "Item name"},
                    "quantity": {"type": "integer", "description": "Quantity (default 1)"},
                    "notes":    {"type": "string",  "description": "Item notes, e.g. '+1 enchanted', 'cursed'"}
                },
                "required": ["name", "item"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "character_remove_item",
            "description": "Remove or consume an item from a character's inventory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name":     {"type": "string",  "description": "Character name"},
                    "item":     {"type": "string",  "description": "Item name"},
                    "quantity": {"type": "integer", "description": "Quantity to remove (default 1)"}
                },
                "required": ["name", "item"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "character_set_condition",
            "description": "Add or remove a condition from a character (poisoned, blinded, stunned, unconscious, etc.).",
            "parameters": {
                "type": "object",
                "properties": {
                    "name":      {"type": "string",  "description": "Character name"},
                    "condition": {"type": "string",  "description": "Condition name, e.g. 'poisoned', 'blinded', 'stunned'"},
                    "active":    {"type": "boolean", "description": "True to apply, False to remove"}
                },
                "required": ["name", "condition", "active"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "character_set_user_controlled",
            "description": (
                "Mark which character(s) the USER is playing. Only the user-controlled character(s) "
                "should take actions based on user input. Other party members are NPC-controlled "
                "and should only act when the user explicitly directs them or in combat."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Character names that the USER is controlling"
                    }
                },
                "required": ["names"]
            }
        }
    }
]


# ── Helpers ────────────────────────────────────────────────────────────────────

def _modifier(score: int) -> str:
    mod = (score - 10) // 2
    return f"+{mod}" if mod >= 0 else str(mod)

def _prof_bonus(level: int) -> int:
    return max(2, (level - 1) // 4 + 2)

def _get_state():
    from core.plugin_loader import plugin_loader
    return plugin_loader.get_plugin_state("dnd-characters")

def _load_all() -> dict:
    state = _get_state()
    return state.get("characters") or {}

def _save_all(chars: dict):
    _get_state().save("characters", chars)

def _find(name: str, chars: dict):
    key = name.lower().strip()
    for k, v in chars.items():
        if k.lower() == key:
            return k, v
    return None, None

def _sync_combat_hp(char_name: str, new_hp: int):
    """
    If this character is in an active combat encounter, sync their HP
    in the encounter tracker so both systems stay in agreement.
    """
    try:
        from core.plugin_loader import plugin_loader
        enc_state = plugin_loader.get_plugin_state("dnd-encounters")
        combat = enc_state.get("combat")
        if not combat:
            return
        combatants = combat.get("combatants", [])
        changed = False
        for c in combatants:
            if c["name"].lower() == char_name.lower():
                c["hp"] = new_hp
                changed = True
                break
        if changed:
            combat["combatants"] = combatants
            enc_state.save("combat", combat)
    except Exception:
        pass  # never crash on sync failure


def _sheet_summary(c: dict) -> str:
    hp     = c.get("hp_current", c.get("hp_max", "?"))
    hp_max = c.get("hp_max", "?")
    hp_tmp = c.get("hp_temp", 0)
    tmp_str = f" (+{hp_tmp} temp)" if hp_tmp else ""
    conditions = c.get("conditions", [])
    cond_str = f" | ⚠️ {', '.join(conditions)}" if conditions else ""
    slots = c.get("spell_slots_current", {})
    slot_str = ""
    if slots:
        slot_parts = [f"L{lvl}:{used}/{c['spell_slots_max'].get(lvl,0)}" for lvl, used in sorted(slots.items())]
        slot_str = f"\nSpell Slots: {', '.join(slot_parts)}"

    inv = c.get("inventory", [])
    inv_str = ""
    if inv:
        inv_lines = [f"  • {i['item']} x{i['quantity']}" + (f" ({i['notes']})" if i.get('notes') else "") for i in inv]
        inv_str = "\nInventory:\n" + "\n".join(inv_lines)

    gold = c.get("gold", 0)

    stats = {k: c.get(k, 10) for k in ["str","dex","con","int","wis","cha"]}
    stat_line = " | ".join(f"{k.upper()} {v}({_modifier(v)})" for k, v in stats.items())

    return (
        f"═══ {c['name']} ═══\n"
        f"{c.get('race','?')} {c.get('class_name','?')} Level {c.get('level',1)}"
        + (f" | {c.get('background','')}" if c.get('background') else "")
        + (f" | {c.get('alignment','')}" if c.get('alignment') else "") + "\n"
        f"HP: {hp}/{hp_max}{tmp_str} | AC: {c.get('ac','?')} | Speed: {c.get('speed',30)}ft{cond_str}\n"
        f"Prof Bonus: +{c.get('proficiency_bonus', _prof_bonus(c.get('level',1)))}\n"
        f"{stat_line}"
        f"{slot_str}"
        f"\nGold: {gold}gp"
        f"{inv_str}"
        + (f"\nNotes: {c['backstory']}" if c.get('backstory') else "")
    )


# ── execute ────────────────────────────────────────────────────────────────────

def execute(function_name, arguments, config):
    chars = _load_all()

    # ── character_create ──
    if function_name == "character_create":
        name = arguments.get("name", "").strip()
        if not name:
            return "Character name is required.", False

        key, existing = _find(name, chars)
        if existing:
            return f"A character named '{name}' already exists. Use character_update to modify them.", False

        level = arguments.get("level", 1)
        hp_max = arguments.get("hp_max", 10)
        spell_slots_raw = arguments.get("spell_slots", {})
        spell_slots_max = {str(k): v for k, v in spell_slots_raw.items()}

        char = {
            "name":             name,
            "player":           arguments.get("player", ""),
            "race":             arguments.get("race", "Human"),
            "class_name":       arguments.get("class_name", "Fighter"),
            "level":            level,
            "background":       arguments.get("background", ""),
            "alignment":        arguments.get("alignment", ""),
            "backstory":        arguments.get("backstory", ""),
            "hp_max":           hp_max,
            "hp_current":       hp_max,
            "hp_temp":          0,
            "ac":               arguments.get("ac", 10),
            "speed":            arguments.get("speed", 30),
            "str":              arguments.get("str", 10),
            "dex":              arguments.get("dex", 10),
            "con":              arguments.get("con", 10),
            "int":              arguments.get("int", 10),
            "wis":              arguments.get("wis", 10),
            "cha":              arguments.get("cha", 10),
            "proficiency_bonus": arguments.get("proficiency_bonus", _prof_bonus(level)),
            "spell_slots_max":     spell_slots_max,
            "spell_slots_current": {k: v for k, v in spell_slots_max.items()},
            "inventory":        [],
            "gold":             0,
            "conditions":       [],
            "death_saves":      {"successes": 0, "failures": 0},
            "created":          datetime.now().strftime("%Y-%m-%d"),
            "user_controlled":  arguments.get("user_controlled", False),
        }
        chars[name] = char
        _save_all(chars)
        return f"✅ Character created!\n\n{_sheet_summary(char)}", True

    # ── character_get ──
    elif function_name == "character_get":
        name = arguments.get("name", "")
        key, char = _find(name, chars)
        if not char:
            return f"No character found named '{name}'. Use character_list to see all characters.", False
        return _sheet_summary(char), True

    # ── character_list ──
    elif function_name == "character_list":
        if not chars:
            return "No characters saved yet. Use character_create to add your party.", True
        lines = ["**Party:**"]
        for c in chars.values():
            hp = c.get("hp_current", "?")
            hp_max = c.get("hp_max", "?")
            conds = f" ⚠️{','.join(c.get('conditions',[]))}" if c.get("conditions") else ""
            lines.append(f"• **{c['name']}** — {c['race']} {c['class_name']} Lv{c['level']} | HP {hp}/{hp_max}{conds}")
        return "\n".join(lines), True

    # ── character_update ──
    elif function_name == "character_update":
        name = arguments.get("name", "")
        key, char = _find(name, chars)
        if not char:
            return f"No character found named '{name}'.", False
        fields = arguments.get("fields", {})
        if not fields:
            return "No fields provided to update.", False
        for k, v in fields.items():
            # Strip "gp" suffix from gold if accidentally included
            if k == "gold" and isinstance(v, str) and v.lower().endswith("gp"):
                v = v[:-2].strip()
                try:
                    v = int(v)
                except ValueError:
                    pass
            char[k] = v
        chars[key] = char
        _save_all(chars)
        changed = ", ".join(f"{k}={v}" for k, v in fields.items())
        return f"✅ {key} updated: {changed}", True

    # ── character_delete ──
    elif function_name == "character_delete":
        name = arguments.get("name", "")
        key, char = _find(name, chars)
        if not char:
            return f"No character named '{name}' found.", False
        del chars[key]
        _save_all(chars)
        return f"🗑️ '{key}' has been deleted.", True

    # ── character_damage ──
    elif function_name == "character_damage":
        name   = arguments.get("name", "")
        amount = int(arguments.get("amount", 0))
        dmg_type = arguments.get("type", "")
        key, char = _find(name, chars)
        if not char:
            return f"No character named '{name}'.", False

        type_str = f" {dmg_type}" if dmg_type else ""
        remaining = amount

        # Burn temp HP first
        temp = char.get("hp_temp", 0)
        if temp > 0:
            absorbed = min(temp, remaining)
            char["hp_temp"] = temp - absorbed
            remaining -= absorbed

        old_hp = char.get("hp_current", char["hp_max"])
        new_hp = max(0, old_hp - remaining)
        char["hp_current"] = new_hp
        chars[key] = char
        _save_all(chars)
        _sync_combat_hp(key, new_hp)  # keep encounter tracker in sync

        msg = f"💥 {key} takes {amount}{type_str} damage. HP: {old_hp} → {new_hp}/{char['hp_max']}"
        if char.get("hp_temp", 0) < temp:
            msg += f" (temp HP absorbed {amount - remaining})"
        if new_hp == 0:
            msg += "\n💀 **DOWN! Make death saving throws.**"
        elif new_hp <= char["hp_max"] // 4:
            msg += "\n⚠️ *Bloodied — critically low HP!*"
        return msg, True

    # ── character_heal ──
    elif function_name == "character_heal":
        name    = arguments.get("name", "")
        amount  = int(arguments.get("amount", 0))
        is_temp = arguments.get("temp", False)
        is_rest = arguments.get("is_rest", "")
        key, char = _find(name, chars)
        if not char:
            return f"No character named '{name}'.", False

        if is_temp:
            current_temp = char.get("hp_temp", 0)
            char["hp_temp"] = max(current_temp, amount)  # temp HP doesn't stack, take higher
            chars[key] = char
            _save_all(chars)
            return f"🛡️ {key} gains {amount} temporary HP. (Temp HP: {char['hp_temp']})", True

        if is_rest == "long":
            char["hp_current"] = char["hp_max"]
            char["hp_temp"]    = 0
            char["death_saves"] = {"successes": 0, "failures": 0}
            char["conditions"]  = [c for c in char.get("conditions", []) if c in ("exhaustion",)]
            # Restore all spell slots
            char["spell_slots_current"] = {k: v for k, v in char.get("spell_slots_max", {}).items()}
            chars[key] = char
            _save_all(chars)
            _sync_combat_hp(key, char["hp_max"])  # keep encounter tracker in sync
            return f"🌙 {key} takes a long rest. HP restored to {char['hp_max']}/{char['hp_max']}. Spell slots restored.", True

        old_hp = char.get("hp_current", char["hp_max"])
        new_hp = min(char["hp_max"], old_hp + amount)
        char["hp_current"] = new_hp
        chars[key] = char
        _save_all(chars)
        _sync_combat_hp(key, new_hp)  # keep encounter tracker in sync
        return f"💚 {key} heals {amount} HP. HP: {old_hp} → {new_hp}/{char['hp_max']}", True

    # ── character_use_spell_slot ──
    elif function_name == "character_use_spell_slot":
        name  = arguments.get("name", "")
        level = str(arguments.get("level", 1))
        key, char = _find(name, chars)
        if not char:
            return f"No character named '{name}'.", False

        current = char.get("spell_slots_current", {})
        max_slots = char.get("spell_slots_max", {})
        available = current.get(level, 0)
        if available <= 0:
            return f"❌ {key} has no level {level} spell slots remaining.", False
        current[level] = available - 1
        char["spell_slots_current"] = current
        chars[key] = char
        _save_all(chars)
        return f"✨ {key} expends a level {level} spell slot. Remaining: {available-1}/{max_slots.get(level,0)}", True

    # ── character_restore_spell_slots ──
    elif function_name == "character_restore_spell_slots":
        name   = arguments.get("name", "")
        levels = arguments.get("levels", None)
        key, char = _find(name, chars)
        if not char:
            return f"No character named '{name}'.", False

        max_slots = char.get("spell_slots_max", {})
        current   = char.get("spell_slots_current", {})
        if levels:
            for lvl in levels:
                lvl_str = str(lvl)
                current[lvl_str] = max_slots.get(lvl_str, 0)
            restored = f"levels {', '.join(str(l) for l in levels)}"
        else:
            current = {k: v for k, v in max_slots.items()}
            restored = "all levels"

        char["spell_slots_current"] = current
        chars[key] = char
        _save_all(chars)
        return f"✨ {key}'s spell slots restored ({restored}).", True

    # ── character_add_item ──
    elif function_name == "character_add_item":
        name  = arguments.get("name", "")
        item  = arguments.get("item", "").strip()
        qty   = int(arguments.get("quantity", 1))
        notes = arguments.get("notes", "")
        key, char = _find(name, chars)
        if not char:
            return f"No character named '{name}'.", False
        if not item:
            return "Item name is required.", False

        inventory = char.get("inventory", [])
        # Check if item already exists
        for entry in inventory:
            if entry["item"].lower() == item.lower():
                entry["quantity"] += qty
                char["inventory"] = inventory
                chars[key] = char
                _save_all(chars)
                return f"🎒 {key}: {item} quantity updated to {entry['quantity']}.", True

        inventory.append({"item": item, "quantity": qty, "notes": notes})
        char["inventory"] = inventory
        chars[key] = char
        _save_all(chars)
        return f"🎒 {key} receives: {item} x{qty}" + (f" ({notes})" if notes else "") + ".", True

    # ── character_remove_item ──
    elif function_name == "character_remove_item":
        name = arguments.get("name", "")
        item = arguments.get("item", "").strip()
        qty  = int(arguments.get("quantity", 1))
        key, char = _find(name, chars)
        if not char:
            return f"No character named '{name}'.", False

        inventory = char.get("inventory", [])
        for i, entry in enumerate(inventory):
            if entry["item"].lower() == item.lower():
                entry["quantity"] -= qty
                if entry["quantity"] <= 0:
                    inventory.pop(i)
                    result = f"🎒 {key}: {item} removed from inventory."
                else:
                    result = f"🎒 {key}: {item} quantity reduced to {entry['quantity']}."
                char["inventory"] = inventory
                chars[key] = char
                _save_all(chars)
                return result, True

        return f"'{item}' not found in {key}'s inventory.", False

    # ── character_set_condition ──
    elif function_name == "character_set_condition":
        name      = arguments.get("name", "")
        condition = arguments.get("condition", "").lower().strip()
        active    = arguments.get("active", True)
        # LLMs often pass booleans as strings — "False" is truthy, so normalise
        if isinstance(active, str):
            active = active.strip().lower() not in ("false", "0", "no", "off", "remove")
        key, char = _find(name, chars)
        if not char:
            return f"No character named '{name}'.", False

        conditions = char.get("conditions", [])
        if active:
            if condition not in conditions:
                conditions.append(condition)
            msg = f"⚠️ {key} is now **{condition}**."
        else:
            conditions = [c for c in conditions if c != condition]
            msg = f"✅ {key} is no longer {condition}."

        char["conditions"] = conditions
        chars[key] = char
        _save_all(chars)
        # Sync conditions to combat tracker too
        try:
            from core.plugin_loader import plugin_loader
            enc_state = plugin_loader.get_plugin_state("dnd-encounters")
            combat = enc_state.get("combat")
            if combat:
                for c in combat.get("combatants", []):
                    if c["name"].lower() == key.lower():
                        c["conditions"] = conditions
                        enc_state.save("combat", combat)
                        break
        except Exception:
            pass
        return msg, True

    # ── character_set_user_controlled ──
    elif function_name == "character_set_user_controlled":
        names = arguments.get("names", [])

        if not names:
            return "Error: provide at least one character name.", False

        # Validate all characters exist
        unknown = []
        for name in names:
            key, char = _find(name, chars)
            if not char:
                unknown.append(name)

        if unknown:
            return f"Unknown characters: {', '.join(unknown)}. Use character_list to see available characters.", False

        # Update user_controlled flag on all characters
        for name in names:
            key, char = _find(name, chars)
            char["user_controlled"] = True
            chars[key] = char

        # Clear flag on characters not in the list
        for key, char in chars.items():
            if key not in [n.lower() for n in names]:
                if char.get("user_controlled", False):
                    char["user_controlled"] = False
                    chars[key] = char

        _save_all(chars)

        user_chars = ", ".join(f"**{n}**" for n in names)
        return f"✅ User-controlled characters: {user_chars}. Only these characters should act based on user input. Other party members are DM-controlled.", True

    return f"Unknown function: {function_name}", False
