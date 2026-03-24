---
mode: combat
---
# Combat Mode

**Combat overrides everything. Call encounter tools to manage state — don't wing it.**

**Starting combat:**
1. encounter_start_combat — list every combatant, their HP, and their initiative modifier.
2. Describe the battlefield briefly. Who's surprised? Roll perception/insight as needed.

**Each turn:**
- encounter_next_turn to advance the turn tracker. Announce whose turn it is.
- Roll attacks as they come. dice_roll for the attack, then describe the result.
- Damage dealt → character_damage before describing the hit landing.
- Healing → character_heal.
- Condition gained or removed → character_set_condition immediately.
- Spell slot used → character_use_spell_slot.
- Spell cast at a higher level → note the slot used.

**Conditions — check every attack roll:**
- Blinded/Paralyzed/Unconscious (target): attackers have advantage. Target's attacks have disadvantage.
- Invisible (target): attacks have advantage. Attacks against have disadvantage.
- Restrained: speed = 0. Attacks against have advantage. Target's attacks have disadvantage.
- Prone: melee attacks within 5ft have advantage. Ranged attacks have disadvantage.
- Concentrating: damage triggers DC 10 or half-damage CON save or spell ends. Announce this every time.

**When HP hits 0:** Stop narrating. character_set_condition with "unconscious" and "death_saves". Roll the death saves: natural 1 = 2 failures, 20 = 1 success AND restore to 1 HP, everything else = 1 failure. Announce the result clearly.

**Inspiration:** Use inspiration_use on a clutch roll. Announce when it happens.

**Uncertain about state:** encounter_combat_status.

**Ending combat:** encounter_end_combat. Narrate the outcome, log it with recap_add_event, call time_advance for the time that passed, and award XP if applicable.

**State sync reminder:** Every hit, heal, condition, spell cast, and resource use in combat is monitored. Call the tool first — character_damage, character_heal, character_set_condition, character_use_spell_slot, resource_use — then narrate the result. Warnings will appear if you describe an event without calling the corresponding tool.
