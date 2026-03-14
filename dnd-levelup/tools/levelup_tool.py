"""
dnd-levelup — XP Tracking & Level-Up Guidance

Solves the two biggest consistency problems for small models:
  1. Nobody knows when a character hits the XP threshold
  2. Nobody knows exactly what to give them when they level up

Tools:
  xp_add        — Award XP to one or all party members
  xp_get        — Check a character's current XP and level status
  xp_check_all  — Show full party XP status, flag anyone ready to level
  levelup_guide — Show exactly what a character gets at their next level
  levelup_apply — Apply a level-up (with choices) to the character sheet
"""

ENABLED = True
EMOJI = '⬆️'
AVAILABLE_FUNCTIONS = [
    'xp_add', 'xp_get', 'xp_check_all', 'levelup_guide', 'levelup_apply'
]

# ── XP Thresholds (total XP needed to reach each level) ─────────────────────
XP_THRESHOLDS = {
    1:  0,
    2:  300,
    3:  900,
    4:  2700,
    5:  6500,
    6:  14000,
    7:  23000,
    8:  34000,
    9:  48000,
    10: 64000,
    11: 85000,
    12: 100000,
    13: 120000,
    14: 140000,
    15: 165000,
    16: 195000,
    17: 225000,
    18: 265000,
    19: 305000,
    20: 355000,
}

def _xp_to_level(xp):
    level = 1
    for lvl, threshold in sorted(XP_THRESHOLDS.items()):
        if xp >= threshold:
            level = lvl
    return min(level, 20)

def _xp_for_next(current_level):
    return XP_THRESHOLDS.get(current_level + 1, None)

# ── Spell Slots by class/level ────────────────────────────────────────────────
# Format: level -> [1st, 2nd, 3rd, 4th, 5th, 6th, 7th, 8th, 9th]
FULL_CASTER_SLOTS = {
    1:  [2,0,0,0,0,0,0,0,0],
    2:  [3,0,0,0,0,0,0,0,0],
    3:  [4,2,0,0,0,0,0,0,0],
    4:  [4,3,0,0,0,0,0,0,0],
    5:  [4,3,2,0,0,0,0,0,0],
    6:  [4,3,3,0,0,0,0,0,0],
    7:  [4,3,3,1,0,0,0,0,0],
    8:  [4,3,3,2,0,0,0,0,0],
    9:  [4,3,3,3,1,0,0,0,0],
    10: [4,3,3,3,2,0,0,0,0],
    11: [4,3,3,3,2,1,0,0,0],
    12: [4,3,3,3,2,1,0,0,0],
    13: [4,3,3,3,2,1,1,0,0],
    14: [4,3,3,3,2,1,1,0,0],
    15: [4,3,3,3,2,1,1,1,0],
    16: [4,3,3,3,2,1,1,1,0],
    17: [4,3,3,3,2,1,1,1,1],
    18: [4,3,3,3,3,1,1,1,1],
    19: [4,3,3,3,3,2,1,1,1],
    20: [4,3,3,3,3,2,2,1,1],
}

HALF_CASTER_SLOTS = {  # Paladin, Ranger
    1:  [0,0,0,0,0,0,0,0,0],
    2:  [2,0,0,0,0,0,0,0,0],
    3:  [3,0,0,0,0,0,0,0,0],
    4:  [3,0,0,0,0,0,0,0,0],
    5:  [4,2,0,0,0,0,0,0,0],
    6:  [4,2,0,0,0,0,0,0,0],
    7:  [4,3,0,0,0,0,0,0,0],
    8:  [4,3,0,0,0,0,0,0,0],
    9:  [4,3,2,0,0,0,0,0,0],
    10: [4,3,2,0,0,0,0,0,0],
    11: [4,3,3,0,0,0,0,0,0],
    12: [4,3,3,0,0,0,0,0,0],
    13: [4,3,3,1,0,0,0,0,0],
    14: [4,3,3,1,0,0,0,0,0],
    15: [4,3,3,2,0,0,0,0,0],
    16: [4,3,3,2,0,0,0,0,0],
    17: [4,3,3,3,1,0,0,0,0],
    18: [4,3,3,3,1,0,0,0,0],
    19: [4,3,3,3,2,0,0,0,0],
    20: [4,3,3,3,2,0,0,0,0],
}

WARLOCK_SLOTS = {  # Pact Magic — slots = 1, level = spell level
    1:  (1, 1), 2: (2, 1), 3: (2, 2), 4: (2, 2), 5: (2, 3),
    6:  (2, 3), 7: (2, 4), 8: (2, 4), 9: (2, 5), 10: (2, 5),
    11: (3, 5), 12: (3, 5), 13: (3, 5), 14: (3, 5), 15: (3, 5),
    16: (3, 5), 17: (4, 5), 18: (4, 5), 19: (4, 5), 20: (4, 5),
}

# ── Proficiency Bonus by level ────────────────────────────────────────────────
def _prof_bonus(level):
    return 2 + (level - 1) // 4

# ── HP dice by class ──────────────────────────────────────────────────────────
HIT_DICE = {
    "barbarian": 12, "fighter": 10, "paladin": 10, "ranger": 10,
    "monk": 8, "bard": 8, "cleric": 8, "druid": 8, "rogue": 8, "warlock": 8,
    "sorcerer": 6, "wizard": 6, "artificer": 8,
}

# ── ASI levels by class ───────────────────────────────────────────────────────
ASI_LEVELS = {
    "fighter":   [4, 6, 8, 10, 12, 14, 16, 19],
    "rogue":     [4, 8, 10, 12, 16, 19],
    "default":   [4, 8, 12, 16, 19],
}

def _get_asi_levels(class_name):
    return ASI_LEVELS.get(class_name.lower(), ASI_LEVELS["default"])

# ── Class features by level ───────────────────────────────────────────────────
CLASS_FEATURES = {
    "barbarian": {
        1:  ["Rage (2/long rest, +2 damage)", "Unarmored Defense (AC = 10 + DEX mod + CON mod)"],
        2:  ["Reckless Attack", "Danger Sense (advantage on DEX saves vs visible threats)"],
        3:  ["Primal Path subclass choice", "Subclass feature"],
        4:  ["ASI or Feat"],
        5:  ["Extra Attack", "Fast Movement (+10 ft speed when not in heavy armor)"],
        6:  ["Subclass feature", "Rage uses: 3/long rest"],
        7:  ["Feral Instinct (advantage on Initiative, can act if surprised while raging)"],
        8:  ["ASI or Feat"],
        9:  ["Brutal Critical (1 extra damage die on crit)", "Rage damage: +3"],
        10: ["Subclass feature"],
        11: ["Relentless Rage (DC 10 CON save to stay at 1 HP when dropped to 0 while raging)"],
        12: ["ASI or Feat", "Rage uses: 4/long rest"],
        13: ["Brutal Critical (2 extra dice)"],
        14: ["Subclass feature"],
        15: ["Persistent Rage (rage only ends if unconscious or you choose to end it)"],
        16: ["ASI or Feat", "Rage damage: +4"],
        17: ["Brutal Critical (3 extra dice)", "Rage uses: 5/long rest"],
        18: ["Indomitable Might (use STR score instead of roll for STR checks if score is higher)"],
        19: ["ASI or Feat"],
        20: ["Primal Champion (+4 STR, +4 CON)", "Unlimited Rages"],
    },
    "bard": {
        1:  ["Spellcasting (full caster, CHA)", "Bardic Inspiration d6 (CHA mod/long rest)", "Choose 2 skills to be proficient in"],
        2:  ["Jack of All Trades (+half proficiency to non-proficient checks)", "Song of Rest (d6)", "Magical Secrets: learn 2 spells from any class list"],
        3:  ["Bard College subclass choice", "Expertise (double proficiency on 2 skills)", "Subclass features"],
        4:  ["ASI or Feat"],
        5:  ["Bardic Inspiration upgrades to d8", "Font of Inspiration (regain Bardic Inspiration on short OR long rest)"],
        6:  ["Subclass feature", "Countercharm (use action to give nearby allies advantage vs frightened/charmed)"],
        7:  [],
        8:  ["ASI or Feat"],
        9:  ["Song of Rest upgrades to d8"],
        10: ["ASI or Feat", "Bardic Inspiration upgrades to d10", "Expertise (2 more skills)", "Magical Secrets: learn 2 more spells from any class list"],
        11: [],
        12: ["ASI or Feat"],
        13: ["Song of Rest upgrades to d10"],
        14: ["Subclass feature", "Magical Secrets: learn 2 more spells from any class list"],
        15: ["Bardic Inspiration upgrades to d12"],
        16: ["ASI or Feat"],
        17: ["Song of Rest upgrades to d12"],
        18: ["Magical Secrets: learn 2 more spells from any class list"],
        19: ["ASI or Feat"],
        20: ["Superior Inspiration (regain 1 Bardic Inspiration on initiative roll if at 0)"],
    },
    "cleric": {
        1:  ["Spellcasting (full caster, WIS)", "Divine Domain subclass choice", "Subclass features (domain spells always prepared)"],
        2:  ["Channel Divinity: Turn Undead (1/short rest)", "Channel Divinity: subclass option"],
        3:  [],
        4:  ["ASI or Feat"],
        5:  ["Destroy Undead (CR 1/2 or lower)"],
        6:  ["Channel Divinity: 2/short rest", "Subclass feature"],
        7:  [],
        8:  ["ASI or Feat", "Subclass feature", "Destroy Undead (CR 1)"],
        9:  [],
        10: ["Divine Intervention (call on your god for aid, 1/week)"],
        11: ["Destroy Undead (CR 2)"],
        12: ["ASI or Feat"],
        13: [],
        14: ["Destroy Undead (CR 3)", "Subclass feature"],
        15: [],
        16: ["ASI or Feat"],
        17: ["Destroy Undead (CR 4)", "Subclass feature"],
        18: ["Channel Divinity: 3/short rest"],
        19: ["ASI or Feat"],
        20: ["Divine Intervention (auto-succeeds now)"],
    },
    "druid": {
        1:  ["Spellcasting (full caster, WIS)", "Druidic language", "Wild Shape: CR 1/4 (no swim/fly)"],
        2:  ["Wild Shape improves: CR 1/2 (swim speed OK)", "Druid Circle subclass choice", "Subclass features"],
        3:  [],
        4:  ["ASI or Feat", "Wild Shape: CR 1 (fly speed OK)"],
        5:  [],
        6:  ["Subclass feature"],
        7:  [],
        8:  ["ASI or Feat", "Wild Shape: CR 2"],
        9:  [],
        10: ["Subclass feature", "Wild Shape: CR 3"],
        11: [],
        12: ["ASI or Feat"],
        13: [],
        14: ["Subclass feature", "Wild Shape: CR 4"],
        15: [],
        16: ["ASI or Feat"],
        17: [],
        18: ["Timeless Body (age 10x slower)", "Beast Spells (cast spells in Wild Shape)"],
        19: ["ASI or Feat"],
        20: ["Archdruid (unlimited Wild Shape uses)"],
    },
    "fighter": {
        1:  ["Fighting Style (choose one)", "Second Wind (heal 1d10+level, 1/short rest)"],
        2:  ["Action Surge (take one extra action, 1/short rest)"],
        3:  ["Martial Archetype subclass choice", "Subclass features"],
        4:  ["ASI or Feat"],
        5:  ["Extra Attack (attack twice per Attack action)"],
        6:  ["ASI or Feat"],
        7:  ["Subclass feature"],
        8:  ["ASI or Feat"],
        9:  ["Indomitable (reroll failed saving throw, 1/long rest)"],
        10: ["Subclass feature"],
        11: ["Extra Attack improves: 3 attacks per Attack action"],
        12: ["ASI or Feat"],
        13: ["Indomitable: 2 uses/long rest"],
        14: ["ASI or Feat"],
        15: ["Subclass feature"],
        16: ["ASI or Feat"],
        17: ["Action Surge: 2/short rest", "Indomitable: 3 uses/long rest"],
        18: ["Subclass feature"],
        19: ["ASI or Feat"],
        20: ["Extra Attack improves: 4 attacks per Attack action"],
    },
    "monk": {
        1:  ["Unarmored Defense (AC = 10 + DEX mod + WIS mod)", "Martial Arts (d4 unarmed, bonus unarmed after Attack action)", "Unarmored Movement (+10 ft speed)"],
        2:  ["Ki points = level (regain on short rest)", "Flurry of Blows (2 ki: 2 bonus unarmed strikes)", "Patient Defense (1 ki: Dodge as bonus action)", "Step of the Wind (1 ki: Disengage or Dash as bonus action, jump distance doubled)"],
        3:  ["Monastic Tradition subclass choice", "Deflect Missiles (reaction: reduce ranged weapon damage by 1d10+DEX+level)", "Subclass features"],
        4:  ["ASI or Feat", "Slow Fall (reaction: reduce fall damage by 5x level)"],
        5:  ["Extra Attack", "Stunning Strike (1 ki after hit: CON save or stunned until end of your next turn)", "Martial Arts upgrades to d6"],
        6:  ["Ki-Empowered Strikes (unarmed strikes = magical)", "Subclass feature", "Unarmored Movement: +15 ft"],
        7:  ["Evasion (DEX save: no damage on success, half on fail)", "Stillness of Mind (action: end charmed or frightened)"],
        8:  ["ASI or Feat"],
        9:  ["Unarmored Movement: +15 ft, can run up walls/across water briefly"],
        10: ["Purity of Body (immune to disease and poison)", "Unarmored Movement: +20 ft"],
        11: ["Subclass feature", "Martial Arts upgrades to d8"],
        12: ["ASI or Feat"],
        13: ["Tongue of Sun and Moon (understand all spoken languages)"],
        14: ["Diamond Soul (proficiency in all saving throws, spend 1 ki to reroll failed save)", "Unarmored Movement: +25 ft"],
        15: ["Timeless Body (age 10x slower, no need for food/water)", "Martial Arts upgrades to d10"],
        16: ["ASI or Feat"],
        17: ["Subclass feature"],
        18: ["Empty Body (4 ki: invisible + resistance to all damage except force, 1 min)", "Unarmored Movement: +30 ft"],
        19: ["ASI or Feat", "Martial Arts upgrades to d12"],
        20: ["Perfect Self (regain 4 ki points on initiative roll if at 0)"],
    },
    "paladin": {
        1:  ["Divine Sense (1+CHA mod/long rest: detect celestials/fiends/undead)", "Lay on Hands (pool = 5×level HP, also cures disease/poison at 5 HP cost)"],
        2:  ["Spellcasting (half caster, CHA)", "Fighting Style (choose one)", "Divine Smite (expend spell slot after hit: 2d8 radiant + 1d8/slot level above 1st, max 5d8; +1d8 vs undead/fiend)"],
        3:  ["Sacred Oath subclass choice", "Divine Health (immune to disease)", "Subclass features (oath spells always prepared)", "Channel Divinity: 1/short rest"],
        4:  ["ASI or Feat"],
        5:  ["Extra Attack", "Improved Divine Smite (+1d8 radiant to all melee weapon hits, no slot needed)"],
        6:  ["Aura of Protection (CHA mod to saving throws for self + allies within 10 ft — minimum +1)"],
        7:  ["Subclass feature"],
        8:  ["ASI or Feat"],
        9:  [],
        10: ["Aura of Courage (immune to frightened + allies within 10 ft immune while you're conscious)"],
        11: ["Improved Divine Smite upgrades to 2d8"],
        12: ["ASI or Feat"],
        13: [],
        14: ["Cleansing Touch (CHA mod/long rest: touch to end one spell on target)"],
        15: ["Subclass feature"],
        16: ["ASI or Feat"],
        17: [],
        18: ["Aura improvements: both auras extend to 30 ft"],
        19: ["ASI or Feat"],
        20: ["Subclass feature (Sacred Oath capstone)"],
    },
    "ranger": {
        1:  ["Favored Enemy (advantage on tracking + recall info, learn language)", "Natural Explorer (expertise in chosen terrain, ignore difficult terrain, extra benefits)"],
        2:  ["Spellcasting (half caster, WIS)", "Fighting Style (choose one)"],
        3:  ["Ranger Archetype subclass choice", "Primeval Awareness (expend spell slot: detect creature types 1 mile, 6 miles in favored terrain)", "Subclass features"],
        4:  ["ASI or Feat"],
        5:  ["Extra Attack"],
        6:  ["Favored Enemy improvement", "Natural Explorer improvement"],
        7:  ["Subclass feature"],
        8:  ["ASI or Feat", "Land's Stride (ignore non-magical difficult terrain, advantage vs plant-based magic)"],
        9:  [],
        10: ["Natural Explorer: 3rd terrain", "Hide in Plain Sight (10 min prep: +10 to Stealth checks while stationary)"],
        11: ["Subclass feature"],
        12: ["ASI or Feat"],
        13: [],
        14: ["Favored Enemy: 3rd enemy", "Vanish (Hide as bonus action, can't be tracked by non-magical means)"],
        15: ["Subclass feature"],
        16: ["ASI or Feat"],
        17: [],
        18: ["Feral Senses (no disadvantage vs invisible, aware of invisible within 30 ft)"],
        19: ["ASI or Feat"],
        20: ["Foe Slayer (once per turn, add WIS mod to attack or damage roll vs favored enemy)"],
    },
    "rogue": {
        1:  ["Expertise (double proficiency on 2 skills)", "Sneak Attack 1d6", "Thieves' Cant (secret language)"],
        2:  ["Cunning Action (bonus action: Dash, Disengage, or Hide)"],
        3:  ["Roguish Archetype subclass choice", "Subclass features", "Sneak Attack 2d6"],
        4:  ["ASI or Feat"],
        5:  ["Uncanny Dodge (reaction: halve damage from attacker you can see)", "Sneak Attack 3d6"],
        6:  ["Expertise (2 more skills)"],
        7:  ["Evasion (DEX save: no damage on success, half on fail)", "Sneak Attack 4d6"],
        8:  ["ASI or Feat"],
        9:  ["Subclass feature", "Sneak Attack 5d6"],
        10: ["ASI or Feat"],
        11: ["Reliable Talent (treat any roll below 10 as 10 on proficient skills)", "Sneak Attack 6d6"],
        12: ["ASI or Feat"],
        13: ["Subclass feature", "Sneak Attack 7d6"],
        14: ["Blindsense (if you can hear, aware of hidden/invisible creatures within 10 ft)"],
        15: ["Slippery Mind (proficiency in WIS saves)", "Sneak Attack 8d6"],
        16: ["ASI or Feat"],
        17: ["Subclass feature", "Sneak Attack 9d6"],
        18: ["Elusive (no creature has advantage on attacks vs you while you're not incapacitated)"],
        19: ["ASI or Feat", "Sneak Attack 10d6"],
        20: ["Stroke of Luck (1/long rest: treat any missed attack as hit, OR any failed ability check as 20)"],
    },
    "sorcerer": {
        1:  ["Spellcasting (full caster, CHA)", "Sorcerous Origin subclass choice", "Subclass features", "4 Sorcery Points at level 2"],
        2:  ["Font of Magic: 2 Sorcery Points (regain on long rest)", "Metamagic: choose 2 options"],
        3:  ["Metamagic: +1 option (3 total)"],
        4:  ["ASI or Feat"],
        5:  [],
        6:  ["Subclass feature"],
        7:  [],
        8:  ["ASI or Feat"],
        9:  [],
        10: ["Metamagic: +1 option (4 total)"],
        11: [],
        12: ["ASI or Feat"],
        13: [],
        14: ["Subclass feature"],
        15: [],
        16: ["ASI or Feat"],
        17: ["Metamagic: +1 option (5 total)"],
        18: ["Subclass feature"],
        19: ["ASI or Feat"],
        20: ["Sorcerous Restoration (regain 4 Sorcery Points on short rest)"],
    },
    "warlock": {
        1:  ["Pact Magic (short-rest slots — see slot table)", "Otherworldly Patron subclass choice", "Subclass features (Expanded Spell List)"],
        2:  ["Eldritch Invocations: choose 2"],
        3:  ["Pact Boon (choose: Pact of the Chain/Blade/Tome)", "Eldritch Invocations: +1 (3 total)"],
        4:  ["ASI or Feat"],
        5:  ["Eldritch Invocations: +1 (4 total)"],
        6:  ["Subclass feature"],
        7:  ["Eldritch Invocations: +1 (5 total)"],
        8:  ["ASI or Feat"],
        9:  ["Eldritch Invocations: +1 (6 total)"],
        10: ["Subclass feature"],
        11: ["Mystic Arcanum: 6th level spell (1/long rest, no slot needed)", "Eldritch Invocations: +1 (7 total)"],
        12: ["ASI or Feat"],
        13: ["Mystic Arcanum: 7th level spell (1/long rest)"],
        14: ["Subclass feature"],
        15: ["Mystic Arcanum: 8th level spell (1/long rest)", "Eldritch Invocations: +1 (8 total)"],
        16: ["ASI or Feat"],
        17: ["Mystic Arcanum: 9th level spell (1/long rest)"],
        18: ["Eldritch Invocations: +1 (9 total)"],
        19: ["ASI or Feat"],
        20: ["Eldritch Master (1/long rest: spend 1 min to regain all Pact Magic slots)"],
    },
    "wizard": {
        1:  ["Spellcasting (full caster, INT)", "Arcane Recovery (short rest: regain spell slots totaling up to half wizard level, rounded up — max 5th level)"],
        2:  ["Arcane Tradition subclass choice", "Subclass features"],
        3:  [],
        4:  ["ASI or Feat"],
        5:  [],
        6:  ["Subclass feature"],
        7:  [],
        8:  ["ASI or Feat"],
        9:  [],
        10: ["Subclass feature"],
        11: [],
        12: ["ASI or Feat"],
        13: [],
        14: ["Subclass feature"],
        15: [],
        16: ["ASI or Feat"],
        17: [],
        18: ["Spell Mastery (choose 1st and 2nd level spell: cast each at will without slots)"],
        19: ["ASI or Feat"],
        20: ["Signature Spells (choose two 3rd level spells: always prepared, cast each once/short rest without slots)"],
    },
    "artificer": {
        1:  ["Magical Tinkering (infuse tiny objects with minor magic)", "Spellcasting (half caster, INT)"],
        2:  ["Infuse Item: 4 infusions known, 2 active at a time"],
        3:  ["Artificer Specialist subclass choice", "The Right Tool for the Job (conjure artisan's tools as action)", "Subclass features"],
        4:  ["ASI or Feat"],
        5:  ["Arcane Jolt (via Arcane Firearm or Steel Defender)", "Extra Attack"],
        6:  ["Tool Expertise (double proficiency on tool checks)", "Subclass feature"],
        7:  [],
        8:  ["ASI or Feat"],
        9:  [],
        10: ["Magic Item Adept (attune to 4 items, craft common/uncommon in half time/cost)", "Subclass feature"],
        11: [],
        12: ["ASI or Feat"],
        13: [],
        14: ["Magic Item Savant (attune to 5 items, ignore class/race/spell/level attunement requirements)"],
        15: ["Subclass feature"],
        16: ["ASI or Feat"],
        17: [],
        18: ["Magic Item Master (attune to 6 items)"],
        19: ["ASI or Feat"],
        20: ["Soul of Artifice (+1 to all saving throws per attuned magic item, reaction: avoid being reduced to 0 HP)"],
    },
}

# Spell cantrips known / spells known / prepared count by class and level
SPELL_NOTES = {
    "bard":     "Knows {cantrips} cantrips, {known} spells (replace 1 when leveling)",
    "ranger":   "Knows {known} spells (replace 1 when leveling) — no cantrips",
    "sorcerer": "Knows {cantrips} cantrips, {known} spells (replace 1 when leveling)",
    "warlock":  "Knows {cantrips} cantrips, {known} spells (replace 1 when leveling)",
    "wizard":   "Knows {cantrips} cantrips; adds 2 spells to spellbook on level-up (can copy more); prepares INT mod + level spells",
    "cleric":   "Knows {cantrips} cantrips; prepares WIS mod + level spells (includes domain spells)",
    "druid":    "Knows {cantrips} cantrips; prepares WIS mod + level spells",
    "paladin":  "No cantrips; prepares CHA mod + half paladin level (rounded down) spells",
    "artificer":"Knows {cantrips} cantrips; prepares INT mod + half artificer level (rounded up) spells",
}

CANTRIPS_KNOWN = {
    "bard":      {1:2,4:3,10:4},
    "cleric":    {1:3,4:4,10:5},
    "druid":     {1:2,4:3,10:4},
    "sorcerer":  {1:4,4:5,10:6},
    "warlock":   {1:2,4:3,10:4},
    "wizard":    {1:3,4:4,10:5},
    "artificer": {1:2,10:3},
}

SPELLS_KNOWN = {  # for known-casters only
    "bard":     {1:4,2:5,3:6,4:7,5:8,6:9,7:10,8:11,9:12,10:14,11:15,13:16,14:18,15:19,17:20,18:22},
    "ranger":   {2:2,3:3,5:4,7:5,9:6,11:7,13:8,15:9,17:10,19:11},
    "sorcerer": {1:2,2:3,3:4,4:5,5:6,6:7,7:8,8:9,9:10,10:11,11:12,12:12,13:13,14:13,15:14,16:14,17:15,18:15,19:15,20:15},
    "warlock":  {1:2,2:3,3:4,4:5,5:6,6:7,7:8,8:9,9:10,10:10,11:11,12:11,13:12,14:12,15:13,16:13,17:14,18:14,19:15,20:15},
}

TOOLS = [
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "xp_add",
            "description": (
                "Award XP to party members after combat or a milestone. "
                "Call this after every combat ends using the XP value from encounter_end_combat. "
                "If the character reaches an XP threshold, returns a level-up notification — "
                "call levelup_guide immediately when this happens."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "xp": {"type": "integer", "description": "Amount of XP to award"},
                    "name": {"type": "string", "description": "Character name, or omit to award to all party members"},
                    "reason": {"type": "string", "description": "Optional — what earned this XP (e.g. 'defeated goblin warband')"}
                },
                "required": ["xp"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "xp_get",
            "description": "Check a character's current XP, level, and how far they are from next level.",
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
            "name": "xp_check_all",
            "description": "Show XP status for all party members. Call at session start to check if anyone is ready to level up.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "levelup_guide",
            "description": (
                "Show exactly what a character gains when leveling up. "
                "Call this the moment a character reaches an XP threshold. "
                "Returns: new features, spell slot changes, HP roll, "
                "whether this is an ASI/feat level, spell choices needed. "
                "Present this info to the player and ask for their choices before calling levelup_apply."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Character name"},
                    "to_level": {"type": "integer", "description": "The level they are advancing TO"}
                },
                "required": ["name", "to_level"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "levelup_apply",
            "description": (
                "Apply a level-up to a character after the player has made their choices. "
                "Updates level, max HP, proficiency bonus, and records new features. "
                "For spell slot changes, the character sheet is updated automatically. "
                "Call this only AFTER presenting choices to the player and receiving their decisions."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Character name"},
                    "to_level": {"type": "integer", "description": "New level"},
                    "hp_roll": {"type": "integer", "description": "HP die roll result (not including CON mod — that is added automatically)"},
                    "asi_choice": {"type": "string", "description": "If ASI level: what the player chose. E.g. 'STR +2' or 'DEX +1, CON +1' or 'Feat: Sharpshooter'"},
                    "new_features": {"type": "string", "description": "Optional notes on subclass choice, spells chosen, etc."}
                },
                "required": ["name", "to_level", "hp_roll"]
            }
        }
    }
]


def _get_state():
    from core.plugin_loader import plugin_loader
    return plugin_loader.get_plugin_state("dnd-levelup")


def _load():
    return _get_state().get("xp_data") or {}


def _save(data):
    _get_state().save("xp_data", data)


def _get_chars():
    """Load character data from dnd-characters plugin."""
    try:
        from core.plugin_loader import plugin_loader
        state = plugin_loader.get_plugin_state("dnd-characters")
        return state.get("characters") or {}
    except Exception:
        return {}


def _save_chars(chars):
    try:
        from core.plugin_loader import plugin_loader
        state = plugin_loader.get_plugin_state("dnd-characters")
        state.save("characters", chars)
    except Exception:
        pass


def _level_status(name, char_xp_data):
    xp      = char_xp_data.get("xp", 0)
    level   = _xp_to_level(xp)
    next_lv = level + 1
    next_xp = _xp_for_next(level)
    if next_xp is None:
        return xp, level, None, None, "MAX LEVEL"
    needed = next_xp - xp
    pct    = int((xp - XP_THRESHOLDS[level]) / (next_xp - XP_THRESHOLDS[level]) * 100)
    return xp, level, next_lv, needed, f"{pct}% to level {next_lv} (need {needed} more XP)"


def _slot_summary(class_name, level):
    cn = class_name.lower()
    if cn == "warlock":
        slots, slot_level = WARLOCK_SLOTS.get(level, (0, 0))
        return f"Pact Magic: {slots} slot(s) at {slot_level}th level (regain on short rest)"
    elif cn in ("paladin", "ranger", "artificer"):
        slots = HALF_CASTER_SLOTS.get(level, [0]*9)
    elif cn in ("bard", "cleric", "druid", "sorcerer", "wizard"):
        slots = FULL_CASTER_SLOTS.get(level, [0]*9)
    else:
        return ""
    filled = [(i+1, s) for i, s in enumerate(slots) if s > 0]
    if not filled:
        return ""
    return "Spell slots: " + ", ".join(f"{s}×{lvl}st/nd/rd/th"[:6+len(str(lvl))] for lvl, s in filled)


def _spell_note(class_name, level):
    cn    = class_name.lower()
    tmpl  = SPELL_NOTES.get(cn, "")
    if not tmpl:
        return ""
    # Cantrips
    cantrips = 0
    for threshold, count in sorted(CANTRIPS_KNOWN.get(cn, {}).items()):
        if level >= threshold:
            cantrips = count
    # Spells known
    known = 0
    for threshold, count in sorted(SPELLS_KNOWN.get(cn, {}).items()):
        if level >= threshold:
            known = count
    return tmpl.format(cantrips=cantrips, known=known)


def execute(function_name, arguments, config):

    # ── xp_add ────────────────────────────────────────────────────────────
    if function_name == "xp_add":
        xp_award = int(arguments.get("xp", 0))
        name     = arguments.get("name", "").strip()
        reason   = arguments.get("reason", "")

        if xp_award <= 0:
            return "Error: XP must be greater than 0.", False

        xp_data  = _load()
        chars    = _get_chars()
        targets  = []

        if name:
            key = next((k for k in chars if k.lower() == name.lower()), None)
            if not key:
                return f"No character named '{name}'. Use xp_check_all to see party.", False
            targets = [key]
        else:
            targets = list(chars.keys())

        if not targets:
            return "No characters found. Create characters first.", False

        level_ups = []
        lines     = [f"Awarded {xp_award} XP" + (f" for: {reason}" if reason else "")]

        for key in targets:
            char = chars[key]
            if not char.get("user_controlled", True) and name == "":
                continue  # skip non-player chars in bulk award
            data      = xp_data.get(key, {"xp": 0})
            old_xp    = data.get("xp", 0)
            old_level = _xp_to_level(old_xp)
            new_xp    = old_xp + xp_award
            new_level = _xp_to_level(new_xp)
            data["xp"]      = new_xp
            xp_data[key]    = data
            lines.append(f"  {key}: {old_xp} → {new_xp} XP")
            if new_level > old_level:
                level_ups.append((key, old_level, new_level))
                lines.append(f"  ⬆️  {key} REACHED LEVEL {new_level}! Call levelup_guide(name='{key}', to_level={new_level}) NOW.")

        _save(xp_data)

        if not level_ups and len(targets) > 0:
            # Show progress for first target
            first = targets[0]
            xp, level, _, needed, status = _level_status(first, xp_data.get(first, {"xp": 0}))
            lines.append(f"\n  {first}: {status}")

        return "\n".join(lines), True

    # ── xp_get ────────────────────────────────────────────────────────────
    elif function_name == "xp_get":
        name  = arguments.get("name", "").strip()
        chars = _get_chars()
        key   = next((k for k in chars if k.lower() == name.lower()), None)
        if not key:
            return f"No character named '{name}'.", False

        xp_data = _load()
        data    = xp_data.get(key, {"xp": 0})
        xp, level, next_lv, needed, status = _level_status(key, data)
        char    = chars[key]
        lines   = [
            f"{key} — Level {level} {char.get('class_name', '')}",
            f"XP: {xp:,}",
            f"Status: {status}",
        ]
        if next_lv:
            lines.append(f"Next level at: {XP_THRESHOLDS[next_lv]:,} XP")
        return "\n".join(lines), True

    # ── xp_check_all ──────────────────────────────────────────────────────
    elif function_name == "xp_check_all":
        chars    = _get_chars()
        xp_data  = _load()

        if not chars:
            return "No characters found.", True

        lines    = ["PARTY XP STATUS:"]
        ready    = []
        for key, char in chars.items():
            data    = xp_data.get(key, {"xp": 0})
            xp, level, next_lv, needed, status = _level_status(key, data)
            class_  = char.get("class_name", "")
            flag    = " ⬆️ READY TO LEVEL UP" if (next_lv and xp >= XP_THRESHOLDS.get(next_lv, 999999)) else ""
            lines.append(f"  {key} (L{level} {class_}): {xp:,} XP — {status}{flag}")
            if flag:
                ready.append((key, next_lv))

        if ready:
            lines.append("\nACTION NEEDED:")
            for name, lv in ready:
                lines.append(f"  Call levelup_guide(name='{name}', to_level={lv})")

        return "\n".join(lines), True

    # ── levelup_guide ─────────────────────────────────────────────────────
    elif function_name == "levelup_guide":
        name     = arguments.get("name", "").strip()
        to_level = int(arguments.get("to_level", 0))

        chars = _get_chars()
        key   = next((k for k in chars if k.lower() == name.lower()), None)
        if not key:
            return f"No character named '{name}'.", False

        char       = chars[key]
        class_name = char.get("class_name", "").lower()
        con_mod    = (char.get("con", 10) - 10) // 2
        hit_die    = HIT_DICE.get(class_name, 8)
        prof       = _prof_bonus(to_level)
        features   = CLASS_FEATURES.get(class_name, {}).get(to_level, [])
        is_asi     = to_level in _get_asi_levels(class_name)
        slots      = _slot_summary(class_name, to_level)
        spell_note = _spell_note(class_name, to_level)

        lines = [
            f"{'='*50}",
            f"LEVEL UP: {key} → Level {to_level}",
            f"Class: {char.get('class_name', 'Unknown')} | Race: {char.get('race', 'Unknown')}",
            f"{'='*50}",
            f"",
            f"HP: Roll 1d{hit_die} + {con_mod} CON (average: {hit_die//2 + 1 + con_mod})",
            f"   Minimum gain: {1 + con_mod} HP  |  Maximum: {hit_die + con_mod} HP",
            f"   Current max HP: {char.get('hp_max', '?')}",
            f"",
            f"Proficiency Bonus: +{prof}",
            f"",
        ]

        if features:
            lines.append("NEW FEATURES:")
            for f in features:
                lines.append(f"  • {f}")
            lines.append("")

        if is_asi:
            lines += [
                "⭐ ASI OR FEAT CHOICE:",
                "  Option A — Ability Score Improvement: +2 to one stat, or +1 to two stats",
                "             (no stat can exceed 20 normally)",
                "  Option B — Feat: choose from PHB feats appropriate to class/build",
                "             Common picks: Alert, Lucky, Sharpshooter (ranged), Great Weapon Master (melee),",
                "             Polearm Master, Sentinel, War Caster (casters), Resilient (saves), Mobile",
                "  → Ask the player which they prefer",
                "",
            ]

        if slots:
            lines.append(f"SPELL SLOTS: {slots}")
        if spell_note:
            lines.append(f"SPELLS: {spell_note}")
        if slots or spell_note:
            lines.append("")

        lines += [
            f"NEXT STEPS:",
            f"  1. Tell the player all of the above",
            f"  2. Ask for their HP roll (or use average: {hit_die//2 + 1 + con_mod})",
            ([f"  3. Get their ASI/Feat choice"] if is_asi else [f"  3. No ASI this level"])[0],
            f"  {'4' if is_asi else '3'}. Call levelup_apply(name='{key}', to_level={to_level}, hp_roll=<roll>{', asi_choice=<choice>' if is_asi else ''})",
        ]

        return "\n".join(lines), True

    # ── levelup_apply ─────────────────────────────────────────────────────
    elif function_name == "levelup_apply":
        name        = arguments.get("name", "").strip()
        to_level    = int(arguments.get("to_level", 0))
        hp_roll     = int(arguments.get("hp_roll", 0))
        asi_choice  = arguments.get("asi_choice", "").strip()
        new_features= arguments.get("new_features", "").strip()

        chars = _get_chars()
        key   = next((k for k in chars if k.lower() == name.lower()), None)
        if not key:
            return f"No character named '{name}'.", False

        char       = chars[key]
        class_name = char.get("class_name", "").lower()
        con_mod    = (char.get("con", 10) - 10) // 2
        hp_gain    = max(1, hp_roll + con_mod)
        old_hp_max = char.get("hp_max", 0)
        new_hp_max = old_hp_max + hp_gain
        prof       = _prof_bonus(to_level)

        char["level"]      = to_level
        char["hp_max"]     = new_hp_max
        char["hp_current"] = char.get("hp_current", old_hp_max) + hp_gain
        char["prof_bonus"] = prof

        # Apply ASI if provided
        if asi_choice and "feat" not in asi_choice.lower():
            parts = [p.strip() for p in asi_choice.replace(",", " ").split() if p.strip()]
            i = 0
            while i < len(parts) - 1:
                stat = parts[i].upper()
                if stat in ("STR", "DEX", "CON", "INT", "WIS", "CHA"):
                    try:
                        delta = int(parts[i+1].replace("+", ""))
                        char[stat.lower()] = min(20, char.get(stat.lower(), 10) + delta)
                        i += 2
                        continue
                    except ValueError:
                        pass
                i += 1

        # Track features
        features_log = char.get("features_log", [])
        gained = CLASS_FEATURES.get(class_name, {}).get(to_level, [])
        entry  = f"L{to_level}: " + ", ".join(gained) if gained else f"L{to_level}: (no new base features)"
        if asi_choice:
            entry += f" | ASI/Feat: {asi_choice}"
        if new_features:
            entry += f" | {new_features}"
        features_log.append(entry)
        char["features_log"] = features_log

        chars[key] = char
        _save_chars(chars)

        lines = [
            f"✅ {key} is now Level {to_level}!",
            f"  HP: {old_hp_max} → {new_hp_max} (rolled {hp_roll} + {con_mod} CON = +{hp_gain})",
            f"  Proficiency Bonus: +{prof}",
        ]
        if asi_choice:
            lines.append(f"  ASI/Feat: {asi_choice}")
        if new_features:
            lines.append(f"  Notes: {new_features}")

        # Spell slot update reminder
        slots = _slot_summary(class_name, to_level)
        if slots:
            lines.append(f"  {slots}")

        lines.append(f"\nCharacter sheet updated. Use character_get('{key}') to confirm.")
        return "\n".join(lines), True

    return f"Unknown function: {function_name}", False
