"""
D&D Loot Generator

Generates treasure hoards and individual monster loot by CR tier.
Includes magic item tables (A–I from DMG), consumables, and coins.
"""

import random

ENABLED = True
EMOJI = '💰'
AVAILABLE_FUNCTIONS = ['loot_generate', 'loot_magic_item']

# ── Coin tables by CR tier ─────────────────────────────────────────────────────
# (cp_dice, sp_dice, ep_dice, gp_dice, pp_dice)

def _roll(count, sides):
    return sum(random.randint(1, sides) for _ in range(count))


def _cr_tier(cr):
    try:
        cr_val = {"0": 0, "1/8": 0.125, "1/4": 0.25, "1/2": 0.5}.get(str(cr), float(cr))
    except Exception:
        cr_val = 1
    if cr_val <= 4:
        return "0-4"
    if cr_val <= 10:
        return "5-10"
    if cr_val <= 16:
        return "11-16"
    return "17+"


def _coins_str(coins: dict) -> str:
    parts = []
    for denomination in ["pp", "gp", "ep", "sp", "cp"]:
        val = coins.get(denomination, 0)
        if val > 0:
            parts.append(f"{val:,} {denomination}")
    return ", ".join(parts) if parts else "nothing"


def _gp_value(coins: dict) -> float:
    rates = {"pp": 10, "gp": 1, "ep": 0.5, "sp": 0.1, "cp": 0.01}
    return sum(v * rates.get(k, 0) for k, v in coins.items())


# Coin tables — each entry is a dict of denomination -> roll expression
_COIN_TABLES = {
    "individual": {
        "0-4":   lambda: {"cp": _roll(5, 6), "sp": _roll(2, 6)},
        "5-10":  lambda: {"sp": _roll(4, 6) * 10, "gp": _roll(2, 6) * 10},
        "11-16": lambda: {"sp": _roll(4, 6) * 100, "gp": _roll(2, 6) * 100, "pp": _roll(1, 6) * 10},
        "17+":   lambda: {"gp": _roll(4, 6) * 1000, "pp": _roll(2, 6) * 100},
    },
    "hoard": {
        "0-4":   lambda: {"cp": _roll(6, 6) * 100, "sp": _roll(3, 6) * 100, "gp": _roll(2, 6) * 10},
        "5-10":  lambda: {"cp": _roll(2, 6) * 100, "sp": _roll(2, 6) * 1000, "gp": _roll(6, 6) * 100, "pp": _roll(3, 6) * 10},
        "11-16": lambda: {"gp": _roll(4, 6) * 1000, "pp": _roll(5, 6) * 100},
        "17+":   lambda: {"gp": _roll(12, 6) * 1000, "pp": _roll(8, 6) * 1000},
    }
}

# ── Gem & art tables ───────────────────────────────────────────────────────────
GEMS = {
    "0-4":   [("10gp", ["Azurite", "Banded agate", "Blue quartz", "Eye agate", "Hematite", "Lapis lazuli", "Malachite", "Moss agate", "Obsidian", "Rhodonite", "Tiger eye", "Turquoise"])],
    "5-10":  [("50gp", ["Bloodstone", "Carnelian", "Chalcedony", "Chrysoprase", "Citrine", "Jasper", "Moonstone", "Onyx", "Quartz", "Sardonyx", "Star rose quartz", "Zircon"]),
              ("100gp", ["Amber", "Amethyst", "Chrysoberyl", "Coral", "Garnet", "Jade", "Jet", "Pearl", "Spinel", "Tourmaline"])],
    "11-16": [("500gp", ["Alexandrite", "Aquamarine", "Black pearl", "Blue spinel", "Peridot", "Topaz"]),
              ("1000gp", ["Black opal", "Blue sapphire", "Emerald", "Fire opal", "Opal", "Star ruby", "Star sapphire", "Yellow sapphire"])],
    "17+":   [("5000gp", ["Black sapphire", "Diamond", "Jacinth", "Ruby"])],
}

ART_OBJECTS = {
    "0-4":   ["Silver ewer", "Carved bone statuette", "Small gold bracelet", "Cloth-of-gold vestments",
              "Black velvet mask stitched with silver", "Copper chalice with silver filigree",
              "Pair of engraved bone dice", "Small mirror with a gilt frame", "Embroidered silk handkerchief",
              "Gold locket with a painted portrait inside"],
    "5-10":  ["Gold ring set with bloodstones", "Carved ivory statuette", "Large gold bracelet",
              "Silver necklace with a gemstone pendant", "Bronze crown", "Silk robe with gold embroidery",
              "Large well-made tapestry", "Brass mug with jade inlay", "Box of turquoise animal figurines",
              "Gold bird cage with electrum filigree"],
    "11-16": ["Silver chalice set with moonstones", "Silver-plated steel longsword", "Carved harp of exotic wood",
              "Small gold idol", "Gold dragon comb set with red garnets", "Bottle stopper cork embossed with gold",
              "Ceremonial electrum dagger", "Silver and gold brooch", "Obsidian statuette with gold fittings",
              "Painted gold war mask"],
    "17+":   ["Jeweled gold crown", "Jeweled platinum ring", "Small gold statuette set with rubies",
              "Gold cup set with emeralds", "Gold jewelry box with platinum filigree",
              "Painted gold child's sarcophagus", "Jade game board with gold playing pieces",
              "Bejeweled ivory drinking horn with gold filigree"],
}

# ── Magic Items (simplified DMG tables) ───────────────────────────────────────
MAGIC_ITEMS = {
    "A": {  # minor, common — potions/scrolls
        "items": [
            "Potion of Healing (2d4+2 HP)",
            "Spell Scroll (cantrip)",
            "Spell Scroll (1st level)",
            "Potion of Climbing (climb speed 30ft, 1 hour)",
            "Potion of Animal Friendship",
            "Potion of Water Breathing (1 hour)",
            "Bag of 20 Caltrops",
            "Bottle of Endless Water",
            "Candle of the Deep",
            "Charlatan's Die (always rolls 6)",
            "Cloak of Billowing",
            "Cloak of Many Fashions",
            "Clockwork Amulet (roll d20 for certain result once/day)",
            "Clothes of Mending",
            "Dark Shard Amulet",
            "Dread Helm",
            "Ear Horn of Hearing",
            "Enduring Spellbook",
            "Ersatz Eye",
        ]
    },
    "B": {  # minor, uncommon
        "items": [
            "Potion of Greater Healing (4d4+4 HP)",
            "Potion of Fire Breath (3 uses — 4d6 fire, DC 13)",
            "Potion of Resistance (one damage type)",
            "Ammunition +1",
            "Potion of Animal Friendship",
            "Potion of Hill Giant Strength (STR 21)",
            "Potion of Growth",
            "Potion of Water Breathing",
            "Spell Scroll (2nd level)",
            "Spell Scroll (3rd level)",
            "Bag of Holding",
            "Keoghtom's Ointment",
            "Oil of Slipperiness",
            "Dust of Disappearance",
            "Dust of Dryness",
            "Dust of Sneezing and Choking",
            "Elemental Gem",
            "Philter of Love",
        ]
    },
    "C": {  # minor, uncommon — weapons/armor
        "items": [
            "Spell Scroll (4th or 5th level)",
            "Potion of Superior Healing (8d4+8 HP)",
            "Potion of Clairvoyance",
            "Potion of Diminution",
            "Potion of Gaseous Form",
            "Potion of Frost Giant Strength (STR 23)",
            "Potion of Stone Giant Strength (STR 23)",
            "Potion of Heroism",
            "Potion of Invulnerability",
            "Potion of Mind Reading",
            "Spell Scroll (5th level)",
            "Elixir of Health",
            "Oil of Etherealness",
        ]
    },
    "D": {  # minor, rare
        "items": [
            "Potion of Supreme Healing (10d4+20 HP)",
            "Potion of Invisibility",
            "Potion of Speed",
            "Spell Scroll (6th level)",
            "Spell Scroll (7th level)",
            "Spell Scroll (8th level)",
            "Potion of Flying",
            "Potion of Cloud Giant Strength (STR 27)",
            "Potion of Storm Giant Strength (STR 29)",
            "Potion of Longevity",
            "Potion of Vitality",
        ]
    },
    "E": {  # minor, very rare
        "items": [
            "Spell Scroll (8th level)",
            "Potion of Storm Giant Strength (STR 29)",
            "Potion of Supreme Healing",
        ]
    },
    "F": {  # major, uncommon — weapons
        "items": [
            "Weapon +1",
            "Shield +1",
            "Sentinel Shield",
            "Amulet of Proof against Detection and Location",
            "Boots of Elvenkind",
            "Boots of Striding and Springing",
            "Bracers of Archery",
            "Brooch of Shielding",
            "Broom of Flying",
            "Circlet of Blasting",
            "Cloak of Elvenkind",
            "Cloak of Protection (+1 AC and saves)",
            "Gauntlets of Ogre Power (STR 19)",
            "Hat of Disguise",
            "Headband of Intellect (INT 19)",
            "Helm of Telepathy",
            "Instrument of the Bards",
            "Medallion of Thoughts",
            "Necklace of Adaptation",
            "Pearl of Power",
            "Rod of the Pact Keeper +1",
            "Slippers of Spider Climbing",
            "Staff of the Adder",
            "Staff of the Python",
            "Sword of Vengeance",
            "Trident of Fish Command",
            "Wand of Magic Detection",
            "Wand of Secrets",
        ]
    },
    "G": {  # major, rare
        "items": [
            "Weapon +2",
            "Figurine of Wondrous Power",
            "Adamantine Armor",
            "Amulet of Health (CON 19)",
            "Armor of Vulnerability",
            "Arrow-Catching Shield",
            "Belt of Dwarvenkind",
            "Belt of Giant Strength (Hill, STR 21)",
            "Berserker Axe",
            "Boots of Levitation",
            "Boots of Speed",
            "Bowl of Commanding Water Elementals",
            "Bracers of Defense (+2 AC, no armor/shield)",
            "Brazier of Commanding Fire Elementals",
            "Cape of the Mountebank",
            "Censer of Controlling Air Elementals",
            "Chime of Opening",
            "Cloak of Displacement",
            "Cloak of the Bat",
            "Cube of Force",
            "Daern's Instant Fortress",
            "Dagger of Venom",
            "Dimensional Shackles",
            "Dragon Slayer Sword",
            "Elven Chain (chain shirt, no proficiency needed)",
            "Flame Tongue Sword",
            "Gem of Seeing",
            "Giant Slayer Axe",
            "Glamoured Studded Leather",
            "Helm of Teleportation",
            "Horn of Blasting",
            "Horn of Valhalla (silver or brass)",
            "Ioun Stone (reserve, sustenance, etc.)",
            "Iron Bands of Bilarro",
            "Mace of Disruption",
            "Mace of Smiting",
            "Mace of Terror",
            "Mantle of Spell Resistance",
            "Necklace of Prayer Beads",
            "Periapt of Proof against Poison",
            "Ring of Animal Influence",
            "Ring of Evasion",
            "Ring of Feather Falling",
            "Ring of Free Action",
            "Ring of Protection (+1 AC and saves)",
            "Ring of Resistance",
            "Ring of Spell Storing",
            "Ring of the Ram",
            "Ring of X-ray Vision",
            "Robe of Useful Items",
            "Rod of Rulership",
            "Rod of the Pact Keeper +2",
            "Rope of Entanglement",
            "Shield of Missile Attraction",
            "Staff of Charming",
            "Staff of Healing",
            "Staff of Swarming Insects",
            "Staff of the Woodlands",
            "Staff of Withering",
            "Stone of Controlling Earth Elementals",
            "Sun Blade",
            "Sword of Life Stealing",
            "Sword of Wounding",
            "Tentacle Rod",
            "Vicious Weapon",
            "Wand of Binding",
            "Wand of Enemy Detection",
            "Wand of Fear",
            "Wand of Fireballs",
            "Wand of Lightning Bolts",
            "Wand of Paralysis",
            "Wand of the War Mage +2",
            "Wand of Wonder",
            "Wings of Flying",
        ]
    },
    "H": {  # major, very rare
        "items": [
            "Weapon +3",
            "Amulet of the Planes",
            "Animated Shield",
            "Belt of Giant Strength (Fire/Frost/Stone, STR 25)",
            "Candle of Invocation",
            "Crystal Ball",
            "Cube of Force (improved)",
            "Demon Armor",
            "Dragon Scale Mail",
            "Dwarven Plate (+2 AC, no speed penalty)",
            "Dwarven Thrower (war hammer, returns when thrown)",
            "Efreeti Bottle",
            "Figurine of Wondrous Power (obsidian steed)",
            "Frost Brand Sword",
            "Helm of Brilliance",
            "Horn of Valhalla (bronze)",
            "Ioun Stone (absorption, agility, fortitude, insight, intellect, leadership, mastery, regeneration, strength, sustenance)",
            "Iron Flask",
            "Manual of Bodily Health",
            "Manual of Gainful Exercise",
            "Manual of Golems",
            "Manual of Quickness of Action",
            "Mirror of Life Trapping",
            "Nine Lives Stealer",
            "Oathbow",
            "Ring of Regeneration",
            "Ring of Shooting Stars",
            "Ring of Telekinesis",
            "Robe of Scintillating Colors",
            "Robe of Stars",
            "Rod of Absorption",
            "Rod of Alertness",
            "Rod of Security",
            "Rod of the Pact Keeper +3",
            "Scimitar of Speed",
            "Shield +3",
            "Spellguard Shield",
            "Staff of Fire",
            "Staff of Frost",
            "Staff of Power",
            "Staff of Striking",
            "Staff of Thunder and Lightning",
            "Sword of Sharpness",
            "Tome of Clear Thought (+2 INT, raises max)",
            "Tome of Leadership and Influence (+2 CHA)",
            "Tome of Understanding (+2 WIS)",
            "Wand of Polymorph",
            "Wand of the War Mage +3",
        ]
    },
    "I": {  # major, legendary
        "items": [
            "Apparatus of Kwalish",
            "Armor of Invulnerability",
            "Belt of Giant Strength (Storm/Cloud, STR 29)",
            "Carpet of Flying",
            "Crystal Ball of Mind Reading",
            "Crystal Ball of Telepathy",
            "Crystal Ball of True Seeing",
            "Dancing Sword",
            "Demon Armor (improved)",
            "Holy Avenger",
            "Horn of Valhalla (iron)",
            "Ioun Stone (greater absorption, reserve)",
            "Iron Flask (improved)",
            "Luck Blade",
            "Plate Armor +3",
            "Ring of Djinni Summoning",
            "Ring of Elemental Command (air/earth/fire/water)",
            "Ring of Invisibility",
            "Ring of Spell Turning",
            "Ring of Three Wishes",
            "Robe of the Archmagi",
            "Rod of Lordly Might",
            "Staff of the Magi",
            "Sword of Answering",
            "Talisman of Pure Good",
            "Talisman of the Sphere",
            "Talisman of Ultimate Evil",
            "Tome of the Stilled Tongue",
            "Vorpal Sword",
            "Well of Many Worlds",
        ]
    }
}

HOARD_MAGIC_ITEMS = {
    "0-4":   [("A", 6), ("B", 4), ("C", 0), ("F", 0)],
    "5-10":  [("A", 4), ("B", 6), ("C", 6), ("F", 2), ("G", 0)],
    "11-16": [("C", 8), ("D", 4), ("E", 0), ("F", 2), ("G", 5), ("H", 0)],
    "17+":   [("C", 6), ("D", 8), ("E", 6), ("F", 0), ("G", 4), ("H", 6), ("I", 2)],
}

TOOLS = [
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "loot_generate",
            "description": "Generate treasure appropriate for a monster or encounter. Use after combat to reward the party with coins, gems, art, and magic items.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cr":          {"type": "string",  "description": "Challenge rating of the monster(s), e.g. '5', '1/4', '17'"},
                    "hoard":       {"type": "boolean", "description": "True for a full treasure hoard (boss/lair). False (default) for individual monster loot."},
                    "magic_items": {"type": "boolean", "description": "Include magic items (default true for hoards, false for individuals)"}
                },
                "required": ["cr"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "loot_magic_item",
            "description": "Generate a single random magic item from a specific rarity tier. Use when awarding a specific magic item reward.",
            "parameters": {
                "type": "object",
                "properties": {
                    "rarity": {"type": "string", "description": "common, uncommon, rare, very_rare, or legendary"}
                },
                "required": ["rarity"]
            }
        }
    }
]


def execute(function_name, arguments, config):

    if function_name == "loot_generate":
        cr             = str(arguments.get("cr", "1"))
        hoard          = bool(arguments.get("hoard", False))
        include_magic  = arguments.get("magic_items", hoard)

        tier = _cr_tier(cr)

        lines = [f"💰 **{'Treasure Hoard' if hoard else 'Individual Loot'} (CR {cr})**"]

        # Coins
        coin_fn  = _COIN_TABLES["hoard" if hoard else "individual"].get(tier)
        coins    = coin_fn() if coin_fn else {"gp": _roll(2, 6)}
        total_gp = _gp_value(coins)
        lines.append(f"\n**Coins:** {_coins_str(coins)} (~{total_gp:,.0f}gp value)")

        if hoard:
            # Gems
            gem_roll = _roll(1, 6)
            if gem_roll >= 3 and tier in GEMS:
                gem_tiers  = GEMS[tier]
                chosen_tier = random.choice(gem_tiers)
                count      = _roll(1, 6)
                gems       = random.choices(chosen_tier[1], k=count)
                lines.append(f"\n**Gems ({count}x {chosen_tier[0]} each):**")
                for g in gems:
                    lines.append(f"  • {g}")

            # Art objects
            art_roll = _roll(1, 6)
            if art_roll >= 3 and tier in ART_OBJECTS:
                count = _roll(1, 4)
                arts  = random.choices(ART_OBJECTS[tier], k=count)
                lines.append(f"\n**Art Objects:**")
                for a in arts:
                    lines.append(f"  • {a}")

        # Magic items
        if include_magic and tier in HOARD_MAGIC_ITEMS:
            magic_lines = []
            for table_key, dc in HOARD_MAGIC_ITEMS[tier]:
                if _roll(1, 100) <= dc:
                    if table_key in MAGIC_ITEMS:
                        item = random.choice(MAGIC_ITEMS[table_key]["items"])
                        magic_lines.append(f"  • {item} (Table {table_key})")
            if magic_lines:
                lines.append(f"\n**Magic Items:**")
                lines.extend(magic_lines)
            else:
                lines.append(f"\n*No magic items this time.*")

        return "\n".join(lines), True

    elif function_name == "loot_magic_item":
        rarity       = arguments.get("rarity", "uncommon").lower()
        rarity_tables = {
            "common":    ["A"],
            "uncommon":  ["B", "F"],
            "rare":      ["C", "G"],
            "very_rare": ["D", "H"],
            "legendary": ["E", "I"],
        }
        tables    = rarity_tables.get(rarity, ["B"])
        table_key = random.choice(tables)
        if table_key not in MAGIC_ITEMS:
            return f"No magic items found for rarity '{rarity}'.", False
        item = random.choice(MAGIC_ITEMS[table_key]["items"])
        return f"✨ **Magic Item ({rarity.replace('_', ' ').title()}):** {item}", True

    return f"Unknown function: {function_name}", False
