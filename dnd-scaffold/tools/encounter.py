"""
Wrapped from dnd-encounters for dnd-scaffold

Features:
  - Random encounter generation by environment and party level
  - XP budget calculator (easy/medium/hard/deadly thresholds)
  - Initiative tracker (roll initiative, track turns, HP during combat)
  - Monster stat block lookup for common creatures
"""

import random

ENABLED = True
EMOJI = '⚔️'
AVAILABLE_FUNCTIONS = [
    'encounter_generate',
    'encounter_start_combat',
    'encounter_next_turn',
    'encounter_end_combat',
    'encounter_combat_status',
    'encounter_xp_budget',
    'monster_lookup',
]

# ── Monster Database (CR, XP, type, environment tags) ──────────────────────────
MONSTERS = [

    # ════════════════════════════════════════════════════════
    # CR 0
    # ════════════════════════════════════════════════════════
    {"name": "Rat",               "cr": "0",    "xp": 10,    "type": "beast",      "env": ["dungeon","city","sewer"],
     "hp": "1d4-1", "ac": 10, "speed": 20, "str":2,"dex":11,"con":9,"int":2,"wis":10,"cha":4,
     "attacks": [{"name":"Bite","hit":"+0","dmg":"1 piercing"}]},
    {"name": "Bat",               "cr": "0",    "xp": 10,    "type": "beast",      "env": ["cave","dungeon"],
     "hp": "1d4-1", "ac": 12, "speed": "5ft, fly 30ft", "str":2,"dex":15,"con":8,"int":2,"wis":12,"cha":4,
     "attacks": [{"name":"Bite","hit":"+0","dmg":"1 piercing"}]},
    {"name": "Cat",               "cr": "0",    "xp": 10,    "type": "beast",      "env": ["city","forest"],
     "hp": "1d4-1", "ac": 12, "speed": 40, "str":3,"dex":15,"con":10,"int":3,"wis":12,"cha":7,
     "attacks": [{"name":"Claws","hit":"+0","dmg":"1 slashing"}]},
    {"name": "Frog",              "cr": "0",    "xp": 10,    "type": "beast",      "env": ["swamp","coast"],
     "hp": "1d4-1", "ac": 11, "speed": "20ft, swim 20ft", "str":1,"dex":13,"con":8,"int":1,"wis":8,"cha":3,
     "attacks": [{"name":"Bite","hit":"+0","dmg":"1 piercing"}]},
    {"name": "Crawling Claw",     "cr": "0",    "xp": 10,    "type": "undead",     "env": ["dungeon","crypt"],
     "hp": "1d4-1", "ac": 12, "speed": 20, "str":13,"dex":14,"con":11,"int":5,"wis":10,"cha":4,
     "attacks": [{"name":"Claw","hit":"+3","dmg":"1d4+1 slashing"}]},

    # ════════════════════════════════════════════════════════
    # CR 1/8
    # ════════════════════════════════════════════════════════
    {"name": "Kobold",            "cr": "1/8",  "xp": 25,    "type": "humanoid",   "env": ["cave","dungeon","mountain"],
     "hp": "2d6-2", "ac": 12, "speed": 30, "str":7,"dex":15,"con":9,"int":8,"wis":7,"cha":8,
     "attacks": [{"name":"Dagger","hit":"+4","dmg":"1d4+2 piercing"},{"name":"Sling","hit":"+4","dmg":"1d4+2 bludgeoning","range":"30/120ft"}]},
    {"name": "Bandit",            "cr": "1/8",  "xp": 25,    "type": "humanoid",   "env": ["road","forest","city"],
     "hp": "2d8", "ac": 12, "speed": 30, "str":11,"dex":12,"con":12,"int":10,"wis":10,"cha":10,
     "attacks": [{"name":"Scimitar","hit":"+3","dmg":"1d6+1 slashing"},{"name":"Light Crossbow","hit":"+3","dmg":"1d8+1 piercing","range":"80/320ft"}]},
    {"name": "Guard",             "cr": "1/8",  "xp": 25,    "type": "humanoid",   "env": ["city","dungeon"],
     "hp": "2d8+2", "ac": 16, "speed": 30, "str":13,"dex":12,"con":12,"int":10,"wis":11,"cha":10,
     "attacks": [{"name":"Spear","hit":"+3","dmg":"1d6+1 piercing"}]},
    {"name": "Merfolk",           "cr": "1/8",  "xp": 25,    "type": "humanoid",   "env": ["coast","underwater"],
     "hp": "2d8", "ac": 11, "speed": "10ft, swim 40ft", "str":10,"dex":13,"con":12,"int":11,"wis":11,"cha":12,
     "attacks": [{"name":"Spear","hit":"+2","dmg":"1d6 piercing"}]},
    {"name": "Twig Blight",       "cr": "1/8",  "xp": 25,    "type": "plant",      "env": ["forest","swamp"],
     "hp": "1d6", "ac": 13, "speed": 20, "str":6,"dex":13,"con":12,"int":4,"wis":8,"cha":3,
     "attacks": [{"name":"Claws","hit":"+3","dmg":"1d4+1 piercing"}]},
    {"name": "Stirge",            "cr": "1/8",  "xp": 25,    "type": "beast",      "env": ["cave","dungeon","swamp"],
     "hp": "1d4", "ac": 14, "speed": "10ft, fly 40ft", "str":4,"dex":16,"con":11,"int":2,"wis":8,"cha":6,
     "attacks": [{"name":"Blood Drain","hit":"+5","dmg":"1d4+3 piercing (attach, drain 1d4+3 HP/turn)"}]},

    # ════════════════════════════════════════════════════════
    # CR 1/4
    # ════════════════════════════════════════════════════════
    {"name": "Goblin",            "cr": "1/4",  "xp": 50,    "type": "humanoid",   "env": ["forest","cave","dungeon","mountain"],
     "hp": "2d6", "ac": 15, "speed": 30, "str":8,"dex":14,"con":10,"int":10,"wis":8,"cha":8,
     "attacks": [{"name":"Scimitar","hit":"+4","dmg":"1d6+2 slashing"},{"name":"Shortbow","hit":"+4","dmg":"1d6+2 piercing","range":"80/320ft"}]},
    {"name": "Skeleton",          "cr": "1/4",  "xp": 50,    "type": "undead",     "env": ["dungeon","crypt","graveyard"],
     "hp": "2d8+4", "ac": 13, "speed": 30, "str":10,"dex":14,"con":15,"int":6,"wis":8,"cha":5,
     "attacks": [{"name":"Shortsword","hit":"+4","dmg":"1d6+2 piercing"},{"name":"Shortbow","hit":"+4","dmg":"1d6+2 piercing","range":"80/320ft"}]},
    {"name": "Zombie",            "cr": "1/4",  "xp": 50,    "type": "undead",     "env": ["dungeon","crypt","graveyard"],
     "hp": "3d8+9", "ac": 8,  "speed": 20, "str":13,"dex":6,"con":16,"int":3,"wis":6,"cha":5,
     "attacks": [{"name":"Slam","hit":"+3","dmg":"1d6+1 bludgeoning"}]},
    {"name": "Wolf",              "cr": "1/4",  "xp": 50,    "type": "beast",      "env": ["forest","arctic","mountain","grassland"],
     "hp": "2d8+2", "ac": 13, "speed": 40, "str":12,"dex":15,"con":12,"int":3,"wis":12,"cha":6,
     "attacks": [{"name":"Bite","hit":"+4","dmg":"2d4+2 piercing (DC 11 Str or knocked prone)"}]},
    {"name": "Needle Blight",     "cr": "1/4",  "xp": 50,    "type": "plant",      "env": ["forest","swamp"],
     "hp": "2d8", "ac": 12, "speed": 30, "str":12,"dex":12,"con":13,"int":4,"wis":8,"cha":3,
     "attacks": [{"name":"Claws","hit":"+3","dmg":"1d4+1 piercing"},{"name":"Needles","hit":"+3","dmg":"2d4+1 piercing","range":"30/60ft"}]},
    {"name": "Mud Mephit",        "cr": "1/4",  "xp": 50,    "type": "elemental",  "env": ["swamp","cave","dungeon"],
     "hp": "6d6+6", "ac": 11, "speed": "20ft, fly 20ft, swim 20ft", "str":8,"dex":12,"con":12,"int":9,"wis":11,"cha":7,
     "attacks": [{"name":"Fists","hit":"+3","dmg":"1d6+1 bludgeoning"}]},
    {"name": "Plesiosaurus",      "cr": "2",    "xp": 450,   "type": "beast",      "env": ["coast","underwater"],
     "hp": "8d10+16", "ac": 13, "speed": "20ft, swim 40ft", "str":18,"dex":15,"con":16,"int":2,"wis":12,"cha":5,
     "attacks": [{"name":"Bite","hit":"+6","dmg":"3d6+4 piercing"}]},
    {"name": "Dust Mephit",       "cr": "1/2",  "xp": 100,   "type": "elemental",  "env": ["desert","cave","dungeon"],
     "hp": "5d6+5", "ac": 12, "speed": "30ft, fly 30ft", "str":5,"dex":14,"con":12,"int":9,"wis":11,"cha":10,
     "attacks": [{"name":"Claws","hit":"+4","dmg":"1d4+2 slashing"},{"name":"Blinding Breath","hit":"—","dmg":"DC 10 Dex or blinded (recharge 6)"}]},
    {"name": "Winged Kobold",     "cr": "1/4",  "xp": 50,    "type": "humanoid",   "env": ["cave","dungeon","mountain"],
     "hp": "2d6-2", "ac": 13, "speed": "30ft, fly 30ft", "str":7,"dex":16,"con":9,"int":8,"wis":7,"cha":8,
     "attacks": [{"name":"Dagger","hit":"+5","dmg":"1d4+3 piercing"},{"name":"Drop Rock","hit":"+5","dmg":"1d6+3 bludgeoning (from above)"}]},
    {"name": "Giant Frog",        "cr": "1/4",  "xp": 50,    "type": "beast",      "env": ["swamp","coast","cave"],
     "hp": "4d8", "ac": 11, "speed": "30ft, swim 30ft", "str":12,"dex":13,"con":11,"int":2,"wis":10,"cha":3,
     "attacks": [{"name":"Bite","hit":"+3","dmg":"1d6+1 piercing (DC 11 Str or swallowed if Small)"}]},
    {"name": "Smoke Mephit",      "cr": "1/4",  "xp": 50,    "type": "elemental",  "env": ["volcano","cave"],
     "hp": "4d6+4", "ac": 12, "speed": "30ft, fly 30ft", "str":6,"dex":14,"con":12,"int":10,"wis":10,"cha":11,
     "attacks": [{"name":"Claws","hit":"+4","dmg":"1d4+2 slashing"},{"name":"Cinder Breath","hit":"—","dmg":"DC 10 Dex, 2d4 fire (recharge 6)"}]},

    # ════════════════════════════════════════════════════════
    # CR 1/2
    # ════════════════════════════════════════════════════════
    {"name": "Orc",               "cr": "1/2",  "xp": 100,   "type": "humanoid",   "env": ["forest","mountain","dungeon","grassland"],
     "hp": "2d8+6", "ac": 13, "speed": 30, "str":16,"dex":12,"con":16,"int":7,"wis":11,"cha":10,
     "attacks": [{"name":"Greataxe","hit":"+5","dmg":"1d12+3 slashing"},{"name":"Javelin","hit":"+5","dmg":"1d6+3 piercing","range":"30/120ft"}]},
    {"name": "Gnoll",             "cr": "1/2",  "xp": 100,   "type": "humanoid",   "env": ["grassland","desert","dungeon"],
     "hp": "5d8+5", "ac": 15, "speed": 30, "str":14,"dex":12,"con":11,"int":6,"wis":10,"cha":7,
     "attacks": [{"name":"Bite","hit":"+4","dmg":"1d4+2 piercing"},{"name":"Spear","hit":"+4","dmg":"1d6+2 piercing"}]},
    {"name": "Hobgoblin",         "cr": "1/2",  "xp": 100,   "type": "humanoid",   "env": ["dungeon","forest","mountain"],
     "hp": "2d8+2", "ac": 18, "speed": 30, "str":13,"dex":12,"con":12,"int":10,"wis":10,"cha":9,
     "attacks": [{"name":"Longsword","hit":"+3","dmg":"1d8+1 slashing"},{"name":"Longbow","hit":"+3","dmg":"1d8+1 piercing","range":"150/600ft"}]},
    {"name": "Lizardfolk",        "cr": "1/2",  "xp": 100,   "type": "humanoid",   "env": ["swamp","coast","dungeon"],
     "hp": "4d8+4", "ac": 15, "speed": "30ft, swim 30ft", "str":15,"dex":10,"con":13,"int":7,"wis":12,"cha":7,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Bite","hit":"+4","dmg":"1d6+2 piercing"},{"name":"Javelin","hit":"+4","dmg":"1d6+2 piercing","range":"30/120ft"}]},
    {"name": "Magmin",            "cr": "1/2",  "xp": 100,   "type": "elemental",  "env": ["volcano","dungeon"],
     "hp": "5d6+5", "ac": 14, "speed": 30, "str":7,"dex":15,"con":12,"int":8,"wis":11,"cha":10,
     "attacks": [{"name":"Touch","hit":"+4","dmg":"2d6 fire (ignites target)"}]},
    {"name": "Vine Blight",       "cr": "1/2",  "xp": 100,   "type": "plant",      "env": ["forest","swamp"],
     "hp": "4d8+8", "ac": 12, "speed": 10, "str":15,"dex":8,"con":14,"int":5,"wis":10,"cha":3,
     "attacks": [{"name":"Constrict","hit":"+4","dmg":"2d6+2 bludgeoning (grappled DC 12)"}]},
    {"name": "Scout",             "cr": "1/2",  "xp": 100,   "type": "humanoid",   "env": ["forest","grassland","mountain"],
     "hp": "3d8+3", "ac": 13, "speed": 30, "str":11,"dex":14,"con":12,"int":11,"wis":13,"cha":11,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Shortsword","hit":"+4","dmg":"1d6+2 piercing"},{"name":"Longbow","hit":"+4","dmg":"1d8+2 piercing","range":"150/600ft"}]},
    {"name": "Shadow",            "cr": "1/2",  "xp": 100,   "type": "undead",     "env": ["dungeon","crypt","graveyard"],
     "hp": "3d8+9", "ac": 12, "speed": 40, "str":6,"dex":14,"con":13,"int":6,"wis":10,"cha":8,
     "attacks": [{"name":"Strength Drain","hit":"+4","dmg":"2d6+2 necrotic (STR -1d4, die if STR 0)"}]},
    {"name": "Cockatrice",        "cr": "1/2",  "xp": 100,   "type": "monstrosity","env": ["grassland","forest"],
     "hp": "6d6+6", "ac": 11, "speed": "20ft, fly 40ft", "str":6,"dex":12,"con":12,"int":2,"wis":13,"cha":5,
     "attacks": [{"name":"Beak","hit":"+3","dmg":"1d4+1 piercing (DC 11 Con or petrified in 24 hrs)"}]},
    {"name": "Pirate",            "cr": "1/2",  "xp": 100,   "type": "humanoid",   "env": ["coast","city","ship"],
     "hp": "3d8+3", "ac": 12, "speed": 30, "str":12,"dex":14,"con":12,"int":10,"wis":10,"cha":11,
     "attacks": [{"name":"Scimitar","hit":"+4","dmg":"1d6+2 slashing"},{"name":"Handaxe","hit":"+4","dmg":"1d6+2 slashing","range":"20/60ft"}]},

    # ════════════════════════════════════════════════════════
    # CR 1
    # ════════════════════════════════════════════════════════
    {"name": "Giant Spider",      "cr": "1",    "xp": 200,   "type": "beast",      "env": ["forest","cave","dungeon"],
     "hp": "4d10+4", "ac": 14, "speed": 30, "str":14,"dex":16,"con":12,"int":2,"wis":11,"cha":4,
     "attacks": [{"name":"Bite","hit":"+5","dmg":"1d8+3 piercing + 2d8 poison (DC 11 Con)"}]},
    {"name": "Ghoul",             "cr": "1",    "xp": 200,   "type": "undead",     "env": ["dungeon","crypt","graveyard"],
     "hp": "5d8", "ac": 12, "speed": 30, "str":13,"dex":15,"con":10,"int":7,"wis":10,"cha":6,
     "attacks": [{"name":"Bite","hit":"+2","dmg":"2d6 piercing"},{"name":"Claws","hit":"+4","dmg":"2d4+2 slashing (DC 10 Con or paralyzed)"}]},
    {"name": "Goblin Boss",       "cr": "1",    "xp": 200,   "type": "humanoid",   "env": ["forest","cave","dungeon"],
     "hp": "6d6+6", "ac": 17, "speed": 30, "str":10,"dex":14,"con":10,"int":10,"wis":8,"cha":10,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Scimitar","hit":"+4","dmg":"1d6+2 slashing"}]},
    {"name": "Dryad",             "cr": "1",    "xp": 200,   "type": "fey",        "env": ["forest"],
     "hp": "5d8+5", "ac": 11, "speed": 30, "str":10,"dex":12,"con":11,"int":14,"wis":15,"cha":18,
     "attacks": [{"name":"Club","hit":"+2","dmg":"1d4 bludgeoning"},{"name":"Fey Charm","hit":"—","dmg":"DC 14 Wis or charmed"}]},
    {"name": "Specter",           "cr": "1",    "xp": 200,   "type": "undead",     "env": ["dungeon","crypt","city"],
     "hp": "5d8", "ac": 12, "speed": "0ft, fly 50ft (hover)", "str":1,"dex":14,"con":11,"int":10,"wis":10,"cha":11,
     "attacks": [{"name":"Life Drain","hit":"+4","dmg":"3d6 necrotic (DC 10 Con or max HP reduced)"}]},
    {"name": "Fire Snake",        "cr": "1",    "xp": 200,   "type": "elemental",  "env": ["volcano","dungeon"],
     "hp": "4d8+4", "ac": 14, "speed": 30, "str":12,"dex":14,"con":12,"int":3,"wis":10,"cha":6,
     "attacks": [{"name":"Bite","hit":"+3","dmg":"1d4+1 piercing + 1d6 fire"},{"name":"Tail","hit":"+3","dmg":"1d6+1 bludgeoning + 1d6 fire"}]},
    {"name": "Harpy",             "cr": "1",    "xp": 200,   "type": "monstrosity","env": ["coast","mountain","grassland"],
     "hp": "7d8", "ac": 11, "speed": "20ft, fly 40ft", "str":12,"dex":13,"con":10,"int":7,"wis":10,"cha":13,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Claws","hit":"+3","dmg":"2d4+1 slashing"},{"name":"Luring Song","hit":"—","dmg":"DC 11 Wis or charmed and incapacitated"}]},
    {"name": "Imp",               "cr": "1",    "xp": 200,   "type": "fiend",      "env": ["dungeon","city"],
     "hp": "3d4+3", "ac": 13, "speed": "20ft, fly 40ft", "str":6,"dex":17,"con":13,"int":11,"wis":12,"cha":14,
     "attacks": [{"name":"Sting","hit":"+5","dmg":"1d4+3 piercing + 3d4 poison (DC 11 Con)"}]},
    {"name": "Kuo-Toa",           "cr": "1/4",  "xp": 50,    "type": "humanoid",   "env": ["underwater","dungeon","cave"],
     "hp": "4d8+4", "ac": 13, "speed": "30ft, swim 30ft", "str":13,"dex":10,"con":11,"int":11,"wis":10,"cha":8,
     "attacks": [{"name":"Bite","hit":"+3","dmg":"1d4+1 piercing"},{"name":"Pincer Staff","hit":"+3","dmg":"1d6+1 bludgeoning (grapple DC 14)"}]},
    {"name": "Faerie Dragon (young)","cr":"1",  "xp": 200,   "type": "dragon",     "env": ["forest"],
     "hp": "4d4+4", "ac": 13, "speed": "10ft, fly 60ft", "str":3,"dex":20,"con":13,"int":14,"wis":12,"cha":16,
     "attacks": [{"name":"Bite","hit":"+7","dmg":"1 piercing"},{"name":"Euphoria Breath","hit":"—","dmg":"DC 11 Wis or incapacitated 1 min (recharge 5-6)"}]},

    # ════════════════════════════════════════════════════════
    # CR 2
    # ════════════════════════════════════════════════════════
    {"name": "Bandit Captain",    "cr": "2",    "xp": 450,   "type": "humanoid",   "env": ["road","forest","city"],
     "hp": "10d8+20", "ac": 15, "speed": 30, "str":15,"dex":16,"con":14,"int":14,"wis":11,"cha":14,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Scimitar","hit":"+5","dmg":"1d6+3 slashing"},{"name":"Dagger","hit":"+5","dmg":"1d4+3 piercing"}]},
    {"name": "Ogre",              "cr": "2",    "xp": 450,   "type": "giant",      "env": ["mountain","dungeon","forest"],
     "hp": "7d10+21", "ac": 11, "speed": 40, "str":19,"dex":8,"con":16,"int":5,"wis":7,"cha":7,
     "attacks": [{"name":"Greatclub","hit":"+6","dmg":"2d8+4 bludgeoning"},{"name":"Javelin","hit":"+6","dmg":"2d6+4 piercing","range":"30/120ft"}]},
    {"name": "Gelatinous Cube",   "cr": "2",    "xp": 450,   "type": "ooze",       "env": ["dungeon"],
     "hp": "8d10+40", "ac": 6,  "speed": 15, "str":14,"dex":3,"con":20,"int":1,"wis":6,"cha":1,
     "attacks": [{"name":"Pseudopod","hit":"+4","dmg":"3d6 acid"},{"name":"Engulf","hit":"—","dmg":"DC 12 Dex or engulfed — 6d6 acid/turn"}]},
    {"name": "Mimic",             "cr": "2",    "xp": 450,   "type": "monstrosity","env": ["dungeon"],
     "hp": "9d8+18", "ac": 12, "speed": 15, "str":17,"dex":12,"con":15,"int":5,"wis":13,"cha":8,
     "attacks": [{"name":"Pseudopod","hit":"+5","dmg":"1d8+3 bludgeoning"},{"name":"Bite","hit":"+5","dmg":"1d8+3 piercing + 1d8 acid"}]},
    {"name": "Ghast",             "cr": "2",    "xp": 450,   "type": "undead",     "env": ["dungeon","crypt"],
     "hp": "8d8", "ac": 13, "speed": 30, "str":16,"dex":17,"con":10,"int":11,"wis":10,"cha":8,
     "attacks": [{"name":"Bite","hit":"+3","dmg":"2d8+1 piercing"},{"name":"Claws","hit":"+5","dmg":"2d6+3 slashing (DC 10 Con or paralyzed)"}]},
    {"name": "Ettercap",          "cr": "2",    "xp": 450,   "type": "monstrosity","env": ["forest","cave"],
     "hp": "6d8+6", "ac": 13, "speed": "30ft, climb 30ft", "str":14,"dex":15,"con":13,"int":7,"wis":12,"cha":8,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Bite","hit":"+4","dmg":"1d8+2 piercing + 2d8 poison"},{"name":"Claws","hit":"+4","dmg":"2d4+2 slashing"}]},
    {"name": "Sahuagin",          "cr": "1/2",  "xp": 100,   "type": "humanoid",   "env": ["coast","underwater"],
     "hp": "4d8+4", "ac": 12, "speed": "30ft, swim 40ft", "str":13,"dex":11,"con":12,"int":12,"wis":13,"cha":9,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Bite","hit":"+3","dmg":"1d4+1 piercing"},{"name":"Claws","hit":"+3","dmg":"1d4+1 slashing"}]},
    {"name": "Gargoyle",          "cr": "2",    "xp": 450,   "type": "elemental",  "env": ["dungeon","mountain","city"],
     "hp": "7d8+21", "ac": 15, "speed": "30ft, fly 60ft", "str":15,"dex":11,"con":16,"int":6,"wis":11,"cha":7,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Claws","hit":"+4","dmg":"2d6+2 slashing"},{"name":"Bite","hit":"+4","dmg":"2d4+2 piercing"}]},
    {"name": "Sea Hag",           "cr": "2",    "xp": 450,   "type": "fey",        "env": ["coast","underwater","swamp"],
     "hp": "7d8+21", "ac": 14, "speed": "30ft, swim 40ft", "str":16,"dex":13,"con":16,"int":12,"wis":12,"cha":13,
     "attacks": [{"name":"Claws","hit":"+5","dmg":"2d6+3 slashing"},{"name":"Death Glare","hit":"—","dmg":"DC 11 Wis or frightened until 0 HP"}]},
    {"name": "Cult Fanatic",      "cr": "2",    "xp": 450,   "type": "humanoid",   "env": ["dungeon","city","crypt"],
     "hp": "6d8+6", "ac": 13, "speed": 30, "str":11,"dex":14,"con":12,"int":10,"wis":13,"cha":14,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Dagger","hit":"+4","dmg":"1d4+2 piercing"},{"name":"Spellcasting","hit":"—","dmg":"Hold Person, Spiritual Weapon, Blindness/Deafness"}]},
    {"name": "Peryton",           "cr": "2",    "xp": 450,   "type": "monstrosity","env": ["mountain","forest"],
     "hp": "7d8+7", "ac": 13, "speed": "20ft, fly 60ft", "str":16,"dex":12,"con":13,"int":9,"wis":12,"cha":10,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Gore","hit":"+5","dmg":"1d8+3 piercing"},{"name":"Talons","hit":"+5","dmg":"2d4+3 piercing"}]},
    {"name": "Ankheg",            "cr": "2",    "xp": 450,   "type": "monstrosity","env": ["grassland","forest"],
     "hp": "6d10+6", "ac": 14, "speed": "30ft, burrow 10ft", "str":17,"dex":11,"con":13,"int":1,"wis":13,"cha":6,
     "attacks": [{"name":"Bite","hit":"+5","dmg":"2d6+3 piercing + 1d6 acid (grapple DC 13)"},{"name":"Acid Spray","hit":"—","dmg":"3d6 acid (DC 13 Dex half, recharge 6)"}]},
    {"name": "Will-o-Wisp",       "cr": "2",    "xp": 450,   "type": "undead",     "env": ["swamp","graveyard"],
     "hp": "9d4", "ac": 19, "speed": "0ft, fly 50ft (hover)", "str":1,"dex":28,"con":10,"int":13,"wis":14,"cha":11,
     "attacks": [{"name":"Shock","hit":"+4","dmg":"2d8 lightning"},{"name":"Consume Life","hit":"—","dmg":"Regain 10d4 HP from creature at 0 HP nearby"}]},

    # ════════════════════════════════════════════════════════
    # CR 3
    # ════════════════════════════════════════════════════════
    {"name": "Owlbear",           "cr": "3",    "xp": 700,   "type": "monstrosity","env": ["forest"],
     "hp": "7d10+21", "ac": 13, "speed": 40, "str":20,"dex":12,"con":17,"int":3,"wis":12,"cha":7,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Claws","hit":"+7","dmg":"2d8+5 slashing"},{"name":"Beak","hit":"+7","dmg":"1d10+5 piercing"}]},
    {"name": "Manticore",         "cr": "3",    "xp": 700,   "type": "monstrosity","env": ["mountain","grassland","dungeon"],
     "hp": "8d10+24", "ac": 14, "speed": "30ft, fly 50ft", "str":17,"dex":16,"con":17,"int":7,"wis":12,"cha":8,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Bite","hit":"+5","dmg":"1d8+3 piercing"},{"name":"Tail Spike","hit":"+5","dmg":"2d6+3 piercing","range":"100/200ft"}]},
    {"name": "Werewolf",          "cr": "3",    "xp": 700,   "type": "humanoid",   "env": ["forest","mountain"],
     "hp": "9d8+18", "ac": 11, "speed": "30ft (40ft wolf)", "str":15,"dex":13,"con":14,"int":10,"wis":11,"cha":10,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Bite","hit":"+4","dmg":"2d6+2 piercing (DC 12 Con or lycanthropy)"},{"name":"Claws","hit":"+4","dmg":"2d4+2 slashing"}]},
    {"name": "Doppelganger",      "cr": "3",    "xp": 700,   "type": "monstrosity","env": ["dungeon","city"],
     "hp": "8d8", "ac": 14, "speed": 30, "str":11,"dex":18,"con":14,"int":11,"wis":12,"cha":14,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Slam","hit":"+6","dmg":"2d6+4 bludgeoning"},{"name":"Read Thoughts","hit":"—","dmg":"DC 13 Wis or read surface thoughts"}]},
    {"name": "Green Hag",         "cr": "3",    "xp": 700,   "type": "fey",        "env": ["forest","swamp"],
     "hp": "9d8+27", "ac": 14, "speed": 30, "str":18,"dex":12,"con":16,"int":13,"wis":14,"cha":14,
     "attacks": [{"name":"Claws","hit":"+6","dmg":"2d6+4 slashing"},{"name":"Illusory Appearance","hit":"—","dmg":"DC 17 Investigation to see through"},{"name":"Invisible Passage","hit":"—","dmg":"Turn invisible at will"}]},
    {"name": "Hell Hound",        "cr": "3",    "xp": 700,   "type": "fiend",      "env": ["dungeon","volcano"],
     "hp": "7d8+21", "ac": 15, "speed": 50, "str":17,"dex":12,"con":14,"int":6,"wis":13,"cha":6,
     "attacks": [{"name":"Bite","hit":"+5","dmg":"1d8+3 piercing + 2d6 fire"},{"name":"Fire Breath","hit":"—","dmg":"6d6 fire (DC 12 Dex half, 15ft cone, recharge 5-6)"}]},
    {"name": "Basilisk",          "cr": "3",    "xp": 700,   "type": "monstrosity","env": ["cave","dungeon","mountain"],
     "hp": "8d8+24", "ac": 15, "speed": 20, "str":16,"dex":8,"con":15,"int":2,"wis":8,"cha":7,
     "attacks": [{"name":"Bite","hit":"+5","dmg":"2d6+3 piercing + 2d6 poison"},{"name":"Petrifying Gaze","hit":"—","dmg":"DC 12 Con or restrained → petrified"}]},
    {"name": "Bugbear Chief",     "cr": "3",    "xp": 700,   "type": "humanoid",   "env": ["dungeon","forest","cave"],
     "hp": "9d8+18", "ac": 17, "speed": 30, "str":17,"dex":14,"con":14,"int":11,"wis":11,"cha":13,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Morningstar","hit":"+5","dmg":"2d8+3 piercing"}]},
    {"name": "Giant Constrictor", "cr": "2",    "xp": 450,   "type": "beast",      "env": ["swamp","forest","coast"],
     "hp": "8d12+16", "ac": 12, "speed": "30ft, swim 30ft", "str":19,"dex":14,"con":12,"int":1,"wis":10,"cha":3,
     "attacks": [{"name":"Bite","hit":"+6","dmg":"2d6+4 piercing"},{"name":"Constrict","hit":"+6","dmg":"2d8+4 bludgeoning (grapple DC 16, restrained)"}]},
    {"name": "Wight",             "cr": "3",    "xp": 700,   "type": "undead",     "env": ["dungeon","crypt","graveyard"],
     "hp": "9d8+18", "ac": 14, "speed": 30, "str":15,"dex":14,"con":16,"int":10,"wis":13,"cha":15,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Longsword","hit":"+4","dmg":"1d8+2 slashing"},{"name":"Life Drain","hit":"+4","dmg":"1d6+2 necrotic (max HP reduced)"}]},
    {"name": "Phase Spider",      "cr": "3",    "xp": 700,   "type": "monstrosity","env": ["dungeon","cave","forest"],
     "hp": "5d10+10", "ac": 13, "speed": "30ft, climb 30ft", "str":15,"dex":15,"con":10,"int":6,"wis":10,"cha":6,
     "attacks": [{"name":"Bite","hit":"+4","dmg":"1d10+2 piercing + 4d6 poison (DC 11 Con)"},{"name":"Ethereal Jaunt","hit":"—","dmg":"Phase in/out of Ethereal Plane"}]},

    # ════════════════════════════════════════════════════════
    # CR 4
    # ════════════════════════════════════════════════════════
    {"name": "Banshee",           "cr": "4",    "xp": 1100,  "type": "undead",     "env": ["dungeon","crypt","graveyard","forest"],
     "hp": "13d8", "ac": 12, "speed": "0ft, fly 40ft (hover)", "str":1,"dex":14,"con":10,"int":12,"wis":11,"cha":17,
     "attacks": [{"name":"Corrupting Touch","hit":"+4","dmg":"3d6 necrotic"},{"name":"Wail","hit":"—","dmg":"DC 13 Con or drop to 0 HP (1/day, not undead/constructs)"},{"name":"Horrifying Visage","hit":"—","dmg":"DC 13 Wis or frightened 1 min"}]},
    {"name": "Ettin",             "cr": "4",    "xp": 1100,  "type": "giant",      "env": ["mountain","dungeon","forest"],
     "hp": "10d10+20", "ac": 12, "speed": 40, "str":21,"dex":8,"con":15,"int":8,"wis":10,"cha":8,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Morningstar","hit":"+7","dmg":"2d8+5 bludgeoning"},{"name":"Battleaxe","hit":"+7","dmg":"2d8+5 slashing"}]},
    {"name": "Incubus/Succubus",  "cr": "4",    "xp": 1100,  "type": "fiend",      "env": ["dungeon","city"],
     "hp": "8d8+8", "ac": 13, "speed": "30ft, fly 60ft", "str":8,"dex":17,"con":13,"int":15,"wis":12,"cha":20,
     "attacks": [{"name":"Claw","hit":"+5","dmg":"1d6+3 slashing"},{"name":"Charm","hit":"—","dmg":"DC 15 Wis or charmed"},{"name":"Draining Kiss","hit":"—","dmg":"5d6+5 psychic (DC 15 Con)"}]},
    {"name": "Flameskull",        "cr": "4",    "xp": 1100,  "type": "undead",     "env": ["dungeon","crypt"],
     "hp": "9d4", "ac": 13, "speed": "0ft, fly 40ft (hover)", "str":1,"dex":17,"con":14,"int":16,"wis":10,"cha":11,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Fire Ray","hit":"+5","dmg":"3d6 fire","range":"30ft"},{"name":"Fireball (3/day)","hit":"—","dmg":"8d6 fire (DC 13 Dex half)"}]},
    {"name": "Wereboar",          "cr": "4",    "xp": 1100,  "type": "humanoid",   "env": ["forest","grassland","mountain"],
     "hp": "12d8+24", "ac": 10, "speed": "30ft (40ft boar)", "str":17,"dex":10,"con":15,"int":10,"wis":11,"cha":8,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Maul","hit":"+5","dmg":"2d6+3 bludgeoning"},{"name":"Tusks","hit":"+5","dmg":"2d6+3 slashing (DC 14 Con or lycanthropy)"}]},
    {"name": "Chuul",             "cr": "4",    "xp": 1100,  "type": "aberration", "env": ["swamp","dungeon","underwater"],
     "hp": "11d10+22", "ac": 16, "speed": "30ft, swim 30ft", "str":19,"dex":10,"con":16,"int":5,"wis":11,"cha":5,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Pincer","hit":"+6","dmg":"2d6+4 bludgeoning (grapple DC 14)"},{"name":"Tentacles","hit":"—","dmg":"DC 13 Con or poisoned and paralyzed (if grappled)"}]},

    # ════════════════════════════════════════════════════════
    # CR 5
    # ════════════════════════════════════════════════════════
    {"name": "Troll",             "cr": "5",    "xp": 1800,  "type": "giant",      "env": ["forest","swamp","mountain","cave"],
     "hp": "8d10+40", "ac": 15, "speed": 30, "str":18,"dex":13,"con":20,"int":7,"wis":9,"cha":7,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Bite","hit":"+7","dmg":"1d6+4 piercing"},{"name":"Claw","hit":"+7","dmg":"2d6+4 slashing"}]},
    {"name": "Vampire Spawn",     "cr": "5",    "xp": 1800,  "type": "undead",     "env": ["dungeon","crypt"],
     "hp": "11d8+22", "ac": 15, "speed": 30, "str":16,"dex":16,"con":16,"int":11,"wis":10,"cha":12,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Claws","hit":"+6","dmg":"2d4+3 slashing"},{"name":"Bite","hit":"+6","dmg":"1d6+3 piercing + 3d6 necrotic"}]},
    {"name": "Wraith",            "cr": "5",    "xp": 1800,  "type": "undead",     "env": ["dungeon","crypt","graveyard"],
     "hp": "9d8", "ac": 13, "speed": "0ft, fly 60ft (hover)", "str":6,"dex":16,"con":16,"int":12,"wis":14,"cha":15,
     "attacks": [{"name":"Life Drain","hit":"+6","dmg":"4d8+3 necrotic (max HP reduced, DC 14 Con)"},{"name":"Create Specter","hit":"—","dmg":"Slain humanoid rises as specter"}]},
    {"name": "Bulette",           "cr": "5",    "xp": 1800,  "type": "monstrosity","env": ["grassland","dungeon"],
     "hp": "9d10+45", "ac": 17, "speed": "40ft, burrow 40ft", "str":19,"dex":11,"con":21,"int":2,"wis":10,"cha":5,
     "attacks": [{"name":"Bite","hit":"+7","dmg":"4d12+4 piercing"},{"name":"Deadly Leap","hit":"—","dmg":"3d6+4 bludgeoning + 3d6+4 slashing (DC 16 Str or knocked prone)"}]},
    {"name": "Roper",             "cr": "5",    "xp": 1800,  "type": "monstrosity","env": ["cave","dungeon"],
     "hp": "10d10+30", "ac": 20, "speed": 10, "str":18,"dex":8,"con":17,"int":7,"wis":16,"cha":6,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"1 bite + up to 6 tendrils"},{"name":"Tendril","hit":"+7","dmg":"Grapple (DC 15 Str, pull 25ft toward bite)"},{"name":"Bite","hit":"+7","dmg":"4d8+4 piercing"}]},
    {"name": "Xorn",              "cr": "5",    "xp": 1800,  "type": "elemental",  "env": ["cave","dungeon","mountain"],
     "hp": "7d8+21", "ac": 19, "speed": "20ft, burrow 20ft", "str":17,"dex":10,"con":22,"int":11,"wis":10,"cha":11,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Claws","hit":"+6","dmg":"1d6+3 slashing"},{"name":"Bite","hit":"+6","dmg":"3d6+3 piercing"}]},
    {"name": "Giant Crocodile",   "cr": "5",    "xp": 1800,  "type": "beast",      "env": ["swamp","coast"],
     "hp": "9d12+36", "ac": 14, "speed": "30ft, swim 50ft", "str":21,"dex":9,"con":17,"int":2,"wis":10,"cha":7,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Bite","hit":"+8","dmg":"3d10+5 piercing (grapple DC 16)"},{"name":"Tail","hit":"+8","dmg":"2d6+5 bludgeoning (DC 16 Str or knocked prone)"}]},

    # ════════════════════════════════════════════════════════
    # CR 6
    # ════════════════════════════════════════════════════════
    {"name": "Wyvern",            "cr": "6",    "xp": 2300,  "type": "dragon",     "env": ["mountain","coast","grassland"],
     "hp": "13d10+52", "ac": 13, "speed": "20ft, fly 80ft", "str":19,"dex":10,"con":16,"int":5,"wis":12,"cha":6,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Bite","hit":"+7","dmg":"2d6+4 piercing"},{"name":"Stinger","hit":"+7","dmg":"2d6+4 piercing + 7d6 poison (DC 15 Con)"}]},
    {"name": "Medusa",            "cr": "6",    "xp": 2300,  "type": "monstrosity","env": ["dungeon","cave"],
     "hp": "11d8+22", "ac": 15, "speed": 30, "str":10,"dex":15,"con":16,"int":12,"wis":13,"cha":15,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks (snake hair + shortbow)"},{"name":"Snake Hair","hit":"+5","dmg":"1d4+3 piercing + 4d6 poison (DC 14 Con)"},{"name":"Petrifying Gaze","hit":"—","dmg":"DC 14 Con: restrained → petrified"}]},
    {"name": "Cyclops",           "cr": "6",    "xp": 2300,  "type": "giant",      "env": ["mountain","coast","grassland"],
     "hp": "11d10+44", "ac": 14, "speed": 30, "str":22,"dex":11,"con":17,"int":8,"wis":6,"cha":10,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Greatclub","hit":"+9","dmg":"3d8+6 bludgeoning"},{"name":"Rock","hit":"+9","dmg":"3d10+6 bludgeoning","range":"30/120ft"}]},
    {"name": "Hobgoblin Warlord", "cr": "6",    "xp": 2300,  "type": "humanoid",   "env": ["dungeon","forest","mountain"],
     "hp": "11d8+22", "ac": 20, "speed": 30, "str":16,"dex":14,"con":14,"int":14,"wis":11,"cha":15,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Longsword","hit":"+5","dmg":"1d8+3 slashing"},{"name":"Shield Bash","hit":"+5","dmg":"1d4+3 bludgeoning (DC 13 Str or knocked prone)"}]},
    {"name": "Chimera",           "cr": "6",    "xp": 2300,  "type": "monstrosity","env": ["mountain","grassland","dungeon"],
     "hp": "12d10+36", "ac": 14, "speed": "30ft, fly 60ft", "str":19,"dex":11,"con":19,"int":3,"wis":14,"cha":10,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Horns","hit":"+6","dmg":"2d10+4 bludgeoning"},{"name":"Claws","hit":"+6","dmg":"2d6+4 slashing"},{"name":"Fire Breath","hit":"—","dmg":"7d8 fire (DC 13 Dex half, 15ft cone, recharge 5-6)"}]},

    # ════════════════════════════════════════════════════════
    # CR 7 – 9
    # ════════════════════════════════════════════════════════
    {"name": "Oni",               "cr": "7",    "xp": 2900,  "type": "giant",      "env": ["dungeon","mountain","city"],
     "hp": "13d10+26", "ac": 16, "speed": "30ft, fly 30ft", "str":19,"dex":11,"con":16,"int":14,"wis":12,"cha":15,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Glaive","hit":"+7","dmg":"2d10+4 slashing + 2d6 necrotic"},{"name":"Cone of Cold (recharge 6)","hit":"—","dmg":"8d8 cold (DC 14 Con half)"}]},
    {"name": "Shield Guardian",   "cr": "7",    "xp": 2900,  "type": "construct",  "env": ["dungeon","city"],
     "hp": "15d10+45", "ac": 17, "speed": 30, "str":18,"dex":8,"con":18,"int":7,"wis":10,"cha":3,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Fist","hit":"+7","dmg":"2d6+4 bludgeoning"}]},
    {"name": "Yuan-Ti Abomination","cr":"7",    "xp": 2900,  "type": "monstrosity","env": ["dungeon","desert","jungle"],
     "hp": "12d10+36", "ac": 15, "speed": "40ft, swim 40ft", "str":19,"dex":16,"con":15,"int":17,"wis":15,"cha":18,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Bite","hit":"+7","dmg":"1d6+4 piercing + 4d6 poison"},{"name":"Constrict","hit":"+7","dmg":"2d6+4 bludgeoning (grapple DC 15)"},{"name":"Spit Poison","hit":"+6","dmg":"4d8 poison (DC 13 Con half)","range":"30ft"}]},
    {"name": "Frost Giant",       "cr": "8",    "xp": 3900,  "type": "giant",      "env": ["arctic","mountain"],
     "hp": "14d12+56", "ac": 15, "speed": 40, "str":23,"dex":9,"con":21,"int":9,"wis":10,"cha":12,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Greataxe","hit":"+9","dmg":"3d12+6 slashing"},{"name":"Rock","hit":"+9","dmg":"4d10+6 bludgeoning","range":"60/240ft"}]},
    {"name": "Cloud Giant",       "cr": "9",    "xp": 5000,  "type": "giant",      "env": ["mountain","sky"],
     "hp": "16d12+80", "ac": 14, "speed": 40, "str":27,"dex":10,"con":22,"int":12,"wis":16,"cha":16,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Morningstar","hit":"+12","dmg":"3d8+8 bludgeoning"},{"name":"Rock","hit":"+12","dmg":"4d10+8 bludgeoning","range":"60/240ft"}]},
    {"name": "Abominable Yeti",   "cr": "9",    "xp": 5000,  "type": "monstrosity","env": ["arctic","mountain"],
     "hp": "9d12+45", "ac": 15, "speed": 40, "str":24,"dex":10,"con":22,"int":9,"wis":13,"cha":9,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Claw","hit":"+11","dmg":"2d6+7 slashing + 3d6 cold"},{"name":"Cold Breath","hit":"—","dmg":"10d6 cold (DC 18 Con half, 30ft cone, recharge 5-6)"}]},
    {"name": "Treant",            "cr": "9",    "xp": 5000,  "type": "plant",      "env": ["forest"],
     "hp": "12d12+60", "ac": 16, "speed": 30, "str":23,"dex":8,"con":21,"int":12,"wis":16,"cha":12,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Slam","hit":"+10","dmg":"3d6+6 bludgeoning"},{"name":"Rock","hit":"+10","dmg":"4d10+6 bludgeoning","range":"60/180ft"},{"name":"Animate Trees (1/day)","hit":"—","dmg":"Up to 2 trees animate as allies"}]},

    # ════════════════════════════════════════════════════════
    # CR 10 – 13
    # ════════════════════════════════════════════════════════
    {"name": "Young Dragon (Red)","cr": "10",   "xp": 5900,  "type": "dragon",     "env": ["mountain","volcano"],
     "hp": "17d10+85", "ac": 18, "speed": "40ft, fly 80ft", "str":23,"dex":10,"con":21,"int":14,"wis":11,"cha":19,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Bite","hit":"+10","dmg":"2d10+6 piercing"},{"name":"Fire Breath","hit":"—","dmg":"16d6 fire (DC 18 Dex half, 30ft cone, recharge 5-6)"}]},
    {"name": "Young Dragon (Blue)","cr":"9",    "xp": 5000,  "type": "dragon",     "env": ["desert","grassland"],
     "hp": "16d10+80", "ac": 18, "speed": "40ft, fly 80ft, burrow 20ft", "str":21,"dex":10,"con":19,"int":14,"wis":13,"cha":17,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Bite","hit":"+9","dmg":"2d10+5 piercing + 1d10 lightning"},{"name":"Lightning Breath","hit":"—","dmg":"12d10 lightning (DC 17 Dex half, 90ft line, recharge 5-6)"}]},
    {"name": "Young Dragon (Green)","cr":"8",   "xp": 3900,  "type": "dragon",     "env": ["forest"],
     "hp": "16d10+48", "ac": 18, "speed": "40ft, fly 80ft, swim 40ft", "str":19,"dex":12,"con":17,"int":16,"wis":13,"cha":15,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Bite","hit":"+7","dmg":"2d10+4 piercing + 2d6 poison"},{"name":"Poison Breath","hit":"—","dmg":"12d6 poison (DC 16 Con half, 30ft cone, recharge 5-6)"}]},
    {"name": "Aboleth",           "cr": "10",   "xp": 5900,  "type": "aberration", "env": ["underwater","dungeon","cave"],
     "hp": "18d10+36", "ac": 17, "speed": "10ft, swim 40ft", "str":21,"dex":9,"con":15,"int":18,"wis":15,"cha":18,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Tentacle","hit":"+9","dmg":"2d6+5 bludgeoning (DC 14 Con or diseased — breathe water only in 1d4 hrs)"},{"name":"Enslave (3/day)","hit":"—","dmg":"DC 14 Wis or charmed until cured"}]},
    {"name": "Death Knight",      "cr": "17",   "xp": 18000, "type": "undead",     "env": ["dungeon","crypt"],
     "hp": "19d8+95", "ac": 20, "speed": 30, "str":20,"dex":11,"con":20,"int":12,"wis":16,"cha":18,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Longsword","hit":"+11","dmg":"1d8+5 slashing + 18 necrotic"},{"name":"Hellfire Orb (1/day)","hit":"—","dmg":"10d6 fire + 10d6 necrotic (DC 20 Dex half, 20ft radius)"}]},
    {"name": "Beholder",          "cr": "13",   "xp": 10000, "type": "aberration", "env": ["dungeon","underdark"],
     "hp": "19d10+95", "ac": 18, "speed": "0ft, fly 20ft (hover)", "str":10,"dex":14,"con":18,"int":17,"wis":15,"cha":17,
     "attacks": [{"name":"Eye Rays","hit":"—","dmg":"3 random rays — charm, paralyze, fear, slow, wound, telekinesis, sleep, petrify, disintegrate, or death (DC 16)"},{"name":"Antimagic Cone","hit":"—","dmg":"Central eye suppresses magic in 150ft cone"}]},
    {"name": "Mind Flayer",       "cr": "7",    "xp": 2900,  "type": "aberration", "env": ["dungeon","underdark"],
     "hp": "10d8+20", "ac": 15, "speed": 30, "str":11,"dex":12,"con":12,"int":19,"wis":17,"cha":17,
     "attacks": [{"name":"Tentacles","hit":"+7","dmg":"2d10+4 psychic (DC 15 Int or stunned)"},{"name":"Extract Brain","hit":"+7","dmg":"10d10 piercing (instantly kills stunned creature)"},{"name":"Mind Blast (recharge 5-6)","hit":"—","dmg":"5d8+4 psychic (DC 15 Int or stunned 1 min, 60ft cone)"}]},
    {"name": "Vampire",           "cr": "13",   "xp": 10000, "type": "undead",     "env": ["dungeon","crypt","city"],
     "hp": "17d8+68", "ac": 16, "speed": 30, "str":18,"dex":18,"con":18,"int":17,"wis":15,"cha":18,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Unarmed Strike","hit":"+9","dmg":"1d8+4 bludgeoning + grapple"},{"name":"Bite","hit":"+9","dmg":"1d6+4 piercing + 3d6 necrotic (regain HP equal to necrotic dealt)"},{"name":"Charm","hit":"—","dmg":"DC 17 Wis or charmed"}]},

    # ════════════════════════════════════════════════════════
    # CR 14 – 21+
    # ════════════════════════════════════════════════════════
    {"name": "Adult Dragon (Red)", "cr":"17",   "xp": 18000, "type": "dragon",     "env": ["mountain","volcano"],
     "hp": "19d12+133", "ac": 19, "speed": "40ft, fly 80ft", "str":27,"dex":10,"con":25,"int":16,"wis":13,"cha":21,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Bite","hit":"+14","dmg":"2d10+8 piercing"},{"name":"Claw","hit":"+14","dmg":"2d6+8 slashing"},{"name":"Fire Breath","hit":"—","dmg":"18d6 fire (DC 21 Dex half, 60ft cone, recharge 5-6)"}]},
    {"name": "Adult Dragon (Blue)","cr":"16",   "xp": 15000, "type": "dragon",     "env": ["desert","grassland"],
     "hp": "18d12+108", "ac": 19, "speed": "40ft, fly 80ft, burrow 30ft", "str":25,"dex":10,"con":23,"int":16,"wis":15,"cha":19,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Bite","hit":"+12","dmg":"2d10+7 piercing + 2d10 lightning"},{"name":"Lightning Breath","hit":"—","dmg":"16d10 lightning (DC 23 Dex half, 120ft line, recharge 5-6)"}]},
    {"name": "Lich",              "cr": "21",   "xp": 33000, "type": "undead",     "env": ["dungeon"],
     "hp": "18d8+90", "ac": 17, "speed": 30, "str":11,"dex":16,"con":16,"int":20,"wis":14,"cha":16,
     "attacks": [{"name":"Paralyzing Touch","hit":"+12","dmg":"3d6 cold (DC 18 Con or paralyzed 1 min)"},{"name":"Spellcasting","hit":"—","dmg":"9th-level wizard spells — Disintegrate, Power Word Kill, Time Stop"},{"name":"Legendary Actions","hit":"—","dmg":"Cantrip, Paralyzing Touch, or Frightening Gaze"}]},
    {"name": "Ancient Dragon (Red)","cr":"24",  "xp": 62000, "type": "dragon",     "env": ["mountain","volcano"],
     "hp": "28d20+252", "ac": 22, "speed": "40ft, fly 80ft", "str":30,"dex":10,"con":29,"int":18,"wis":15,"cha":23,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks + Frightful Presence"},{"name":"Bite","hit":"+17","dmg":"2d10+10 piercing"},{"name":"Claw","hit":"+17","dmg":"2d6+10 slashing"},{"name":"Fire Breath","hit":"—","dmg":"26d6 fire (DC 24 Dex half, 90ft cone, recharge 5-6)"}]},
    {"name": "Tarrasque",         "cr": "30",   "xp": 155000,"type": "monstrosity","env": ["any"],
     "hp": "33d20+330", "ac": 25, "speed": 40, "str":30,"dex":11,"con":30,"int":3,"wis":11,"cha":11,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"5 attacks"},{"name":"Bite","hit":"+19","dmg":"4d12+10 piercing"},{"name":"Claw","hit":"+19","dmg":"4d8+10 slashing"},{"name":"Horns","hit":"+19","dmg":"4d10+10 piercing"},{"name":"Tail","hit":"+19","dmg":"4d6+10 bludgeoning (DC 20 Str or knocked prone)"},{"name":"Reflective Carapace","hit":"—","dmg":"Spells of 7th level or lower are reflected back"}]},

    # ════════════════════════════════════════════════════════
    # BEASTS (continued)
    # ════════════════════════════════════════════════════════
    {"name": "Brown Bear",          "cr": "1",    "xp": 200,   "type": "beast",      "env": ["forest","mountain","arctic"],
     "hp": "4d10+8", "ac": 11, "speed": 40, "str":19,"dex":10,"con":16,"int":2,"wis":13,"cha":7,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Bite","hit":"+5","dmg":"1d8+4 piercing"},{"name":"Claws","hit":"+5","dmg":"2d6+4 slashing"}]},
    {"name": "Black Bear",          "cr": "1/2",  "xp": 100,   "type": "beast",      "env": ["forest","mountain"],
     "hp": "3d8+6", "ac": 11, "speed": 40, "str":15,"dex":10,"con":14,"int":2,"wis":12,"cha":7,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Bite","hit":"+3","dmg":"1d6+2 piercing"},{"name":"Claws","hit":"+3","dmg":"2d4+2 slashing"}]},
    {"name": "Polar Bear",          "cr": "2",    "xp": 450,   "type": "beast",      "env": ["arctic"],
     "hp": "6d10+18", "ac": 12, "speed": 40, "str":20,"dex":10,"con":16,"int":2,"wis":13,"cha":7,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Bite","hit":"+7","dmg":"1d8+5 piercing"},{"name":"Claws","hit":"+7","dmg":"2d6+5 slashing"}]},
    {"name": "Giant Eagle",         "cr": "1",    "xp": 200,   "type": "beast",      "env": ["mountain","grassland","coast"],
     "hp": "4d10+4", "ac": 13, "speed": "10ft, fly 80ft", "str":16,"dex":17,"con":13,"int":8,"wis":14,"cha":10,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Beak","hit":"+5","dmg":"1d6+3 piercing"},{"name":"Talons","hit":"+5","dmg":"2d6+3 slashing"}]},
    {"name": "Giant Elk",           "cr": "2",    "xp": 450,   "type": "beast",      "env": ["forest","grassland","arctic"],
     "hp": "5d12+10", "ac": 14, "speed": 60, "str":19,"dex":16,"con":14,"int":7,"wis":14,"cha":10,
     "attacks": [{"name":"Ram","hit":"+6","dmg":"2d6+4 bludgeoning"},{"name":"Hooves","hit":"+6","dmg":"4d8+4 bludgeoning (DC 14 Str or knocked prone)"}]},
    {"name": "Giant Hyena",         "cr": "1",    "xp": 200,   "type": "beast",      "env": ["grassland","desert"],
     "hp": "6d10+6", "ac": 12, "speed": 50, "str":16,"dex":14,"con":14,"int":2,"wis":12,"cha":7,
     "attacks": [{"name":"Bite","hit":"+5","dmg":"2d6+3 piercing"}]},
    {"name": "Giant Toad",          "cr": "1",    "xp": 200,   "type": "beast",      "env": ["swamp","cave","dungeon"],
     "hp": "6d10+6", "ac": 11, "speed": "20ft, swim 40ft", "str":15,"dex":13,"con":13,"int":2,"wis":10,"cha":3,
     "attacks": [{"name":"Bite","hit":"+4","dmg":"1d10+2 piercing + 5 poison (grapple DC 13, swallow Small or smaller)"}]},
    {"name": "Giant Vulture",       "cr": "1",    "xp": 200,   "type": "beast",      "env": ["grassland","desert","mountain"],
     "hp": "5d10+10", "ac": 10, "speed": "10ft, fly 60ft", "str":15,"dex":10,"con":15,"int":6,"wis":12,"cha":7,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Beak","hit":"+4","dmg":"2d6+2 piercing"},{"name":"Talons","hit":"+4","dmg":"2d6+2 slashing"}]},
    {"name": "Giant Scorpion",      "cr": "3",    "xp": 700,   "type": "beast",      "env": ["desert","cave","dungeon"],
     "hp": "7d10+21", "ac": 15, "speed": 40, "str":15,"dex":13,"con":15,"int":1,"wis":9,"cha":3,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Claw","hit":"+4","dmg":"1d8+2 bludgeoning (grapple DC 12)"},{"name":"Sting","hit":"+4","dmg":"1d10+2 piercing + 4d10 poison (DC 12 Con)"}]},
    {"name": "Giant Octopus",       "cr": "1",    "xp": 200,   "type": "beast",      "env": ["coast","underwater"],
     "hp": "5d10+5", "ac": 11, "speed": "10ft, swim 60ft", "str":17,"dex":13,"con":13,"int":4,"wis":10,"cha":4,
     "attacks": [{"name":"Tentacles","hit":"+5","dmg":"2d6+3 bludgeoning (grapple DC 16, restrained, blinded)"},{"name":"Ink Cloud (recharge 6)","hit":"—","dmg":"20ft radius blind in water, Dash as bonus action"}]},
    {"name": "Giant Shark",         "cr": "5",    "xp": 1800,  "type": "beast",      "env": ["underwater","coast"],
     "hp": "11d12+44", "ac": 13, "speed": "0ft, swim 50ft", "str":23,"dex":11,"con":21,"int":1,"wis":10,"cha":5,
     "attacks": [{"name":"Bite","hit":"+9","dmg":"3d10+6 piercing"}]},
    {"name": "Mammoth",             "cr": "6",    "xp": 2300,  "type": "beast",      "env": ["arctic","grassland"],
     "hp": "11d12+55", "ac": 13, "speed": 40, "str":24,"dex":9,"con":21,"int":3,"wis":11,"cha":6,
     "attacks": [{"name":"Gore","hit":"+10","dmg":"4d8+7 piercing"},{"name":"Stomp","hit":"+10","dmg":"4d10+7 bludgeoning (DC 18 Str or knocked prone, prone targets only)"}]},
    {"name": "Griffon",             "cr": "2",    "xp": 450,   "type": "beast",      "env": ["mountain","grassland"],
     "hp": "7d10+21", "ac": 12, "speed": "30ft, fly 80ft", "str":18,"dex":15,"con":16,"int":2,"wis":13,"cha":8,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Beak","hit":"+6","dmg":"1d8+4 piercing"},{"name":"Talons","hit":"+6","dmg":"2d6+4 slashing (grapple DC 15)"}]},
    {"name": "Hippogriff",          "cr": "1",    "xp": 200,   "type": "beast",      "env": ["mountain","grassland","forest"],
     "hp": "5d10+10", "ac": 11, "speed": "40ft, fly 60ft", "str":17,"dex":13,"con":13,"int":2,"wis":10,"cha":8,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Beak","hit":"+5","dmg":"1d10+3 piercing"},{"name":"Claws","hit":"+5","dmg":"2d6+3 slashing"}]},
    {"name": "Pegasus",             "cr": "2",    "xp": 450,   "type": "celestial",  "env": ["mountain","grassland","sky"],
     "hp": "7d10+21", "ac": 12, "speed": "60ft, fly 90ft", "str":18,"dex":15,"con":16,"int":10,"wis":15,"cha":13,
     "attacks": [{"name":"Hooves","hit":"+6","dmg":"2d6+4 bludgeoning"}]},
    {"name": "Roc",                 "cr": "11",   "xp": 7200,  "type": "beast",      "env": ["mountain","coast","sky"],
     "hp": "16d20+112", "ac": 15, "speed": "20ft, fly 120ft", "str":28,"dex":10,"con":20,"int":3,"wis":10,"cha":9,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Beak","hit":"+13","dmg":"4d8+9 piercing"},{"name":"Talons","hit":"+13","dmg":"4d6+9 slashing (grapple DC 19)"}]},
    {"name": "Triceratops",         "cr": "5",    "xp": 1800,  "type": "beast",      "env": ["grassland"],
     "hp": "11d12+55", "ac": 13, "speed": 50, "str":22,"dex":9,"con":17,"int":2,"wis":11,"cha":5,
     "attacks": [{"name":"Gore","hit":"+9","dmg":"4d8+6 piercing"},{"name":"Stomp","hit":"+9","dmg":"3d10+6 bludgeoning (DC 20 Str or knocked prone)"}]},
    {"name": "Tyrannosaurus Rex",   "cr": "8",    "xp": 3900,  "type": "beast",      "env": ["grassland","forest"],
     "hp": "13d12+52", "ac": 13, "speed": 50, "str":25,"dex":10,"con":19,"int":2,"wis":12,"cha":9,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Bite","hit":"+10","dmg":"4d12+7 piercing (grapple DC 17)"},{"name":"Tail","hit":"+10","dmg":"3d8+7 bludgeoning (DC 19 Str or knocked prone)"}]},
    {"name": "Swarm of Rats",       "cr": "1/4",  "xp": 50,    "type": "beast",      "env": ["dungeon","city","sewer"],
     "hp": "4d8", "ac": 10, "speed": 30, "str":9,"dex":11,"con":9,"int":2,"wis":10,"cha":3,
     "attacks": [{"name":"Bites","hit":"+2","dmg":"2d6 piercing (or 1d6 if half HP)"}]},
    {"name": "Swarm of Bats",       "cr": "1/4",  "xp": 50,    "type": "beast",      "env": ["cave","dungeon"],
     "hp": "4d8", "ac": 12, "speed": "0ft, fly 30ft", "str":5,"dex":15,"con":10,"int":2,"wis":12,"cha":4,
     "attacks": [{"name":"Bites","hit":"+4","dmg":"2d4 piercing (or 1d4 if half HP)"}]},
    {"name": "Swarm of Insects",    "cr": "1/2",  "xp": 100,   "type": "beast",      "env": ["forest","swamp","dungeon"],
     "hp": "5d8", "ac": 12, "speed": "20ft, climb 20ft", "str":3,"dex":13,"con":10,"int":1,"wis":7,"cha":1,
     "attacks": [{"name":"Bites","hit":"+3","dmg":"2d10 piercing (or 1d10 if half HP)"}]},
    {"name": "Swarm of Poisonous Snakes","cr":"2","xp": 450,   "type": "beast",      "env": ["swamp","forest","dungeon"],
     "hp": "5d8", "ac": 14, "speed": 30, "str":8,"dex":18,"con":11,"int":1,"wis":10,"cha":3,
     "attacks": [{"name":"Bites","hit":"+6","dmg":"2d6 piercing + 3d6 poison (DC 10 Con, or 1d6+1d6 if half HP)"}]},

    # ════════════════════════════════════════════════════════
    # CONSTRUCTS
    # ════════════════════════════════════════════════════════
    {"name": "Animated Armor",      "cr": "1",    "xp": 200,   "type": "construct",  "env": ["dungeon","city"],
     "hp": "6d8+6", "ac": 18, "speed": 25, "str":14,"dex":11,"con":13,"int":1,"wis":3,"cha":1,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Slam","hit":"+4","dmg":"1d6+2 bludgeoning"}]},
    {"name": "Flying Sword",        "cr": "1/4",  "xp": 50,    "type": "construct",  "env": ["dungeon","city"],
     "hp": "2d6", "ac": 17, "speed": "0ft, fly 50ft (hover)", "str":12,"dex":15,"con":11,"int":1,"wis":5,"cha":1,
     "attacks": [{"name":"Longsword","hit":"+3","dmg":"1d8+1 slashing"}]},
    {"name": "Rug of Smothering",   "cr": "2",    "xp": 450,   "type": "construct",  "env": ["dungeon","city"],
     "hp": "6d10+6", "ac": 12, "speed": 10, "str":17,"dex":14,"con":10,"int":1,"wis":3,"cha":1,
     "attacks": [{"name":"Smother","hit":"+5","dmg":"2d6+3 bludgeoning (grapple DC 13, restrained, blinded, suffocating)"}]},
    {"name": "Flesh Golem",         "cr": "5",    "xp": 1800,  "type": "construct",  "env": ["dungeon","city"],
     "hp": "11d8+44", "ac": 9,  "speed": 30, "str":19,"dex":9,"con":18,"int":6,"wis":10,"cha":5,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Slam","hit":"+7","dmg":"2d8+4 bludgeoning"}]},
    {"name": "Clay Golem",          "cr": "9",    "xp": 5000,  "type": "construct",  "env": ["dungeon","city"],
     "hp": "14d10+56", "ac": 14, "speed": 20, "str":20,"dex":9,"con":18,"int":3,"wis":8,"cha":1,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Slam","hit":"+8","dmg":"2d10+5 bludgeoning (DC 15 Con or cursed — max HP reduced by damage)"}]},
    {"name": "Stone Golem",         "cr": "10",   "xp": 5900,  "type": "construct",  "env": ["dungeon","city","mountain"],
     "hp": "17d10+85", "ac": 17, "speed": 30, "str":22,"dex":9,"con":20,"int":3,"wis":11,"cha":1,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Slam","hit":"+10","dmg":"3d8+6 bludgeoning"},{"name":"Slow (recharge 5-6)","hit":"—","dmg":"DC 17 Wis or slowed — half speed, no reactions, 1 attack only"}]},
    {"name": "Iron Golem",          "cr": "16",   "xp": 15000, "type": "construct",  "env": ["dungeon","city"],
     "hp": "20d10+100", "ac": 20, "speed": 30, "str":24,"dex":9,"con":20,"int":3,"wis":11,"cha":1,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Slam","hit":"+13","dmg":"3d8+7 bludgeoning"},{"name":"Sword","hit":"+13","dmg":"3d10+7 slashing"},{"name":"Poison Breath (recharge 6)","hit":"—","dmg":"10d8 poison (DC 19 Con half, 15ft cone)"}]},
    {"name": "Helmed Horror",       "cr": "4",    "xp": 1100,  "type": "construct",  "env": ["dungeon","city"],
     "hp": "12d8+12", "ac": 20, "speed": "30ft, fly 30ft", "str":18,"dex":13,"con":16,"int":10,"wis":10,"cha":10,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Longsword","hit":"+7","dmg":"1d8+4 slashing"}]},
    {"name": "Scarecrow",           "cr": "1",    "xp": 200,   "type": "construct",  "env": ["grassland","forest","dungeon"],
     "hp": "5d8", "ac": 11, "speed": 30, "str":11,"dex":13,"con":11,"int":10,"wis":10,"cha":13,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Claws","hit":"+3","dmg":"2d4+1 slashing"},{"name":"Terrifying Glare","hit":"—","dmg":"DC 11 Wis or frightened until end of next turn"}]},

    # ════════════════════════════════════════════════════════
    # DEMONS
    # ════════════════════════════════════════════════════════
    {"name": "Quasit",              "cr": "1",    "xp": 200,   "type": "fiend",      "env": ["dungeon","city"],
     "hp": "3d4+3", "ac": 13, "speed": 40, "str":5,"dex":17,"con":10,"int":7,"wis":10,"cha":10,
     "attacks": [{"name":"Claws","hit":"+4","dmg":"1d4+3 piercing + 1d4 poison (DC 10 Con or poisoned 1 min)"},{"name":"Scare (1/day)","hit":"—","dmg":"DC 10 Wis or frightened 1 min"}]},
    {"name": "Dretch",              "cr": "1/4",  "xp": 50,    "type": "fiend",      "env": ["dungeon"],
     "hp": "4d6+4", "ac": 11, "speed": 20, "str":11,"dex":11,"con":12,"int":5,"wis":8,"cha":3,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Bite","hit":"+2","dmg":"1d6 piercing"},{"name":"Claws","hit":"+2","dmg":"2d4 slashing"},{"name":"Fetid Cloud (1/day)","hit":"—","dmg":"DC 11 Con or poisoned 1 min (10ft radius)"}]},
    {"name": "Shadow Demon",        "cr": "4",    "xp": 1100,  "type": "fiend",      "env": ["dungeon","crypt"],
     "hp": "3d8", "ac": 13, "speed": "30ft, fly 30ft", "str":1,"dex":17,"con":11,"int":12,"wis":10,"cha":13,
     "attacks": [{"name":"Claws","hit":"+5","dmg":"2d6+3 psychic (disadvantage in bright light)"}]},
    {"name": "Vrock",               "cr": "6",    "xp": 2300,  "type": "fiend",      "env": ["dungeon"],
     "hp": "11d10+44", "ac": 15, "speed": "40ft, fly 60ft", "str":17,"dex":15,"con":18,"int":8,"wis":13,"cha":8,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Talons","hit":"+6","dmg":"2d10+3 slashing"},{"name":"Beak","hit":"+6","dmg":"2d6+3 piercing"},{"name":"Spores (recharge 6)","hit":"—","dmg":"DC 14 Con or poisoned 1 min (10ft radius)"},{"name":"Stunning Screech (1/day)","hit":"—","dmg":"DC 14 Con or stunned until end of next turn"}]},
    {"name": "Hezrou",              "cr": "8",    "xp": 3900,  "type": "fiend",      "env": ["dungeon","swamp"],
     "hp": "13d10+52", "ac": 16, "speed": 30, "str":19,"dex":17,"con":20,"int":5,"wis":12,"cha":13,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Bite","hit":"+7","dmg":"2d10+4 piercing"},{"name":"Claws","hit":"+7","dmg":"2d6+4 slashing"},{"name":"Stench","hit":"—","dmg":"DC 14 Con or poisoned while within 10ft"}]},
    {"name": "Glabrezu",            "cr": "9",    "xp": 5000,  "type": "fiend",      "env": ["dungeon"],
     "hp": "15d10+75", "ac": 17, "speed": 40, "str":20,"dex":15,"con":21,"int":19,"wis":17,"cha":16,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"4 attacks (2 pincers + 2 fists, or 2 pincers + 1 spell)"},{"name":"Pincer","hit":"+9","dmg":"2d10+5 bludgeoning (grapple DC 15)"},{"name":"Fist","hit":"+9","dmg":"2d6+5 bludgeoning"},{"name":"Confusion (1/day)","hit":"—","dmg":"As spell, DC 17 Wis"}]},
    {"name": "Nalfeshnee",          "cr": "13",   "xp": 10000, "type": "fiend",      "env": ["dungeon"],
     "hp": "16d10+96", "ac": 18, "speed": "20ft, fly 30ft", "str":21,"dex":10,"con":22,"int":19,"wis":12,"cha":15,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Bite","hit":"+9","dmg":"2d10+5 piercing"},{"name":"Claw","hit":"+9","dmg":"2d6+5 slashing"},{"name":"Horror Nimbus (1/day)","hit":"—","dmg":"DC 15 Wis or frightened 1 min (spectral light, 15ft radius)"}]},
    {"name": "Marilith",            "cr": "16",   "xp": 15000, "type": "fiend",      "env": ["dungeon"],
     "hp": "18d10+90", "ac": 18, "speed": 40, "str":18,"dex":20,"con":20,"int":18,"wis":16,"cha":20,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"7 attacks (6 longswords + 1 tail)"},{"name":"Longsword","hit":"+9","dmg":"2d8+5 slashing"},{"name":"Tail","hit":"+9","dmg":"2d10+5 bludgeoning (grapple DC 19)"},{"name":"Teleport","hit":"—","dmg":"Teleport up to 120ft to unoccupied space"}]},
    {"name": "Balor",               "cr": "19",   "xp": 22000, "type": "fiend",      "env": ["dungeon"],
     "hp": "21d10+147", "ac": 19, "speed": "40ft, fly 80ft", "str":26,"dex":15,"con":22,"int":20,"wis":16,"cha":22,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Longsword","hit":"+14","dmg":"3d8+8 slashing + 3d8 lightning"},{"name":"Whip","hit":"+14","dmg":"2d6+8 slashing + 3d6 fire (reach 30ft, DC 20 Str or pulled 25ft)"},{"name":"Fire Aura","hit":"—","dmg":"10 fire to anything that starts turn within 5ft or hits in melee"},{"name":"Death Throes","hit":"—","dmg":"On death: explode, 20d6 fire (DC 20 Dex half, 30ft radius)"}]},
    {"name": "Demogorgon",          "cr": "26",   "xp": 90000, "type": "fiend",      "env": ["dungeon","underdark"],
     "hp": "22d12+154", "ac": 22, "speed": "50ft, swim 50ft", "str":29,"dex":14,"con":26,"int":20,"wis":17,"cha":25,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 tentacle attacks"},{"name":"Tentacle","hit":"+17","dmg":"4d6+9 bludgeoning (DC 23 Con or max HP reduced by damage)"},{"name":"Gaze","hit":"—","dmg":"DC 23 Wis or Confused/Frightened/Stunned (random)"},{"name":"Legendary Actions","hit":"—","dmg":"Tail, Gaze, or Cast a Spell"}]},

    # ════════════════════════════════════════════════════════
    # DEVILS
    # ════════════════════════════════════════════════════════
    {"name": "Lemure",              "cr": "0",    "xp": 10,    "type": "fiend",      "env": ["dungeon"],
     "hp": "3d8+3", "ac": 7,  "speed": 15, "str":10,"dex":5,"con":11,"int":1,"wis":11,"cha":3,
     "attacks": [{"name":"Fist","hit":"+3","dmg":"1d4+1 bludgeoning"}]},
    {"name": "Bearded Devil",       "cr": "3",    "xp": 700,   "type": "fiend",      "env": ["dungeon"],
     "hp": "10d8+20", "ac": 13, "speed": 30, "str":16,"dex":15,"con":15,"int":9,"wis":11,"cha":11,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Beard","hit":"+5","dmg":"1d8+3 piercing + 1d8 poison (DC 12 Con or poisoned until short/long rest)"},{"name":"Glaive","hit":"+5","dmg":"1d10+3 slashing"}]},
    {"name": "Barbed Devil",        "cr": "5",    "xp": 1800,  "type": "fiend",      "env": ["dungeon"],
     "hp": "13d8+52", "ac": 15, "speed": 30, "str":16,"dex":17,"con":18,"int":12,"wis":14,"cha":14,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Claw","hit":"+6","dmg":"2d6+3 piercing"},{"name":"Tail","hit":"+6","dmg":"2d8+3 piercing"},{"name":"Barbed Hide","hit":"—","dmg":"5 piercing to creatures grappling or grappled by it"}]},
    {"name": "Chain Devil",         "cr": "8",    "xp": 3900,  "type": "fiend",      "env": ["dungeon"],
     "hp": "10d8+40", "ac": 16, "speed": 30, "str":18,"dex":15,"con":18,"int":11,"wis":12,"cha":14,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Chain","hit":"+8","dmg":"2d6+4 slashing (grapple DC 14, restrained)"},{"name":"Animate Chains (recharge 5-6)","hit":"—","dmg":"Up to 4 chains animate and restrain creatures nearby"}]},
    {"name": "Bone Devil",          "cr": "9",    "xp": 5000,  "type": "fiend",      "env": ["dungeon"],
     "hp": "15d10+60", "ac": 19, "speed": "40ft, fly 40ft", "str":18,"dex":16,"con":18,"int":13,"wis":14,"cha":16,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Claw","hit":"+8","dmg":"1d8+4 slashing"},{"name":"Sting","hit":"+8","dmg":"2d8+4 piercing + 4d8 poison (DC 14 Con)"}]},
    {"name": "Ice Devil",           "cr": "14",   "xp": 11500, "type": "fiend",      "env": ["dungeon","arctic"],
     "hp": "19d10+76", "ac": 18, "speed": 40, "str":21,"dex":14,"con":18,"int":18,"wis":15,"cha":18,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Claws","hit":"+10","dmg":"2d6+5 slashing"},{"name":"Tail","hit":"+10","dmg":"3d6+5 bludgeoning"},{"name":"Ice Spear","hit":"+10","dmg":"3d8+5 piercing + 3d8 cold (DC 15 Con or restrained)"}]},
    {"name": "Erinyes",             "cr": "12",   "xp": 8400,  "type": "fiend",      "env": ["dungeon","city"],
     "hp": "18d8+72", "ac": 18, "speed": "30ft, fly 60ft", "str":18,"dex":16,"con":18,"int":14,"wis":14,"cha":18,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Longsword","hit":"+8","dmg":"1d8+4 slashing + 3d8 poison"},{"name":"Longbow","hit":"+7","dmg":"1d8+3 piercing + 3d8 poison (DC 14 Con or poisoned)","range":"150/600ft"},{"name":"Rope of Entanglement","hit":"—","dmg":"DC 15 Dex or restrained"}]},
    {"name": "Horned Devil",        "cr": "11",   "xp": 7200,  "type": "fiend",      "env": ["dungeon"],
     "hp": "17d10+85", "ac": 18, "speed": "20ft, fly 60ft", "str":22,"dex":17,"con":21,"int":12,"wis":16,"cha":17,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Fork","hit":"+10","dmg":"2d8+6 piercing"},{"name":"Tail","hit":"+10","dmg":"1d8+6 piercing + 3d6 fire"},{"name":"Infernal Wound","hit":"—","dmg":"3d6 damage at start of each turn until DC 17 Medicine check or magical healing"}]},
    {"name": "Pit Fiend",           "cr": "20",   "xp": 25000, "type": "fiend",      "env": ["dungeon"],
     "hp": "24d10+120", "ac": 19, "speed": "30ft, fly 60ft", "str":26,"dex":14,"con":24,"int":22,"wis":18,"cha":24,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"4 attacks"},{"name":"Bite","hit":"+14","dmg":"4d6+8 piercing + 5d8 poison (DC 21 Con or poisoned for 1 min)"},{"name":"Claw","hit":"+14","dmg":"2d8+8 slashing"},{"name":"Mace","hit":"+14","dmg":"2d6+8 bludgeoning + 3d6 fire"},{"name":"Tail","hit":"+14","dmg":"2d12+8 bludgeoning"},{"name":"Fireball (at will)","hit":"—","dmg":"As spell, DC 21 Dex"}]},

    # ════════════════════════════════════════════════════════
    # ELEMENTALS
    # ════════════════════════════════════════════════════════
    {"name": "Air Elemental",       "cr": "5",    "xp": 1800,  "type": "elemental",  "env": ["any","mountain","sky"],
     "hp": "12d10+12", "ac": 15, "speed": "0ft, fly 90ft (hover)", "str":14,"dex":20,"con":14,"int":6,"wis":10,"cha":6,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Slam","hit":"+8","dmg":"2d8+5 bludgeoning"},{"name":"Whirlwind (recharge 4-6)","hit":"—","dmg":"DC 13 Str or 3d8+5 bludgeoning + flung 20ft and knocked prone"}]},
    {"name": "Earth Elemental",     "cr": "5",    "xp": 1800,  "type": "elemental",  "env": ["cave","dungeon","mountain"],
     "hp": "12d10+60", "ac": 17, "speed": "30ft, burrow 30ft", "str":20,"dex":8,"con":20,"int":5,"wis":10,"cha":5,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Slam","hit":"+8","dmg":"2d8+5 bludgeoning"}]},
    {"name": "Fire Elemental",      "cr": "5",    "xp": 1800,  "type": "elemental",  "env": ["volcano","dungeon"],
     "hp": "12d10+12", "ac": 13, "speed": 50, "str":10,"dex":17,"con":16,"int":6,"wis":10,"cha":7,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Touch","hit":"+6","dmg":"2d6+3 fire (ignites flammable objects)"},{"name":"Fire Form","hit":"—","dmg":"5 fire to anyone entering space or ending turn within 5ft"}]},
    {"name": "Water Elemental",     "cr": "5",    "xp": 1800,  "type": "elemental",  "env": ["coast","underwater","swamp"],
     "hp": "12d10+36", "ac": 14, "speed": "30ft, swim 90ft", "str":18,"dex":14,"con":18,"int":5,"wis":10,"cha":8,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Slam","hit":"+7","dmg":"2d8+4 bludgeoning"},{"name":"Whelm (recharge 4-6)","hit":"—","dmg":"DC 15 Str or grappled inside elemental, restrained, 2d8+4/turn"}]},
    {"name": "Djinni",              "cr": "11",   "xp": 7200,  "type": "elemental",  "env": ["desert","sky","any"],
     "hp": "14d10+35", "ac": 17, "speed": "30ft, fly 90ft", "str":21,"dex":15,"con":22,"int":15,"wis":16,"cha":20,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Scimitar","hit":"+9","dmg":"2d6+5 slashing + 1d6 lightning or thunder"},{"name":"Create Whirlwind","hit":"—","dmg":"DC 18 Str or caught in whirlwind — 2d8+4/turn"}]},
    {"name": "Efreeti",             "cr": "11",   "xp": 7200,  "type": "elemental",  "env": ["volcano","desert","dungeon"],
     "hp": "22d10+110", "ac": 17, "speed": "40ft, fly 60ft", "str":22,"dex":12,"con":24,"int":16,"wis":15,"cha":16,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Scimitar","hit":"+10","dmg":"2d6+6 slashing + 2d6 fire"},{"name":"Hurl Flame","hit":"+10","dmg":"5d6 fire (range 120ft)"}]},
    {"name": "Marid",               "cr": "11",   "xp": 7200,  "type": "elemental",  "env": ["underwater","coast"],
     "hp": "22d10+66", "ac": 17, "speed": "30ft, fly 60ft, swim 90ft", "str":22,"dex":12,"con":26,"int":18,"wis":17,"cha":18,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Trident","hit":"+10","dmg":"2d6+6 piercing"},{"name":"Water Jet","hit":"+10","dmg":"4d8 bludgeoning (DC 18 Str or pushed 20ft and knocked prone)"}]},
    {"name": "Dao",                 "cr": "11",   "xp": 7200,  "type": "elemental",  "env": ["cave","dungeon","mountain"],
     "hp": "15d10+60", "ac": 18, "speed": "30ft, burrow 30ft, fly 30ft", "str":23,"dex":12,"con":20,"int":14,"wis":13,"cha":16,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Maul","hit":"+10","dmg":"2d6+6 bludgeoning + 1d6 thunder"}]},
    {"name": "Magma Mephit",        "cr": "1/2",  "xp": 100,   "type": "elemental",  "env": ["volcano","dungeon"],
     "hp": "6d6+6", "ac": 11, "speed": "30ft, fly 30ft", "str":7,"dex":12,"con":12,"int":8,"wis":11,"cha":10,
     "attacks": [{"name":"Claws","hit":"+3","dmg":"1d4+1 slashing + 1d4 fire"},{"name":"Fire Breath (recharge 6)","hit":"—","dmg":"DC 11 Dex, 2d6 fire"}]},
    {"name": "Ice Mephit",          "cr": "1/2",  "xp": 100,   "type": "elemental",  "env": ["arctic","cave","dungeon"],
     "hp": "6d6", "ac": 11, "speed": "30ft, fly 30ft", "str":7,"dex":13,"con":10,"int":9,"wis":11,"cha":12,
     "attacks": [{"name":"Claws","hit":"+3","dmg":"1d4+1 slashing + 1d4 cold"},{"name":"Frost Breath (recharge 6)","hit":"—","dmg":"DC 10 Dex, 3d6 cold"}]},
    {"name": "Steam Mephit",        "cr": "1/4",  "xp": 50,    "type": "elemental",  "env": ["volcano","dungeon"],
     "hp": "4d6+4", "ac": 10, "speed": "30ft, fly 30ft", "str":5,"dex":11,"con":10,"int":11,"wis":10,"cha":12,
     "attacks": [{"name":"Claws","hit":"+2","dmg":"1d4 slashing + 1d4 fire"},{"name":"Steam Breath (recharge 6)","hit":"—","dmg":"DC 10 Dex, 2d4 fire"}]},

    # ════════════════════════════════════════════════════════
    # FEY
    # ════════════════════════════════════════════════════════
    {"name": "Pixie",               "cr": "1/4",  "xp": 50,    "type": "fey",        "env": ["forest"],
     "hp": "1d4-1", "ac": 15, "speed": "10ft, fly 30ft", "str":2,"dex":20,"con":8,"int":10,"wis":14,"cha":15,
     "attacks": [{"name":"Shortsword","hit":"+7","dmg":"1d6+5 piercing (tiny, 1 damage from tiny weapon)"},{"name":"Spellcasting","hit":"—","dmg":"Confusion, dancing lights, detect evil, detect thoughts, dispel magic, entangle, fly, phantasmal force, polymorph, sleep"}]},
    {"name": "Sprite",              "cr": "1/4",  "xp": 50,    "type": "fey",        "env": ["forest"],
     "hp": "1d4-1", "ac": 15, "speed": "10ft, fly 40ft", "str":3,"dex":18,"con":10,"int":14,"wis":13,"cha":11,
     "attacks": [{"name":"Longsword","hit":"+2","dmg":"1 piercing (tiny)"},{"name":"Shortbow","hit":"+6","dmg":"1 piercing + DC 10 Con or sleep 1 min","range":"40/160ft"},{"name":"Heart Sight","hit":"—","dmg":"Touch creature — learn alignment, DC 10 Cha to hide emotions"}]},
    {"name": "Satyr",               "cr": "1/2",  "xp": 100,   "type": "fey",        "env": ["forest"],
     "hp": "7d8", "ac": 14, "speed": 40, "str":12,"dex":16,"con":11,"int":12,"wis":10,"cha":14,
     "attacks": [{"name":"Ram","hit":"+3","dmg":"2d4+1 bludgeoning"},{"name":"Shortsword","hit":"+5","dmg":"1d6+3 piercing"},{"name":"Shortbow","hit":"+5","dmg":"1d6+3 piercing","range":"80/320ft"}]},
    {"name": "Unicorn",             "cr": "5",    "xp": 1800,  "type": "celestial",  "env": ["forest"],
     "hp": "9d10+36", "ac": 12, "speed": 50, "str":18,"dex":14,"con":15,"int":11,"wis":17,"cha":16,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Hooves","hit":"+7","dmg":"2d6+4 bludgeoning"},{"name":"Horn","hit":"+7","dmg":"1d8+4 piercing + 1d8 radiant (charge: +9 piercing, DC 15 Str or knocked prone)"},{"name":"Healing Touch (3/day)","hit":"—","dmg":"Touch: 2d8+2 HP restored, remove poison/disease"}]},
    {"name": "Hag (Night Hag)",     "cr": "5",    "xp": 1800,  "type": "fiend",      "env": ["dungeon","swamp","graveyard"],
     "hp": "15d8+45", "ac": 17, "speed": 30, "str":18,"dex":15,"con":16,"int":16,"wis":14,"cha":16,
     "attacks": [{"name":"Claws","hit":"+7","dmg":"2d8+4 slashing"},{"name":"Etherealness","hit":"—","dmg":"Enter Ethereal Plane (Dream Haunting)"},{"name":"Nightmare Haunting (1/day)","hit":"—","dmg":"Sleeping humanoid: DC 11 Wis or cursed — no benefit from sleep, gain 1 exhaustion/night"}]},
    {"name": "Bheur Hag",           "cr": "7",    "xp": 2900,  "type": "fey",        "env": ["arctic","mountain"],
     "hp": "13d8+26", "ac": 17, "speed": "30ft, fly 50ft (only in wild, on graywood staff)", "str":13,"dex":16,"con":14,"int":12,"wis":12,"cha":13,
     "attacks": [{"name":"Claws","hit":"+6","dmg":"2d6+3 slashing + 3d6 cold"},{"name":"Icy Spear","hit":"+6","dmg":"3d6+3 cold","range":"60ft"},{"name":"Spellcasting","hit":"—","dmg":"Cone of Cold, Hold Person, Fly, Sleet Storm"}]},
    {"name": "Annis Hag",           "cr": "6",    "xp": 2300,  "type": "fey",        "env": ["mountain","forest","swamp"],
     "hp": "10d8+30", "ac": 17, "speed": 40, "str":21,"dex":12,"con":14,"int":13,"wis":14,"cha":15,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Claw","hit":"+8","dmg":"2d8+5 slashing"},{"name":"Crushing Hug","hit":"+8","dmg":"3d6+5 bludgeoning (grapple DC 15, restrained, 3d6+5 auto/turn)"}]},
    {"name": "Banshee",             "cr": "4",    "xp": 1100,  "type": "undead",     "env": ["dungeon","crypt","graveyard","forest"],
     "hp": "13d8", "ac": 12, "speed": "0ft, fly 40ft (hover)", "str":1,"dex":14,"con":10,"int":12,"wis":11,"cha":17,
     "attacks": [{"name":"Corrupting Touch","hit":"+4","dmg":"3d6 necrotic"},{"name":"Horrifying Visage","hit":"—","dmg":"DC 13 Wis or aged 1d4×10 years + frightened"},{"name":"Wail (1/day)","hit":"—","dmg":"DC 13 Con or drop to 0 HP (not undead/constructs)"}]},
    {"name": "Quickling",           "cr": "1",    "xp": 200,   "type": "fey",        "env": ["forest"],
     "hp": "3d4", "ac": 16, "speed": 120, "str":4,"dex":23,"con":8,"int":10,"wis":10,"cha":10,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Dagger","hit":"+8","dmg":"1d4+6 piercing"}]},

    # ════════════════════════════════════════════════════════
    # GIANTS (full set)
    # ════════════════════════════════════════════════════════
    {"name": "Hill Giant",          "cr": "5",    "xp": 1800,  "type": "giant",      "env": ["grassland","mountain","forest"],
     "hp": "10d12+40", "ac": 13, "speed": 40, "str":21,"dex":8,"con":19,"int":5,"wis":9,"cha":6,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Greatclub","hit":"+8","dmg":"3d8+5 bludgeoning"},{"name":"Rock","hit":"+8","dmg":"3d10+5 bludgeoning","range":"60/240ft"}]},
    {"name": "Stone Giant",         "cr": "7",    "xp": 2900,  "type": "giant",      "env": ["mountain","cave"],
     "hp": "11d12+44", "ac": 17, "speed": 40, "str":23,"dex":15,"con":20,"int":10,"wis":12,"cha":9,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Greatclub","hit":"+9","dmg":"3d8+6 bludgeoning"},{"name":"Rock","hit":"+9","dmg":"4d10+6 bludgeoning (DC 17 Str or knocked prone)","range":"60/240ft"}]},
    {"name": "Fire Giant",          "cr": "9",    "xp": 5000,  "type": "giant",      "env": ["mountain","volcano"],
     "hp": "13d12+65", "ac": 18, "speed": 30, "str":25,"dex":9,"con":23,"int":10,"wis":14,"cha":13,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Greatsword","hit":"+11","dmg":"6d6+7 slashing"},{"name":"Rock","hit":"+11","dmg":"4d10+7 bludgeoning + 2d10 fire","range":"60/240ft"}]},
    {"name": "Storm Giant",         "cr": "13",   "xp": 10000, "type": "giant",      "env": ["mountain","coast","sky"],
     "hp": "20d12+100", "ac": 16, "speed": "50ft, swim 50ft", "str":29,"dex":14,"con":20,"int":16,"wis":18,"cha":18,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Greatsword","hit":"+14","dmg":"4d6+9 slashing + 2d6 lightning"},{"name":"Rock","hit":"+14","dmg":"4d10+9 bludgeoning","range":"60/240ft"},{"name":"Lightning Strike (recharge 5-6)","hit":"—","dmg":"12d8 lightning (DC 17 Dex half, 500ft range)"}]},
    {"name": "Fomorian",            "cr": "8",    "xp": 3900,  "type": "giant",      "env": ["cave","dungeon"],
     "hp": "14d12+56", "ac": 14, "speed": 30, "str":23,"dex":10,"con":23,"int":9,"wis":13,"cha":8,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Greatclub","hit":"+9","dmg":"3d8+6 bludgeoning"},{"name":"Curse of the Evil Eye (recharge 5-6)","hit":"—","dmg":"DC 14 Cha or polymorphed into beast for 1 hour"}]},
    {"name": "Verbeeg",             "cr": "4",    "xp": 1100,  "type": "giant",      "env": ["mountain","forest","dungeon"],
     "hp": "8d10+16", "ac": 14, "speed": 40, "str":19,"dex":11,"con":14,"int":11,"wis":10,"cha":9,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Spear","hit":"+6","dmg":"2d8+4 piercing"}]},

    # ════════════════════════════════════════════════════════
    # HUMANOIDS (expanded)
    # ════════════════════════════════════════════════════════
    {"name": "Drow",                "cr": "1/4",  "xp": 50,    "type": "humanoid",   "env": ["dungeon","underdark"],
     "hp": "3d8", "ac": 15, "speed": 30, "str":10,"dex":14,"con":10,"int":11,"wis":11,"cha":12,
     "attacks": [{"name":"Shortsword","hit":"+4","dmg":"1d6+2 piercing + 3d6 poison (DC 13 Con)"},{"name":"Hand Crossbow","hit":"+4","dmg":"1d6+2 piercing + 3d6 poison (DC 13 Con, sleep on fail)","range":"30/120ft"},{"name":"Innate Spells","hit":"—","dmg":"Dancing lights (at will), darkness, faerie fire (1/day each)"}]},
    {"name": "Drow Elite Warrior",  "cr": "5",    "xp": 1800,  "type": "humanoid",   "env": ["dungeon","underdark"],
     "hp": "10d8+20", "ac": 18, "speed": 30, "str":13,"dex":18,"con":14,"int":11,"wis":13,"cha":12,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Shortsword","hit":"+7","dmg":"1d6+4 piercing + 3d6 poison (DC 13 Con)"},{"name":"Hand Crossbow","hit":"+7","dmg":"1d6+4 piercing + 3d6 poison","range":"30/120ft"}]},
    {"name": "Drow Mage",           "cr": "7",    "xp": 2900,  "type": "humanoid",   "env": ["dungeon","underdark"],
     "hp": "13d8+13", "ac": 12, "speed": 30, "str":9,"dex":14,"con":10,"int":17,"wis":13,"cha":12,
     "attacks": [{"name":"Staff","hit":"+2","dmg":"1d6-1 bludgeoning"},{"name":"Spellcasting","hit":"—","dmg":"Mage Armor, Shield, Misty Step, Fly, Lightning Bolt, Fireball, Cloudkill (DC 14)"}]},
    {"name": "Drow Priestess",      "cr": "8",    "xp": 3900,  "type": "humanoid",   "env": ["dungeon","underdark"],
     "hp": "12d8+24", "ac": 16, "speed": 30, "str":10,"dex":14,"con":13,"int":11,"wis":17,"cha":13,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Scourge","hit":"+5","dmg":"1d6+2 slashing + 3d6 poison"},{"name":"Spellcasting","hit":"—","dmg":"Cleric spells: Heal, Banishment, Hold Person, Harm (DC 14)"}]},
    {"name": "Githyanki Warrior",   "cr": "3",    "xp": 700,   "type": "humanoid",   "env": ["dungeon","city","astral"],
     "hp": "9d8+9", "ac": 17, "speed": 30, "str":15,"dex":14,"con":12,"int":13,"wis":13,"cha":10,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Silver Greatsword","hit":"+4","dmg":"2d6+2 slashing + 1d6 psychic"},{"name":"Innate Spells","hit":"—","dmg":"Mage Hand (at will), Jump, Misty Step (3/day)"}]},
    {"name": "Githzerai Monk",      "cr": "2",    "xp": 450,   "type": "humanoid",   "env": ["dungeon","astral"],
     "hp": "9d8+9", "ac": 14, "speed": 30, "str":12,"dex":15,"con":12,"int":13,"wis":14,"cha":10,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Unarmed Strike","hit":"+4","dmg":"1d8+2 bludgeoning + 1d8 psychic"}]},
    {"name": "Kenku",               "cr": "1/4",  "xp": 50,    "type": "humanoid",   "env": ["city","dungeon","forest"],
     "hp": "3d8+3", "ac": 13, "speed": 30, "str":10,"dex":16,"con":10,"int":11,"wis":10,"cha":10,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Shortsword","hit":"+5","dmg":"1d6+3 piercing"},{"name":"Shortbow","hit":"+5","dmg":"1d6+3 piercing","range":"80/320ft"}]},
    {"name": "Kuo-Toa Archpriest",  "cr": "6",    "xp": 2300,  "type": "humanoid",   "env": ["underwater","dungeon","cave"],
     "hp": "10d8+10", "ac": 13, "speed": "30ft, swim 30ft", "str":16,"dex":14,"con":13,"int":13,"wis":16,"cha":13,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Scepter","hit":"+6","dmg":"1d6+3 bludgeoning + 2d6 lightning"},{"name":"Spellcasting","hit":"—","dmg":"Thaumaturgy, Sacred Flame, Guidance, Shatter, Spiritual Weapon, Lightning Bolt (DC 14)"}]},
    {"name": "Thri-kreen",          "cr": "1",    "xp": 200,   "type": "humanoid",   "env": ["desert","grassland","dungeon"],
     "hp": "7d8+7", "ac": 15, "speed": 40, "str":12,"dex":15,"con":10,"int":8,"wis":12,"cha":7,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Bite","hit":"+3","dmg":"1d4+1 piercing + DC 11 Con or paralyzed 1 min"},{"name":"Claw","hit":"+3","dmg":"1d6+1 slashing"},{"name":"Glaive","hit":"+3","dmg":"1d10+1 slashing"}]},
    {"name": "Yuan-Ti Pureblood",   "cr": "1",    "xp": 200,   "type": "humanoid",   "env": ["dungeon","desert","jungle"],
     "hp": "9d8+9", "ac": 11, "speed": 30, "str":16,"dex":12,"con":13,"int":14,"wis":12,"cha":14,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Scimitar","hit":"+5","dmg":"1d6+3 slashing"},{"name":"Shortbow","hit":"+3","dmg":"1d6+1 piercing + 2d6 poison (DC 13 Con)","range":"80/320ft"},{"name":"Innate Spells","hit":"—","dmg":"Animal Friendship (snakes), Suggestion (3/day), Poison Spray (DC 12)"}]},
    {"name": "Yuan-Ti Malison",     "cr": "3",    "xp": 700,   "type": "humanoid",   "env": ["dungeon","desert","jungle"],
     "hp": "9d8+9", "ac": 12, "speed": 30, "str":16,"dex":14,"con":13,"int":14,"wis":12,"cha":16,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Constrict","hit":"+5","dmg":"1d6+3 bludgeoning (grapple DC 13)"},{"name":"Scimitar","hit":"+5","dmg":"1d6+3 slashing"},{"name":"Innate Spells","hit":"—","dmg":"Animal Friendship (snakes), Suggestion, Fear (3/day)"}]},
    {"name": "Bugbear",             "cr": "1",    "xp": 200,   "type": "humanoid",   "env": ["dungeon","forest","cave"],
     "hp": "5d8+5", "ac": 16, "speed": 30, "str":15,"dex":14,"con":13,"int":8,"wis":11,"cha":9,
     "attacks": [{"name":"Morningstar","hit":"+4","dmg":"2d8+2 piercing (surprise: +2d6)"},{"name":"Javelin","hit":"+4","dmg":"1d6+2 piercing","range":"30/120ft"}]},
    {"name": "Hobgoblin Captain",   "cr": "3",    "xp": 700,   "type": "humanoid",   "env": ["dungeon","forest","mountain"],
     "hp": "10d8+20", "ac": 17, "speed": 30, "str":15,"dex":14,"con":14,"int":12,"wis":10,"cha":13,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Greatsword","hit":"+4","dmg":"2d6+2 slashing"},{"name":"Javelin","hit":"+4","dmg":"1d6+2 piercing","range":"30/120ft"},{"name":"Leadership (recharge short/long)","hit":"—","dmg":"Allies within 30ft add 1d4 to attack rolls and saves for 1 min"}]},
    {"name": "Gnoll Pack Lord",     "cr": "2",    "xp": 450,   "type": "humanoid",   "env": ["grassland","desert","dungeon"],
     "hp": "9d8+9", "ac": 15, "speed": 30, "str":16,"dex":14,"con":13,"int":8,"wis":11,"cha":9,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Flail","hit":"+5","dmg":"1d8+3 bludgeoning"},{"name":"Longbow","hit":"+4","dmg":"1d8+2 piercing","range":"150/600ft"},{"name":"Incite Rampage (recharge 5-6)","hit":"—","dmg":"One gnoll within 30ft can bite as reaction"}]},
    {"name": "Orc War Chief",       "cr": "4",    "xp": 1100,  "type": "humanoid",   "env": ["mountain","dungeon","forest"],
     "hp": "11d8+44", "ac": 16, "speed": 30, "str":18,"dex":12,"con":18,"int":11,"wis":11,"cha":16,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Greataxe","hit":"+6","dmg":"1d12+4 slashing"},{"name":"Javelin","hit":"+6","dmg":"1d6+4 piercing","range":"30/120ft"},{"name":"Battle Cry (recharge 5-6)","hit":"—","dmg":"Allies within 30ft have advantage on attacks until start of war chief's next turn"}]},
    {"name": "Tribal Warrior",      "cr": "1/8",  "xp": 25,    "type": "humanoid",   "env": ["forest","grassland","mountain","coast"],
     "hp": "2d8+2", "ac": 12, "speed": 30, "str":13,"dex":11,"con":12,"int":8,"wis":11,"cha":8,
     "attacks": [{"name":"Spear","hit":"+3","dmg":"1d6+1 piercing"}]},
    {"name": "Berserker",           "cr": "2",    "xp": 450,   "type": "humanoid",   "env": ["mountain","forest","arctic","grassland"],
     "hp": "9d8+27", "ac": 13, "speed": 30, "str":16,"dex":12,"con":17,"int":9,"wis":11,"cha":9,
     "attacks": [{"name":"Greataxe","hit":"+5","dmg":"1d12+3 slashing (reckless: advantage to hit, enemies have advantage back)"}]},
    {"name": "Knight",              "cr": "3",    "xp": 700,   "type": "humanoid",   "env": ["city","dungeon","grassland"],
     "hp": "8d8+24", "ac": 18, "speed": 30, "str":16,"dex":11,"con":16,"int":11,"wis":11,"cha":15,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Greatsword","hit":"+5","dmg":"2d6+3 slashing"},{"name":"Heavy Crossbow","hit":"+2","dmg":"1d10 piercing","range":"100/400ft"},{"name":"Leadership (recharge short/long)","hit":"—","dmg":"Allies add 1d4 to attacks/saves for 1 min"}]},
    {"name": "Mage",                "cr": "6",    "xp": 2300,  "type": "humanoid",   "env": ["city","dungeon"],
     "hp": "9d8+18", "ac": 12, "speed": 30, "str":9,"dex":14,"con":11,"int":17,"wis":12,"cha":11,
     "attacks": [{"name":"Dagger","hit":"+5","dmg":"1d4+2 piercing"},{"name":"Spellcasting","hit":"—","dmg":"Fire Bolt, Mage Armor, Magic Missile, Shield, Misty Step, Counterspell, Fireball, Fly, Cone of Cold (DC 14)"}]},
    {"name": "Archmage",            "cr": "12",   "xp": 8400,  "type": "humanoid",   "env": ["city","dungeon"],
     "hp": "18d8+18", "ac": 12, "speed": 30, "str":10,"dex":14,"con":12,"int":20,"wis":15,"cha":16,
     "attacks": [{"name":"Dagger","hit":"+6","dmg":"1d4+2 piercing"},{"name":"Spellcasting","hit":"—","dmg":"9th-level wizard spells — Timestop, Mind Blank, Maze, Power Word Stun (DC 17)"}]},
    {"name": "Priest",              "cr": "2",    "xp": 450,   "type": "humanoid",   "env": ["city","dungeon"],
     "hp": "5d8+10", "ac": 13, "speed": 30, "str":10,"dex":10,"con":12,"int":13,"wis":16,"cha":13,
     "attacks": [{"name":"Mace","hit":"+2","dmg":"1d6 bludgeoning"},{"name":"Spellcasting","hit":"—","dmg":"Sacred Flame, Sanctuary, Bless, Cure Wounds, Guiding Bolt, Spiritual Weapon (DC 13)"}]},
    {"name": "Veteran",             "cr": "3",    "xp": 700,   "type": "humanoid",   "env": ["city","dungeon","grassland"],
     "hp": "9d8+18", "ac": 17, "speed": 30, "str":16,"dex":13,"con":14,"int":10,"wis":11,"cha":10,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Longsword","hit":"+5","dmg":"1d8+3 slashing"},{"name":"Shortsword","hit":"+5","dmg":"1d6+3 piercing"},{"name":"Heavy Crossbow","hit":"+3","dmg":"1d10+1 piercing","range":"100/400ft"}]},
    {"name": "Assassin",            "cr": "8",    "xp": 3900,  "type": "humanoid",   "env": ["city","dungeon"],
     "hp": "12d8+24", "ac": 15, "speed": 30, "str":11,"dex":16,"con":14,"int":13,"wis":11,"cha":10,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Shortsword","hit":"+6","dmg":"1d6+3 piercing + 3d6 poison (DC 15 Con)"},{"name":"Light Crossbow","hit":"+6","dmg":"1d8+3 piercing + 3d6 poison","range":"80/320ft"},{"name":"Sneak Attack (1/turn)","hit":"—","dmg":"+4d6 when advantage or ally adjacent to target"}]},
    {"name": "Spy",                 "cr": "1",    "xp": 200,   "type": "humanoid",   "env": ["city","dungeon"],
     "hp": "6d8", "ac": 12, "speed": 30, "str":10,"dex":15,"con":10,"int":12,"wis":14,"cha":16,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Shortsword","hit":"+4","dmg":"1d6+2 piercing"},{"name":"Hand Crossbow","hit":"+4","dmg":"1d6+2 piercing","range":"30/120ft"}]},
    {"name": "Gladiator",           "cr": "5",    "xp": 1800,  "type": "humanoid",   "env": ["city","dungeon"],
     "hp": "15d8+45", "ac": 16, "speed": 30, "str":18,"dex":15,"con":16,"int":10,"wis":12,"cha":15,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Spear","hit":"+7","dmg":"1d8+4 piercing (2d6+4 two-handed)"},{"name":"Shield Bash","hit":"+7","dmg":"2d6+4 bludgeoning (DC 15 Str or knocked prone)"}]},
    {"name": "Wererat",             "cr": "2",    "xp": 450,   "type": "humanoid",   "env": ["city","dungeon","sewer"],
     "hp": "9d8+9", "ac": 12, "speed": 30, "str":10,"dex":15,"con":12,"int":11,"wis":10,"cha":8,
     "attacks": [{"name":"Multiattack (humanoid only)","hit":"—","dmg":"2 attacks"},{"name":"Shortsword","hit":"+4","dmg":"1d6+2 piercing"},{"name":"Hand Crossbow","hit":"+4","dmg":"1d6+2 piercing","range":"30/120ft"},{"name":"Bite (rat/hybrid)","hit":"+4","dmg":"1d4+2 piercing (DC 11 Con or lycanthropy)"}]},
    {"name": "Weretiger",           "cr": "4",    "xp": 1100,  "type": "humanoid",   "env": ["forest","grassland","city"],
     "hp": "12d8+24", "ac": 12, "speed": "30ft (40ft tiger)", "str":17,"dex":15,"con":16,"int":10,"wis":13,"cha":10,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks (4 in tiger form)"},{"name":"Longsword","hit":"+5","dmg":"1d8+3 slashing"},{"name":"Longbow","hit":"+4","dmg":"1d8+2 piercing","range":"150/600ft"},{"name":"Bite (tiger)","hit":"+5","dmg":"1d10+3 piercing (DC 13 Str or knocked prone)"},{"name":"Claw (tiger)","hit":"+5","dmg":"1d8+3 slashing"}]},
    {"name": "Werebear",            "cr": "5",    "xp": 1800,  "type": "humanoid",   "env": ["forest","mountain","arctic"],
     "hp": "18d8+72", "ac": 11, "speed": "30ft (40ft bear)", "str":19,"dex":10,"con":17,"int":11,"wis":12,"cha":12,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Greataxe","hit":"+7","dmg":"1d12+4 slashing"},{"name":"Handaxe","hit":"+7","dmg":"1d6+4 slashing"},{"name":"Bite (bear)","hit":"+7","dmg":"2d10+4 piercing (DC 14 Con or lycanthropy)"},{"name":"Claws (bear)","hit":"+7","dmg":"2d8+4 slashing"}]},

    # ════════════════════════════════════════════════════════
    # MONSTROSITIES (expanded)
    # ════════════════════════════════════════════════════════
    {"name": "Displacer Beast",     "cr": "3",    "xp": 700,   "type": "monstrosity","env": ["forest","dungeon"],
     "hp": "10d10+30", "ac": 13, "speed": 40, "str":18,"dex":15,"con":16,"int":6,"wis":12,"cha":8,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Tentacle","hit":"+6","dmg":"1d6+4 piercing + 1d6+4 bludgeoning"},{"name":"Displacement","hit":"—","dmg":"Attacks against it have disadvantage (until hit)"}]},
    {"name": "Gorgon",              "cr": "5",    "xp": 1800,  "type": "monstrosity","env": ["grassland","mountain"],
     "hp": "19d10+38", "ac": 19, "speed": 40, "str":20,"dex":11,"con":20,"int":2,"wis":12,"cha":7,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Gore","hit":"+8","dmg":"2d12+5 piercing"},{"name":"Hooves","hit":"+8","dmg":"3d10+5 bludgeoning"},{"name":"Petrifying Breath (recharge 5-6)","hit":"—","dmg":"DC 13 Con: restrained → petrified (30ft cone)"}]},
    {"name": "Hydra",               "cr": "8",    "xp": 3900,  "type": "monstrosity","env": ["swamp","coast","dungeon"],
     "hp": "15d12+75", "ac": 15, "speed": "30ft, swim 30ft", "str":20,"dex":12,"con":20,"int":2,"wis":10,"cha":7,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"As many attacks as heads (starts 5)"},{"name":"Bite","hit":"+8","dmg":"1d10+5 piercing"},{"name":"Regrow Heads","hit":"—","dmg":"If 25+ HP lost in one turn, lose head. Otherwise regrow 2 at end of turn."}]},
    {"name": "Sphinx (Androsphinx)","cr": "17",   "xp": 18000, "type": "monstrosity","env": ["desert","dungeon"],
     "hp": "19d10+95", "ac": 17, "speed": "40ft, fly 60ft", "str":22,"dex":10,"con":20,"int":16,"wis":18,"cha":23,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Claw","hit":"+12","dmg":"2d10+6 slashing"},{"name":"Roar (3/day)","hit":"—","dmg":"DC 18 Wis: 1st roar = frightened 1 min, 2nd = frightened + deafened, 3rd = stunned 1 min"},{"name":"Spellcasting","hit":"—","dmg":"9th-level cleric spells (DC 21)"}]},
    {"name": "Sphinx (Gynosphinx)","cr": "11",    "xp": 7200,  "type": "monstrosity","env": ["desert","dungeon"],
     "hp": "16d10+48", "ac": 17, "speed": "40ft, fly 60ft", "str":18,"dex":15,"con":16,"int":18,"wis":18,"cha":18,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Claw","hit":"+8","dmg":"2d8+4 slashing"},{"name":"Spellcasting","hit":"—","dmg":"6th-level wizard/cleric spells (DC 16)"}]},
    {"name": "Umber Hulk",          "cr": "5",    "xp": 1800,  "type": "monstrosity","env": ["dungeon","underground","mountain"],
     "hp": "15d10+45", "ac": 18, "speed": "30ft, burrow 20ft", "str":20,"dex":13,"con":16,"int":9,"wis":10,"cha":10,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Claw","hit":"+8","dmg":"1d8+5 slashing"},{"name":"Mandible","hit":"+8","dmg":"2d6+5 slashing"},{"name":"Confusing Gaze","hit":"—","dmg":"DC 15 Cha or confused (roll 1d8 for action)"}]},
    {"name": "Carrion Crawler",     "cr": "2",    "xp": 450,   "type": "monstrosity","env": ["dungeon","cave","sewer"],
     "hp": "6d10+12", "ac": 13, "speed": "30ft, climb 30ft", "str":14,"dex":13,"con":16,"int":1,"wis":12,"cha":5,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Tentacles","hit":"+8","dmg":"4d8 poison (DC 13 Con or paralyzed 1 min)"},{"name":"Bite","hit":"+4","dmg":"2d6+2 piercing"}]},
    {"name": "Remorhaz",            "cr": "11",   "xp": 7200,  "type": "monstrosity","env": ["arctic","dungeon"],
     "hp": "17d12+102", "ac": 17, "speed": "30ft, burrow 20ft", "str":24,"dex":13,"con":21,"int":4,"wis":10,"cha":5,
     "attacks": [{"name":"Bite","hit":"+11","dmg":"6d10+7 piercing (swallow: DC 17 Dex or swallowed — 3d6+7 acid/turn)"},{"name":"Heated Body","hit":"—","dmg":"10 fire to anyone touching or hitting with melee"}]},
    {"name": "Young Remorhaz",      "cr": "5",    "xp": 1800,  "type": "monstrosity","env": ["arctic"],
     "hp": "11d10+33", "ac": 14, "speed": "30ft, burrow 10ft", "str":18,"dex":13,"con":17,"int":3,"wis":10,"cha":4,
     "attacks": [{"name":"Bite","hit":"+6","dmg":"3d6+4 piercing"},{"name":"Heated Body","hit":"—","dmg":"5 fire to anyone touching or hitting with melee"}]},
    {"name": "Hook Horror",         "cr": "3",    "xp": 700,   "type": "monstrosity","env": ["dungeon","cave","underdark"],
     "hp": "10d10+30", "ac": 15, "speed": "30ft, climb 30ft", "str":18,"dex":10,"con":15,"int":6,"wis":12,"cha":7,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Hook","hit":"+6","dmg":"2d6+4 piercing"}]},
    {"name": "Nothic",              "cr": "2",    "xp": 450,   "type": "aberration", "env": ["dungeon"],
     "hp": "6d8+12", "ac": 15, "speed": 30, "str":14,"dex":16,"con":16,"int":13,"wis":10,"cha":8,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Rotting Gaze","hit":"—","dmg":"DC 12 Con or 3d6 necrotic (30ft, sight line)"},{"name":"Claws","hit":"+4","dmg":"1d6+3 slashing"},{"name":"Weird Insight","hit":"—","dmg":"Contest: Perception vs Deception — learn one secret"}]},
    {"name": "Gibbering Mouther",   "cr": "2",    "xp": 450,   "type": "aberration", "env": ["dungeon","underdark"],
     "hp": "9d8+27", "ac": 9,  "speed": "10ft, swim 10ft", "str":10,"dex":8,"con":16,"int":3,"wis":10,"cha":6,
     "attacks": [{"name":"Bites","hit":"+2","dmg":"5d6 piercing (DC 10 Con or stunned until end of next turn)"},{"name":"Blinding Spittle (recharge 5-6)","hit":"—","dmg":"DC 13 Dex or blinded 1 min (15ft range)"},{"name":"Gibbering","hit":"—","dmg":"DC 10 Wis or random action on turn (within 30ft)"}]},
    {"name": "Intellect Devourer",  "cr": "2",    "xp": 450,   "type": "aberration", "env": ["dungeon","underdark"],
     "hp": "4d4+4", "ac": 12, "speed": 40, "str":6,"dex":14,"con":13,"int":12,"wis":11,"cha":10,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Claws","hit":"+4","dmg":"2d6+2 slashing"},{"name":"Devour Intellect","hit":"+4","dmg":"DC 12 Int: 3d6 psychic, Int reduced by rolled amount (0 = stunned)"},{"name":"Body Thief","hit":"—","dmg":"Enter skull of incapacitated humanoid — control body"}]},
    {"name": "Flumph",              "cr": "1/8",  "xp": 25,    "type": "aberration", "env": ["dungeon","underdark"],
     "hp": "2d6-2", "ac": 12, "speed": "0ft, fly 30ft (hover)", "str":6,"dex":15,"con":10,"int":14,"wis":14,"cha":11,
     "attacks": [{"name":"Tendrils","hit":"+4","dmg":"1d4+2 piercing + DC 10 Con or 1d4 acid/turn for 1 min (cure: DC 10 Dex to remove)"},{"name":"Stench Spray (recharge 6)","hit":"—","dmg":"DC 12 Con or poisoned 1 min (15ft line)"}]},
    {"name": "Grell",               "cr": "3",    "xp": 700,   "type": "aberration", "env": ["dungeon","underdark","cave"],
     "hp": "10d8+10", "ac": 12, "speed": "10ft, fly 30ft (hover)", "str":15,"dex":14,"con":13,"int":12,"wis":11,"cha":9,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Tentacles","hit":"+4","dmg":"1d10+2 piercing (grapple DC 12, paralyzed DC 11 Con 1 min)"},{"name":"Beak","hit":"+4","dmg":"2d4+2 piercing"}]},

    # ════════════════════════════════════════════════════════
    # OOZES (expanded)
    # ════════════════════════════════════════════════════════
    {"name": "Black Pudding",       "cr": "4",    "xp": 1100,  "type": "ooze",       "env": ["dungeon","cave"],
     "hp": "10d10+30", "ac": 7,  "speed": "20ft, climb 20ft", "str":16,"dex":5,"con":16,"int":1,"wis":6,"cha":1,
     "attacks": [{"name":"Pseudopod","hit":"+5","dmg":"1d6+3 bludgeoning + 4d8 acid (metal/wood destroyed on miss too)"},{"name":"Split","hit":"—","dmg":"When hit by slashing/lightning: splits into two CR 1 puddings if 10+ HP"}]},
    {"name": "Gray Ooze",           "cr": "1/2",  "xp": 100,   "type": "ooze",       "env": ["dungeon","cave","swamp"],
     "hp": "3d8+9", "ac": 8,  "speed": 10, "str":12,"dex":6,"con":16,"int":1,"wis":6,"cha":2,
     "attacks": [{"name":"Pseudopod","hit":"+3","dmg":"1d6+1 bludgeoning + 1d6 acid (non-magic metal corroded: -1 AC per hit)"}]},
    {"name": "Ochre Jelly",         "cr": "2",    "xp": 450,   "type": "ooze",       "env": ["dungeon","cave"],
     "hp": "6d10+12", "ac": 8,  "speed": "10ft, climb 10ft", "str":15,"dex":6,"con":14,"int":2,"wis":6,"cha":1,
     "attacks": [{"name":"Pseudopod","hit":"+4","dmg":"2d6+2 bludgeoning + 1d6 acid"},{"name":"Split","hit":"—","dmg":"When hit by slashing/lightning: splits into two CR 1/2 jellies"}]},

    # ════════════════════════════════════════════════════════
    # PLANTS (expanded)
    # ════════════════════════════════════════════════════════
    {"name": "Shambling Mound",     "cr": "5",    "xp": 1800,  "type": "plant",      "env": ["swamp","forest"],
     "hp": "16d10+48", "ac": 15, "speed": "20ft, swim 20ft", "str":18,"dex":8,"con":16,"int":5,"wis":10,"cha":5,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Slam","hit":"+7","dmg":"2d8+4 bludgeoning (grapple DC 14)"},{"name":"Engulf","hit":"—","dmg":"Grappled creature swallowed — blinded, restrained, 2d8+4 bludgeoning/turn"}]},
    {"name": "Myconid Adult",       "cr": "1/2",  "xp": 100,   "type": "plant",      "env": ["dungeon","cave","underdark"],
     "hp": "5d8", "ac": 12, "speed": 20, "str":10,"dex":10,"con":12,"int":10,"wis":11,"cha":9,
     "attacks": [{"name":"Fist","hit":"+2","dmg":"1d6 bludgeoning + 1d6 poison"},{"name":"Rapport Spores","hit":"—","dmg":"Willing creatures telepathically linked (30ft radius)"},{"name":"Pacifying Spores (3/day)","hit":"—","dmg":"DC 11 Con or stunned 1 min (only non-plants)"}]},
    {"name": "Myconid Sovereign",   "cr": "2",    "xp": 450,   "type": "plant",      "env": ["dungeon","cave","underdark"],
     "hp": "9d8+9", "ac": 13, "speed": 30, "str":12,"dex":10,"con":12,"int":10,"wis":13,"cha":9,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Slam","hit":"+3","dmg":"1d8+1 bludgeoning + 1d8 poison"},{"name":"Animating Spores (6/day)","hit":"—","dmg":"Humanoid corpse rises as spore servant"},{"name":"Hallucination Spores","hit":"—","dmg":"DC 12 Con or poisoned and incapacitated 1 min (30ft)"}]},
    {"name": "Myconid Sprout",      "cr": "0",    "xp": 10,    "type": "plant",      "env": ["dungeon","cave"],
     "hp": "2d6-2", "ac": 10, "speed": 10, "str":8,"dex":10,"con":10,"int":8,"wis":11,"cha":5,
     "attacks": [{"name":"Fist","hit":"+1","dmg":"1d4-1 bludgeoning + 1d4 poison"},{"name":"Pacifying Spores","hit":"—","dmg":"DC 10 Con or stunned 1 min"}]},

    # ════════════════════════════════════════════════════════
    # UNDEAD (expanded)
    # ════════════════════════════════════════════════════════
    {"name": "Revenant",            "cr": "5",    "xp": 1800,  "type": "undead",     "env": ["dungeon","crypt","graveyard","any"],
     "hp": "13d8+26", "ac": 13, "speed": 30, "str":18,"dex":14,"con":18,"int":13,"wis":16,"cha":18,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Fist","hit":"+7","dmg":"2d6+4 bludgeoning + 3d6 psychic (DC 14 Wis or frightened)"},{"name":"Vengeful Glare","hit":"—","dmg":"DC 15 Wis or paralyzed 1 min (30ft, only target of revenge)"}]},
    {"name": "Mummy",               "cr": "3",    "xp": 700,   "type": "undead",     "env": ["dungeon","crypt","desert"],
     "hp": "9d8+36", "ac": 11, "speed": 20, "str":16,"dex":8,"con":15,"int":6,"wis":10,"cha":12,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Rotting Fist","hit":"+5","dmg":"2d6+3 bludgeoning + DC 12 Con or cursed (rotting disease, max HP halved each day until cure)"},{"name":"Dreadful Glare","hit":"—","dmg":"DC 11 Wis or frightened until end of next turn"}]},
    {"name": "Mummy Lord",          "cr": "15",   "xp": 13000, "type": "undead",     "env": ["dungeon","crypt","desert"],
     "hp": "13d8+65", "ac": 17, "speed": 20, "str":18,"dex":10,"con":17,"int":11,"wis":18,"cha":16,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks + one use of Dreadful Glare"},{"name":"Rotting Fist","hit":"+9","dmg":"3d6+4 bludgeoning + DC 17 Con or mummy rot curse"},{"name":"Dreadful Glare","hit":"—","dmg":"DC 16 Wis or frightened + paralyzed if fails by 5+"},{"name":"Legendary Actions","hit":"—","dmg":"Attack, Blinding Dust, Blasphemous Word, Channel Negative Energy, Whirlwind of Sand"}]},
    {"name": "Demilich",            "cr": "18",   "xp": 20000, "type": "undead",     "env": ["dungeon"],
     "hp": "20d4", "ac": 20, "speed": "0ft, fly 30ft (hover)", "str":1,"dex":20,"con":10,"int":20,"wis":17,"cha":20,
     "attacks": [{"name":"Howl (recharge 5-6)","hit":"—","dmg":"DC 15 Con: 4d6+5 psychic, failure by 10+ = instant death"},{"name":"Life Drain","hit":"—","dmg":"Max HP reduced by 3d6+5 (DC 19 Con)"},{"name":"Legendary Resistances (3/day)","hit":"—","dmg":"Succeed on failed save"},{"name":"Teleport","hit":"—","dmg":"Legendary Action: teleport up to 30ft"}]},
    {"name": "Death Tyrant",        "cr": "14",   "xp": 11500, "type": "undead",     "env": ["dungeon","underdark"],
     "hp": "19d10+95", "ac": 19, "speed": "0ft, fly 20ft (hover)", "str":10,"dex":14,"con":18,"int":19,"wis":15,"cha":19,
     "attacks": [{"name":"Eye Rays","hit":"—","dmg":"3 random rays (same as beholder) + central eye: antimagic cone (undead immune)"},{"name":"Create Undead","hit":"—","dmg":"Creatures reduced to 0 HP by eye rays rise as zombies under its control"}]},
    {"name": "Poltergeist",         "cr": "2",    "xp": 450,   "type": "undead",     "env": ["dungeon","crypt","city"],
     "hp": "9d8", "ac": 12, "speed": "0ft, fly 50ft (hover)", "str":1,"dex":14,"con":11,"int":10,"wis":10,"cha":11,
     "attacks": [{"name":"Forceful Slam","hit":"+4","dmg":"3d6 force"},{"name":"Telekinetic Thrust","hit":"+4","dmg":"DC 12 Str or hurled up to 30ft — 1d6 per 10ft fall"}]},
    {"name": "Flameskull",          "cr": "4",    "xp": 1100,  "type": "undead",     "env": ["dungeon","crypt"],
     "hp": "9d4", "ac": 13, "speed": "0ft, fly 40ft (hover)", "str":1,"dex":17,"con":14,"int":16,"wis":10,"cha":11,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Fire Ray","hit":"+5","dmg":"3d6 fire (30ft)"},{"name":"Fireball (3/day)","hit":"—","dmg":"8d6 fire, DC 13 Dex half"},{"name":"Rejuvenation","hit":"—","dmg":"Returns in 1 hour unless holy water/dispel magic used"}]},
    {"name": "Swarm of Zombies",    "cr": "3",    "xp": 700,   "type": "undead",     "env": ["dungeon","crypt","graveyard"],
     "hp": "9d10+18", "ac": 8,  "speed": 20, "str":14,"dex":6,"con":16,"int":3,"wis":6,"cha":5,
     "attacks": [{"name":"Slams","hit":"+4","dmg":"4d6+2 bludgeoning (or 2d6+2 if half HP)"}]},
    {"name": "Ghost",               "cr": "4",    "xp": 1100,  "type": "undead",     "env": ["dungeon","crypt","city","graveyard"],
     "hp": "10d8", "ac": 11, "speed": "0ft, fly 40ft (hover)", "str":7,"dex":13,"con":10,"int":10,"wis":12,"cha":17,
     "attacks": [{"name":"Withering Touch","hit":"+5","dmg":"4d6+3 necrotic"},{"name":"Horrifying Visage","hit":"—","dmg":"DC 13 Wis or frightened 1 min (can age 1d4×10 yrs on fail)"},{"name":"Possession (recharge 6)","hit":"—","dmg":"DC 13 Cha or possessed — ghost controls body, host immune to further possession"}]},

    # ════════════════════════════════════════════════════════
    # DRAGONS (remaining colors)
    # ════════════════════════════════════════════════════════
    {"name": "Young Dragon (White)","cr": "6",    "xp": 2300,  "type": "dragon",     "env": ["arctic","mountain"],
     "hp": "14d10+42", "ac": 17, "speed": "40ft, burrow 20ft, fly 80ft, swim 40ft", "str":18,"dex":10,"con":17,"int":6,"wis":11,"cha":12,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Bite","hit":"+7","dmg":"2d10+4 piercing"},{"name":"Cold Breath","hit":"—","dmg":"10d8 cold (DC 14 Con half, 30ft cone, recharge 5-6)"}]},
    {"name": "Young Dragon (Black)","cr": "7",    "xp": 2900,  "type": "dragon",     "env": ["swamp","dungeon"],
     "hp": "15d10+45", "ac": 18, "speed": "40ft, fly 80ft, swim 40ft", "str":19,"dex":14,"con":17,"int":12,"wis":11,"cha":15,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Bite","hit":"+7","dmg":"2d10+4 piercing + 1d8 acid"},{"name":"Acid Breath","hit":"—","dmg":"11d8 acid (DC 14 Dex half, 30ft×5ft line, recharge 5-6)"}]},
    {"name": "Young Dragon (Copper)","cr":"7",    "xp": 2900,  "type": "dragon",     "env": ["mountain","dungeon"],
     "hp": "16d10+48", "ac": 17, "speed": "40ft, climb 40ft, fly 80ft", "str":19,"dex":12,"con":17,"int":16,"wis":13,"cha":15,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Bite","hit":"+7","dmg":"2d10+4 piercing"},{"name":"Acid Breath","hit":"—","dmg":"9d8 acid (DC 14 Dex half, recharge 5-6)"},{"name":"Slowing Breath","hit":"—","dmg":"DC 14 Con or slowed — half speed, no reactions, 1 attack (recharge 5-6)"}]},
    {"name": "Young Dragon (Silver)","cr":"9",    "xp": 5000,  "type": "dragon",     "env": ["mountain","arctic"],
     "hp": "16d10+64", "ac": 18, "speed": "40ft, fly 80ft", "str":23,"dex":10,"con":21,"int":14,"wis":11,"cha":19,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Bite","hit":"+10","dmg":"2d10+6 piercing"},{"name":"Cold Breath","hit":"—","dmg":"12d8 cold (DC 17 Con half, recharge 5-6)"},{"name":"Paralyzing Breath","hit":"—","dmg":"DC 17 Con or paralyzed 1 min (recharge 5-6)"}]},
    {"name": "Young Dragon (Gold)", "cr": "10",   "xp": 5900,  "type": "dragon",     "env": ["grassland","coast","dungeon"],
     "hp": "17d10+85", "ac": 18, "speed": "40ft, fly 80ft, swim 40ft", "str":23,"dex":14,"con":21,"int":16,"wis":13,"cha":20,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Bite","hit":"+10","dmg":"2d10+6 piercing"},{"name":"Fire Breath","hit":"—","dmg":"12d10 fire (DC 17 Dex half, 30ft cone, recharge 5-6)"},{"name":"Weakening Breath","hit":"—","dmg":"DC 17 Str or disadvantage on Str checks/saves/attacks 1 min (recharge 5-6)"}]},
    {"name": "Young Dragon (Brass)","cr": "6",    "xp": 2300,  "type": "dragon",     "env": ["desert","grassland"],
     "hp": "13d10+39", "ac": 17, "speed": "40ft, burrow 20ft, fly 80ft", "str":19,"dex":10,"con":17,"int":12,"wis":11,"cha":15,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Bite","hit":"+7","dmg":"2d10+4 piercing"},{"name":"Fire Breath","hit":"—","dmg":"9d6 fire (DC 14 Dex half, 40ft×5ft line, recharge 5-6)"},{"name":"Sleep Breath","hit":"—","dmg":"DC 14 Con or asleep 5 min (60ft cone, recharge 5-6)"}]},
    {"name": "Adult Dragon (Green)","cr":"15",    "xp": 13000, "type": "dragon",     "env": ["forest"],
     "hp": "18d12+90", "ac": 19, "speed": "40ft, fly 80ft, swim 40ft", "str":23,"dex":12,"con":21,"int":18,"wis":15,"cha":17,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Bite","hit":"+11","dmg":"2d10+6 piercing + 2d6 poison"},{"name":"Claw","hit":"+11","dmg":"2d6+6 slashing"},{"name":"Poison Breath","hit":"—","dmg":"16d6 poison (DC 18 Con half, 60ft cone, recharge 5-6)"}]},
    {"name": "Adult Dragon (Black)","cr":"14",    "xp": 11500, "type": "dragon",     "env": ["swamp","dungeon"],
     "hp": "17d12+68", "ac": 19, "speed": "40ft, fly 80ft, swim 40ft", "str":23,"dex":14,"con":21,"int":14,"wis":13,"cha":17,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Bite","hit":"+11","dmg":"2d10+6 piercing + 2d8 acid"},{"name":"Acid Breath","hit":"—","dmg":"13d8 acid (DC 18 Dex half, 90ft×5ft line, recharge 5-6)"}]},
    {"name": "Adult Dragon (White)","cr":"13",    "xp": 10000, "type": "dragon",     "env": ["arctic","mountain"],
     "hp": "18d12+72", "ac": 18, "speed": "40ft, burrow 30ft, fly 80ft, swim 40ft", "str":22,"dex":10,"con":22,"int":8,"wis":12,"cha":12,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Bite","hit":"+11","dmg":"2d10+6 piercing"},{"name":"Cold Breath","hit":"—","dmg":"16d8 cold (DC 19 Con half, 60ft cone, recharge 5-6)"}]},
    {"name": "Adult Dragon (Silver)","cr":"16",   "xp": 15000, "type": "dragon",     "env": ["mountain","arctic"],
     "hp": "18d12+108", "ac": 19, "speed": "40ft, fly 80ft", "str":27,"dex":10,"con":25,"int":16,"wis":13,"cha":21,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Bite","hit":"+13","dmg":"2d10+8 piercing"},{"name":"Cold Breath","hit":"—","dmg":"12d8 cold (DC 20 Con half, 60ft cone, recharge 5-6)"},{"name":"Paralyzing Breath","hit":"—","dmg":"DC 20 Con or paralyzed 1 min (recharge 5-6)"}]},
    {"name": "Adult Dragon (Gold)", "cr":"17",    "xp": 18000, "type": "dragon",     "env": ["grassland","coast"],
     "hp": "19d12+133", "ac": 19, "speed": "40ft, fly 80ft, swim 40ft", "str":27,"dex":14,"con":25,"int":16,"wis":13,"cha":24,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Bite","hit":"+14","dmg":"2d10+8 piercing"},{"name":"Fire Breath","hit":"—","dmg":"12d10 fire (DC 22 Dex half, 60ft cone, recharge 5-6)"},{"name":"Weakening Breath","hit":"—","dmg":"DC 22 Str or disadvantage on Str (recharge 5-6)"}]},
    {"name": "Ancient Dragon (White)","cr":"20",  "xp": 25000, "type": "dragon",     "env": ["arctic","mountain"],
     "hp": "18d20+126", "ac": 20, "speed": "40ft, burrow 40ft, fly 80ft, swim 40ft", "str":26,"dex":10,"con":26,"int":10,"wis":13,"cha":14,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Bite","hit":"+14","dmg":"2d10+8 piercing"},{"name":"Cold Breath","hit":"—","dmg":"20d8 cold (DC 22 Con half, 90ft cone, recharge 5-6)"}]},
    {"name": "Ancient Dragon (Black)","cr":"21",  "xp": 33000, "type": "dragon",     "env": ["swamp","dungeon"],
     "hp": "21d20+147", "ac": 22, "speed": "40ft, fly 80ft, swim 40ft", "str":27,"dex":14,"con":25,"int":16,"wis":15,"cha":19,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Bite","hit":"+14","dmg":"2d10+8 piercing + 2d8 acid"},{"name":"Acid Breath","hit":"—","dmg":"15d8 acid (DC 22 Dex half, 120ft×5ft line, recharge 5-6)"}]},
    {"name": "Ancient Dragon (Green)","cr":"22",  "xp": 41000, "type": "dragon",     "env": ["forest"],
     "hp": "22d20+176", "ac": 21, "speed": "40ft, fly 80ft, swim 40ft", "str":27,"dex":12,"con":25,"int":20,"wis":17,"cha":19,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Bite","hit":"+15","dmg":"2d10+8 piercing + 2d6 poison"},{"name":"Poison Breath","hit":"—","dmg":"22d6 poison (DC 22 Con half, 90ft cone, recharge 5-6)"}]},
    {"name": "Ancient Dragon (Silver)","cr":"23", "xp": 50000, "type": "dragon",     "env": ["mountain","arctic"],
     "hp": "25d20+200", "ac": 22, "speed": "40ft, fly 80ft", "str":30,"dex":10,"con":29,"int":18,"wis":15,"cha":23,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Bite","hit":"+17","dmg":"2d10+10 piercing"},{"name":"Cold Breath","hit":"—","dmg":"20d8 cold (DC 24 Con half, recharge 5-6)"},{"name":"Paralyzing Breath","hit":"—","dmg":"DC 24 Con or paralyzed 1 min (recharge 5-6)"}]},
    {"name": "Ancient Dragon (Gold)","cr":"24",   "xp": 62000, "type": "dragon",     "env": ["grassland","coast"],
     "hp": "28d20+252", "ac": 22, "speed": "40ft, fly 80ft, swim 40ft", "str":30,"dex":14,"con":29,"int":18,"wis":17,"cha":28,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Bite","hit":"+17","dmg":"2d10+10 piercing"},{"name":"Fire Breath","hit":"—","dmg":"26d6 fire (DC 24 Dex half, 90ft cone, recharge 5-6)"},{"name":"Weakening Breath","hit":"—","dmg":"DC 24 Str (recharge 5-6)"}]},

    # ════════════════════════════════════════════════════════
    # CELESTIALS
    # ════════════════════════════════════════════════════════
    {"name": "Couatl",              "cr": "4",    "xp": 1100,  "type": "celestial",  "env": ["forest","dungeon","any"],
     "hp": "13d8+26", "ac": 19, "speed": "30ft, fly 90ft", "str":16,"dex":20,"con":17,"int":18,"wis":20,"cha":18,
     "attacks": [{"name":"Bite","hit":"+8","dmg":"1d6+5 piercing + 2d6 psychic (DC 13 Con or poisoned, asleep on fail)"},{"name":"Constrict","hit":"+6","dmg":"2d6+3 bludgeoning (grapple DC 15)"},{"name":"Spellcasting","hit":"—","dmg":"Detect evil, detect thoughts, create food, daylight, lesser restoration, scrying, freedom of movement, dream (DC 14)"}]},
    {"name": "Deva",                "cr": "10",   "xp": 5900,  "type": "celestial",  "env": ["any"],
     "hp": "16d8+48", "ac": 17, "speed": "30ft, fly 90ft", "str":18,"dex":18,"con":18,"int":17,"wis":20,"cha":20,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Mace","hit":"+8","dmg":"1d6+4 bludgeoning + 4d8 radiant"},{"name":"Healing Touch (3/day)","hit":"—","dmg":"Restore 2d8+7 HP, remove curse/disease/poison"},{"name":"Change Shape","hit":"—","dmg":"Assume humanoid or beast form"}]},
    {"name": "Planetar",            "cr": "16",   "xp": 15000, "type": "celestial",  "env": ["any"],
     "hp": "16d10+80", "ac": 19, "speed": "40ft, fly 120ft", "str":24,"dex":20,"con":24,"int":19,"wis":22,"cha":25,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Greatsword","hit":"+12","dmg":"4d6+7 slashing + 5d8 radiant"},{"name":"Healing Touch (4/day)","hit":"—","dmg":"Restore 4d8+7 HP"},{"name":"Spellcasting","hit":"—","dmg":"Commune, control weather, dispel evil, flame strike, raise dead (DC 20)"}]},
    {"name": "Solar",               "cr": "21",   "xp": 33000, "type": "celestial",  "env": ["any"],
     "hp": "18d10+126", "ac": 21, "speed": "50ft, fly 150ft", "str":26,"dex":22,"con":26,"int":25,"wis":25,"cha":30,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks (or 2 ranged)"},{"name":"Greatsword","hit":"+15","dmg":"4d6+8 slashing + 6d8 radiant"},{"name":"Slaying Longbow","hit":"+13","dmg":"2d8+6 piercing + 6d8 radiant (DC 15 Con or stunned)","range":"150/600ft"},{"name":"Spellcasting","hit":"—","dmg":"Commune, control weather, divine word, resurrection (DC 25)"}]},

    # ════════════════════════════════════════════════════════
    # ADDITIONAL MISC & CLASSIC ENCOUNTERS
    # ════════════════════════════════════════════════════════
    {"name": "Werewolf (pack)",     "cr": "4",    "xp": 1100,  "type": "humanoid",   "env": ["forest","mountain","grassland"],
     "hp": "8d8+16", "ac": 12, "speed": "30ft (wolf: 40ft)", "str":15,"dex":13,"con":14,"int":10,"wis":11,"cha":10,
     "attacks": [{"name":"Multiattack (humanoid/hybrid)","hit":"—","dmg":"2 attacks"},{"name":"Spear","hit":"+4","dmg":"1d8+2 piercing"},{"name":"Claws (hybrid)","hit":"+4","dmg":"2d4+2 slashing"},{"name":"Bite","hit":"+4","dmg":"2d6+2 piercing (DC 12 Con or lycanthropy)"}]},
    {"name": "Girallon",            "cr": "4",    "xp": 1100,  "type": "monstrosity","env": ["forest","dungeon"],
     "hp": "8d10+24", "ac": 13, "speed": "40ft, climb 40ft", "str":18,"dex":16,"con":16,"int":5,"wis":12,"cha":7,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"5 attacks"},{"name":"Claw","hit":"+6","dmg":"1d6+4 slashing"}]},
    {"name": "Darkmantle",          "cr": "1/2",  "xp": 100,   "type": "monstrosity","env": ["cave","dungeon"],
     "hp": "6d6+6", "ac": 11, "speed": "10ft, fly 30ft", "str":16,"dex":12,"con":13,"int":2,"wis":10,"cha":5,
     "attacks": [{"name":"Crush","hit":"+5","dmg":"1d6+3 bludgeoning (grapple DC 13, darkness spell affects area while grappling)"}]},
    {"name": "Cloaker",             "cr": "8",    "xp": 3900,  "type": "aberration", "env": ["dungeon","underdark"],
     "hp": "12d10+24", "ac": 14, "speed": "10ft, fly 40ft", "str":17,"dex":15,"con":12,"int":13,"wis":12,"cha":14,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Bite","hit":"+6","dmg":"2d6+3 piercing"},{"name":"Tail","hit":"+6","dmg":"1d10+3 slashing"},{"name":"Engulf","hit":"—","dmg":"Attacks versus grappled creature hit cloaker on miss"},{"name":"Moan","hit":"—","dmg":"DC 13 Wis or frightened until end of next turn"}]},
    {"name": "Purple Worm",         "cr": "15",   "xp": 13000, "type": "monstrosity","env": ["dungeon","desert","underground"],
     "hp": "15d20+105", "ac": 18, "speed": "50ft, burrow 30ft", "str":28,"dex":7,"con":22,"int":1,"wis":8,"cha":4,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Bite","hit":"+14","dmg":"3d8+9 piercing (DC 19 Dex or swallowed: blinded, restrained, 6d6 acid/turn)"},{"name":"Tail Stinger","hit":"+14","dmg":"3d6+9 piercing + 7d6 poison (DC 19 Con or poisoned, 12 damage/turn for 7 rounds)"}]},
    {"name": "Otyugh",              "cr": "5",    "xp": 1800,  "type": "aberration", "env": ["dungeon","sewer","swamp"],
     "hp": "12d10+36", "ac": 14, "speed": 30, "str":16,"dex":11,"con":19,"int":6,"wis":13,"cha":6,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Tentacle","hit":"+6","dmg":"1d8+3 bludgeoning + 1d8+3 piercing (grapple DC 13)"},{"name":"Bite","hit":"+6","dmg":"2d8+3 piercing (DC 15 Con or diseased)"},{"name":"Psychic Crush (recharge 5-6)","hit":"—","dmg":"DC 14 Int or 4d8+3 psychic and stunned until end of next turn (30ft)"}]},
    {"name": "Rust Monster",        "cr": "1/2",  "xp": 100,   "type": "monstrosity","env": ["dungeon","cave"],
     "hp": "5d8+5", "ac": 14, "speed": 40, "str":13,"dex":12,"con":13,"int":2,"wis":13,"cha":6,
     "attacks": [{"name":"Bite","hit":"+3","dmg":"1d8+1 piercing"},{"name":"Antennae","hit":"+3","dmg":"Non-magical metal weapon or armor touched: permanently -1 AC/damage (destroyed at -5)"}]},
    {"name": "Galeb Duhr",          "cr": "6",    "xp": 2300,  "type": "elemental",  "env": ["mountain","cave","dungeon"],
     "hp": "14d10+28", "ac": 16, "speed": "15ft, burrow 15ft", "str":20,"dex":14,"con":14,"int":11,"wis":12,"cha":11,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Slam","hit":"+8","dmg":"2d10+5 bludgeoning"},{"name":"Animate Boulders (1/day)","hit":"—","dmg":"Up to 2 boulders animate as awakened earth creatures for 1 min"}]},
    {"name": "Bullywug",            "cr": "1/4",  "xp": 50,    "type": "humanoid",   "env": ["swamp","cave"],
     "hp": "2d8", "ac": 15, "speed": "20ft, swim 40ft", "str":12,"dex":12,"con":13,"int":7,"wis":10,"cha":7,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Bite","hit":"+3","dmg":"1d4+1 piercing"},{"name":"Spear","hit":"+3","dmg":"1d6+1 piercing"}]},
    {"name": "Tabaxi Rogue",        "cr": "1",    "xp": 200,   "type": "humanoid",   "env": ["city","forest","dungeon"],
     "hp": "4d8+4", "ac": 14, "speed": "30ft, climb 20ft", "str":10,"dex":17,"con":12,"int":12,"wis":14,"cha":14,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Shortsword","hit":"+5","dmg":"1d6+3 piercing"},{"name":"Claws","hit":"+5","dmg":"1d4+3 slashing"}]},
    {"name": "Lizardfolk Shaman",   "cr": "2",    "xp": 450,   "type": "humanoid",   "env": ["swamp","dungeon"],
     "hp": "9d8+9", "ac": 13, "speed": "30ft, swim 30ft", "str":15,"dex":10,"con":13,"int":10,"wis":15,"cha":8,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Claws","hit":"+4","dmg":"1d6+2 slashing"},{"name":"Spellcasting","hit":"—","dmg":"Shillelagh, guidance, poison spray, animal friendship, speak with animals, conjure animals (DC 12)"}]},

    # ════════════════════════════════════════════════════════
    # ABERRATIONS (additional)
    # ════════════════════════════════════════════════════════
    {"name": "Spectator",           "cr": "3",    "xp": 700,   "type": "aberration", "env": ["dungeon"],
     "hp": "7d8+7", "ac": 14, "speed": "0ft, fly 30ft (hover)", "str":8,"dex":14,"con":14,"int":13,"wis":14,"cha":11,
     "attacks": [{"name":"Eye Rays","hit":"—","dmg":"2 random rays — confusion (DC 13 Wis), paralyzing (DC 13 Con), wounding (+5, 3d6 piercing), or maddening"},{"name":"Bite","hit":"+1","dmg":"1d6-1 piercing"}]},
    {"name": "Beholder Zombie",     "cr": "5",    "xp": 1800,  "type": "undead",     "env": ["dungeon"],
     "hp": "11d10+44", "ac": 15, "speed": "0ft, fly 20ft (hover)", "str":10,"dex":8,"con":16,"int":3,"wis":8,"cha":5,
     "attacks": [{"name":"Bite","hit":"+3","dmg":"4d6 piercing"},{"name":"Eye Ray (1/turn)","hit":"—","dmg":"Random single ray from beholder list (DC 12)"}]},
    {"name": "Mindwitness",         "cr": "5",    "xp": 1800,  "type": "aberration", "env": ["dungeon","underdark"],
     "hp": "9d10+27", "ac": 15, "speed": "0ft, fly 20ft (hover)", "str":10,"dex":14,"con":14,"int":15,"wis":15,"cha":10,
     "attacks": [{"name":"Eye Rays","hit":"—","dmg":"2 random rays (telekinetic, charming, paralyzing, wounding)"},{"name":"Tentacles","hit":"+5","dmg":"2d10+2 psychic (DC 13 Int or stunned)"}]},
    {"name": "Neogi",               "cr": "3",    "xp": 700,   "type": "aberration", "env": ["dungeon","underdark"],
     "hp": "7d6+7", "ac": 15, "speed": 30, "str":6,"dex":16,"con":12,"int":13,"wis":12,"cha":15,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Bite","hit":"+5","dmg":"1d6+3 piercing + 3d6 poison (DC 12 Con)"},{"name":"Claws","hit":"+5","dmg":"1d6+3 slashing"},{"name":"Enslave (3/day)","hit":"—","dmg":"DC 14 Wis or charmed until cured (100ft)"}]},
    {"name": "Ulitharid",           "cr": "9",    "xp": 5000,  "type": "aberration", "env": ["dungeon","underdark"],
     "hp": "13d10+26", "ac": 15, "speed": 30, "str":15,"dex":12,"con":15,"int":21,"wis":19,"cha":21,
     "attacks": [{"name":"Tentacles","hit":"+9","dmg":"2d10+5 psychic (DC 17 Int or stunned)"},{"name":"Extract Brain","hit":"+9","dmg":"10d10 piercing (kills stunned creatures)"},{"name":"Mind Blast (recharge 5-6)","hit":"—","dmg":"6d8+5 psychic (DC 17 Int or stunned, 90ft cone)"}]},
    {"name": "Elder Brain",         "cr": "14",   "xp": 11500, "type": "aberration", "env": ["dungeon","underdark"],
     "hp": "21d10+84", "ac": 10, "speed": "5ft, swim 10ft", "str":15,"dex":10,"con":20,"int":21,"wis":19,"cha":24,
     "attacks": [{"name":"Tentacle","hit":"+7","dmg":"4d8+2 bludgeoning + DC 15 Int or stunned"},{"name":"Mind Blast (recharge 5-6)","hit":"—","dmg":"10d8+5 psychic (DC 18 Int or stunned, 60ft radius)"},{"name":"Psychic Link","hit":"—","dmg":"Dominate monster at will (DC 18) on up to 5 mind flayers in range"},{"name":"Legendary Actions","hit":"—","dmg":"Tentacle, Psychic Pulse, Break Concentration"}]},

    # ════════════════════════════════════════════════════════
    # MORE UNDEAD
    # ════════════════════════════════════════════════════════
    {"name": "Allip",               "cr": "5",    "xp": 1800,  "type": "undead",     "env": ["dungeon","crypt","graveyard"],
     "hp": "10d8", "ac": 13, "speed": "0ft, fly 40ft (hover)", "str":6,"dex":17,"con":10,"int":17,"wis":15,"cha":17,
     "attacks": [{"name":"Maddening Touch","hit":"+6","dmg":"4d8+3 psychic"},{"name":"Whispers of Madness","hit":"—","dmg":"DC 14 Wis or charmed until end of next turn — attack nearest ally"},{"name":"Babble","hit":"—","dmg":"DC 13 Wis or incapacitated until end of next turn (60ft, concentration)"}]},
    {"name": "Sword Wraith",        "cr": "8",    "xp": 3900,  "type": "undead",     "env": ["dungeon","crypt","graveyard"],
     "hp": "10d8+30", "ac": 16, "speed": "0ft, fly 60ft (hover)", "str":18,"dex":14,"con":15,"int":11,"wis":12,"cha":14,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Longsword","hit":"+7","dmg":"1d8+4 slashing + 4d8 necrotic"},{"name":"Martial Fury","hit":"—","dmg":"Allies within 30ft gain +1d6 to attacks until end of its next turn (bonus action)"}]},
    {"name": "Deathlock",           "cr": "4",    "xp": 1100,  "type": "undead",     "env": ["dungeon","crypt"],
     "hp": "7d8", "ac": 13, "speed": 30, "str":11,"dex":16,"con":10,"int":14,"wis":12,"cha":16,
     "attacks": [{"name":"Deathly Claw","hit":"+5","dmg":"1d6+3 slashing + 2d6 necrotic"},{"name":"Spellcasting","hit":"—","dmg":"Eldritch Blast (+5, 1d10+3 force), Dispel Magic, Hold Person, Hunger of Hadar (DC 14)"}]},
    {"name": "Boneclaw",            "cr": "12",   "xp": 8400,  "type": "undead",     "env": ["dungeon","crypt"],
     "hp": "18d10+54", "ac": 16, "speed": 40, "str":21,"dex":18,"con":15,"int":10,"wis":12,"cha":7,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Piercing Claw (reach 15ft)","hit":"+9","dmg":"3d6+5 slashing + 3d6 cold"},{"name":"Slash to the Bone","hit":"—","dmg":"On hit, target's speed halved until healed (DC 18 Con)"}]},
    {"name": "Strahd Zombie",       "cr": "1",    "xp": 200,   "type": "undead",     "env": ["dungeon","crypt"],
     "hp": "5d8+10", "ac": 8,  "speed": 20, "str":13,"dex":5,"con":15,"int":3,"wis":6,"cha":5,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Slam","hit":"+3","dmg":"1d6+1 bludgeoning"},{"name":"Undead Fortitude","hit":"—","dmg":"When reduced to 0, DC 10+damage Con save or falls — stands 1 min later at 1 HP (fire damage or critical: no save)"}]},
    {"name": "Crawling Claw (swarm)","cr":"1",    "xp": 200,   "type": "undead",     "env": ["dungeon","crypt"],
     "hp": "4d8", "ac": 12, "speed": 25, "str":14,"dex":14,"con":11,"int":5,"wis":10,"cha":4,
     "attacks": [{"name":"Claws","hit":"+4","dmg":"2d6+2 slashing (or 1d6+2 if half HP)"}]},
    {"name": "Zombie Ogre",         "cr": "2",    "xp": 450,   "type": "undead",     "env": ["dungeon","graveyard"],
     "hp": "9d10+36", "ac": 8,  "speed": 30, "str":18,"dex":6,"con":18,"int":3,"wis":6,"cha":5,
     "attacks": [{"name":"Morningstar","hit":"+6","dmg":"2d8+4 bludgeoning"},{"name":"Undead Fortitude","hit":"—","dmg":"DC 5+damage Con or stays at 1 HP (not vs fire/crits)"}]},
    {"name": "Undead Bulette",      "cr": "6",    "xp": 2300,  "type": "undead",     "env": ["dungeon","graveyard"],
     "hp": "9d10+45", "ac": 17, "speed": "40ft, burrow 40ft", "str":19,"dex":11,"con":21,"int":2,"wis":10,"cha":5,
     "attacks": [{"name":"Bite","hit":"+7","dmg":"4d12+4 piercing"},{"name":"Deadly Leap","hit":"—","dmg":"3d6+4 + 3d6+4 (DC 16 Str or prone)"}]},

    # ════════════════════════════════════════════════════════
    # MORE FIENDS (Yugoloth, lesser demons)
    # ════════════════════════════════════════════════════════
    {"name": "Mezzoloth",           "cr": "5",    "xp": 1800,  "type": "fiend",      "env": ["dungeon","city"],
     "hp": "10d8+40", "ac": 18, "speed": 40, "str":18,"dex":11,"con":18,"int":8,"wis":12,"cha":8,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Trident","hit":"+7","dmg":"1d6+4 piercing"},{"name":"Toxic Cloud (recharge 6)","hit":"—","dmg":"DC 15 Con: 3d8 poison, poisoned 1 min (20ft radius)"}]},
    {"name": "Nycaloth",            "cr": "9",    "xp": 5000,  "type": "fiend",      "env": ["dungeon","city"],
     "hp": "14d10+56", "ac": 18, "speed": "40ft, fly 60ft", "str":20,"dex":11,"con":19,"int":12,"wis":10,"cha":15,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Greataxe","hit":"+9","dmg":"2d12+5 slashing + 1d6 fire"},{"name":"Claw","hit":"+9","dmg":"2d4+5 slashing (teleport after grapple: 60ft)"}]},
    {"name": "Arcanaloth",          "cr": "12",   "xp": 8400,  "type": "fiend",      "env": ["dungeon","city"],
     "hp": "13d8+26", "ac": 17, "speed": "30ft, fly 30ft", "str":17,"dex":12,"con":14,"int":20,"wis":16,"cha":17,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Claws","hit":"+7","dmg":"1d8+3 slashing"},{"name":"Spellcasting","hit":"—","dmg":"Counterspell, Fireball, Cone of Cold, Finger of Death, Wall of Fire (DC 18)"}]},
    {"name": "Ultroloth",           "cr": "13",   "xp": 10000, "type": "fiend",      "env": ["dungeon"],
     "hp": "18d8+54", "ac": 19, "speed": "30ft, fly 60ft", "str":16,"dex":18,"con":18,"int":18,"wis":15,"cha":19,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Longsword","hit":"+8","dmg":"2d8+4 slashing + 2d8 fire"},{"name":"Hypnotic Gaze","hit":"—","dmg":"DC 17 Wis or charmed + incapacitated 1 min"},{"name":"Spellcasting","hit":"—","dmg":"Alter Self, Blur, Detect Thoughts, Hypnotic Pattern, Wall of Fire (DC 17)"}]},
    {"name": "Rutterkin",           "cr": "2",    "xp": 450,   "type": "fiend",      "env": ["dungeon"],
     "hp": "7d8+7", "ac": 12, "speed": 20, "str":14,"dex":13,"con":13,"int":5,"wis":9,"cha":6,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Bite","hit":"+4","dmg":"1d6+2 piercing"},{"name":"Claw","hit":"+4","dmg":"2d4+2 slashing"}]},
    {"name": "Babau",               "cr": "4",    "xp": 1100,  "type": "fiend",      "env": ["dungeon","city"],
     "hp": "9d8+27", "ac": 16, "speed": 40, "str":19,"dex":16,"con":16,"int":11,"wis":12,"cha":13,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Claws","hit":"+7","dmg":"1d6+4 slashing"},{"name":"Weakening Gaze","hit":"—","dmg":"DC 13 Con or Str to 1 for 1 min (range 30ft)"}]},
    {"name": "Chasme",              "cr": "6",    "xp": 2300,  "type": "fiend",      "env": ["dungeon"],
     "hp": "10d10+30", "ac": 15, "speed": "20ft, fly 60ft", "str":15,"dex":15,"con":16,"int":11,"wis":14,"cha":10,
     "attacks": [{"name":"Proboscis","hit":"+5","dmg":"2d6+2 piercing + 3d6 necrotic (DC 13 Con or paralyzed)"},{"name":"Droning (recharge 5-6)","hit":"—","dmg":"DC 12 Con or unconscious 10 min (30ft, not demons)"}]},

    # ════════════════════════════════════════════════════════
    # ADDITIONAL MONSTROSITIES & CLASSIC ENCOUNTERS
    # ════════════════════════════════════════════════════════
    {"name": "Catoblepas",          "cr": "5",    "xp": 1800,  "type": "monstrosity","env": ["swamp"],
     "hp": "10d10+30", "ac": 14, "speed": 30, "str":19,"dex":12,"con":16,"int":3,"wis":14,"cha":8,
     "attacks": [{"name":"Tail","hit":"+7","dmg":"2d6+4 bludgeoning (DC 14 Str or knocked prone)"},{"name":"Death Ray (recharge 5-6)","hit":"—","dmg":"DC 13 Con or drop to 0 HP (range 30ft, line of sight)"}]},
    {"name": "Leucrotta",           "cr": "3",    "xp": 700,   "type": "monstrosity","env": ["grassland","forest","dungeon"],
     "hp": "7d8+21", "ac": 14, "speed": 50, "str":18,"dex":14,"con":17,"int":9,"wis":11,"cha":6,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Bite","hit":"+6","dmg":"2d6+4 piercing (DC 15 Con or stunned)"},{"name":"Cloven Hooves","hit":"+6","dmg":"2d4+4 bludgeoning"},{"name":"Mimicry","hit":"—","dmg":"Imitate any sound or voice it has heard"}]},
    {"name": "Korred",              "cr": "7",    "xp": 2900,  "type": "fey",        "env": ["forest","mountain","cave"],
     "hp": "10d6+30", "ac": 17, "speed": "30ft, burrow 30ft", "str":23,"dex":14,"con":17,"int":10,"wis":15,"cha":9,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Club","hit":"+9","dmg":"1d4+6 bludgeoning + 1d10 thunder"},{"name":"Magic Hair (recharge 4-6)","hit":"—","dmg":"Hair entangles and restrains (DC 13 Str) or animate as separate creature"}]},
    {"name": "Meenlock",            "cr": "2",    "xp": 450,   "type": "fey",        "env": ["dungeon","forest","swamp"],
     "hp": "7d6+7", "ac": 13, "speed": 30, "str":7,"dex":15,"con":12,"int":11,"wis":10,"cha":8,
     "attacks": [{"name":"Claws","hit":"+4","dmg":"2d6+2 slashing"},{"name":"Fear Aura","hit":"—","dmg":"DC 11 Wis or frightened until end of next turn (10ft)"},{"name":"Telepathic Terror","hit":"—","dmg":"DC 11 Wis or psychic distress — can only take action OR move, not both (60ft)"}]},
    {"name": "Froghemoth",          "cr": "10",   "xp": 5900,  "type": "monstrosity","env": ["swamp"],
     "hp": "19d12+95", "ac": 14, "speed": "30ft, swim 30ft", "str":23,"dex":13,"con":20,"int":2,"wis":12,"cha":5,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"1 bite + 4 tentacles"},{"name":"Bite","hit":"+10","dmg":"3d8+6 piercing (swallow DC 18 Dex or swallowed: blinded, restrained, 3d8 acid/turn)"},{"name":"Tentacle","hit":"+10","dmg":"2d6+6 bludgeoning (grapple DC 16)"},{"name":"Tongue","hit":"+10","dmg":"pull grappled creature 20ft closer"}]},
    {"name": "Aurumvorax",          "cr": "6",    "xp": 2300,  "type": "monstrosity","env": ["forest","dungeon","mountain"],
     "hp": "13d8+52", "ac": 15, "speed": "25ft, burrow 25ft", "str":18,"dex":14,"con":18,"int":2,"wis":13,"cha":6,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"5 attacks"},{"name":"Claw","hit":"+7","dmg":"1d4+4 slashing"},{"name":"Bite","hit":"+7","dmg":"2d6+4 piercing (attach: DC 16 Str to remove)"}]},
    {"name": "Brontosaurus",        "cr": "5",    "xp": 1800,  "type": "beast",      "env": ["grassland","forest"],
     "hp": "12d20+60", "ac": 15, "speed": 30, "str":21,"dex":9,"con":17,"int":2,"wis":10,"cha":7,
     "attacks": [{"name":"Stomp","hit":"+8","dmg":"5d8+5 bludgeoning (DC 14 Str or knocked prone)"},{"name":"Tail","hit":"+8","dmg":"5d6+5 bludgeoning (DC 18 Str or knocked prone — 10ft reach)"}]},
    {"name": "Allosaurus",          "cr": "2",    "xp": 450,   "type": "beast",      "env": ["grassland","forest"],
     "hp": "6d10+12", "ac": 13, "speed": 60, "str":19,"dex":13,"con":17,"int":2,"wis":12,"cha":5,
     "attacks": [{"name":"Bite","hit":"+6","dmg":"2d10+4 piercing"},{"name":"Claws","hit":"+6","dmg":"1d8+4 slashing (DC 13 Str or knocked prone)"}]},
    {"name": "Pteranodon",          "cr": "1/4",  "xp": 50,    "type": "beast",      "env": ["coast","grassland","sky"],
     "hp": "3d8+3", "ac": 13, "speed": "10ft, fly 60ft", "str":12,"dex":15,"con":10,"int":2,"wis":9,"cha":5,
     "attacks": [{"name":"Bite","hit":"+3","dmg":"2d4+1 piercing"}]},
    {"name": "Stegosaurus",         "cr": "4",    "xp": 1100,  "type": "beast",      "env": ["grassland","forest"],
     "hp": "11d12+44", "ac": 13, "speed": 40, "str":20,"dex":9,"con":17,"int":2,"wis":11,"cha":5,
     "attacks": [{"name":"Tail","hit":"+7","dmg":"4d6+5 bludgeoning (DC 15 Str or knocked prone)"}]},

    # ════════════════════════════════════════════════════════
    # CLASSIC NPC STAT BLOCKS (PHB/DMG)
    # ════════════════════════════════════════════════════════
    {"name": "Thug",                "cr": "1/2",  "xp": 100,   "type": "humanoid",   "env": ["city","dungeon"],
     "hp": "5d8+10", "ac": 11, "speed": 30, "str":15,"dex":11,"con":14,"int":10,"wis":10,"cha":11,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Mace","hit":"+4","dmg":"1d6+2 bludgeoning"},{"name":"Heavy Crossbow","hit":"+2","dmg":"1d10 piercing","range":"100/400ft"},{"name":"Pack Tactics","hit":"—","dmg":"Advantage on attacks when ally is adjacent to target"}]},
    {"name": "Bandit (pack of 6)",  "cr": "3",    "xp": 700,   "type": "humanoid",   "env": ["road","forest","city"],
     "hp": "12d8", "ac": 12, "speed": 30, "str":11,"dex":12,"con":12,"int":10,"wis":10,"cha":10,
     "attacks": [{"name":"Scimitar x6","hit":"+3","dmg":"1d6+1 slashing per bandit"},{"name":"Light Crossbow x6","hit":"+3","dmg":"1d8+1 piercing","range":"80/320ft"}]},
    {"name": "Commoner",            "cr": "0",    "xp": 10,    "type": "humanoid",   "env": ["city","grassland"],
     "hp": "1d8", "ac": 10, "speed": 30, "str":10,"dex":10,"con":10,"int":10,"wis":10,"cha":10,
     "attacks": [{"name":"Club","hit":"+2","dmg":"1d4 bludgeoning"}]},
    {"name": "Noble",               "cr": "1/8",  "xp": 25,    "type": "humanoid",   "env": ["city"],
     "hp": "2d8", "ac": 15, "speed": 30, "str":11,"dex":12,"con":11,"int":12,"wis":14,"cha":16,
     "attacks": [{"name":"Rapier","hit":"+3","dmg":"1d8+1 piercing"},{"name":"Parry","hit":"—","dmg":"+2 AC reaction against one melee hit"}]},
    {"name": "Cultist",             "cr": "1/8",  "xp": 25,    "type": "humanoid",   "env": ["city","dungeon"],
     "hp": "2d8", "ac": 12, "speed": 30, "str":11,"dex":12,"con":10,"int":10,"wis":11,"cha":10,
     "attacks": [{"name":"Scimitar","hit":"+3","dmg":"1d6+1 slashing"}]},
    {"name": "Acolyte",             "cr": "1/4",  "xp": 50,    "type": "humanoid",   "env": ["city","dungeon"],
     "hp": "2d8", "ac": 10, "speed": 30, "str":10,"dex":10,"con":10,"int":10,"wis":14,"cha":11,
     "attacks": [{"name":"Club","hit":"+2","dmg":"1d4 bludgeoning"},{"name":"Spellcasting","hit":"—","dmg":"Sacred Flame (DC 12), Bless, Cure Wounds, Sanctuary (2 first-level slots)"}]},
    {"name": "Druid",               "cr": "2",    "xp": 450,   "type": "humanoid",   "env": ["forest","grassland","swamp"],
     "hp": "5d8+5", "ac": 11, "speed": 30, "str":10,"dex":12,"con":13,"int":12,"wis":15,"cha":11,
     "attacks": [{"name":"Quarterstaff","hit":"+2","dmg":"1d6 bludgeoning"},{"name":"Spellcasting","hit":"—","dmg":"Thunderwave, Entangle, Shillelagh, Thunderwave, Call Lightning (DC 12)"},{"name":"Wild Shape","hit":"—","dmg":"Transform into CR 1 beast (Brown Bear stat block)"}]},
    {"name": "Warlock of the Fiend","cr": "7",    "xp": 2900,  "type": "humanoid",   "env": ["city","dungeon"],
     "hp": "9d8+18", "ac": 13, "speed": 30, "str":10,"dex":14,"con":15,"int":12,"wis":12,"cha":18,
     "attacks": [{"name":"Mace","hit":"+3","dmg":"1d6 bludgeoning"},{"name":"Spellcasting","hit":"—","dmg":"Eldritch Blast (+7, 1d10+4 force, push/pull 10ft), Fireball, Banishment, Flame Strike (DC 15)"},{"name":"Darkness (2/day)","hit":"—","dmg":"15ft radius magical darkness, 1 min"}]},
    {"name": "Illusionist Wizard",  "cr": "3",    "xp": 700,   "type": "humanoid",   "env": ["city","dungeon"],
     "hp": "7d8", "ac": 11, "speed": 30, "str":9,"dex":14,"con":11,"int":17,"wis":12,"cha":11,
     "attacks": [{"name":"Quarterstaff","hit":"+1","dmg":"1d6-1 bludgeoning"},{"name":"Spellcasting","hit":"—","dmg":"Minor Illusion, Disguise Self, Hypnotic Pattern, Major Image, Phantasmal Force (DC 13)"}]},
    {"name": "Transmuter Wizard",   "cr": "9",    "xp": 5000,  "type": "humanoid",   "env": ["city","dungeon"],
     "hp": "13d8+26", "ac": 12, "speed": 30, "str":9,"dex":14,"con":11,"int":17,"wis":12,"cha":11,
     "attacks": [{"name":"Quarterstaff","hit":"+2","dmg":"1d6-1 bludgeoning"},{"name":"Spellcasting","hit":"—","dmg":"Polymorph, Fly, Disintegrate, Flesh to Stone (DC 16)"},{"name":"Transmuter's Stone","hit":"—","dmg":"Darkvision 60ft, or +10 speed, or proficiency in Con saves, or resistance to one damage type"}]},

    # ════════════════════════════════════════════════════════
    # WILDERNESS & TERRAIN ENCOUNTERS
    # ════════════════════════════════════════════════════════
    {"name": "Will-o-Wisp (swamp)", "cr": "2",    "xp": 450,   "type": "undead",     "env": ["swamp","graveyard","forest"],
     "hp": "9d4", "ac": 19, "speed": "0ft, fly 50ft (hover)", "str":1,"dex":28,"con":10,"int":13,"wis":14,"cha":11,
     "attacks": [{"name":"Shock","hit":"+4","dmg":"2d8 lightning"},{"name":"Consume Life","hit":"—","dmg":"Regain 10d4 HP from dying creature within 5ft"},{"name":"Invisibility","hit":"—","dmg":"Become invisible until attacking or using Consume Life"}]},
    {"name": "Sea Serpent",         "cr": "6",    "xp": 2300,  "type": "beast",      "env": ["coast","underwater"],
     "hp": "11d12+44", "ac": 15, "speed": "30ft, swim 60ft", "str":21,"dex":13,"con":19,"int":2,"wis":12,"cha":6,
     "attacks": [{"name":"Bite","hit":"+8","dmg":"3d6+5 piercing"},{"name":"Constrict","hit":"+8","dmg":"3d6+5 bludgeoning (grapple DC 16, restrained)"},{"name":"Capsizing Wave","hit":"—","dmg":"DC 15 Str or vessel rocks — passengers make DC 10 Athletics or fall overboard"}]},
    {"name": "Storm Crow",          "cr": "1",    "xp": 200,   "type": "beast",      "env": ["mountain","sky","arctic"],
     "hp": "4d8+4", "ac": 12, "speed": "10ft, fly 60ft", "str":10,"dex":15,"con":12,"int":3,"wis":12,"cha":5,
     "attacks": [{"name":"Beak","hit":"+4","dmg":"1d6+2 piercing"},{"name":"Talons","hit":"+4","dmg":"1d6+2 slashing"},{"name":"Stormcall","hit":"—","dmg":"Disadvantage on ranged attacks within 60ft of it in stormy conditions"}]},
    {"name": "Bandit Gang (mixed)", "cr": "4",    "xp": 1100,  "type": "humanoid",   "env": ["road","city","forest"],
     "hp": "9d8+18", "ac": 13, "speed": 30, "str":14,"dex":13,"con":14,"int":10,"wis":10,"cha":12,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Shortsword","hit":"+5","dmg":"1d6+3 piercing"},{"name":"Shortbow","hit":"+4","dmg":"1d6+2 piercing","range":"80/320ft"},{"name":"Ambush","hit":"—","dmg":"+2d6 sneak attack when hidden or ally adjacent"}]},
    {"name": "Jackalwere",          "cr": "1/2",  "xp": 100,   "type": "humanoid",   "env": ["desert","grassland"],
     "hp": "4d8+4", "ac": 12, "speed": 40, "str":11,"dex":15,"con":11,"int":13,"wis":11,"cha":10,
     "attacks": [{"name":"Multiattack (humanoid)","hit":"—","dmg":"2 attacks"},{"name":"Scimitar","hit":"+4","dmg":"1d6+2 slashing"},{"name":"Bite (jackal/hybrid)","hit":"+4","dmg":"1d4+2 piercing"},{"name":"Sleepy Gaze","hit":"—","dmg":"DC 10 Wis or asleep 10 min (one creature, 30ft, not if undead)"}]},
    {"name": "Yuan-Ti Mind Whisperer","cr":"4",   "xp": 1100,  "type": "humanoid",   "env": ["dungeon","desert","jungle"],
     "hp": "10d8+10", "ac": 14, "speed": 30, "str":16,"dex":14,"con":13,"int":14,"wis":14,"cha":16,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Bite","hit":"+5","dmg":"1d6+3 piercing + 3d6 poison (DC 13 Con)"},{"name":"Hypnotic Gaze","hit":"—","dmg":"DC 13 Wis or charmed 1 min"},{"name":"Spellcasting","hit":"—","dmg":"Detect Thoughts, Suggestion, Phantasmal Force (DC 13)"}]},
    {"name": "Flind",               "cr": "9",    "xp": 5000,  "type": "humanoid",   "env": ["dungeon","grassland","desert"],
     "hp": "15d8+60", "ac": 16, "speed": 30, "str":20,"dex":10,"con":19,"int":10,"wis":12,"cha":14,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Flail of Gnolls","hit":"+9","dmg":"2d8+5 bludgeoning (special: DC 14 Wis or commands a gnoll in 60ft to use reaction to attack)"},{"name":"Flail of Madness","hit":"+9","dmg":"2d8+5 bludgeoning (DC 14 Wis or frightened 1 min)"},{"name":"Flail of Confusion","hit":"+9","dmg":"2d8+5 bludgeoning (DC 14 Wis or incapacitated 1 min)"}]},

    # ════════════════════════════════════════════════════════
    # VOLO'S GUIDE STAPLES
    # ════════════════════════════════════════════════════════
    {"name": "Archer",              "cr": "3",    "xp": 700,   "type": "humanoid",   "env": ["forest","grassland","dungeon","city"],
     "hp": "9d8+9", "ac": 16, "speed": 30, "str":11,"dex":18,"con":13,"int":10,"wis":13,"cha":10,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Shortsword","hit":"+6","dmg":"1d6+4 piercing"},{"name":"Longbow","hit":"+6","dmg":"1d8+4 piercing (range advantage if stationary)","range":"150/600ft"}]},
    {"name": "Swashbuckler",        "cr": "3",    "xp": 700,   "type": "humanoid",   "env": ["city","coast","dungeon"],
     "hp": "9d8+18", "ac": 17, "speed": 30, "str":12,"dex":18,"con":14,"int":14,"wis":11,"cha":15,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Rapier","hit":"+6","dmg":"1d8+4 piercing"},{"name":"Fancy Footwork","hit":"—","dmg":"After melee attack, target can't make opportunity attacks against it this turn"}]},
    {"name": "War Priest",          "cr": "9",    "xp": 5000,  "type": "humanoid",   "env": ["city","dungeon","grassland"],
     "hp": "16d8+48", "ac": 18, "speed": 30, "str":16,"dex":10,"con":14,"int":11,"wis":17,"cha":13,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Maul","hit":"+7","dmg":"2d6+3 bludgeoning"},{"name":"Spellcasting","hit":"—","dmg":"Sacred Flame (DC 14), Spiritual Weapon, Shield of Faith, Banishment, Flame Strike (DC 14)"},{"name":"Divine Eminence","hit":"—","dmg":"Expend spell slot: weapon deals extra 3d6 radiant for 1 min"}]},
    {"name": "Warlord",             "cr": "12",   "xp": 8400,  "type": "humanoid",   "env": ["city","dungeon","grassland"],
     "hp": "18d8+72", "ac": 18, "speed": 30, "str":20,"dex":16,"con":18,"int":12,"wis":12,"cha":18,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Longsword","hit":"+9","dmg":"1d8+5 slashing + 2d8 fire"},{"name":"Command (recharge 5-6)","hit":"—","dmg":"Up to 3 allies within 60ft: each uses reaction to immediately attack one creature"},{"name":"Parry","hit":"—","dmg":"+4 AC reaction"}]},
    {"name": "Martial Arts Adept",  "cr": "3",    "xp": 700,   "type": "humanoid",   "env": ["city","dungeon","forest"],
     "hp": "9d8+18", "ac": 16, "speed": 40, "str":11,"dex":17,"con":13,"int":11,"wis":16,"cha":10,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"4 attacks"},{"name":"Unarmed Strike","hit":"+5","dmg":"1d6+3 bludgeoning"},{"name":"Dart","hit":"+5","dmg":"1d4+3 piercing","range":"20/60ft"},{"name":"Stunning Strike (recharge 5-6)","hit":"—","dmg":"DC 13 Con or stunned 1 min"}]},
    {"name": "Bard",                "cr": "2",    "xp": 450,   "type": "humanoid",   "env": ["city","dungeon"],
     "hp": "5d8+10", "ac": 15, "speed": 30, "str":11,"dex":14,"con":12,"int":10,"wis":13,"cha":14,
     "attacks": [{"name":"Shortsword","hit":"+4","dmg":"1d6+2 piercing"},{"name":"Spellcasting","hit":"—","dmg":"Vicious Mockery (DC 12 Wis, 2d4 psychic + disadvantage), Charm Person, Suggestion, Hold Person"},{"name":"Bardic Inspiration","hit":"—","dmg":"Ally adds 1d6 to attack, ability check, or save"}]},
    {"name": "Conjurer Wizard",     "cr": "6",    "xp": 2300,  "type": "humanoid",   "env": ["city","dungeon"],
     "hp": "9d8+9", "ac": 12, "speed": 30, "str":9,"dex":14,"con":11,"int":17,"wis":12,"cha":12,
     "attacks": [{"name":"Dagger","hit":"+5","dmg":"1d4+2 piercing"},{"name":"Spellcasting","hit":"—","dmg":"Poison Spray, Mage Armor, Fog Cloud, Misty Step, Fireball (DC 14), Conjure Elemental"},{"name":"Benign Transposition (recharge short/long)","hit":"—","dmg":"Teleport to ally or conjured creature within 30ft"}]},
    {"name": "Evoker Wizard",       "cr": "9",    "xp": 5000,  "type": "humanoid",   "env": ["city","dungeon"],
     "hp": "11d8+22", "ac": 12, "speed": 30, "str":9,"dex":14,"con":14,"int":18,"wis":12,"cha":11,
     "attacks": [{"name":"Quarterstaff","hit":"+2","dmg":"1d6-1 bludgeoning"},{"name":"Spellcasting","hit":"—","dmg":"Fire Bolt (3d10), Shield, Fireball (8d6), Cone of Cold (8d8), Wall of Fire (DC 17)"},{"name":"Overchannel","hit":"—","dmg":"Deal max damage on 5th-level or lower spell (1/turn, 2d12 necrotic per use after first)"}]},
    {"name": "Necromancer Wizard",  "cr": "9",    "xp": 5000,  "type": "humanoid",   "env": ["dungeon","crypt","city"],
     "hp": "11d8+22", "ac": 12, "speed": 30, "str":9,"dex":14,"con":14,"int":17,"wis":12,"cha":11,
     "attacks": [{"name":"Withering Gaze","hit":"+7","dmg":"2d8+3 necrotic (30ft)"},{"name":"Spellcasting","hit":"—","dmg":"Toll the Dead (DC 15), Animate Dead, Bestow Curse, Blight, Circle of Death (DC 15)"},{"name":"Grim Harvest","hit":"—","dmg":"Regain HP = twice spell slot level (or thrice for necromancy) when killing with spell"}]},
    {"name": "Diviner Wizard",      "cr": "8",    "xp": 3900,  "type": "humanoid",   "env": ["city","dungeon"],
     "hp": "13d8+13", "ac": 12, "speed": 30, "str":9,"dex":14,"con":13,"int":18,"wis":13,"cha":11,
     "attacks": [{"name":"Dagger","hit":"+5","dmg":"1d4+2 piercing"},{"name":"Spellcasting","hit":"—","dmg":"Detect Thoughts, Scrying, Foresight, True Seeing (DC 15)"},{"name":"Portent (2/day)","hit":"—","dmg":"Replace any attack roll, saving throw, or ability check with 2 pre-rolled dice"}]},
    {"name": "Abjurer Wizard",      "cr": "9",    "xp": 5000,  "type": "humanoid",   "env": ["city","dungeon"],
     "hp": "11d8+22", "ac": 12, "speed": 30, "str":9,"dex":14,"con":14,"int":17,"wis":13,"cha":11,
     "attacks": [{"name":"Quarterstaff","hit":"+2","dmg":"1d6-1 bludgeoning"},{"name":"Spellcasting","hit":"—","dmg":"Shocking Grasp, Counterspell, Globe of Invulnerability, Prismatic Wall (DC 15)"},{"name":"Arcane Ward","hit":"—","dmg":"30-HP shield that absorbs damage first, replenished by abjuration spells"}]},

    # ════════════════════════════════════════════════════════
    # MORDENKAINEN'S TOME ADDITIONS
    # ════════════════════════════════════════════════════════
    {"name": "Vampiric Mist",       "cr": "3",    "xp": 700,   "type": "undead",     "env": ["dungeon","crypt"],
     "hp": "10d8-10", "ac": 13, "speed": "0ft, fly 30ft (hover)", "str":6,"dex":17,"con":10,"int":6,"wis":10,"cha":6,
     "attacks": [{"name":"Life Drain","hit":"+5","dmg":"2d6+3 necrotic (DC 13 Con or max HP reduced, regain equal to damage dealt)"},{"name":"Misty Form","hit":"—","dmg":"Only physical in 5ft, immune to prone, grapple, restraint — dispersed by sunlight"}]},
    {"name": "Yochlol",             "cr": "10",   "xp": 5900,  "type": "fiend",      "env": ["dungeon","underdark"],
     "hp": "18d8+54", "ac": 15, "speed": "30ft, climb 30ft, fly 30ft (mist only)", "str":15,"dex":14,"con":18,"int":13,"wis":15,"cha":15,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Slam","hit":"+6","dmg":"1d6+2 bludgeoning + 2d6 poison (DC 14 Con or poisoned 1 min)"},{"name":"Maddening Whispers","hit":"—","dmg":"DC 14 Wis or spend reaction to attack nearest ally"},{"name":"Shapechange","hit":"—","dmg":"Assume spider, humanoid, or mist form"}]},
    {"name": "Cadaver Collector",   "cr": "14",   "xp": 11500, "type": "construct",  "env": ["dungeon","grassland"],
     "hp": "21d12+84", "ac": 17, "speed": 30, "str":21,"dex":10,"con":20,"int":5,"wis":11,"cha":3,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Slam","hit":"+10","dmg":"3d8+5 bludgeoning + 2d8 lightning"},{"name":"Paralyzing Breath (recharge 5-6)","hit":"—","dmg":"DC 18 Con or paralyzed 1 min (30ft cone)"},{"name":"Corpse Collection","hit":"—","dmg":"Paralyze or kill: corpse attaches to its body, granting half cover and damage"}]},
    {"name": "Wastrilith",          "cr": "13",   "xp": 10000, "type": "fiend",      "env": ["underwater","dungeon","swamp"],
     "hp": "19d10+95", "ac": 18, "speed": "30ft, swim 80ft", "str":19,"dex":18,"con":21,"int":19,"wis":14,"cha":18,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Bite","hit":"+9","dmg":"2d6+4 piercing + 3d6 acid"},{"name":"Claws","hit":"+9","dmg":"1d8+4 slashing + 1d8 acid"},{"name":"Corrupting Touch","hit":"—","dmg":"All water in 60ft becomes corrosive — 3d6 acid/turn to creatures in it"}]},
    {"name": "Alhoon",              "cr": "10",   "xp": 5900,  "type": "undead",     "env": ["dungeon","underdark"],
     "hp": "13d8+26", "ac": 15, "speed": 30, "str":11,"dex":12,"con":12,"int":19,"wis":17,"cha":16,
     "attacks": [{"name":"Chilling Grasp","hit":"+8","dmg":"2d8 cold (reach — DC 15 Con or speed 0 until end of next turn)"},{"name":"Mind Blast (recharge 5-6)","hit":"—","dmg":"5d8+4 psychic (DC 15 Int or stunned, 60ft cone)"},{"name":"Spellcasting","hit":"—","dmg":"Detect Thoughts, Dominate Monster, Plane Shift, Telekinesis, Wall of Ice (DC 15)"}]},
    {"name": "Skull Lord",          "cr": "15",   "xp": 13000, "type": "undead",     "env": ["dungeon","crypt"],
     "hp": "15d8+45", "ac": 18, "speed": 30, "str":14,"dex":16,"con":17,"int":19,"wis":19,"cha":16,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"3 attacks"},{"name":"Bone Staff","hit":"+9","dmg":"1d8+4 bludgeoning + 4d6 necrotic"},{"name":"Spellcasting","hit":"—","dmg":"Cloudkill, Cone of Cold, Finger of Death, Power Word Stun (DC 18)"},{"name":"Legendary Actions","hit":"—","dmg":"Move, Cantrip, Bone Staff, or Disrupt Life (1d6+4 necrotic, DC 18 Con, all creatures in 60ft)"}]},
    {"name": "Star Spawn Grue",     "cr": "1/4",  "xp": 50,    "type": "aberration", "env": ["dungeon","any"],
     "hp": "3d4", "ac": 11, "speed": 35, "str":6,"dex":13,"con":10,"int":5,"wis":8,"cha":6,
     "attacks": [{"name":"Bite","hit":"+3","dmg":"2d4 piercing"},{"name":"Aura of Madness","hit":"—","dmg":"Attacks against it have disadvantage unless attacker is immune to the frightened condition (10ft)"}]},
    {"name": "Star Spawn Hulk",     "cr": "10",   "xp": 5900,  "type": "aberration", "env": ["dungeon","any"],
     "hp": "17d10+68", "ac": 16, "speed": 30, "str":20,"dex":8,"con":21,"int":7,"wis":12,"cha":9,
     "attacks": [{"name":"Multiattack","hit":"—","dmg":"2 attacks"},{"name":"Slam","hit":"+9","dmg":"2d8+5 bludgeoning + 2d8 psychic"},{"name":"Retaliation Burst","hit":"—","dmg":"When reduced to 0 HP: DC 17 Dex or 3d8+5 psychic (10ft radius)"}]},
    {"name": "Oblex Spawn",         "cr": "1/4",  "xp": 50,    "type": "ooze",       "env": ["dungeon","sewer","underdark"],
     "hp": "3d6", "ac": 10, "speed": 20, "str":8,"dex":10,"con":14,"int":3,"wis":8,"cha":5,
     "attacks": [{"name":"Pseudopod","hit":"+1","dmg":"1d4-1 bludgeoning + 2d4 psychic"}]},
    {"name": "Adult Oblex",         "cr": "5",    "xp": 1800,  "type": "ooze",       "env": ["dungeon","sewer"],
     "hp": "14d8+28", "ac": 14, "speed": 20, "str":8,"dex":19,"con":15,"int":19,"wis":12,"cha":18,
     "attacks": [{"name":"Pseudopod","hit":"+7","dmg":"1d8+4 bludgeoning + 4d8 psychic"},{"name":"Eat Memories (recharge 5-6)","hit":"—","dmg":"DC 15 Int or lose memory of 1 proficiency until cure — oblex copies mannerisms"},{"name":"Sulfurous Impersonation","hit":"—","dmg":"Extends tendril to impersonate a creature whose memories it has consumed"}]},
]

CR_ORDER = {"0":0,"1/8":0.125,"1/4":0.25,"1/2":0.5,
            **{str(i): float(i) for i in range(1, 31)}}

# XP thresholds per character level [easy, medium, hard, deadly]
XP_THRESHOLDS = {
    1: [25, 50, 75, 100],
    2: [50, 100, 150, 200],
    3: [75, 150, 225, 400],
    4: [125, 250, 375, 500],
    5: [250, 500, 750, 1100],
    6: [300, 600, 900, 1400],
    7: [350, 750, 1100, 1700],
    8: [450, 900, 1400, 2100],
    9: [550, 1100, 1600, 2400],
    10: [600, 1200, 1900, 2800],
    11: [800, 1600, 2400, 3600],
    12: [1000, 2000, 3000, 4500],
    13: [1100, 2200, 3400, 5100],
    14: [1250, 2500, 3800, 5700],
    15: [1400, 2800, 4300, 6400],
    16: [1600, 3200, 4800, 7200],
    17: [2000, 3900, 5900, 8800],
    18: [2100, 4200, 6300, 9500],
    19: [2400, 4900, 7300, 10900],
    20: [2800, 5700, 8500, 12700],
}

MONSTER_COUNT_MULTIPLIERS = [
    (1, 1, 1.0), (2, 2, 1.5), (3, 6, 2.0), (7, 10, 2.5),
    (11, 14, 3.0), (15, 99, 4.0)
]

TOOLS = [
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "encounter_generate",
            "description": "Generate a random D&D encounter appropriate for the party's level and environment. Use when starting a new encounter or populating an area.",
            "parameters": {
                "type": "object",
                "properties": {
                    "party_levels": {"type": "array", "items": {"type": "integer"}, "description": "List of levels for each party member, e.g. [4,4,4,3]"},
                    "difficulty":   {"type": "string", "description": "easy, medium, hard, or deadly"},
                    "environment":  {"type": "string", "description": "forest, cave, dungeon, road, mountain, swamp, city, crypt, grassland, coast, or random"},
                    "monster_type": {"type": "string", "description": "Filter by type: humanoid, undead, beast, dragon, giant, ooze, monstrosity, aberration, or any"}
                },
                "required": ["party_levels"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "encounter_start_combat",
            "description": "Begin combat. Roll initiative for all combatants and set up the initiative order. Call this at the start of every fight. If combatants are omitted, automatically uses all player characters from the current campaign roster.",
            "parameters": {
                "type": "object",
                "properties": {
                    "combatants": {
                        "type": "array",
                        "description": "List of combatants entering combat",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name":    {"type": "string",  "description": "Combatant name"},
                                "dex_mod": {"type": "integer", "description": "Dexterity modifier for initiative"},
                                "hp":      {"type": "integer", "description": "Current HP"},
                                "hp_max":  {"type": "integer", "description": "Max HP (if different from hp)"},
                                "is_player": {"type": "boolean", "description": "True for player characters"}
                            },
                            "required": ["name"]
                        }
                    }
                },
                "required": ["combatants"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "encounter_next_turn",
            "description": "Advance to the next turn in initiative order. Optionally update HP for damage dealt this round.",
            "parameters": {
                "type": "object",
                "properties": {
                    "hp_updates": {
                        "type": "array",
                        "description": "HP changes this turn, e.g. [{\"name\": \"Goblin 1\", \"hp\": 4}]",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "hp":   {"type": "integer", "description": "New current HP value"}
                            }
                        }
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "encounter_combat_status",
            "description": "Show the current combat state — initiative order, HP, turn number.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "encounter_end_combat",
            "description": "End the current combat encounter. Returns XP earned summary.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "encounter_xp_budget",
            "description": "Calculate XP thresholds for a party and check difficulty of a given total XP.",
            "parameters": {
                "type": "object",
                "properties": {
                    "party_levels": {"type": "array", "items": {"type": "integer"}, "description": "Levels of each party member"},
                    "monster_xp":   {"type": "integer", "description": "Total XP of monsters in the encounter (optional — omit to just see thresholds)"}
                },
                "required": ["party_levels"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "monster_lookup",
            "description": "Look up stats for a monster by name — HP, AC, attacks, CR, XP.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Monster name to look up"}
                },
                "required": ["name"]
            }
        }
    }
]


DEFAULT_CAMPAIGN_ID = "default"


def _get_state():
    from core.plugin_loader import plugin_loader
    return plugin_loader.get_plugin_state("dnd-scaffold")


def _get_campaign_id(config=None) -> str:
    from core.plugin_loader import plugin_loader
    try:
        campaign_state = plugin_loader.get_plugin_state("dnd-campaign")
        return campaign_state.get("active_campaign", DEFAULT_CAMPAIGN_ID)
    except Exception:
        return DEFAULT_CAMPAIGN_ID


def _migrate_if_needed(campaign_id: str):
    state = _get_state()
    migration_key = f"_legacy_migrated_{campaign_id}"
    if state.get(migration_key):
        return
    legacy = state.get("combat")
    if legacy:
        state.save(f"combat:{campaign_id}", legacy)
        state.save(migration_key, True)


def _load_combat(config=None):
    campaign_id = _get_campaign_id(config)
    state = _get_state()
    _migrate_if_needed(campaign_id)
    campaign_combat = state.get(f"combat:{campaign_id}")
    if campaign_combat:
        return campaign_combat
    return state.get("combat") or {}


def _save_combat(combat, config=None):
    campaign_id = _get_campaign_id(config)
    _get_state().save(f"combat:{campaign_id}", combat)

def _xp_difficulty(party_levels, monster_xp):
    totals = [0, 0, 0, 0]
    for lvl in party_levels:
        thresh = XP_THRESHOLDS.get(min(lvl, 20), XP_THRESHOLDS[20])
        for i in range(4): totals[i] += thresh[i]

    if monster_xp < totals[0]: return "Below Easy", totals
    if monster_xp < totals[1]: return "Easy", totals
    if monster_xp < totals[2]: return "Medium", totals
    if monster_xp < totals[3]: return "Hard", totals
    return "Deadly", totals


def _cn(c):
    """Get combatant name, handling both 'Name' and 'name' keys safely."""
    return c.get("Name") or c.get("name") or ""


def _award_xp(combat, config):
    """
    Compute and persist XP from a completed combat encounter.
    Returns a formatted XP result string. Used by both encounter_end_combat
    and encounter_next_turn (when enemies are auto-defeated).
    """
    combatants = combat.get("combatants", [])
    total_xp = 0
    defeated = []
    player_chars = []

    for c in combatants:
        char_name = _cn(c)
        if c.get("is_player"):
            player_chars.append(char_name)
        else:
            # Use the xp field stored on the combatant at encounter_start_combat
            monster_xp = c.get("xp", 0)
            if monster_xp > 0:
                total_xp += monster_xp
                defeated.append(f"{char_name} ({monster_xp} XP)")

    if total_xp > 0 and player_chars:
        per_pc = total_xp // len(player_chars)
        remainder = total_xp % len(player_chars)
        try:
            from core.plugin_loader import plugin_loader
            campaign_id = _get_campaign_id(config)
            xp_state = plugin_loader.get_plugin_state("dnd-levelup")
            xp_data_key = f"xp_data:{campaign_id}"
            xp_data = xp_state.get(xp_data_key) or {}

            char_state = plugin_loader.get_plugin_state("dnd-scaffold")
            chars = char_state.get(f"characters:{campaign_id}") or char_state.get("characters") or {}

            for pname in player_chars:
                char_entry = chars.get(pname, {})
                sheet_level = char_entry.get("level", 1)
                baseline = 0
                if pname not in xp_data:
                    baseline = XP_THRESHOLDS.get(sheet_level, 0)
                current_xp = xp_data.get(pname, {}).get("xp", baseline)
                xp_data[pname] = {"xp": current_xp + per_pc}

            xp_state.save(xp_data_key, xp_data)
            xp_written = True
        except Exception:
            xp_written = False
    else:
        per_pc = 0
        xp_written = False

    lines = []
    if defeated:
        lines.append(f"**Enemies defeated:** {', '.join(defeated)}")
    if total_xp > 0 and player_chars:
        lines.append(f"**Total XP:** {total_xp}")
        lines.append(f"**Award:** {per_pc} XP each to: {', '.join(player_chars)}")
        if remainder > 0:
            lines.append(f"(+{remainder} XP unclaimed — grant manually)")
        if xp_written:
            lines.append("✅ XP recorded — use `xp_check_all` to verify.")
        else:
            lines.append("⚠️ XP could not be auto-saved — use `xp_add` manually.")
    elif not player_chars:
        lines.append("(No player characters found)")
    else:
        lines.append("(No enemies with XP values in this encounter)")

    return "\n".join(lines)


def _hp_roll(expression: str) -> int:
    import re
    m = re.match(r'(\d+)d(\d+)([+-]\d+)?', str(expression))
    if not m:
        try: return int(expression)
        except: return 10
    count, sides = int(m.group(1)), int(m.group(2))
    mod = int(m.group(3)) if m.group(3) else 0
    return sum(random.randint(1, sides) for _ in range(count)) + mod

def execute(function_name, arguments, config):

    def _load_party(config):
        """Load player characters from dnd-scaffold state and format as combatants."""
        try:
            from core.plugin_loader import plugin_loader
            campaign_state = plugin_loader.get_plugin_state("dnd-campaign")
            campaign_id = campaign_state.get("active_campaign", "default")
            char_state = plugin_loader.get_plugin_state("dnd-scaffold")
            chars = char_state.get(f"characters:{campaign_id}") or char_state.get("characters") or {}
            combatants = []
            for name, char in chars.items():
                dex = char.get("dex", 10)
                dex_mod = (dex - 10) // 2
                hp = char.get("hp_current", char.get("hp_max", 10))
                hp_max = char.get("hp_max", 10)
                combatants.append({
                    "name": name,
                    "dex_mod": dex_mod,
                    "hp": hp,
                    "hp_max": hp_max,
                    "is_player": char.get("user_controlled", True),
                })
            return combatants
        except Exception:
            return []

    # ── encounter_generate ──
    if function_name == "encounter_generate":
        party_levels = arguments.get("party_levels", [1])
        difficulty   = arguments.get("difficulty", "medium").lower()
        environment  = arguments.get("environment", "random").lower()
        monster_type = arguments.get("monster_type", "any").lower()

        diff_idx = {"easy": 0, "medium": 1, "hard": 2, "deadly": 3}.get(difficulty, 1)

        # Build XP budget
        total_budget = sum(
            XP_THRESHOLDS.get(min(l, 20), XP_THRESHOLDS[20])[diff_idx]
            for l in party_levels
        )

        # Filter monsters by environment and type
        pool = MONSTERS[:]
        if environment != "random":
            pool = [m for m in pool if environment in m.get("env", [])]
        if monster_type != "any":
            pool = [m for m in pool if m["type"] == monster_type]
        if not pool:
            pool = MONSTERS[:]

        # Pick monsters that fit the budget
        chosen = []
        spent = 0
        random.shuffle(pool)

        for monster in pool:
            if spent >= total_budget * 0.7:
                break
            count = random.randint(1, max(1, total_budget // max(monster["xp"], 1) // 2))
            count = max(1, min(count, 8))
            xp_cost = monster["xp"] * count
            if spent + xp_cost <= total_budget * 1.1:
                chosen.append((monster, count))
                spent += xp_cost
                if spent >= total_budget * 0.7:
                    break

        if not chosen:
            monster = random.choice(pool)
            chosen = [(monster, 1)]
            spent = monster["xp"]

        diff_label, thresholds = _xp_difficulty(party_levels, spent)

        lines = [f"⚔️ **{difficulty.title()} Encounter** ({environment if environment != 'random' else 'any terrain'})"]
        total_xp = 0
        for m, count in chosen:
            hp_each = _hp_roll(m["hp"])
            lines.append(f"• **{m['name']}** x{count} | CR {m['cr']} | {m['xp']} XP each | HP ~{hp_each} | AC {m['ac']}")
            total_xp += m["xp"] * count

        lines.append(f"\n**Total XP:** {total_xp} | **Adjusted Difficulty:** {diff_label}")
        lines.append(f"Party thresholds — Easy:{thresholds[0]} Medium:{thresholds[1]} Hard:{thresholds[2]} Deadly:{thresholds[3]}")
        return "\n".join(lines), True

    # ── encounter_start_combat ──
    elif function_name == "encounter_start_combat":
        combatants_raw = arguments.get("combatants", [])
        if not combatants_raw:
            # Auto-populate from the party roster in dnd-scaffold
            combatants_raw = _load_party(config)
            if not combatants_raw:
                return "No combatants provided and no characters found in campaign. Create characters first with character_create.", False

        # Build XP lookup from MONSTERS (case-insensitive)
        monster_xp_map = {}
        for m in MONSTERS:
            for key in ("Name", "name"):
                if key in m:
                    monster_xp_map[m[key].lower()] = m["xp"]
                    break

        combatants = []
        for c in combatants_raw:
            dex_mod  = c.get("dex_mod", 0)
            init_roll = random.randint(1, 20) + dex_mod
            hp = c.get("hp", 10)
            # Normalize name to always use lowercase "name" key
            char_name = c.get("Name") or c.get("name") or ""
            # Respect explicitly passed XP; otherwise auto-lookup from MONSTERS
            # Also try to look up by "xp" (lowercase) from the combatant record
            xp = c.get("xp", None)
            if xp is None and not c.get("is_player", False):
                xp = monster_xp_map.get(char_name.lower(), 0)
            if xp is None:
                xp = 0
            combatants.append({
                "name":      char_name,  # always lowercase "name" for consistency
                "initiative": init_roll,
                "dex_mod":   dex_mod,
                "hp":        hp,
                "hp_max":    c.get("hp_max", hp),
                "is_player": c.get("is_player", False),
                "conditions": [],
                "xp":        xp,  # stored for _award_xp on combat end
            })

        combatants.sort(key=lambda x: x["initiative"], reverse=True)

        combat = {
            "combatants": combatants,
            "current_turn": 0,
            "round": 1,
            "total_xp": 0,
        }
        _save_combat(combat, config)

        lines = ["⚔️ **Combat Begins! Initiative Order:**"]
        for i, c in enumerate(combatants):
            marker = " ← *FIRST*" if i == 0 else ""
            tag = " (PC)" if c.get("is_player", False) else ""
            lines.append(f"{i+1}. **{_cn(c)}{tag}** — Initiative {c.get('initiative', '?')} | HP {c.get('hp', '?')}/{c.get('hp_max', '?')}{marker}")
        return "\n".join(lines), True

    # ── encounter_next_turn ──
    elif function_name == "encounter_next_turn":
        combat = _load_combat(config)
        if not combat:
            return "No active combat. Use encounter_start_combat first.", False

        hp_updates = arguments.get("hp_updates", [])
        combatants = combat["combatants"]

        # Apply HP updates
        for upd in hp_updates:
            upd_name = upd.get("Name") or upd.get("name") or ""
            for c in combatants:
                if _cn(c).lower() == upd_name.lower():
                    c["hp"] = upd.get("hp", c.get("hp", 0))

        # Remove dead enemies (keep dead PCs for death saves)
        alive = [c for c in combatants if c.get("hp", 0) > 0 or c.get("is_player", False)]
        combat["combatants"] = alive

        if not alive:
            _save_combat({}, config)
            return "All combatants are down. Combat over.", True

        # Check if only players remain
        enemies_alive = [c for c in alive if not c.get("is_player", False) and c.get("hp", 0) > 0]
        if not enemies_alive:
            # Award XP before clearing — pass the FULL combatants list so dead enemies are included
            xp_result = _award_xp({"combatants": combatants}, config)
            _save_combat({}, config)
            return "🎉 **All enemies defeated!** Combat ends.\n\n" + xp_result, True

        # Advance turn
        current = combat["current_turn"]
        next_turn = (current + 1) % len(alive)
        if next_turn == 0:
            combat["round"] += 1
        combat["current_turn"] = next_turn
        combat["combatants"] = alive
        _save_combat(combat, config)

        active = alive[next_turn]
        lines = [f"🎲 **Round {combat['round']} — {_cn(active)}'s turn**"]
        for i, c in enumerate(alive):
            marker = " ◄" if i == next_turn else ""
            status = f"HP {c.get('hp', '?')}/{c.get('hp_max', '?')}"
            if c.get("hp", 1) <= 0: status = "💀 DOWN"
            conds = f" [{','.join(c.get('conditions', []))}]" if c.get("conditions") else ""
            lines.append(f"  {'→' if i == next_turn else ' '} {_cn(c)}: {status}{conds}{marker}")
        return "\n".join(lines), True

    # ── encounter_combat_status ──
    elif function_name == "encounter_combat_status":
        combat = _load_combat(config)
        if not combat:
            return "No active combat.", True

        combatants = combat["combatants"]
        current = combat.get("current_turn", 0)
        lines = [f"⚔️ **Combat Status — Round {combat.get('round',1)}**"]
        for i, c in enumerate(combatants):
            marker = " ◄ ACTIVE" if i == current else ""
            status = f"HP {c.get('hp', '?')}/{c.get('hp_max', '?')}"
            if c.get("hp", 1) <= 0: status = "💀 DOWN"
            conds = f" [{','.join(c.get('conditions', []))}]" if c.get("conditions") else ""
            lines.append(f"  {i+1}. **{_cn(c)}**: {status}{conds}{marker}")
        return "\n".join(lines), True

    # ── encounter_end_combat ──
    elif function_name == "encounter_end_combat":
        combat = _load_combat(config)
        if not combat:
            return "No active combat to end.", True

        xp_result = _award_xp(combat, config)
        lines = ["✅ Combat ended."]
        if xp_result:
            lines.append("")
            lines.append(xp_result)
        lines.append("\nCheck for loot before wrapping up!")
        _save_combat({}, config)
        return "\n".join(lines), True

    # ── encounter_xp_budget ──
    elif function_name == "encounter_xp_budget":
        party_levels = arguments.get("party_levels", [1])
        monster_xp   = arguments.get("monster_xp", None)

        diff_label, thresholds = _xp_difficulty(party_levels, monster_xp or 0)
        lines = [f"**XP Thresholds for party of {len(party_levels)}:**"]
        labels = ["Easy", "Medium", "Hard", "Deadly"]
        for i, label in enumerate(labels):
            lines.append(f"  {label}: {thresholds[i]} XP")

        if monster_xp is not None:
            lines.append(f"\nMonster XP: {monster_xp} → **{diff_label}** encounter")
        return "\n".join(lines), True

    # ── monster_lookup ──
    elif function_name == "monster_lookup":
        query = arguments.get("name", "").lower()
        for m in MONSTERS:
            if m["name"].lower() == query or query in m["name"].lower():
                attacks = "\n".join(
                    f"    • {a['name']}: {a['hit']} to hit, {a['dmg']}" +
                    (f" (range {a['range']})" if 'range' in a else "")
                    for a in m.get("attacks", [])
                )
                return (
                    f"**{m['name']}**\n"
                    f"CR {m['cr']} | {m['xp']} XP | Type: {m['type']}\n"
                    f"HP: {m['hp']} | AC: {m['ac']} | Speed: {m.get('speed',30)}\n"
                    f"STR {m['str']} DEX {m['dex']} CON {m['con']} "
                    f"INT {m['int']} WIS {m['wis']} CHA {m['cha']}\n"
                    f"Environments: {', '.join(m.get('env',[]))}\n"
                    f"Attacks:\n{attacks}"
                ), True
        names = ", ".join(m["name"] for m in MONSTERS)
        return f"Monster '{arguments.get('name','')}' not found. Available: {names}", False

    return f"Unknown function: {function_name}", False
