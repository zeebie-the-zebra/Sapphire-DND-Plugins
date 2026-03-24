# dnd-scaffold — Tool Reference

All tools are called by name with keyword arguments. Every tool returns `(result_string, success_bool)`.

---

## Characters

**character_create** — Create a new D&D player character sheet.
- `name`, `race`, `class_name`, `hp_max`, `ac`, `level`, `str/dex/con/int/wis/cha`, `background`, `alignment`, `backstory`, `spell_slots`, `user_controlled`

**character_get** — Retrieve a character's full sheet.
- `name`

**character_update** — Update any fields on a character sheet.
- `name`, `fields` (dict of key-value pairs)

**character_list** — List all characters in the current campaign.

**character_delete** — Permanently delete a character sheet.
- `name`

**character_damage** — Apply damage. Handles temp HP first, then real HP. Tracks death saves at 0 HP.
- `name`, `amount`, `type` (optional)

**character_heal** — Restore HP. Cap at max unless `temp=true`.
- `name`, `amount`, `temp` (bool), `is_rest` ('short' or 'long')

**character_use_spell_slot** — Expend a spell slot.
- `name`, `level`

**character_restore_spell_slots** — Restore spell slots after a rest.
- `name`, `levels` (optional list of specific levels; omit for all)

**character_add_item** — Add an item to a character's inventory. MANDATORY after any loot drop, purchase, pickpocketing, NPC gift, or treasure find. Call immediately — do not wait.
- `name`, `item`, `quantity`, `notes`

**character_remove_item** — Remove or consume an item. Call immediately when lost, stolen, sold, consumed, given away, or destroyed.
- `name`, `item`, `quantity`

**character_set_condition** — Add or remove a condition (poisoned, frightened, unconscious, etc.).
- `name`, `condition`, `active` (bool)

**character_set_user_controlled** — Mark which character(s) the user is playing.
- `names` (list)

---

## Combat

**encounter_generate** — Generate a random encounter appropriate for party level and environment.
- `party_levels`, `difficulty` ('easy'/'medium'/'hard'/'deadly'), `environment`, `monster_type`

**encounter_start_combat** — Begin combat. Roll initiative for all combatants. Auto-populates from the campaign roster if no combatants are provided.
- `combatants` (optional list; each combatant may have `Name`, `hp`, `xp`, `is_player`, `dex_mod`)

**encounter_next_turn** — Advance to the next turn. Apply HP updates to keep combat state current.
- `hp_updates` (optional list of `{name, hp}`)

**encounter_combat_status** — Show current initiative order, HP, conditions, and round number.

**encounter_end_combat** — End combat. Awards XP from defeated enemies and clears combat state.

**encounter_xp_budget** — Calculate XP thresholds for a party vs. a given monster XP total.
- `party_levels`, `monster_xp`

**monster_lookup** — Look up a monster's full stats by name.
- `name`

---

## Spells

**spell_lookup** — Look up a D&D 5e spell by name. Returns school, level, casting time, range, components, duration, and full description.
- `name`

**spell_list** — List all D&D 5e spells, optionally filtered.
- `level` (0-9 or 'cantrip'), `school`

---

## Dice

**dice_roll** — Roll dice in AdndB notation (e.g. `2d6+3`, `4d6kh3`, `1d20 Advantage`). Returns individual die results and total.
- `expression`, `label` (optional)

**dice_history** — Show the last 20 dice rolls with timestamps.

---

## Resources

**resource_setup** — Configure tracked class resources for a character (rages, ki, sorcery points, lay on hands, etc.). Call on character creation and after level-ups.
- `name`, `class_name`, `level`

**resource_use** — Mark a resource use as spent.
- `name`, `resource`, `amount`

**resource_restore** — Restore resources after a rest. `rest_type='long'` restores everything; `'short'` restores short-rest resources only.
- `name` (optional — omit to restore for whole party), `rest_type`

**resource_get** — Get current remaining uses for a specific character's resources.
- `name`

**resource_list** — List all tracked resources for all party members showing current/max.

**resource_set_max** — Manually add or update a resource (for subclass features, magic items, etc.).
- `name`, `resource`, `max`, `recharge` ('short'/'long'/'dawn'/'passive'/'reaction'), `note`

---

## Rest

**rest_long** — Take a long rest (6+ hours). Restores HP to max, recovers half hit dice, resets all resources. Automatically calls `resource_restore` for each character.
- `character_names` (comma-separated), `day`, `recover_hp`

**rest_short** — Take a short rest (1 hour). Call `rest_spend_hit_dice` to recover HP. Automatically calls `resource_restore` for short-rest resources.
- `character_names`, `resources`

**rest_spend_hit_dice** — Spend hit dice during a short rest to recover HP. Simulates rolling.
- `character_name`, `dice_count`, `con_modifier`, `current_hd`, `max_hd`

**rest_has_long_rested** — Check whether a character has already long-rested today.
- `character_name`

**rest_reset_day** — Reset daily rest flags at the start of a new in-game day.

**rest_history** — Show recent rest history.
- `count`

**rest_status** — Show rest status for all characters — long rest taken today, short rests, HD expended.
- `character_name` (optional)

---

## XP & Level-Up

**xp_add** — Add XP to a character. Automatically checks for level-up and warns if threshold reached.
- `name`, `amount`

**xp_get** — Get current XP and level for a character.
- `name`

**xp_check_all** — Check all characters for level-up eligibility. Shows XP to next level.

**levelup_guide** — Show what a character gains at a new level (hit dice, features, spell slots, ability score improvements).
- `name`, `target_level`

**levelup_apply** — Apply a level-up to a character. Increments level, updates HP max, records new features.
- `name`, `target_level`, `features` (optional list)

---

## Inspiration

**inspiration_award** — Award inspiration to a character.
- `name`, `reason` (optional)

**inspiration_use** — Mark inspiration as used (grants advantage on one roll).

**inspiration_grant_if_none** — Grant inspiration only if the character doesn't already have it.
- `name`

**inspiration_reset** — Reset inspiration after a long rest (fresh inspiration).

**inspiration_list** — List which characters currently have inspiration.

**inspiration_history** — Show recent inspiration events.

---

## Campaign

**campaign_create** — Create a new campaign.
- `name`, `campaign_id`, `chapter`, `location`

**campaign_list** — List all campaigns and show which is active.

**campaign_switch** — Switch to a different campaign by ID. Isolates all character, combat, and scene data.
- `campaign_id`

**campaign_delete** — Delete a campaign and all its state.
- `campaign_id`, `confirm` (must be true)

**campaign_set** — Set campaign fields.
- `name`, `chapter`, `location`, `time`, `last_session`, `world_notes`, `factions`

**campaign_get** — Get current campaign details.

**campaign_quest** — Add, update, or remove a quest in the current campaign.
- `action` ('add'/'update'/'complete'/'delete'), `quest` (dict), `quest_id`

**campaign_set_mode** — Set DM mode.
- `mode` ('in_character' or 'voice')

**campaign_debug** — Dump raw campaign state for debugging.

**campaign_clean_migration** — Migrate legacy campaign data to campaign-scoped keys.

---

## Scene

**scene_move** — Move to a new scene/location. Loads saved layout if visited before. Validates character and NPC names in the `present` list.
- `name`, `present` (optional list), `time`, `mood`

**scene_set** — Save the permanent layout of the current location. Lock in description, lighting, notes. Loads automatically on future visits.
- `description`, `lighting_default`, `notes`

**scene_get** — Get current scene details — location, mood, lighting, who is present.

**scene_add_person** — Add a character or NPC to the current scene. Validates against roster.
- `name`, `note` (optional)

**scene_remove_person** — Remove a person from the current scene.
- `name`, `reason` (optional)

**scene_update** — Update per-visit details (mood, lighting, time, visit_notes). Does not change the saved room.
- `field`, `value`

**scene_update_location** — PERMANENTLY change a saved location (wall destroyed, secret door found, etc.). Affects all future visits.
- `field`, `value`, `change_reason`

**scene_list_locations** — List all known locations with visit counts and descriptions.

**scene_edit_location** — Edit a saved location's details by name without being present.
- `name`, `field`, `value`

**scene_delete_location** — Delete a location from the library.
- `name`, `confirm` (must be true)

---

## Travel

**travel_start** — Begin an overland travel sequence.
- `destination`, `distance`, `pace` ('slow'/'normal'/'fast'), `environment`, `characters`

**travel_advance** — Advance travel by one segment. Decrements distance, tracks time, handles exhaustion.
- `segment_type` ('march'/'rest'/'forage'/'explore'), `distance`

**travel_add_exhaustion** — Add exhaustion levels to characters (1-6 scale).
- `character_names`, `levels`

**travel_remove_exhaustion** — Remove one level of exhaustion from a character.
- `character_name`

**travel_get** — Get current travel state — destination, distance remaining, pace, party status.

**travel_cancel** — Cancel the current travel session.

**travel_forage** — Attempt to forage for food and water during travel.

---

## Weather

**weather_set** — Set weather conditions for a location or globally.
- `condition`, `description`, `mechanics`, `location`

**weather_generate** — Generate weather appropriate for biome, season, and time of day.
- `biome`, `season`, `time_of_day`

**weather_get** — Get current weather for a location or default.

**weather_advance** — Advance weather by one time period (dawn/day/dusk/night). Includes shift chance.
- `period`

**weather_forecast** — Generate a multi-day weather forecast for a location.
- `days`, `location`

**weather_list_locations** — List all tracked weather locations.

**weather_delete_location** — Remove a location's weather record.
- `location`

**weather_auto_advance** — Automatically advance weather based on game clock passage.

---

## NPCs

**npc_generate** — Generate a random NPC with name, race, occupation, personality, physical description, and secret.
- `race`, `gender`, `occupation`, `save` (bool)

**npc_save** — Save or update a custom NPC to the roster.
- `name`, `race`, `gender`, `occupation`, `appearance`, `personality`, `attitude`, `notes`

**npc_get** — Get full details for a saved NPC.
- `name`

**npc_list** — List all saved NPCs with attitude and occupation.

**npc_update** — Update an NPC's attitude or notes.
- `name`, `attitude`, `notes`

**npc_delete** — Remove an NPC from the roster.
- `name`

---

## Shops

**shop_create** — Create a shop with a name, type, description, and starting inventory.
- `name`, `type` ('blacksmith'/'apothecary'/'magic'/'fence'), `description`, `inventory` (optional dict)

**shop_get** — Get full shop details including inventory and pricing.
- `name`

**shop_sell** — Sell items from a shop to a character. Handles gold transfer.
- `character_name`, `item`, `quantity`, `price_each`

**shop_restock** — Restock a shop with new items and adjust prices.
- `name`, `items`, `adjust_prices_by`

**shop_update** — Update shop details.
- `name`, `description`, `shop_type`

**shop_list** — List all shops in the current campaign.

---

## Mysteries

**mystery_create** — Create a new mystery with title, description, and urgency.
- `title`, `description`, `urgency`

**clue_add** — Add a clue to a mystery.
- `mystery_id`, `description`, `clue_id`

**clue_reveal** — Mark a clue as revealed to the party.
- `clue_id`

**clue_connect** — Connect two clues in a mystery (implies a relationship between them).
- `clue_id_1`, `clue_id_2`

**red_herring_add** — Add a red herring to a mystery.
- `mystery_id`, `description`, `red_herring_id`

**red_herring_reveal** — Mark a red herring as revealed to the party.
- `red_herring_id`

**suspect_add** — Add a suspect to a mystery.
- `mystery_id`, `name`, `description`

**suspect_rulout** — Rule out a suspect (clears them from consideration but records they were investigated).
- `suspect_id`

**mystery_status** — Get formatted status — clues revealed, suspects remaining, red herrings, solution.
- `mystery_id`

**mystery_solve** — Set the solution and mark the mystery as solved.
- `mystery_id`, `solution`

**mystery_delete** — Delete a mystery and all its data.
- `mystery_id`

---

## Threads

**thread_add** — Add a new narrative thread.
- `description`, `urgency` ('high'/'medium'/'low'), `status`

**thread_resolve** — Mark a thread as resolved.
- `thread_id`

**thread_list** — List all threads, optionally filtered.
- `status`, `urgency`

**thread_update_urgency** — Change a thread's urgency.
- `thread_id`, `urgency`

---

## World Facts

**fact_set** — Save a world fact under a key. Overwrites if key exists.
- `key`, `fact`

**fact_get** — Retrieve a world fact by key.
- `key`

**fact_list** — List all saved world facts.

**fact_delete** — Delete a world fact by key.
- `key`

---

## Relations

**relation_set** — Set the attitude between an NPC or faction and the party.
- `name`, `attitude` ('friendly'/'neutral'/'suspicious'/'hostile'), `notes`

**relation_update** — Update attitude score or notes for an existing relation.
- `name`, `attitude`, `notes`

**relation_get** — Get current attitude for an NPC or faction.
- `name`

**relation_list** — List all tracked NPC and faction relations.

**relation_delete** — Remove a relation entry.
- `name`

---

## Homebrew

**homebrew_add** — Add a homebrew entry (monster, item, spell, character, etc.) to the library.
- `name`, `type`, `data`

**homebrew_get** — Get a homebrew entry by name and type.
- `name`, `type`

**homebrew_list** — List all homebrew entries, optionally filtered by type.
- `type`

**homebrew_update** — Update a homebrew entry's fields.
- `name`, `type`, `data`

**homebrew_delete** — Delete a homebrew entry.
- `name`, `type`

**homebrew_search** — Search homebrew entries by name or tag.
- `query`, `type`

---

## Recap

**recap_add_event** — Log an event to the current session recap. Call after every significant action, discovery, combat, or social interaction.
- `event`, `event_type`, `character`

**recap_get** — Get the current session recap as a formatted narrative.

**recap_compress** — Compress the event log into a shorter narrative summary. Called automatically every 5 minutes.

**recap_summarize** — Get an LLM-written summary of the campaign so far, built from compressed recaps.

**recap_new_session** — Start a new session. Archives the previous session's recap and begins fresh.

---

## Random Tables

**table_list** — List all available D&D random tables grouped by category. Call this first to discover table names.

**table_roll** — Roll on a named random table.
- `table_name`, `count`

**table_generate_npc** — Generate a quick NPC with name, race, occupation, appearance, and personality quirk.

**table_generate_tavern** — Generate a complete tavern with name, district, ambiance, and a notable regular patron.

**table_generate_shop** — Generate a shop name and current inventory.

**table_generate_encounter** — Generate a random encounter suited to the environment.

**table_generate_treasure** — Generate random treasure including mundane valuables, art objects, and gemstones.

**table_generate_magic_item** — Generate a magic item with name, origin, and unique quirk.

**table_generate_curse** — Generate a curse with minor effect, major effect, and removal difficulty.

**table_generate_lair** — Generate a creature's lair with distinctive features and dressing.

**table_generate_dungeon_room** — Generate a dungeon room with room type, interesting feature, and atmospheric dressing.

**table_generate_wildmagic** — Generate a wild magic surge result.

**table_generate_potion_effect** — Generate a potion miseffect when something goes wrong with potion creation or storage.

---

## Game Clock

**time_set** — Set the game clock to a specific day and time of day.
- `day`, `time_of_day`

**time_advance** — Advance the game clock by a duration.
- `duration` (e.g. '2 hours', '30 minutes')

**time_get** — Get the current game clock state.

**time_set_day** — Set the day number without changing time of day.
- `day`

**time_reset** — Reset the game clock to Day 1, Dawn.

---

## Status

**status_get_all** — Full snapshot across all D&D plugins — campaign, time, scene, weather, party HP/conditions, resources, combat, threads, quests. Optionally includes NPC attitudes.
- `include_npcs` (bool)

**status_party** — Quick party HP and conditions snapshot only.

---

## Reset

**campaign_reset** — Reset the current campaign. Clears all character state, combat, active effects, and quest progress.
- `confirm` (must be true), `mode` ('full' or 'session')

---

## Mode Commands

**game on** / **game off** — Toggle D&D mode. When off, the AI operates as a normal assistant and ignores all D&D tools and state.

**session** / **combat** / **exploration** / **social** / **downtime** — Push a mode onto the mode stack. Combat mode always stays on top. Each mode injects relevant reminders into the prompt.
