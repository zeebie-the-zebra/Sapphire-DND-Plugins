---
mode: social
---
# Social Mode

**An NPC interaction is in focus. Track every meaningful exchange.**

**First contact:** Call npc_get to pull up the NPC's details. If they don't exist yet → table_generate_npc or npc_generate. Then relation_set to record their starting attitude toward the party.

**Social rolls:**
- Persuasion, Deception, Insight → dice_roll. Apply the NPC's attitude modifier: Friendly = +2 to +5, Neutral = +0, Hostile = -2 to -5.
- The charmer has advantage on social checks against a charmed creature.
- Frightened creature: can't move closer to the source of fear — enforce this in dialogue.

**Attitude shifts:** A successful persuasion, a threat made, a gift given, or a lie detected → relation_update. The NPC's attitude should feel responsive to how the party behaves. Call it out: "She seems more receptive now."

**Promises and threats:** The party offers a deal, makes a threat, or reveals information → thread_add immediately. This is the most common thing that gets forgotten in social encounters.

**Discoveries in conversation:** A clue, a lie, a motive → clue_add. A broader conspiracy → mystery_create.

**Inspiration:** inspiration_award for exceptional roleplay. Not just good dice rolls — good character choices, funny moments, meaningful decisions.

**NPCs the party wants to track:** npc_save after a meaningful interaction so their details persist. Update with npc_update when the relationship changes.
