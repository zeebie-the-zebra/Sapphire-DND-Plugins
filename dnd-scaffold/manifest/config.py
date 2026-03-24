"""
dnd-scaffold — manifest/config.py

All mode/tool/trigger configuration for the consolidated D&D plugin.
This is the central configuration that drives the mode tracking system.

Modes:
  session     — general campaign state, recap, status
  combat      — initiative, attacks, HP tracking (always on top of stack)
  exploration — travel, weather, scene, random encounters
  social      — NPC interactions, persuasion, relations
  downtime    — shopping, rest, level-up, crafting
"""

# ── Mode definitions ───────────────────────────────────────────────────────────
MODES = ["session", "combat", "exploration", "social", "downtime"]

# Which mode(s) each tool belongs to (for UI/filtering purposes)
TOOL_MODES = {
    # Characters — all modes
    "character_create":       ["session", "combat", "exploration", "social", "downtime"],
    "character_get":         ["session", "combat", "exploration", "social", "downtime"],
    "character_update":      ["session", "combat", "exploration", "social", "downtime"],
    "character_list":        ["session", "combat", "exploration", "social", "downtime"],
    "character_delete":      ["session", "downtime"],
    "character_damage":      ["combat"],
    "character_heal":        ["combat", "downtime"],
    "character_spell_slots": ["session", "combat", "downtime"],
    "character_add_item":    ["session", "downtime"],
    "character_remove_item": ["session", "downtime"],
    "character_set_condition": ["combat", "session"],
    "character_set_user_controlled": ["session"],
    "character_level_up":    ["downtime"],

    # Combat — combat mode
    "encounter_generate":    ["exploration"],
    "encounter_start_combat": ["combat"],
    "encounter_next_turn":   ["combat"],
    "encounter_combat_status": ["combat"],
    "encounter_end_combat":  ["combat"],
    "encounter_xp_budget":   ["session"],
    "monster_lookup":        ["session", "combat", "exploration"],

    # Dice — all modes
    "dice_roll":             ["session", "combat", "exploration", "social", "downtime"],
    "dice_history":          ["session"],

    # Spells — all modes
    "spell_lookup":          ["session", "combat", "exploration", "social", "downtime"],
    "spell_list":            ["session", "combat", "exploration", "social", "downtime"],
    "condition_lookup":      ["session", "combat", "exploration", "social", "downtime"],
    "rules_lookup":          ["session", "combat", "exploration", "social", "downtime"],
    "action_lookup":         ["session", "combat"],

    # Resources — all modes
    "resource_get":          ["session", "combat", "exploration", "social", "downtime"],
    "resource_set":          ["session", "combat", "exploration", "social", "downtime"],
    "resource_use":          ["combat", "exploration", "social"],
    "resource_reset":        ["downtime"],
    "inspiration_award":     ["session", "social", "downtime"],
    "inspiration_grant_if_none": ["session", "social", "downtime"],
    "inspiration_use":      ["combat", "social"],
    "inspiration_list":     ["session"],
    "inspiration_reset":    ["downtime"],

    # Travel & Weather — exploration
    "travel_advance":        ["exploration"],
    "travel_get":            ["exploration"],
    "weather_get":           ["exploration"],
    "weather_set":           ["exploration"],
    "weather_advance":       ["exploration"],
    "weather_forecast":      ["exploration"],

    # Scene — exploration
    "scene_move":            ["exploration"],
    "scene_get":             ["exploration"],
    "scene_update":          ["exploration"],
    "scene_list":            ["exploration"],

    # NPCs & Relations — social
    "npc_generate":          ["social", "exploration"],
    "npc_save":              ["social"],
    "npc_get":               ["social"],
    "npc_list":              ["session", "social"],
    "npc_update":             ["social"],
    "npc_delete":            ["social"],
    "relation_set":           ["social"],
    "relation_get":           ["social"],
    "relation_list":          ["social"],

    # Shop — downtime
    "shop_create":           ["downtime"],
    "shop_get":              ["downtime"],
    "shop_buy":               ["downtime"],
    "shop_sell":              ["downtime"],
    "shop_list":             ["downtime"],

    # Loot & Rewards — all modes
    "loot_generate":          ["exploration", "combat", "downtime"],
    "loot_magic_item":        ["downtime"],
    "xp_add":               ["session"],
    "xp_get":               ["session"],
    "xp_check_all":         ["session"],
    "levelup_guide":         ["downtime"],
    "levelup_apply":          ["downtime"],
    "homebrew_add":          ["downtime"],
    "homebrew_get":          ["session", "downtime"],
    "homebrew_list":         ["session", "downtime"],
    "homebrew_update":       ["downtime"],
    "homebrew_delete":       ["downtime"],
    "homebrew_search":       ["session", "downtime"],

    # Narrative — session
    "thread_add":            ["session", "social"],
    "thread_resolve":        ["session"],
    "thread_list":           ["session"],
    "fact_set":              ["session", "social", "exploration"],
    "fact_get":              ["session", "social", "exploration"],
    "fact_list":             ["session"],
    "fact_delete":           ["session"],
    "mystery_create":        ["session"],
    "clue_add":              ["session"],
    "clue_reveal":           ["session"],
    "clue_connect":          ["session"],
    "red_herring_add":       ["session"],
    "red_herring_reveal":    ["session"],
    "suspect_add":           ["session"],
    "suspect_rulout":        ["session"],
    "mystery_status":        ["session"],
    "mystery_solve":         ["session"],
    "mystery_delete":        ["session"],

    # Campaign — session
    "campaign_set":          ["session"],
    "campaign_get":          ["session"],
    "campaign_quest":        ["session"],
    "campaign_set_mode":     ["session"],
    "campaign_create":       ["session"],
    "campaign_list":         ["session"],
    "campaign_switch":       ["session"],
    "campaign_delete":       ["session"],
    "campaign_debug":        ["session"],
    "campaign_clean_migration": ["session"],

    # Recap & Status — session
    "recap_get":             ["session"],
    "recap_compress":        ["session"],
    "status_get_all":        ["session"],
    "status_party":          ["session"],

    # Time — session
    "time_set":              ["session"],
    "time_get":              ["session"],
    "time_advance":          ["session", "exploration"],

    # Tables — all modes
    "table_generate_npc":    ["social", "exploration"],
    "table_generate_road":   ["exploration"],
    "table_generate_dungeon": ["exploration"],
    "table_generate_city":   ["social", "downtime"],
    "table_generate_tavern": ["social", "downtime"],
    "table_generate_shop":   ["downtime"],
    "table_generate_loot":   ["exploration", "downtime"],
    "table_generate_weather": ["exploration"],
    "table_generate_rumor":  ["social"],
    "table_generate_quest":   ["session"],
    "table_generate_name":   ["social", "exploration"],

    # Rest — downtime
    "rest_long":             ["downtime"],
    "rest_short":            ["downtime"],
    "rest_spend_hit_dice":   ["downtime"],
    "rest_status":           ["downtime"],

    # Reset — session
    "campaign_reset":        ["session"],
}

# ── Mode push triggers — tool calls that push a mode onto the stack ────────────
MODE_PUSH_TRIGGERS = {
    "combat": [
        "encounter_start_combat",
        "encounter_next_turn",  # keep combat active through turns
    ],
    "exploration": [
        "scene_move",
        "travel_advance",
    ],
    "social": [
        "npc_generate",
        "npc_save",
        "npc_get",
    ],
    "downtime": [
        "rest_long",
        "rest_short",
        "shop_get",
        "shop_buy",
        "shop_sell",
        "levelup_guide",
        "levelup_apply",
    ],
}

# ── Mode pop triggers — tool calls that pop a mode from the stack ─────────────
# Combat is special: it always pops to the previous mode, never fully clears
# unless encounter_end_combat is called
MODE_POP_TRIGGERS = {
    "combat": [
        "encounter_end_combat",
    ],
    "exploration": [
        "encounter_start_combat",  # entering combat from exploration
        "npc_generate",            # transitioning to social
        "npc_save",
    ],
    "social": [
        "scene_move",
        "encounter_start_combat",
    ],
    "downtime": [
        "scene_move",
        "travel_advance",
        "encounter_start_combat",
    ],
}

# ── Mode context files ─────────────────────────────────────────────────────────
MODE_CONTEXTS = {
    "session":     "mode_contexts/session.md",
    "combat":      "mode_contexts/combat.md",
    "exploration": "mode_contexts/exploration.md",
    "social":      "mode_contexts/social.md",
    "downtime":    "mode_contexts/downtime.md",
}

# ── Mode injection order ────────────────────────────────────────────────────────
# Lower numbers = injected first. Modes are rendered in stack order (bottom to top)
# so combat (always on top) gets rendered last in its slot.
MODE_INJECT_ORDER = {
    "session":     10,
    "exploration": 20,
    "social":      30,
    "downtime":    40,
    "combat":      50,  # combat is always top of stack
}

# ── Default campaign ID ────────────────────────────────────────────────────────
DEFAULT_CAMPAIGN_ID = "default"

# ── Context budget settings (from dnd-context-budget) ─────────────────────────
DEFAULT_CHAR_BUDGET = 6000
DEFAULT_WARN_AT_PERCENT = 80

# ── Priority for hooks ─────────────────────────────────────────────────────────
# prompt_inject runs at priority 45 by default for the consolidated plugin
PROMPT_INJECT_PRIORITY = 45
