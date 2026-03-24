---
mode: exploration
---
# Exploration Mode

**The party is navigating a dungeon, wilderness, or other location.**

**Entering a new area:** scene_move with the location name, who's present, the time, and the mood. If it's a dungeon room the party hasn't visited before → table_generate_dungeon_room to populate it.

**Random encounters:** Call encounter_generate if the party triggers one (stealth failure, loud noise, random check, etc.). If it turns into a fight → encounter_start_combat.

**Overland travel:**
- Set travel pace and terrain at the start with travel_advance.
- Each day or significant leg → travel_advance to update progress, rations, and exhaustion.
- weather_get and weather_advance to track conditions.
- time_advance explicitly — don't let hours disappear.

**Hazards and consequences:** A trap is triggered, a wall collapses, someone falls → thread_add with urgency "high". Log it with recap_add_event.

**Discoveries:** A clue → clue_add. A secret door or hidden room → fact_set (category "secrets"). An important NPC in the dungeon → npc_save.

**Exhaustion:** Keep track. fast pace = risk of exhaustion at level 3+. Don't let it sneak up on the party without warning.

**Random tables:** Use them freely — table_generate_tavern, table_generate_npc, table_generate_road_encounter — to keep the world alive between set-piece moments.
