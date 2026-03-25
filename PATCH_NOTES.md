---
Bug Fixes

1. combat_hooks.py:151 — any() TypeError
- any(re.search(...), re.search(...)) passed two arguments instead of one iterable
- Fixed by wrapping in []

2. campaign.py:108 — Wrong plugin in campaign_debug
- Read from dnd-characters plugin state instead of dnd-scaffold
- Fixed to dnd-scaffold

3. mode_tracker.py:95-115 — Wrong plugin in character_delete guard
- Same issue: read from dnd-characters + legacy key instead of dnd-scaffold campaign-scoped storage
- Fixed to match the character tools' storage path

4. prompt_inject.py — 5 wrong plugin lookups + 1 crash
- _get_all_characters: dnd-characters → dnd-scaffold + isinstance guard
- _is_combat_active: dnd-encounters → dnd-scaffold + isinstance guard
- _get_inspiration_state: dnd-inspiration → dnd-scaffold + isinstance guard
- _get_travel_state: dnd-travel → dnd-scaffold + isinstance guard (this was the crash)
- _get_high_urgency_threads: dnd-threads → dnd-scaffold + isinstance guard

5. Full dnd-* plugin state audit — 26 broken references fixed

┌─────────────────────────┬───────┐
│          File           │ Count │
├─────────────────────────┼───────┤
│ tools/rest.py           │ 1     │
├─────────────────────────┼───────┤
│ tools/dice.py           │ 2     │
├─────────────────────────┼───────┤
│ tools/weather.py        │ 1     │
├─────────────────────────┼───────┤
│ tools/inspiration.py    │ 1     │
├─────────────────────────┼───────┤
│ tools/time.py           │ 1     │
├─────────────────────────┼───────┤
│ tools/travel.py         │ 1     │
├─────────────────────────┼───────┤
│ tools/shop.py           │ 1     │
├─────────────────────────┼───────┤
│ tools/levelup.py        │ 1     │
├─────────────────────────┼───────┤
│ tools/encounter.py      │ 1     │
├─────────────────────────┼───────┤
│ tools/resources.py      │ 1     │
├─────────────────────────┼───────┤
│ tools/npcs.py           │ 1     │
├─────────────────────────┼───────┤
│ tools/scene.py          │ 3     │
├─────────────────────────┼───────┤
│ tools/relations.py      │ 1     │
├─────────────────────────┼───────┤
│ tools/status.py         │ 3     │
├─────────────────────────┼───────┤
│ tools/homebrew.py       │ 1     │
├─────────────────────────┼───────┤
│ hooks/voice_commands.py │ 3     │
├─────────────────────────┼───────┤
│ hooks/combat_hooks.py   │ 1     │
└─────────────────────────┴───────┘

All old dnd-* plugin names changed to dnd-scaffold. dnd-campaign and dnd-scaffold references left as-is. campaign.py:161 (_campaign_clean_migration) intentionally left reading from
dnd-characters for migration.

6. rest.py — Silent import failure causing rest tools to vanish
- from tools.resources import ... failed because tools are exec'd, not imported as packages
- Entire rest.py module was being skipped from the toolset
- Inlined _resource_load, _resource_save, _resource_auto_setup directly in rest.py
- Both rest_long and rest_short now auto-setup resources if not configured

7. scene.py - Returns Unknown function: scene_add_person, scene_remove_person also silently succeeds when the person isn't even in the scene.
- scene_add_person: Added missing body — gets current scene, adds person to present list, saves, returns success. Also handles idempotently (returns success if already present).

8. hooks/compress.py
- Now iterates all known campaigns and compresses each one's recap independently    
- "recap" now uses word-boundary regex (\brecap\b) instead of substring matching, so only the standalone word recap triggers it — not compress, recapulated, etc.

---
New Features

7. dice.py — Keep/drop notation (kh/kl)
- 4d6kh3 (keep highest 3), 2d20kl1 (keep lowest 1)
- Multi-group support: 4d6kh3+2d6+3
- Updated regex, _parse_notation, _format_roll_result, _handle_multi_group_roll
- Updated tool description and module docstring

8. encounter.py — Fuzzy monster name matching
- "Ancient Red Dragon" now matches "Ancient Dragon (Red)"
- Token-based fuzzy match: strips parentheticals, extracts words, requires all query tokens to be present in monster name
- Falls back to exact/substring match first for specificity

9. rest.py — Auto-populate resources on rest
- rest_long and rest_short now auto-call resource_setup if a character's resources aren't configured, pulling class/level from the character store

10. campaign.py — campaign_quest_delete
- New tool to permanently remove a quest
- Added to TOOLS list and manifest
- campaign_quest now validates status values (rejects delete or any invalid value with a clear error pointing to campaign_quest_delete)
