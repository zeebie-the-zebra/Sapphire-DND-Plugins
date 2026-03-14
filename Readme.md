# D&D Tools Documentation

A comprehensive guide to all D&D-related plugins and tools available in Sapphire.

PLEASE CHECK DND-TOGGLE INSTRUCTIONS BEFORE USE.

---

## Table of Contents

1. [dnd-characters](#dnd-characters) — Character Sheet Manager
2. [dnd-npcs](#dnd-npcs) — NPC Generator & Roster
3. [dnd-scene](#dnd-scene) — Scene & Location Tracker
4. [dnd-time](#dnd-time) — Time Tracker
5. [dnd-campaign](#dnd-campaign) — Campaign Management
6. [dnd-encounters](#dnd-encounters) — Encounter Builder & Combat Tracker
7. [dnd-dice-roller](#dnd-dice-roller) — Dice Roller
8. [dnd-recap](#dnd-recap) — Session Summary
9. [dnd-facts](#dnd-facts) — World Facts Registry
10. [dnd-loot](#dnd-loot) — Treasure Generator
11. [dnd-spells](#dnd-spells) — Spell Database
12. [dnd-threads](#dnd-threads) — Story Threads Tracker
13. [dnd-levelup](#dnd-levelup) — XP Tracking & Level-Up Guide
14. [dnd-resources](#dnd-resources) — Class Resource Tracker
15. [dnd-rules](#dnd-rules) — Rules Reference
16. [dnd-guards](#dnd-guards) — Safety Guardrails
17. [dnd-logger](#dnd-logger) — Session Logging
18. [dnd-voice](#dnd-voice) — Voice Commands
19. [dnd-voice-polish](#dnd-voice-polish) — OOC Filter
20. [dnd-reset](#dnd-reset) — Campaign Reset
21. [dnd-toggle](#dnd-toggle) — Game Mode Toggle
22. [dnd-active-conditions](#dnd-active-conditions) — Active Condition Tracker  - Not in this release, still being tested.
23. [dnd-random-tables](#dnd-random-tables) — Random Content Tables  - Not in this release, still being tested.
24. [dnd-shop](#dnd-shop) — Shop & Bartering System  - Not in this release, still being tested.
25. [dnd-status](#dnd-status) — Party Status Overview  - Not in this release, still being tested.
26. [dnd-weather](#dnd-weather) — Weather System  - Not in this release, still being tested.
27. [dnd-npc-relations](#dnd-npc-relations) — NPC Relationship Tracker  - Not in this release, still being tested.
28. [dnd-context-budget](#dnd-context-budget) — Context Management - Not in this release, still being tested.

---

## dnd-characters

**Purpose:** Persistent character sheet management for player characters.

**Tools:**

| Tool | Description |
|------|-------------|
| `character_create` | Create a new character with stats, HP, AC, class, race, background |
| `character_get` | Get full character sheet |
| `character_update` | Update any character fields |
| `character_list` | List all party characters |
| `character_delete` | Delete a character |
| `character_damage` | Apply damage (handles temp HP first, tracks death saves) |
| `character_heal` | Heal HP, add temp HP, or perform rests |
| `character_use_spell_slot` | Expend a spell slot |
| `character_restore_spell_slots` | Restore spell slots after rest |
| `character_add_item` | Add item to inventory |
| `character_remove_item` | Remove item from inventory |
| `character_set_condition` | Add/remove conditions (poisoned, stunned, etc.) |
| `character_set_user_controlled` | Mark which character(s) the USER controls |

**Example:**
```
character_create(name="Aragorn", race="Human", class_name="Ranger", level=5, hp_max=45, ac=15, user_controlled=true)
```

---

## dnd-npcs

**Purpose:** Generate and track NPCs with persistent storage across sessions.

**Tools:**

| Tool | Description |
|------|-------------|
| `npc_generate` | Generate a random NPC with name, race, occupation, appearance, personality, bonds, flaws |
| `npc_save` | Save a custom NPC to memory |
| `npc_get` | Get saved NPC details |
| `npc_list` | List all saved NPCs |
| `npc_update` | Update NPC fields (attitude, notes, secrets) |
| `npc_delete` | Delete an NPC |

**Example:**
```
npc_generate(race="Elf", occupation="Innkeeper", attitude="friendly")
```

---

## dnd-scene

**Purpose:** Track the current scene/location — who is present, mood, lighting, and persistent room descriptions.

**Tools:**

| Tool | Description |
|------|-------------|
| `scene_move` | Move party to a location (loads saved layout if known) |
| `scene_set` | Save permanent description of current location |
| `scene_get` | Get current scene state |
| `scene_add_person` | Add NPC to current scene |
| `scene_remove_person` | Remove NPC from scene |
| `scene_update` | Update per-visit details (mood, lighting, time) |
| `scene_update_location` | Permanently change room layout |
| `scene_list_locations` | List all saved locations |
| `scene_edit_location` | Edit a saved location by name (without being there) |
| `scene_delete_location` | Delete a location from library |

**Example:**
```
scene_move(name="The Rusty Flagon, common room", present=["Gimli", "Legolas"], time="evening", mood="tense")
scene_set(description="Bar on north wall, boar head above, kitchen door behind bar, four round tables...")
```

---

## dnd-time

**Purpose:** Persistent time tracking — time of day, game clock, day count. Injected every turn so the DM never forgets.

**Tools:**

| Tool | Description |
|------|-------------|
| `time_set` | Set current time (morning/afternoon/evening/night, hour, day) |
| `time_advance` | Advance time by hours/minutes |
| `time_get` | Get current time info |
| `time_set_day` | Set day number |
| `time_reset` | Reset time for new session |

**Example:**
```
time_set(time_of_day="morning", hour=8, day=1)
time_advance(hours=2, event="Travel through the forest")
```

---

## dnd-campaign

**Purpose:** Manage campaign-level state — location, quests, chapter, factions.

**Tools:**

| Tool | Description |
|------|-------------|
| `campaign_set` | Set/update campaign name, chapter, location, time, world notes, factions |
| `campaign_get` | Get current campaign state |
| `campaign_quest` | Add/update/complete quests |
| `campaign_set_mode` | Switch between in_character and paused modes |

**Example:**
```
campaign_set(name="Curse of Strahd", chapter="Chapter 3: The Amber Temple", location="Village of Barovia", factions="City Guard: hostile")
```

---

## dnd-encounters

**Purpose:** Build encounters, track initiative, manage combat.

**Tools:**

| Tool | Description |
|------|-------------|
| `encounter_generate` | Generate random encounter by environment and party level |
| `encounter_start_combat` | Start combat with initiative tracking |
| `encounter_next_turn` | Advance to next combatant's turn |
| `encounter_end_combat` | End combat and clear tracker |
| `encounter_combat_status` | Show current combat state |
| `encounter_xp_budget` | Calculate XP budget for encounter difficulty |
| `monster_lookup` | Look up monster stats by name |

**Example:**
```
encounter_generate(environment="dungeon", party_level=5, difficulty="medium")
encounter_start_combat()
```

---

## dnd-dice-roller

**Purpose:** Roll dice with full notation support.

**Tools:**

| Tool | Description |
|------|-------------|
| `dice_roll` | Roll dice (1d20, 2d6+3, advantage, disadvantage) |
| `dice_history` | Show recent roll history |

**Example:**
```
dice_roll(rolls=[{"notation": "1d20", "label": "Attack roll", "advantage": "advantage"}, {"notation": "2d6+3", "label": "Damage"}])
```

**Notation Support:**
- Standard: `1d20`, `2d6`, `4d4-1`
- Advantage: roll twice, take higher
- Disadvantage: roll twice, take lower
- Multiple rolls in one call

---

## dnd-recap

**Purpose:** Maintains a running narrative summary that gets injected into every LLM prompt. This is the LLM's "memory" of the game state.

**How it works:**
- `prompt_inject` hook: Injects session summary at the top of every system prompt so the LLM never forgets
- `post_chat` hook (auto_log.py): Logs a brief note every 3 turns
- Scheduled task (compress.py): Every 5 minutes, compresses raw events (simple text join - no LLM to avoid chat pollution)

**IMPORTANT:** When you want a narrative-style summary, just ask the LLM! Say "what happened?" or "recap" - the LLM has all the recap context injected and will provide a narrative summary naturally. You don't need a separate summarization step.

**Tools:**

| Tool | Description |
|------|-------------|
| `recap_add_event` | Log important event to session recap |
| `recap_get` | Get full session recap |
| `recap_compress` | Manually compress old events (simple join) |
| `recap_summarize` | Save current events to summary context (then ask "what happened?" for narrative) |
| `recap_new_session` | Archive current session and start fresh |

**Example:**
```
recap_add_event(event="Party discovered Harbormaster Voss is blackmailed by the Sea Prince")
```

**Note:** This plugin provides context TO THE LLM. The summaries are joined with " | " separators automatically. Ask the LLM directly for narrative summaries.

---

## dnd-facts

**Purpose:** Store specific world facts that must stay consistent (NPC details, passwords, secrets).

**Tools:**

| Tool | Description |
|------|-------------|
| `fact_set` | Save a fact by key (category: npcs, locations, secrets, promises, lore, clues, items) |
| `fact_get` | Retrieve a fact by key |
| `fact_list` | List all facts, optionally filtered by category |
| `fact_delete` | Delete a fact |

**Example:**
```
fact_set(key="inn_rusty_flagon", value="Green door, smells of fish, run by Petra (one-armed, red hair)", category="locations")
fact_set(key="duke_password", value="silverbell", category="secrets")
```

---

## dnd-loot

**Purpose:** Generate treasure hoards and magic items by CR tier.

**Tools:**

| Tool | Description |
|------|-------------|
| `loot_generate` | Generate loot for individual monsters or hoards by CR tier |
| `loot_magic_item` | Roll on magic item tables (A-I from DMG) |

**Example:**
```
loot_generate(cr_tier="5-10", hoard=true)
loot_magic_item(table="C")
```

---

## dnd-spells

**Purpose:** Look up D&D 5e spell mechanics.

**Tools:**

| Tool | Description |
|------|-------------|
| `spell_lookup` | Get spell details (casting time, range, components, duration, description) |
| `spell_list` | List spells by level or class |

**Example:**
```
spell_lookup(name="Fireball")
spell_list(level=1, class="Wizard")
```

---

## dnd-threads

**Purpose:** Track loose ends, consequences, and unresolved story beats. High-urgency threads are injected every turn so the DM weaves them back naturally.

**Tools:**

| Tool | Description |
|------|-------------|
| `thread_add` | Add an open narrative thread (consequence, promise, clue, threat, opportunity, revelation) |
| `thread_resolve` | Mark a thread as resolved |
| `thread_list` | List all threads with their status |
| `thread_update_urgency` | Change thread urgency (high/medium/low) |

**Example:**
```
thread_add(description="The villain saw the party escape — he knows their faces", type="consequence", urgency="high")
```

---

---

## dnd-levelup

**Purpose:** XP tracking and level-up guidance. Tells the model exactly when a character is ready to level up, what they gain, and walks through choices before writing back to the character sheet.

**Solves:** Small models not knowing XP thresholds, what a class gets at each level, or when to trigger an ASI/feat choice.

**Tools:**

| Tool | Description |
|------|-------------|
| `xp_add` | Award XP to one or all party members. Returns a level-up alert if a threshold is crossed |
| `xp_get` | Check a character’s current XP, level, and progress to next level |
| `xp_check_all` | Show full party XP status — flags anyone ready to level up |
| `levelup_guide` | Show exactly what a character gains at their next level: features, spell slots, HP roll range, ASI/feat choices |
| `levelup_apply` | Apply the level-up to the character sheet after the player makes their choices |

**Hook:** `prompt_inject` — injects a loud `⬆️ LEVEL UP READY` flag if any character has crossed an XP threshold, so Remmi can’t miss it.

**Covers all 13 classes:** Barbarian, Bard, Cleric, Druid, Fighter, Monk, Paladin, Ranger, Rogue, Sorcerer, Warlock, Wizard, Artificer — with correct features, spell slot tables (full/half/pact casters), and ASI levels per class.

**Workflow:**
```
# After combat ends:
xp_add(xp=450, reason="defeated goblin warband")
# → "⬆️ Aldric REACHED LEVEL 3! Call levelup_guide(name='Aldric', to_level=3) NOW."

levelup_guide(name="Aldric", to_level=3)
# → Shows new features, HP roll, spell slots, subclass choice prompt

# After player decides:
levelup_apply(name="Aldric", to_level=3, hp_roll=5, new_features="Chose Battle Master subclass")
```

**Setup:** Call `resource_setup` (dnd-resources) after every `levelup_apply` so class resources update to match the new level.

---

## dnd-resources

**Purpose:** Tracks per-rest consumable class resources so Remmi never loses count mid-combat.

**Solves:** Small models forgetting how many rages a Barbarian has left, or whether Channel Divinity has been used.

**Tracked resources by class:**

| Class | Resources Tracked |
|-------|------------------|
| Barbarian | Rage (uses scale with level, +damage tracked) |
| Bard | Bardic Inspiration (recharges on short rest at L5+) |
| Cleric | Channel Divinity (1–3 uses/short rest) |
| Druid | Wild Shape (2 uses/short rest, CR limit by level) |
| Fighter | Second Wind, Action Surge, Indomitable |
| Monk | Ki Points (= level, short rest) |
| Paladin | Lay on Hands pool, Divine Sense, Channel Divinity |
| Sorcerer | Sorcery Points (= level) |
| Warlock | Pact Magic slots (short rest, all same level) |
| Wizard | Arcane Recovery (1/short rest) |

**Tools:**

| Tool | Description |
|------|-------------|
| `resource_setup` | Populate correct resources for a character’s class and level. Call on creation and after level-up |
| `resource_use` | Mark uses as spent (Rage activated, Ki spent, Bardic Inspiration given, etc.) |
| `resource_restore` | Restore resources after a short or long rest |
| `resource_get` | Get current resource status for one character |
| `resource_list` | Get resource status for all party members |
| `resource_set_max` | Add or edit a resource manually (subclass features, magic items, etc.) |

**Hook:** `prompt_inject` — only injects when resources are partially or fully spent. Silent when everything is full. Shows `⚠️ EMPTY` warnings for depleted resources.

**Example:**
```
resource_setup(name="Thorin", class_name="Barbarian", level=5)
# → "Rage: 3/3 [long rest] — +2 damage, resistance to physical damage"

resource_use(name="Thorin", resource="Rage")
# → "Thorin used 1× Rage. Remaining: 2/3"

resource_restore(rest_type="long")
# → "Long rest — resources restored: Thorin: Rage"
```

---

## dnd-rules

**Purpose:** Instant lookup for D&D 5e rules, conditions, actions, and mechanics. Prevents hallucinated or misremembered rules mid-session.

**Solves:** Small models confidently getting conditions wrong (e.g. poisoned applies disadvantage to both attacks AND ability checks), or misruling bonus action spells, concentration, death saves, etc.

**Tools:**

| Tool | Description |
|------|-------------|
| `condition_lookup` | Exact mechanical effects of any condition |
| `action_lookup` | What actions, bonus actions, and reactions do — with edge cases |
| `rules_lookup` | Common mechanics: cover, crits, surprise, concentration, short/long rest, etc. |

**Conditions covered:** blinded, charmed, deafened, exhaustion (all 6 levels), frightened, grappled, incapacitated, invisible, paralyzed, petrified, poisoned, prone, restrained, stunned, unconscious, concentration, death saves

**Actions covered:** attack, cast a spell, dash, disengage, dodge, help, hide, ready, search, use an object, opportunity attack, grapple, shove, two-weapon fighting

**Rules covered:** cover, advantage/disadvantage stacking, critical hits, surprise, concentration saves, bonus action spell restriction, short rest, long rest, spell save DC, multiclassing, falling damage, difficult terrain, attunement, sneak attack, ritual spells

**Example:**
```
condition_lookup(condition="poisoned")
# → "DISADVANTAGE on attack rolls. DISADVANTAGE on ability checks."

rules_lookup(rule="bonus action spell")
# → "If you cast ANY spell with a bonus action, the only other spell
#    you can cast that turn is a cantrip with a 1-action casting time."
```

No state — pure reference lookup. No setup required.

## dnd-guards

**Purpose:** Safety guardrails that protect the campaign from accidents and automate tracking.

**Pre-Execute Hook (before tool calls):**
- **Hard-blocks ALL D&D tools** when game is off (reads `dnd-toggle` state) — no tool can fire during normal chat
- **Blocks `campaign_reset`** without explicit `confirm=true` — prevents accidental wipes
- **Blocks `character_delete`** if character doesn't exist — prevents hallucination bugs
- **Enforces `scene_update_location`** requires a change_reason — maintains audit trail
- **Logs all tool calls** to audit trail (last 50 calls)

**Post-Execute Hook (after tool calls):**
- **Death save detection** — When HP hits 0, auto-creates high-urgency thread and logs to recap
- **Auto recap logging** — Automatically logs combat end, scene moves, quest changes, NPC saves
- **Combat XP logging** — Logs XP earned when combat ends
- **Scene move logging** — Logs location changes automatically

This is a hook-only plugin (no tools). It runs automatically.

---

## dnd-logger

**Purpose:** Stores a complete transcript of every conversation that can be queried by the user. This is separate from dnd-recap which provides context to the LLM.

**What it does (hook-only, no tools):**
- Logs every player message + DM response to `session_log`
- Tracks `turn_count` and `session_num`
- Auto-increments session number on new day
- Does NOT call the LLM (summarization is handled by dnd-recap's scheduled task)

**Note:** This plugin stores raw conversation logs for user queries. Use dnd-recap for LLM context.

---

## dnd-voice

**Purpose:** Voice command handlers that respond to specific phrases WITHOUT calling the LLM. These are instant triggers.

**Commands (hook-only):**

| Trigger Phrases | Action |
|-----------------|--------|
| "pause game", "out of character", "ooc" | Pause game, switch to OOC mode |
| "resume game", "in character", "back to the game" | Resume game, return to DM mode |
| "save game", "save session" | Save progress |
| "party status", "show party", "check party" | Show party stats |
| "end session", "session over" | End the session |
| "recap", "what happened", "story so far" | Prime for recap response |

This is a hook-only plugin (no tools). Say these phrases to trigger instant responses.

---

## dnd-voice-polish

**Purpose:** Post-processing filter that strips out-of-character (OOC) lines from the DM's responses before they are spoken.

**What it strips:**
- "As an AI...", "I should note..."
- "As the DM...", "[DM narration begins]"
- "Note: this is a fictional scenario..."
- Orphaned tool call markers
- Repeated framing lines

This is a hook-only plugin (no tools). It runs automatically after every LLM response.

---

## dnd-reset

**Purpose:** Reset campaign state between sessions or campaigns.

**Tool:**

| Tool | Description |
|------|-------------|
| `campaign_reset` | Full or session reset (clears characters, NPCs, scenes, time, combat, logs) |

**Modes:**
- `full` — Wipe everything for a new campaign
- `session` — Clear combat/scenes/logs, keep characters and campaign data

**Example:**
```
campaign_reset(mode="session", confirm=true)
```

---

---

## dnd-toggle

**Purpose:** Single-phrase toggle to switch between D&D game mode and normal chat — no UI required.

**How it works:**
- A `pre_chat` hook intercepts the trigger phrase **before** it reaches the LLM — instant, no inference cost
- Saves a `dnd_active` flag to plugin state
- A `prompt_inject` hook inserts a soft override at the top of every system prompt when game is off
- `dnd-guards` reads the same flag and **hard-blocks** all D&D tool calls at the `pre_execute` level

**Trigger Phrases:**

| Say this | Effect |
|----------|--------|
| `"game on"`, `"start game"`, `"dnd on"`, `"remmi on"`, `"start session"`, `"begin session"` | Activates Remmi and all D&D tools |
| `"game off"`, `"stop game"`, `"dnd off"`, `"remmi off"`, `"end session"`, `"pause game"` | Returns to normal chat, blocks all D&D tools |

**What happens when game is OFF:**
- **Soft block:** `prompt_inject` inserts `"You are a normal assistant, ignore all D&D context"` at position 0 of the system prompt — above everything else any other plugin injects
- **Hard block:** `dnd-guards` `pre_execute` intercepts any D&D tool call and returns `⛔ blocked — D&D mode is off. Say 'game on' to activate.`
- All other D&D plugins remain installed and enabled — they simply cannot fire

**Default state:** OFF — you must say `"game on"` to activate. The LLM is never involved in the toggle itself.

**Required:** Both `dnd-toggle` and `dnd-guards` must be installed. The hard block lives in `dnd-guards/hooks/pre_execute.py`.

This is a hook-only plugin (no tools). It runs automatically.

---

## dnd-active-conditions

**Purpose:** Track active conditions and ongoing effects on characters, including concentration spells, status effects, and temporary buffs/debuffs.

**Solves:** Low-parameter models forgetting concentration spells, which character has which condition, or when effects expire.

**Tools:**

| Tool | Description |
|------|-------------|
| `condition_add` | Add an active condition to a character (name, condition, duration, source) |
| `condition_remove` | Remove a condition from a character |
| `condition_list` | List all active conditions for a character or entire party |
| `condition_check` | Check if a character has a specific condition |
| `condition_tick` | Advance time on all duration-based conditions |

**Hook:** `prompt_inject` — injects active conditions summary when any character has active effects. Shows concentration spells separately.

**Example:**
```
condition_add(target="Gandalf", condition="Concentration: Hold Person", duration=6, source="Gandalf")
condition_add(target="Thorin", condition="Poisoned", duration=1, source="Snake bite")
condition_list(target="Gandalf")
# → "Concentration: Hold Person (5 rounds remaining)"
```

---

## dnd-random-tables

**Purpose:** Pre-built random tables for content generation — eliminates generation effort for low-parameter models.

**Solves:** Low-parameter models making up inconsistent or boring results. Pre-rolled tables ensure variety and consistency.

**Tables available:**

| Table Category | Examples |
|----------------|----------|
| Traps | Spike pit, collapsing ceiling, poison gas, tripwire |
| Weather | Clear, cloudy, rain, snow, fog, storm, heat wave |
| Random Encounters | Goblins, bandits, merchant caravan, lost traveler |
| Dungeon Rooms | Empty, treasure, puzzle, trap, monster, secret |
| Tavern Rumors | Lost artifact, cursed land, hidden cult, royal secret |
| Treasure | Coins, gems, art, mundane items, magic items |
| NPC Hooks | Seeking hirelings, fleeing danger, carrying message |

**Tools:**

| Tool | Description |
|------|-------------|
| `table_roll` | Roll on a named table (returns pre-stored result) |
| `table_list` | List all available tables |
| `table_custom` | Create a custom table with weighted options |

**Example:**
```
table_roll(table="tavern_rumors")
# → "A merchant claims to have seen a dragon's nest in the mountains"

table_roll(table="dungeon_room", location="crypt")
# → "Sarcophagus with animated skeleton defender"
```

---

## dnd-shop

**Purpose:** Manage shops, inventories, and bartering — tracks available goods, prices, and player purchases.

**Solves:** Low-parameter models forgetting what's for sale, making up inconsistent prices, or losing track of player purchases.

**Tools:**

| Tool | Description |
|------|-------------|
| `shop_create` | Create a shop with name, type, inventory |
| `shop_get` | Get current shop inventory and details |
| `shop_add_item` | Add items to shop inventory |
| `shop_remove_item` | Remove/sell an item from shop |
| `shop_list` | List all known shops |
| `barter` | Calculate final price with charisma modifier and persuasion |

**Inventory tracking:** Shop inventory is persistent. When an item is purchased, it's removed from stock automatically.

**Example:**
```
shop_create(name="Iron & Steel", type="blacksmith", location="Town Square")
shop_add_item(name="Iron & Steel", item="Longsword", price=15, quantity=3)
shop_add_item(name="Iron & Steel", item="Crossbow bolts (20)", price=2, quantity=10)
shop_get(name="Iron & Steel")
# → "Longsword (15 gp) x3, Crossbow bolts (2 gp) x10"

barter(base_price=15, charisma_mod=2, difficulty="hard")
# → "Final price: 12 gp (persuasion success)"
```

---

## dnd-status

**Purpose:** Quick overview of entire party state — HP, conditions, resources, and location at a glance.

**Solves:** Low-parameter models losing track of party state. Provides a single reference instead of scattered tool calls.

**Tools:**

| Tool | Description |
|------|-------------|
| `status_party` | Full party status (HP, conditions, location, active resources) |
| `status_combat` | Combat-focused status (initiative order, current turn) |
| `status_brief` | One-line per character summary |

**Hook:** `prompt_inject` — can inject abbreviated status every turn if enabled.

**Example:**
```
status_party()
# → "Gandalf: 45/45 HP, Concentrating on Hold Person | Thorin: 12/45 HP, Poisoned | Legolas: 38/38 HP"
status_brief()
# → "Gandalf (45/45) | Thorin (12/45) Poisoned | Legolas (38/38)"
```

---

## dnd-weather

**Purpose:** Track weather conditions and generate appropriate atmosphere for scenes. Supports multi-location weather and forecasting.

**Solves:** Low-parameter models forgetting to adjust atmosphere based on weather, or generating inconsistent weather.

**Climate presets:** temperate, arctic, desert, tropical, coastal, mountain, swamp

**Tools:**

| Tool | Description |
|------|-------------|
| `weather_set` | Set current weather (optionally per location) |
| `weather_generate` | Random weather based on climate and season |
| `weather_get` | Get current weather (optionally for specific location) |
| `weather_advance` | Advance weather after time passes |
| `weather_forecast` | Generate multi-day weather forecast |
| `weather_list_locations` | List all locations with tracked weather |
| `weather_delete_location` | Clear weather for a location |

**Weather states:** clear, overcast, light_rain, heavy_rain, fog, windy, snow, blizzard, clear_cold, clear_hot, windy_sand, rare_rain, thunderstorm, humid_overcast, clear_humid, sea_fog, strong_wind, storm

**Mechanical impacts (auto-injected):**
- Blizzard: CON save DC 12 each hour or gain exhaustion
- Heavy rain/fog: Perception disadvantage
- Thunderstorm: Lightning strike chance
- Windy/strong wind: Ranged attack disadvantage
- Clear hot: Exhaustion after 2 hours unshaded travel
- Snow: Difficult terrain

**Hooks:**
- `prompt_inject` — injects weather description with mechanical warnings. Shows per-location weather when tracking multiple areas.

**Example:**
```
# Set global weather
weather_set(condition="clear", temperature="comfortable")
# → "Weather set: clear | Comfortable temperature"

# Set location-specific weather
weather_generate(climate="mountain", season="winter", location="High Pass")
# → "Weather set [High Pass]: blizzard | Travel dangerous..."

# Get weather for specific location
weather_get(location="High Pass")
# → "Current weather [High Pass]: blizzard"

# Generate 3-day forecast for travel planning
weather_forecast(climate="temperate", days=3)
# → "Day 1: clear | Day 2: light_rain | Day 3: clear"

# Advance weather after long rest
weather_advance(hours_passed=8, climate="temperate")
# → "Weather holds: clear. No significant change after 8 hours."

# List all tracked locations
weather_list_locations()
# → "[Default]: clear | High Pass: blizzard"

**Auto-advance (dnd-time integration):**
```
# Enable automatic weather changes when time_advance is called
weather_auto_advance(enabled=true, climate="temperate")
# → "Auto-weather enabled (climate: temperate)"

# Now when time_advance(hours_passed=8) is called, weather may change automatically
```

---

## dnd-npc-relations

**Purpose:** Track relationship standings between NPCs and player characters — formalizes reputation, bonds, and attitudes.

**Solves:** Low-parameter models being inconsistent about who likes/hates whom, or forgetting past interactions.

**Relationship scale:** Hostile (<-3) → Unfriendly (-2) → Neutral (-1 to 1) → Friendly (2) → Ally (3+)

**Tools:**

| Tool | Description |
|------|-------------|
| `relation_set` | Set relationship between NPC and character |
| `relation_modify` | Adjust relationship (positive or negative) |
| `relation_get` | Get relationship status between NPC and character |
| `relation_list_npc` | List all relationships for an NPC |
| `relation_list_character` | List all relationships for a character |

**Hook:** `prompt_inject` — injects high/hostile relationships as warnings when relevant.

**Example:**
```
relation_set(npc="Gundar", character="Aragorn", standing=2, note="Saved his daughter from wolves")
relation_modify(npc="Gundar", character="Aragorn", change=1, reason="Delivered medicine to his sick wife")
relation_get(npc="Gundar", character="Aragorn")
# → "Friendly (3) — Saved daughter, delivered medicine"
```

---

## dnd-context-budget

**Purpose:** Monitor and manage context window usage to prevent overflow during long sessions.

**Solves:** Low-parameter models losing track of context limits, causing truncated responses or lost state.

**What it tracks:**
- Current token count
- Estimated tokens per inject source
- Warning thresholds (75%, 90%, 100%)
- Oldest injected content

**Tools:**

| Tool | Description |
|------|-------------|
| `context_get` | Get current context usage (tokens, percentage, sources) |
| `context_sources` | List all content sources contributing to context |
| `context_clear` | Manually clear old injects (recap compression recommended instead) |
| `context_warning` | Check if approaching limit, returns warning level |

**Hook:** `prompt_inject` — includes context usage stats when above 75%.

**Example:**
```
context_get()
# → "Usage: 4,200/8,000 tokens (52.5%) | Sources: recap(2000), facts(800), threads(600), resources(400)"
context_warning()
# → "OK" / "Approaching limit (78%) — consider compressing recap"
```

---

## Plugin Integration Summary

| Plugin | Injects Context | Tracks State |
|--------|----------------|--------------|
| dnd-characters | Party + user control | HP, inventory, conditions |
| dnd-scene | Current location/layout | Scene, library |
| dnd-time | Current time/day | Time, elapsed |
| dnd-campaign | Location, quests, chapter | Campaign state |
| dnd-recap | Session summary | Events |
| dnd-facts | World facts | Facts |
| dnd-threads | Open story threads | Threads |
| dnd-guards | — | Audit log (tool calls) |
| dnd-logger | — | Session log, journal |
| dnd-voice | — | (voice command handlers) |
| dnd-levelup | Level-up alerts | XP per character |
| dnd-resources | Spent resource warnings | Per-rest resource counts |
| dnd-rules | — | (pure lookup, no state) |
| dnd-voice-polish | — | (OOC filter) |
| dnd-toggle | Game mode state override | dnd_active flag |
| dnd-active-conditions | Active effects summary | Concentration, conditions |
| dnd-random-tables | — | (pre-built content) |
| dnd-shop | — | Shop inventories, transactions |
| dnd-status | Party status summary | Quick reference |
| dnd-weather | Weather description | Weather state |
| dnd-npc-relations | Relationship warnings | NPC attitudes |
| dnd-context-budget | Context usage stats | Token tracking |

---

## Quick Start

At session start, set up:

```
# 1. Set campaign
campaign_set(name="Your Campaign", chapter="Chapter 1", location="Starting town")

# 2. Set time
time_set(time_of_day="morning", hour=8, day=1)

# 3. Create characters
character_create(name="Hero1", class_name="Fighter", race="Human", hp_max=30, user_controlled=true)

# 4. Move to starting location
scene_move(name="Tavern main room", present=["Hero1"])
scene_set(description="Your description here...")

# 5. Set up class resources (dnd-resources)
resource_setup(name="Hero1", class_name="Fighter", level=1)

# 6. Add recap event
recap_add_event(event="The adventure begins...")

# After combat — award XP (dnd-levelup)
xp_add(xp=200, reason="defeated bandits")
```

> **Tip:** If you have `dnd-toggle` installed, say `"game on"` before running any of the above. All D&D tools are blocked until game mode is active.
