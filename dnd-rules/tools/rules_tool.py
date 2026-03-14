"""
dnd-rules — D&D 5e Rules Reference

Prevents small models from hallucinating rule details mid-session.
No state — pure lookup. Call this before adjudicating any rule you
are not 100% certain of.

Tools:
  condition_lookup — Exact mechanics of any condition
  action_lookup    — What actions, bonus actions, and reactions can do
  rules_lookup     — Common mechanics (grapple, shove, cover, etc.)
"""

ENABLED = True
EMOJI = '📖'
AVAILABLE_FUNCTIONS = ['condition_lookup', 'action_lookup', 'rules_lookup']

# ── CONDITIONS ────────────────────────────────────────────────────────────────
CONDITIONS = {
    "blinded": {
        "effects": [
            "Can't see. Automatically fails any ability check requiring sight.",
            "Attack rolls against blinded creature have ADVANTAGE.",
            "Blinded creature's attack rolls have DISADVANTAGE.",
        ],
        "ends": "Varies by source (spell ends, magic removed, etc.)"
    },
    "charmed": {
        "effects": [
            "Can't attack the charmer or target them with harmful abilities/spells.",
            "The charmer has ADVANTAGE on social checks against the charmed creature.",
        ],
        "ends": "Varies by source. Creature that charmed you becoming hostile can end it."
    },
    "deafened": {
        "effects": [
            "Can't hear. Automatically fails any ability check requiring hearing.",
        ],
        "ends": "Varies by source."
    },
    "exhaustion": {
        "effects": [
            "Level 1: Disadvantage on ability checks",
            "Level 2: Speed halved",
            "Level 3: Disadvantage on attack rolls AND saving throws",
            "Level 4: Hit point maximum halved",
            "Level 5: Speed reduced to 0",
            "Level 6: Death",
        ],
        "ends": "Long rest removes 1 level. Must also have food and water."
    },
    "frightened": {
        "effects": [
            "DISADVANTAGE on ability checks and attack rolls while source of fear is in line of sight.",
            "Can't willingly move CLOSER to the source of fear.",
        ],
        "ends": "Varies by source. Line of sight to source is key — if you can't see it, some effects end."
    },
    "grappled": {
        "effects": [
            "Speed becomes 0. Speed bonuses have no effect.",
        ],
        "ends": "Grappler is incapacitated. Target escapes with Athletics or Acrobatics check vs grappler's Athletics."
    },
    "incapacitated": {
        "effects": [
            "Can't take actions or reactions.",
        ],
        "ends": "Varies by source."
    },
    "invisible": {
        "effects": [
            "Impossible to see without special sense. Treated as heavily obscured for hiding.",
            "Invisible creature's attack rolls have ADVANTAGE.",
            "Attack rolls against invisible creature have DISADVANTAGE.",
            "Invisible creature can still be heard, smelled, or detected by other means.",
        ],
        "ends": "Varies by source."
    },
    "paralyzed": {
        "effects": [
            "Incapacitated (can't act or react).",
            "Can't move or speak.",
            "Automatically fails STR and DEX saving throws.",
            "Attack rolls against paralyzed creature have ADVANTAGE.",
            "Any attack that hits from within 5 ft is a CRITICAL HIT.",
        ],
        "ends": "Varies by source."
    },
    "petrified": {
        "effects": [
            "Transformed into stone. Incapacitated, can't move or speak.",
            "Unaware of surroundings.",
            "Attack rolls against petrified creature have ADVANTAGE.",
            "Automatically fails STR and DEX saving throws.",
            "Resistance to all damage.",
            "Immune to poison and disease (existing ones suspended, not cured).",
        ],
        "ends": "Greater Restoration or similar magic."
    },
    "poisoned": {
        "effects": [
            "DISADVANTAGE on attack rolls.",
            "DISADVANTAGE on ability checks.",
        ],
        "ends": "Varies by source. Some last hours, some until removed."
    },
    "prone": {
        "effects": [
            "Only movement option is to crawl (costs double movement) or stand up (costs half speed).",
            "DISADVANTAGE on attack rolls.",
            "Attack rolls against prone creature: ADVANTAGE if attacker is within 5 ft, DISADVANTAGE if further.",
        ],
        "ends": "Use half your speed to stand up."
    },
    "restrained": {
        "effects": [
            "Speed becomes 0. Speed bonuses have no effect.",
            "Attack rolls against restrained creature have ADVANTAGE.",
            "Restrained creature's attack rolls have DISADVANTAGE.",
            "DISADVANTAGE on DEX saving throws.",
        ],
        "ends": "Varies by source."
    },
    "stunned": {
        "effects": [
            "Incapacitated (can't act or react).",
            "Can't move.",
            "Can speak only falteringly.",
            "Automatically fails STR and DEX saving throws.",
            "Attack rolls against stunned creature have ADVANTAGE.",
        ],
        "ends": "Usually end of the turn of whoever stunned you, or start of your next turn."
    },
    "unconscious": {
        "effects": [
            "Incapacitated (can't act or react).",
            "Can't move or speak.",
            "Unaware of surroundings. Drops held items. Falls prone.",
            "Automatically fails STR and DEX saving throws.",
            "Attack rolls against unconscious creature have ADVANTAGE.",
            "Any attack that hits from within 5 ft is a CRITICAL HIT.",
        ],
        "ends": "Regain consciousness (healing, stabilization, etc.)"
    },
    "concentration": {
        "effects": [
            "Can only concentrate on ONE spell at a time — new concentration spell ends the old one.",
            "Taking damage: CON saving throw DC = max(10, half damage taken). Fail = lose concentration.",
            "Incapacitated or killed = lose concentration.",
            "Distracted by environment (DM's discretion): DC 10 CON save.",
            "War Caster feat: ADVANTAGE on concentration saves.",
            "Resilient (CON) feat: proficiency on CON saves.",
        ],
        "ends": "Take an action to end it. Lose concentration. Spell duration ends."
    },
    "death saves": {
        "effects": [
            "At 0 HP: make CON saving throw at start of each turn.",
            "DC 10. Roll in secret.",
            "3 successes = STABLE (unconscious at 0 HP, no more saves).",
            "3 failures = DEAD.",
            "Natural 1 = 2 failures.",
            "Natural 20 = regain 1 HP and consciousness.",
            "Taking any damage at 0 HP = 1 failure (2 if critical hit).",
            "Damage from 5 ft away that hits counts as critical at 0 HP.",
            "Healing or being stabilized (DC 10 Medicine check) stops saves.",
        ],
        "ends": "Stable (3 successes), dead (3 failures), healed, or stabilized."
    },
}

# ── ACTIONS ───────────────────────────────────────────────────────────────────
ACTIONS = {
    "attack": {
        "type": "action",
        "description": "Make one melee or ranged attack. Extra Attack feature allows additional attacks.",
        "notes": "Two-weapon fighting: if you attack with a light weapon in main hand, BONUS ACTION attack with light weapon in off-hand (no ability modifier to damage unless negative).",
    },
    "cast a spell": {
        "type": "varies",
        "description": "Cast time varies by spell: action, bonus action, reaction, or longer. Check the spell.",
        "notes": "Bonus action spell rule: if you cast a spell with a bonus action, the ONLY other spell you can cast that turn is a cantrip with a casting time of 1 action.",
    },
    "dash": {
        "type": "action",
        "description": "Extra movement equal to your speed this turn.",
        "notes": "Cunning Action (Rogue) and Step of the Wind (Monk) can Dash as bonus action.",
    },
    "disengage": {
        "type": "action",
        "description": "Movement doesn't provoke opportunity attacks for the rest of the turn.",
        "notes": "Cunning Action (Rogue) and Step of the Wind (Monk) can Disengage as bonus action.",
    },
    "dodge": {
        "type": "action",
        "description": "Until start of next turn: attack rolls against you have DISADVANTAGE (if you can see attacker), and you have ADVANTAGE on DEX saves.",
        "notes": "Patient Defense (Monk) can Dodge as bonus action. Incapacitated or speed 0 = benefit lost.",
    },
    "help": {
        "type": "action",
        "description": "Give an ally ADVANTAGE on their next ability check or attack roll vs a creature within 5 ft of you.",
        "notes": "Must be adjacent to the target of the task or the creature being attacked.",
    },
    "hide": {
        "type": "action",
        "description": "Make a DEX (Stealth) check. On success you are hidden until you give away your position.",
        "notes": "Must be obscured. Can't hide if clearly visible. Cunning Action (Rogue) can Hide as bonus action.",
    },
    "ready": {
        "type": "action",
        "description": "Prepare an action to trigger when a condition is met (a REACTION).",
        "notes": "Choose the action and the trigger. Uses your REACTION when trigger occurs. If it's a spell, maintain concentration until triggered (or end of next turn). If trigger doesn't occur, nothing happens.",
    },
    "search": {
        "type": "action",
        "description": "Make a WIS (Perception) or INT (Investigation) check to find something hidden.",
        "notes": "DM decides which skill applies and whether a check is needed.",
    },
    "use an object": {
        "type": "action",
        "description": "Interact with a second object beyond the free object interaction per turn.",
        "notes": "One free object interaction per turn (draw weapon, open door). Using a magic item or drinking a potion typically requires this action.",
    },
    "opportunity attack": {
        "type": "reaction",
        "description": "When a creature you can see moves OUT of your reach, you can make one melee attack against it.",
        "notes": "Only triggers on VOLUNTARY movement. Teleportation, forced movement, and Disengage do NOT trigger OAs. Only once per round (reaction).",
    },
    "grapple": {
        "type": "special attack",
        "description": "Use the Attack action to attempt a grapple. Make STR (Athletics) check vs target's STR (Athletics) or DEX (Acrobatics) — target's choice.",
        "notes": "On success: target is GRAPPLED. You must have a free hand. Target must be within your reach and no more than one size larger than you.",
    },
    "shove": {
        "type": "special attack",
        "description": "Use the Attack action to shove a creature PRONE or push it 5 ft away. Make STR (Athletics) vs target's STR (Athletics) or DEX (Acrobatics).",
        "notes": "Target must be within 5 ft and no more than one size larger than you. Can be done instead of one of your attacks if you have Extra Attack.",
    },
    "two-weapon fighting": {
        "type": "bonus action",
        "description": "After attacking with a light melee weapon in your main hand, attack with a different light melee weapon in your off-hand as a BONUS ACTION.",
        "notes": "You don't add your ability modifier to the off-hand attack's DAMAGE (unless it's negative). Both weapons must have the light property unless you have the Dual Wielder feat.",
    },
}

# ── RULES ─────────────────────────────────────────────────────────────────────
RULES = {
    "cover": {
        "summary": "Obstacles between attacker and target.",
        "rules": [
            "Half cover (+2 AC, DEX saves): low walls, other creatures, foliage.",
            "Three-quarters cover (+5 AC, DEX saves): arrow slit, thick tree trunk.",
            "Full cover: can't be targeted directly. Can still be affected by AoE.",
            "A creature provides half cover to targets behind it.",
        ]
    },
    "flanking": {
        "summary": "Optional rule (not default 5e). Two enemies on opposite sides of a creature.",
        "rules": [
            "If using flanking: attackers have ADVANTAGE when on directly opposite sides of a creature.",
            "This is an OPTIONAL rule from the DMG. Many tables don't use it.",
            "Default 5e has no flanking mechanics — confirm with your table.",
        ]
    },
    "advantage disadvantage": {
        "summary": "Roll 2d20, take higher (advantage) or lower (disadvantage).",
        "rules": [
            "Multiple sources of advantage don't stack — still roll 2d20.",
            "One source of disadvantage cancels ALL sources of advantage.",
            "If you have both advantage AND disadvantage from any source, they cancel out — roll normally.",
            "Certain features let you reroll one die — this is different from advantage.",
        ]
    },
    "critical hit": {
        "summary": "Natural 20 on an attack roll.",
        "rules": [
            "Roll ALL damage dice TWICE and add modifiers once.",
            "Example: 1d8+3 on a hit → critical = 2d8+3.",
            "Extra damage dice from features (Sneak Attack, Divine Smite, Brutal Critical) are also doubled.",
            "Flat bonuses (+3, etc.) are NOT doubled.",
            "Paralyzed or unconscious creatures are auto-crit when hit from within 5 ft.",
        ]
    },
    "surprise": {
        "summary": "Combat starts with some creatures unaware.",
        "rules": [
            "The DM determines if anyone is surprised at the start of combat.",
            "A surprised creature can't move or take actions on its FIRST turn of combat.",
            "A surprised creature can't take reactions until its first turn ends.",
            "After first turn, surprised condition ends — creature is no longer surprised.",
            "Members of a group can be surprised even if others in the group aren't.",
        ]
    },
    "spells concentration": {
        "summary": "Some spells require sustained focus.",
        "rules": [
            "You can only concentrate on ONE spell at a time.",
            "New concentration spell = old one ends immediately.",
            "Taking damage: CON save DC = max(10, half damage taken). Fail = concentration lost.",
            "Being incapacitated or killed ends concentration automatically.",
            "War Caster feat: advantage on concentration saves.",
            "Resilient (Constitution): proficiency on all CON saves.",
        ]
    },
    "bonus action spell": {
        "summary": "The bonus-action spellcasting restriction.",
        "rules": [
            "If you cast ANY spell with a bonus action casting time, the only OTHER spell you can cast that turn is a cantrip with a 1-action casting time.",
            "This means: Misty Step (bonus action) + Toll the Dead (cantrip, action) = OK.",
            "Misty Step (bonus action) + Fireball (action, 3rd level) = NOT ALLOWED.",
            "This restriction applies even if the bonus action spell is from an item or feature.",
        ]
    },
    "short rest": {
        "summary": "1 hour of rest. No strenuous activity.",
        "rules": [
            "Can spend Hit Dice: roll die + CON modifier to regain HP.",
            "Regains: Warlock Pact Magic slots, Ki points, Second Wind, Action Surge, Channel Divinity.",
            "Bard's Song of Rest: party members spending HD regain an extra die of HP.",
        ]
    },
    "long rest": {
        "summary": "8 hours. At least 6 hours sleep.",
        "rules": [
            "Regain all lost HP.",
            "Regain all expended Hit Dice up to half your total (minimum 1).",
            "Regain all spell slots.",
            "Regain all long-rest resources (Rage uses, etc.).",
            "Can't benefit from more than one long rest per 24 hours.",
            "Must have at least 1 HP to benefit.",
        ]
    },
    "spellcasting saving throw": {
        "summary": "Spell save DC.",
        "rules": [
            "Spell Save DC = 8 + proficiency bonus + spellcasting ability modifier.",
            "Spellcasting ability: INT (Wizard/Artificer), WIS (Cleric/Druid/Ranger), CHA (Bard/Paladin/Sorcerer/Warlock).",
            "Spell Attack Bonus = proficiency bonus + spellcasting ability modifier.",
        ]
    },
    "multiclassing": {
        "summary": "Key multiclassing rules.",
        "rules": [
            "Must meet minimum ability score for new class (e.g., STR/DEX 13 for Fighter).",
            "Hit dice, saving throw proficiencies, armor/weapon proficiencies: only from first level in a class.",
            "Spell slots: combine spell levels for table in PHB. Use the combined table for slots.",
            "Spells known: use each class's own known spells — they DON'T combine.",
            "Proficiency bonus: based on TOTAL character level, not class level.",
        ]
    },
    "falling": {
        "summary": "Falling damage.",
        "rules": [
            "Take 1d6 bludgeoning damage per 10 ft fallen, max 20d6 (200 ft).",
            "Land prone unless you avoid damage somehow.",
            "Falling into water or a soft surface: DM may reduce or eliminate damage.",
            "Feather Fall spell (reaction): fall at 60 ft/round, no damage.",
        ]
    },
    "difficult terrain": {
        "summary": "Costs double movement.",
        "rules": [
            "Every 1 ft of movement in difficult terrain costs 2 ft of speed.",
            "Examples: deep snow, rubble, shallow water, tangled undergrowth, steep stairs.",
            "Two sources of difficult terrain don't stack.",
            "Spider Climb, flying, and similar movement can ignore difficult terrain.",
        ]
    },
    "attunement": {
        "summary": "Attuning to magic items.",
        "rules": [
            "Maximum 3 attuned items at a time (unless a feature says otherwise).",
            "Short rest to attune to an item (must be in physical contact).",
            "Can break attunement as a bonus action, or when you die.",
            "Some items have class/alignment/ability score requirements.",
        ]
    },
    "sneak attack": {
        "summary": "Rogue damage bonus.",
        "rules": [
            "Once per TURN (not per round — you can use it on OAs and Readied actions).",
            "Requires: Finesse or ranged weapon.",
            "Requires EITHER: Advantage on the attack, OR an ally adjacent to target who isn't incapacitated.",
            "Can't use if you have DISADVANTAGE on the attack roll.",
        ]
    },
    "ritual spells": {
        "summary": "Casting spells as rituals.",
        "rules": [
            "Ritual = 10 extra minutes of casting time. No spell slot expended.",
            "Only spells with the 'ritual' tag can be cast this way.",
            "Wizard: can cast any ritual spell from their spellbook without having prepared it.",
            "Cleric/Druid/Artificer: must have the spell prepared to ritual cast.",
            "Bard (Book of Ancient Secrets)/Warlock (Pact of the Tome invocation): can cast known rituals.",
        ]
    },
}

TOOLS = [
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "condition_lookup",
            "description": (
                "Look up the exact mechanical effects of a condition. "
                "Call this BEFORE adjudicating any condition — poisoned, stunned, grappled, etc. "
                "Do not rely on memory for condition mechanics. "
                "Available: blinded, charmed, deafened, exhaustion, frightened, grappled, "
                "incapacitated, invisible, paralyzed, petrified, poisoned, prone, restrained, "
                "stunned, unconscious, concentration, death saves"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "condition": {"type": "string", "description": "Condition name"}
                },
                "required": ["condition"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "action_lookup",
            "description": (
                "Look up what an action, bonus action, or reaction does in combat. "
                "Call this when a player asks about an action they can take. "
                "Available: attack, cast a spell, dash, disengage, dodge, help, hide, ready, "
                "search, use an object, opportunity attack, grapple, shove, two-weapon fighting"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "description": "Action name"}
                },
                "required": ["action"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "rules_lookup",
            "description": (
                "Look up a specific D&D 5e rule or mechanic. "
                "Call this before making any ruling you're uncertain about. "
                "Available: cover, flanking, advantage disadvantage, critical hit, surprise, "
                "spells concentration, bonus action spell, short rest, long rest, "
                "spellcasting saving throw, multiclassing, falling, difficult terrain, "
                "attunement, sneak attack, ritual spells"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "rule": {"type": "string", "description": "Rule or mechanic name"}
                },
                "required": ["rule"]
            }
        }
    }
]


def _fuzzy_match(query, options):
    q = query.lower().strip()
    if q in options:
        return q
    # partial match
    for key in options:
        if q in key or key in q:
            return key
    # word match
    q_words = set(q.split())
    for key in options:
        k_words = set(key.split())
        if q_words & k_words:
            return key
    return None


def _format_entry(name, entry, source_type):
    lines = [f"{'='*40}", f"{name.upper()}", f"{'='*40}"]

    if source_type == "condition":
        effects = entry.get("effects", [])
        ends    = entry.get("ends", "")
        if effects:
            lines.append("\nEFFECTS:")
            for e in effects:
                lines.append(f"  • {e}")
        if ends:
            lines.append(f"\nENDS WHEN: {ends}")

    elif source_type == "action":
        lines.append(f"Type: {entry.get('type', '').upper()}")
        lines.append(f"\n{entry.get('description', '')}")
        if entry.get("notes"):
            lines.append(f"\nNotes: {entry['notes']}")

    elif source_type == "rule":
        summary = entry.get("summary", "")
        rules   = entry.get("rules", [])
        if summary:
            lines.append(f"\n{summary}")
        if rules:
            lines.append("")
            for r in rules:
                lines.append(f"  • {r}")

    return "\n".join(lines)


def execute(function_name, arguments, config):

    if function_name == "condition_lookup":
        query = arguments.get("condition", "").strip()
        key   = _fuzzy_match(query, CONDITIONS)
        if not key:
            available = ", ".join(sorted(CONDITIONS.keys()))
            return f"Condition '{query}' not found.\nAvailable: {available}", False
        return _format_entry(key, CONDITIONS[key], "condition"), True

    elif function_name == "action_lookup":
        query = arguments.get("action", "").strip()
        key   = _fuzzy_match(query, ACTIONS)
        if not key:
            available = ", ".join(sorted(ACTIONS.keys()))
            return f"Action '{query}' not found.\nAvailable: {available}", False
        return _format_entry(key, ACTIONS[key], "action"), True

    elif function_name == "rules_lookup":
        query = arguments.get("rule", "").strip()
        key   = _fuzzy_match(query, RULES)
        if not key:
            available = ", ".join(sorted(RULES.keys()))
            return f"Rule '{query}' not found.\nAvailable: {available}", False
        return _format_entry(key, RULES[key], "rule"), True

    return f"Unknown function: {function_name}", False
