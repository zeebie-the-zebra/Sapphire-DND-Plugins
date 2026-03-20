"""
dnd-random-tables — tools

Pre-built rollable tables for common improvisation moments.
Use these instead of generating content from scratch — reduces
hallucination and repetition, especially in low-parameter models.

All results are seeded by a dice roll so the LLM should call dice_roll
first and pass the result in, or use table_roll which handles rolling internally.
"""

import random
import json

ENABLED = True
EMOJI = '🎲'
AVAILABLE_FUNCTIONS = [
    'table_list',
    'table_roll',
    'table_generate_npc',
    'table_generate_tavern',
    'table_generate_shop',
    'table_generate_encounter',
    'table_generate_treasure',
    'table_generate_magic_item',
    'table_generate_curse',
    'table_generate_lair',
    'table_generate_dungeon_room',
    'table_generate_wildmagic',
    'table_generate_potion_effect',
]

# ---------------------------------------------------------------------------
# TABLE DATA
# ---------------------------------------------------------------------------

TABLES = {

    # -------------------------------------------------------------------------
    # NPC NAMES BY RACE
    # -------------------------------------------------------------------------
    "names_human_male": [
        "Aldric", "Bram", "Callan", "Doven", "Edmund", "Finn", "Garrett", "Hadwin",
        "Ivan", "Jasper", "Kester", "Leon", "Marcus", "Nolan", "Oswin", "Perrin",
        "Quentin", "Roland", "Sebastian", "Theron", "Ulric", "Victor", "Wyatt", "Xavier",
        "York", "Zander"
    ],
    "names_human_female": [
        "Adela", "Brynn", "Cora", "Dara", "Elara", "Fiona", "Gwendolyn", "Helena",
        "Isolde", "Joanna", "Katarina", "Lyra", "Mirabel", "Nadia", "Ophelia", "Petra",
        "Quinn", "Rosalind", "Seraphina", "Thea", "Una", "Veronica", "Willa", "Xena",
        "Yvette", "Zara"
    ],
    "names_human_surname": [
        "Ashford", "Blackwood", "Cromwell", "Dunmore", "Everhart", "Fairfax", "Greystone",
        "Hawthorne", "Ironside", "Jasper", "Kingsley", "Lockwood", "Moorland", "Northcott",
        "Oakenshield", "Proudfoot", "Queensbury", "Ravencrest", "Silverdale", "Thornwood",
        "Underhill", "Valmont", "Wyndham", "Yarrow", "Zephyrus"
    ],

    "names_elf": [
        "Aelindra", "Caladwen", "Eirien", "Faelith", "Galadhor", "Ithilwen",
        "Laerindë", "Mireth", "Naeris", "Orophin", "Rúmil", "Silwen",
        "Tauriel", "Vanyel", "Xandrel", "Yrial", "Zephyril", "Aelric",
        "Caelum", "Elowen", "Faelyn", "Gilraen", "Iminya", "Luthien"
    ],
    "names_dwarf": [
        "Aldana", "Bofri", "Darri", "Dunn", "Erna", "Fori", "Gimra", "Helga",
        "Ingvar", "Jorunn", "Kettil", "Kili", "Lofna", "Magni", "Nori", "Ormr",
        "Sigrid", "Thorin", "Thorva", "Trorin", "Undis", "Vigdis", "Durin", "Balin"
    ],
    "names_halfling": [
        "Arlo", "Bingo", "Callie", "Daisy", "Elmo", "Fanny", "Garnet", "Halfred",
        "Isbo", "Jasper", "Kester", "Lila", "Lobelia", "Mable", "Merric", "Ned",
        "Olo", "Osborn", "Perrin", "Pip", "Rosie", "Rosamund", "Samson", "Seraphina",
        "Tillman", "Togo", "Wendel", "Wilibald", "Willow"
    ],
    "names_tiefling": [
        "Akta", "Brimstone", "Carrion", "Damakos", "Ekemon", "Iados", "Kairon",
        "Leucis", "Melech", "Morthos", "Nemeia", "Orianna", "Pelaios", "Rieta",
        "Therai", "Virtue", "Zariel", "Akta", "Bune", "Criella", "Dantalion", "Eligor"
    ],
    "names_dragonborn": [
        "Arjhan", "Balasar", "Bharash", "Donaar", "Ghesh", "Heskan", "Kriv",
        "Medrash", "Mehen", "Nadarr", "Pandjed", "Patrin", "Rhogar", "Shamash",
        "Shedinn", "Tarhun", "Torinn", "Akta", "Mishann", "Uadjit"
    ],
    "names_gnome": [
        "Alston", "Alvyn", "Bimpnottin", "Namfoodle", "Zooko", "Breena", "Caramip",
        "Donab", "Eldon", "Erky", "Fizwick", "Fonkin", "Frug", "Gerbo", "Gimble",
        "Glim", "Jebeddo", "Kellen", "Namfoodle", "Orryn", "Roondar", "Seebo", "Sindri",
        "Warryn", "Wrenn", "Zook"
    ],
    "names_orc": [
        "Bagrak", "Dench", "Feng", "Gell", "Henk", "Holg", "Imsh", "Keth",
        "Krusk", "Mhurren", "Ront", "Shump", "Thokk", "Varg", "Yurk", "Grom"
    ],

    # -------------------------------------------------------------------------
    # TAVERN NAMES & DETAILS
    # -------------------------------------------------------------------------
    "tavern_names": [
        "The Rusty Flagon", "The Broken Wheel", "The Salty Anchor", "The Blind Pig",
        "The Wandering Minstrel", "The Copper Kettle", "The Black Sheep",
        "The Silver Stag", "The Crow's Nest", "The Two Lanterns",
        "The Lucky Bastard", "The Hanging Rope", "The Tipped Scales",
        "The Muddy Boot", "The Gilded Goat", "The Sleeping Giant",
        "The Dragon's Breath", "The King's Folly", "The Witch's Cup",
        "The Old Oak", "The Frying Pan", "The Laughing Horse", "The Drowned Rat"
    ],
    "tavern_ambiance": [
        "A fire crackles in a massive hearth, smoke curling toward soot-stained rafters",
        "The smell of roasting meat mingles with pipe smoke, patrons laughing boisterously",
        "Tattered maps and worn weapons adorn the walls, testimony to adventurers who came before",
        "A battered lute hangs above the bar, waiting for a brave (or drunk) performer",
        "The floorboards creak with every step, and every table tells a story in its scratches",
        "A large black cauldron bubbles over the fire — the cook's legendary stew",
        "Faded portraits of forgotten nobles line the walls, their eyes following movement",
        "Stale ale and old secrets hang in the air equally thick"
    ],
    "tavern_regulars": [
        "A one-eyed dwarf nursing the same drink for three hours",
        "A group of merchants arguing quietly over a ledger",
        "A bard tuning a fiddle, waiting for the right moment to perform",
        "Two off-duty guards playing dice in the corner",
        "A mysterious cloaked figure in the darkest booth",
        "A loudly boasting mercenary telling war stories no one believes",
        "An elderly woman knitting while she sips tea — seemingly out of place",
        "A nervous young noble sneakily sampling ale for the first time"
    ],

    # -------------------------------------------------------------------------
    # CITY/LOCATION NAMES
    # -------------------------------------------------------------------------
    "city_prefix": [
        "Port", "Fort", "New", "Old", "High", "Low", "River", "Stone",
        "Iron", "Silver", "Golden", "King's", "Queen's", "Lord's", "Winter"
    ],
    "city_suffix": [
        "haven", "ford", "watch", "gate", "vale", "hollow", "hold", "keep",
        "bridge", "march", "ton", "burg", "shire", "reach", "port", "point"
    ],
    "tavern_districts": [
        "The Docks", "The Temple District", "The Market Square", "The Merchant's Row",
        "The Old Quarter", "The Warehouse District", "The Noble Heights", "The Slums",
        "The Wizard's Tower District", "The Military Ward", "The Artisan's Guild",
        "The Old Gate", "The Riverfront", "The Crematorium", "The Foreign Quarter"
    ],

    # -------------------------------------------------------------------------
    # NPC DETAILS
    # -------------------------------------------------------------------------
    "npc_appearance": [
        "A distinctive scar running from eyebrow to cheek",
        "Unusually pale or dark skin for their race",
        "Missing a hand (or has a prosthetic)",
        "Wild, untamed hair that seems to have a life of its own",
        "Tattoos covering visible skin — tribal or decorative",
        "An eyepatch, though both eyes seem present beneath",
        "Wears mismatched but high-quality clothing",
        "Always sweating, even in cold weather",
        "Speaks with a noticeable stutter or lisp",
        "Moves with an unusual hitch or limp",
        "Has a nervous habit of touching their weapon",
        "Wears their profession visibly — apron, tabard, robes",
        "Has an unusually large or small stature",
        "Carries an unusual pet or creature",
        "Their shadow seems to move slightly wrong"
    ],
    "npc_quirks": [
        "Never makes eye contact, always scanning exits",
        "Repeats the last word of every sentence twice",
        "Has an opinion about everything but states it as obvious fact",
        "Fidgets constantly with a small object (coin, ring, dagger)",
        "Laughs before finishing sentences when nervous",
        "Refers to themselves in the third person",
        "Smells strongly of a single herb (lavender, garlic, cloves)",
        "Asks one personal question before answering anything",
        "Has a visible scar they offer a different explanation for",
        "Speaks entirely in understatements — 'a bit of a situation' means catastrophe",
        "Can't resist correcting people's grammar",
        "Always whistles when nervous",
        "Collects strange things in their pockets",
        "Speaks to themselves when thinking",
        "Has an irrational fear of a common object"
    ],
    "npc_occupations": [
        "Innkeeper", "Blacksmith", "Apothecary", "Dockworker", "Cartographer",
        "Fence (criminal)", "Herbalist", "Tax Collector", "Beggar (retired spy)",
        "Travelling Merchant", "Retired Soldier", "Priest (lapsed)", "Gravedigger",
        "Scribe", "Ratcatcher", "Courier", "Tattooist", "Butcher", "Midwife",
        "Bounty Hunter", "Jailer", "Beekeeper", "Farrier", "Chandler", "Tanner",
        "Brewer", "Jeweler", "Glassblower", "Glass Painter", "Architect",
        "Bookbinder", "Cook", "Dyer", "Fletcher", "Leatherworker", "Mason",
        "Miller", "Minstrel", "Painter", "Potter", "Ropemaker", "Shipwright"
    ],
    "npc_bond": [
        "Owes a debt to a powerful crime lord",
        "Secretly in love with a noble's spouse",
        "Is actually a noble in disguise",
        "Seeking revenge for a murdered family member",
        "Possesses a map to a legendary treasure",
        "Is an informant for the city watch",
        "Smuggles refugees out of the city",
        "Knows secrets about the local temple",
        "Has been cursed by a fey creature",
        "Is searching for a missing sibling"
    ],
    "npc_secret": [
        "Actually three separate people taking turns",
        "Is a shapechanger in disguise",
        "Their fortune comes from dark deals",
        "Is secretly training to be an assassin",
        "Knows powerful magic but pretends not to",
        "Is a ghost who doesn't realize they're dead",
        "Owes their life to an evil entity",
        "Has been replaced by a doppelganger",
        "Is actually a disguised dragon",
        "Knows the location of a lost artifact"
    ],

    # -------------------------------------------------------------------------
    # ENCOUNTERS
    # -------------------------------------------------------------------------
    "road_encounters": [
        "A merchant wagon with a broken axle, driver waving down help",
        "A riderless horse with an empty saddle, blood on the saddlebag",
        "A group of refugees heading the opposite direction, looking frightened",
        "A toll booth that wasn't on any map, staffed by three rough-looking men",
        "A fresh grave beside the road with no name marker",
        "A child sitting alone on a milestone, watching the party approach",
        "A travelling tinker with a cart full of oddly specific items",
        "Smoke rising from a farmstead just off the road",
        "A military patrol moving fast, ignoring everything around them",
        "An injured wolf lying in the road — not growling, just watching",
        "A shrine to a god of the road, recently vandalized",
        "A tree in the middle of the road that definitely wasn't there before",
        "The sounds of arguing from the treeline — two voices, no resolution",
        "A royal courier on a lathered horse heading in the opposite direction",
        "A bridge with a toll — the troll was deported, now just a bored guard",
        "A campfire still burning — food on the fire, no one around",
        "A peddler selling 'cured' dragon scales that are clearly fake",
        "A half-collapsed bridge with a nervous goat standing on it",
        "A strange monolith covered in glowing runes (no one can read them)",
        "A wedding procession blocking the road, everyone drunk and happy"
    ],
    "forest_encounters": [
        "Giant spiderwebs stretch between trees, glistening with morning dew",
        "A clearing filled with stone statues — people frozen mid-step",
        "A hollow tree that whispers when approached",
        "Mushrooms forming a perfect circle, some bioluminescent",
        "A dead end in the path with scratch marks suggesting something climbed out",
        "A stream with water that sparkles unnaturally",
        "An old stone altar, weathered but with fresh blood stains",
        "Birdsong that suddenly stops — the forest has gone silent",
        "A massive oak with a door-sized hollow, warm light inside",
        "Tracks of something massive that doesn't match any known creature",
        "A pond with a reflection that doesn't match the viewer",
        "Fey lights dancing between the trees, beckoning deeper",
        "A wounded unicorn, horn dimmed, begging for help",
        "A statue of a forgotten god, vines slowly reclaiming it",
        "A patch of flowers that all turn to face the party"
    ],
    "dungeon_encounters": [
        "A hallway that seems to get longer the more they walk",
        "A room filled with mirrors — one shows a different room",
        "A skeleton in noble's clothing, clutching a locket",
        "Glyphs on the floor that glow when approached",
        "A pit trap that's been sprung — bones at the bottom",
        "A chest that screams when opened (trapped, but not violently)",
        "Walls covered in writing that moves when not looked at directly",
        "A fountain with water that turns to blood when touched",
        "An obvious pressure plate with no visible traps nearby",
        "A door with dozens of scratch marks from the inside",
        "A creature that's been dead for centuries but still 'lives'",
        "A room where gravity works differently",
        "A mirror that shows the viewer's deepest fear",
        "Animated armor standing at attention, awaiting orders",
        "A pile of treasure with a displacer beast sleeping on top"
    ],
    "urban_encounters": [
        "A pickpocket trying to lift something from the party",
        "An angry mob forming outside a suspected witch's home",
        "A street performer with actual magic abilities",
        "A drunk noble causing a scene, demanding 'the best room'",
        "The city watch searching everyone entering a district",
        "A child's ball thrown over a fence, owner too scared to retrieve it",
        "A street vendor selling 'authentic' dragon scales",
        "Two merchants in a heated argument about territory",
        "A funeral procession blocking the main road",
        "A sudden flash of magic from an upper story window",
        "A beggar offering to guide the party 'somewhere interesting'",
        "The smell of fresh bread from a bakery, impossibly enticing",
        "A heated debate at a philosophical society meeting",
        "A lost pet pixie causing chaos (literally on fire)",
        "A sudden eclipse — or is someone blocking the sun?"
    ],

    # -------------------------------------------------------------------------
    # DUNGEON DRESSING
    # -------------------------------------------------------------------------
    "dungeon_dressing_traps": [
        "A pressure plate disguised as a normal stone, hairline crack visible",
        "Poison gas venting from ceiling grates (mechanism visible)",
        "A pit in the darkness with sharpened stakes at the bottom",
        "Swinging axe blades, motion-triggered, saw marks in the walls",
        "A door handle that shocks when touched (metal visibly different)",
        "Arrows protruding from the wall at random angles",
        "A floor section that's noticeably darker than surroundings",
        "Tripwire at ankle height, connected to a bell in the walls",
        "Ceiling glyphs that pulse faintly with magical energy",
        "A section of wall that's actually a hidden door (seams visible)"
    ],
    "dungeon_dressing_atmosphere": [
        "A sconce with a torch burned down to a stub hours ago",
        "Scratches on the floor suggesting something heavy was dragged recently",
        "An iron door, ajar, with three different locks — all unlocked",
        "Water stains on the ceiling in the shape of a face",
        "A small pile of copper coins, arranged into a neat triangle",
        "A boot, just the one, standing upright in the middle of the corridor",
        "Bones of a small animal in a corner — picked completely clean",
        "A shattered lantern surrounded by a splash of old oil",
        "Writing scratched into the wall, too worn to read fully",
        "A rope tied to an iron ring in the ceiling, end frayed",
        "A crate that's been opened from the inside",
        "The smell of sulfur with no visible source",
        "A door that opens inward — into a wall",
        "An empty scabbard, quality leather, buckle broken",
        "Wet footprints leading to a dead end",
        "Mysterious bloodstains that don't match any creature type",
        "Dust that's been disturbed recently in a specific pattern",
        "A child's toy lying in the middle of a dangerous corridor",
        "Writings in a language that hurts to look at",
        "A bowl of fruit on a table — still fresh after centuries"
    ],
    "dungeon_dressing_treasure": [
        "A loose stone that hides a small pouch of gems",
        "A weapon rack — one still has a +1 weapon, the rest rusted",
        "A chest with a broken lock (forced open previously)",
        "A pile of bones with a signet ring on one finger",
        "A bookshelf with one book that doesn't match the others",
        "A suit of armor that's actually magical",
        "A mirror that's worth a small fortune",
        "A loose flagstone hiding a secret compartment",
        "A broken clock that still has precious metals inside",
        "A tapestry showing a battle — has a hidden pocket in the hem"
    ],
    "dungeon_dressing_corpses": [
        "A skeleton in armor, clutching a dagger, surrounded by coin",
        "A body that looks like it simply sat down and died",
        "Charred remains near a fire trap that didn't fully work",
        "A corpse reaching toward a door that won't open",
        "Two skeletons locked in combat, both have weapons",
        "A pile of bodies suggesting a last stand",
        "A single hand reaching out from rubble",
        "A headless body — the head is elsewhere in the room",
        "Remains that are... eating something. It's not alone.",
        "A body that's perfectly preserved in ice"
    ],

    # -------------------------------------------------------------------------
    # TRAPS (d20)
    # -------------------------------------------------------------------------
    "traps": [
        "Pressure plate triggers swinging axes from walls",
        "Pit trap with spikes at bottom — depth suggests 20ft",
        "Poison dart fired from wall when stepping on specific stone",
        "Door handle delivers electrical shock (2d8 lightning damage)",
        "Floor collapses into a spider-filled pit",
        "Glyph of warding triggers fire explosion (5d6 fire)",
        "Net drops from ceiling, raises victim to ceiling",
        "Grease on floor causes automatic DEX save or fall",
        "Magic mouth triggers and screams loudly (attracts attention)",
        "Ceiling collapses (15d6 bludgeoning, DEX save for half)",
        "Falling block traps the target (6d6 bludgeoning)",
        "Hypnotic pattern on walls causes confusion (WIS save)",
        "Gust of wind pushes party into a deeper pit",
        "Water fills room (swim or sink, CON save or hold breath)",
        "Silence field — no sound can escape or enter",
        "Alarm triggers — magical, can't be disabled without dispel",
        "Caltrops in floor — DEX save or 1d4 piercing per step",
        "Illusory floor hides a 30ft drop",
        "Gas leaks in — CON save or fall asleep for 1d4 hours",
        "Magic mouth delivers a cryptic warning before trap triggers"
    ],

    # -------------------------------------------------------------------------
    # TREASURE
    # -------------------------------------------------------------------------
    "mundane_treasures": [
        "A set of brass scales, expertly crafted",
        "A silver-backed mirror worth 25 gp",
        "A leather-bound journal with blank pages (the binding is valuable)",
        "A bronze statue of a minor deity worth 30 gp",
        "A bundle of exotic spices worth 20 gp",
        "A quality spyglass (works, but cracked lens reduces effectiveness)",
        "A music box that plays a haunting melody",
        "A vial of rare perfume worth 15 gp",
        "A carved ivory comb worth 35 gp",
        "A clockwork toy that still functions",
        "A painting of a noble (the noble is still alive and local)",
        "A ceremonial dagger with jeweled hilt worth 45 gp",
        "A set of gaming pieces made from semiprecious stones",
        "A sealed letter marked with a royal seal (don't open)",
        "A compass that points to the nearest magic item"
    ],
    "art_objects": [
        "A gold chalice engraved with scenes of a forgotten war",
        "A lapis lazuli sculpture of a dragon worth 150 gp",
        "A painted portrait in an ornate frame worth 75 gp",
        "A silk tapestry depicting a divine scene worth 200 gp",
        "A carved ivory box with scenes of hunting worth 100 gp",
        "A set of crystal glasses each worth 25 gp",
        "A bronze mask in the style of an ancient civilization worth 80 gp",
        "A silver-inlaid lute, the silver alone worth 50 gp",
        "A marble bust of an unknown noble worth 60 gp",
        "A collection of three gold coins from a fallen kingdom",
        "A ceremonial sword with a blade that never dulls (magical?)",
        "A mosaic made of semi-precious stones worth 250 gp",
        "A bloodstone ring with an inscription worth 40 gp",
        "A bejeweled birdcage with a skeleton inside",
        "A crown that clearly belongs to a fallen monarchy"
    ],
    "gemstones": [
        "Banded agate (10 gp)", "Blue quartz (10 gp)", "Eye agate (20 gp)",
        "Hematite (10 gp)", "Lapis lazuli (25 gp)", "Malachite (15 gp)",
        "Moss agate (15 gp)", "Obsidian (20 gp)", "Pyrite (5 gp)",
        "Rhodochrosite (15 gp)", "Tiger eye agate (20 gp)", "Tourmaline (30 gp)",
        "Bloodstone (35 gp)", "Chalcedony (25 gp)", "Chrysoprase (30 gp)",
        "Jasper (25 gp)", "Moonstone (40 gp)", "Onyx (30 gp)", "Quartz (20 gp)"
    ],

    # -------------------------------------------------------------------------
    # MERCHANT INVENTORIES
    # -------------------------------------------------------------------------
    "shop_general_goods": [
        "Rope (50ft), torches, iron rations, a crowbar of dubious quality",
        "Lanterns, oil, locks (poor quality), leather straps",
        "Healing herbs (non-magical), bandages, needles, thread",
        "Used adventuring gear: dented shield, mismatched boots, good backpack",
        "Dried meat, hard cheese, waybread, a keg of cheap ale",
        "Blank journals, inkpots, candles, a folded map (local area only)",
        "Tools: hammers, chisels, saw, nails, a spirit level",
        "Assorted oddities: compass that points south, glass eye, seven identical keys"
    ],
    "shop_weapons": [
        "Three shortswords, good quality, 15 gp each",
        "A masterwork longbow, 75 gp",
        "A suit of chainmail (used), 50 gp",
        "Two handaxes, freshly forged, 10 gp each",
        "A heavy crossbow with 20 bolts, 35 gp",
        "A silvered dagger (for lycanthropes), 105 gp",
        "A net, three caltrops, and ball bearings — trick weapons",
        "A composite longbow, 50 gp, requires 16 STR"
    ],
    "shop_armor": [
        "Leather armor (new), 10 gp | Studded leather, 45 gp",
        "Chain shirt, 50 gp | Scale mail, 50 gp",
        "Breastplate (used, dented), 200 gp | Full plate (custom order)",
        "Shields: wood (3 gp), steel (10 gp), spiked (15 gp)",
        "Helmets: leather (2 gp), metal (10 gp), visored (25 gp)",
        "Gauntlets: leather (1 gp), chain (8 gp), plate (15 gp)",
        "Boots: soft (2 gp), hard (5 gp), armored (20 gp)",
        "Cloaks: wool (2 gp), fur-lined (25 gp), magical (500+ gp)"
    ],
    "shop_alchemist": [
        "Healing potion (common), 50 gp | Antitoxin, 20 gp",
        "Alchemist's fire (2d6 fire), 20 gp | Acid vial (2d6 acid), 25 gp",
        "Sunrod (4 hours bright), 2 gp | Tinderbox, 5 gp",
        "Basic herbs: wolfsbane (5 gp), lavender (2 gp), sage (1 gp)",
        "Empty vials (1 sp each), stoppered bottles, alchemy glass",
        "Potion of water breathing, 150 gp (rare!)",
        "Alchemist's kit (complete), 45 gp",
        "A mysterious unlabeled vial — 'buyer beware', 10 gp"
    ],
    "shop_bookstore": [
        "A tome of local history, 25 gp",
        "A spellbook (blank), 50 gp",
        "Maps: local (5 gp), regional (15 gp), kingdom (50 gp)",
        "A book of nursery rhymes with hidden code in first letters",
        "Philosophy texts (three volumes), 30 gp total",
        "A journal of a dead adventurer (adventure hook inside!)",
        "A bestiary of local creatures, 40 gp",
        "An obviously fake 'ancient' text, 100 gp (not worth 1 cp)"
    ],
    "shop_magic_items": [
        "Potion of healing (standard), 50 gp | Potion of greater healing, 150 gp",
        "Bag of holding (200 gp, slightly damaged — intermittent issues)",
        "Cloak of billowing (purely cosmetic, 100 gp)",
        "Dust of disappearance, 150 gp | Dust of dryness, 100 gp",
        "A scroll of a 1st-level spell (25 gp), 2nd-level (75 gp)",
        "Ring of water walking, 400 gp (slightly too tight)",
        "A wand of magic missiles (7 charges), 450 gp",
        "Driftglobe (continues to float, can't be grounded), 250 gp"
    ],

    # -------------------------------------------------------------------------
    # WEATHER & ENVIRONMENT
    # -------------------------------------------------------------------------
    "weather_temperate": [
        "Clear skies — comfortable temperature, good visibility",
        "Thin clouds — diffused light, comfortable walking",
        "Overcast — heavy cloud cover, no sun, oppressive feel",
        "Light rain — hoods up, ground damp, fires struggle",
        "Heavy rain — visibility reduced, rivers rising, roads muddy",
        "Dense fog — visibility 60ft, sounds carry strangely",
        "Strong wind — riding difficult, ranged attacks at disadvantage",
        "Light snow — tracks covered, cold but manageable",
        "Hot and clear — exhaustion risk after 2 hours unshaded",
        "Cold snap — ice on surfaces, exposed skin stings"
    ],
    "weather_desert": [
        "Clear and scorching — water critical, shade essential",
        "Hot wind — sand gets everywhere, eyes water",
        "Overcast and close — dust storm building",
        "Sandstorm — visibility near zero, shelter essential",
        "Unseasonable rain — flash flood risk in canyons",
        "Cold desert night — temperature plummets",
        "Heat shimmer — mirages on horizon, distance distorted",
        "Perfect weather — rare, suspicious"
    ],

    # -------------------------------------------------------------------------
    # PLOT HOOKS & SECRETS
    # -------------------------------------------------------------------------
    "plot_hooks_quest": [
        "A dying courier presses a sealed letter into your hands and dies",
        "A child tugs your sleeve: 'The man in the tower told me to find you'",
        "You've been followed since entering town — they finally approach",
        "A notice board is covered in wanted posters — one looks like you",
        "An anonymous letter offers gold for a 'collection' from a crypt",
        "A noble publicly offers a reward for a lost family heirloom",
        "You're approached by someone claiming to be your distant relative",
        "A religious order sends a formal invitation to their temple",
        "A merchant offers free supplies in exchange for a 'small favor'",
        "The local lord demands to see you — immediately"
    ],
    "plot_hooks_mystery": [
        "Everyone in town insists the old mill is abandoned — smoke rises nightly",
        "The blacksmith's door has been welded shut from the inside",
        "A witness claims the murder victim was seen arguing with... themselves",
        "The key to a locked room was inside the room when the door opened",
        "Three separate people claim to be the real Baron",
        "The body is gone by morning — no tracks, no evidence",
        "A servant remembers everything except the night in question",
        "The only witness is a creature that only speaks the truth — but is cryptic",
        "Evidence points to someone who has been dead for ten years",
        "The victim was killed by their own weapon — which is still in their hand"
    ],
    "rumors_city": [
        "A merchant's warehouse burned down last night — some say it wasn't an accident",
        "The city guard has been doubling patrols near the docks for three nights",
        "Someone's been paying street kids silver to watch the north gate",
        "A noblewoman hasn't been seen in public for two weeks — illness?",
        "There's a new fence operating out of the tannery district",
        "The temple has been turning away sick pilgrims, priests look frightened",
        "Three sailors went missing — their ship found drifting, cargo intact",
        "A beggar claims he saw a body dragged through an alley",
        "The blacksmith's apprentice disappeared same night as a weapon shipment",
        "The old wizard's tower at the edge of town has lights in it again",
        "The tax collector raised the merchant levy — half the stalls went dark",
        "Someone's been leaving dead ravens on guild leaders' doorsteps",
        "A traveller arrived three days ago, hasn't left their inn room since",
        "The rat catcher swears the rats move in organized columns",
        "There's a betting pool on when the mayor resigns",
        "A cartographer arrived asking very specific questions about sewers",
        "Two rival thieves' guild lieutenants found dead — no marks",
        "The herbalist has had a line out her door since yesterday — why?",
        "A travelling circus set up outside the east wall — pay in gold",
        "The city's wells have been tasting strange for a fortnight"
    ],
    "rumors_tavern": [
        "They say the cellar connects to the old catacombs",
        "The previous owner disappeared — some say he's still here",
        "There's a back room where... certain dealings happen",
        "The ghost of a previous patron appears to certain people",
        "The cook uses meat from... let's say 'unusual sources'",
        "There's a hidden wine cellar from before the plague years",
        "A certain regular is actually a noble in disguise",
        "The tavern was built on the site of an ancient sacrifice",
        "The owner knows things about the future — how?",
        "Someone tried to burn the place down last month"
    ],
    "secrets_dark": [
        "The town guard is controlled by a secret society",
        "The mayor has been dead for a month — no one noticed",
        "The temple is actually a front for a thieves' guild",
        "Children have been disappearing on specific nights",
        "A merchant is selling people into slavery — right in town",
        "The 'healing' potions are made from something terrible",
        "The bank has been embezzling for years",
        "The local lord is actually a shapechanger",
        "The well water is slowly poisoning the town",
        "Someone in town is a serial killer — they kill once a month"
    ],

    # -------------------------------------------------------------------------
    # CREATURE APPEARANCE (for encounters)
    # -------------------------------------------------------------------------
    "goblin_appearance": [
        "A large goblin with a impressive scar across its face",
        "A goblin wearing mismatched armor that's two sizes too big",
        "A goblin trying to look tough but visibly shaking",
        "An unusually clean goblin — unsettlingly so",
        "A goblin with a collection of stolen shiny things",
        "A goblin missing most of its teeth, grinning horribly",
        "A goblin commander with a tattered banner",
        "A goblin that keeps twitching and looking around"
    ],
    "undead_appearance": [
        "Skeleton in rusted armor, one bone missing from its hand",
        "Zombie in burial clothes, flesh still partly intact",
        "Ghost that flickers in and out of visibility",
        "Ghoul with unusually long claws, crouching",
        "Wight that still wears its heraldry — a forgotten noble house",
        "Skeleton with bone growths in wrong places",
        "Crawling claw reaching for your ankle",
        "Ghostly child that says nothing, only watches"
    ],

    # -------------------------------------------------------------------------
    # TIME & EVENTS
    # -------------------------------------------------------------------------
    "time_of_day_events": [
        "Dawn: Mist rolling off the water, birds beginning to sing",
        "Morning: Market setting up, children heading to school",
        "Midday: Crowds in the streets, merchants at peak business",
        "Afternoon: People growing tired, shadows lengthening",
        "Evening: Lights flickering on, families gathering",
        "Night: Streets empty except for guards and criminals",
        "Midnight: The truly strange things begin to stir",
        "Witching hour: A church bell rings though it shouldn't"
    ],
    "festival_events": [
        "Harvest festival — everyone drunk, everyone happy",
        "Founding day — military parade, speeches, free food",
        "Religious holiday — temple celebrations, pilgrims arriving",
        "Market fair — merchants from across the realm, rare goods",
        "Anniversary of a great victory — military displays",
        "Midwinter — warmth festivals, fires in the streets",
        "Coming of age ceremony — young people proving themselves",
        "Royal visit — everything cleaned, everything polished",
        "Funeral games — competitive memorial for a great figure",
        "Midsummer — bonfires, celebrations, magic in the air"
    ],

    # -------------------------------------------------------------------------
    # RANDOM DETAILS
    # -------------------------------------------------------------------------
    "strange_smells": [
        "Rotting fish and salt air",
        "Fresh bread and honey",
        "Sulfur and something burning",
        "Lavender and old paper",
        "Blood and iron",
        "Rain on hot stone",
        "Death and lilies",
        "Smoke and roasting meat",
        "Musk and animal fur",
        "Something sweet but wrong"
    ],
    "strange_sounds": [
        "Distant bells — but no church nearby",
        "Whispering with no visible source",
        "Children singing a nursery rhyme in a dead language",
        "A door slamming repeatedly",
        "Crying from inside a locked room",
        "Footsteps following when alone",
        "Music from beneath the floorboards",
        "An animal howling in a language it shouldn't know",
        "A baby laughing — in an abandoned building",
        "Breathing that isn't yours"
    ],

    # -------------------------------------------------------------------------
    # MAGIC ITEM QUIRKS
    # -------------------------------------------------------------------------
    "magic_item_quirks": [
        "The item hums with a barely audible melody only the wielder can hear",
        "Slight temperature fluctuations — warm to the touch in summer, cool in winter",
        "Faint glow that intensifies near magic users or sources",
        "The item weighs twice what it should",
        "Leaves a faint residue on hands that smells of ozone",
        "Occasionally displays a memory the wielder didn't expect (a past owner's memory)",
        "Changes color subtly based on the wielder's mood",
        "Whispers fragments of advice in stressful situations",
        "Refuses to be willingly dropped — grips the hand tighter",
        "Shows a brief vision when first picked up by a new owner",
        "The item is always slightly damp, no matter the conditions",
        "Makes a soft chiming sound when the moon is full",
        "Inscriptions on the item shift and rearrange when not being observed",
        "The item is unnaturally quiet — never makes a sound even when knocked",
        "Slightly too large or small for its apparent size category",
        "Has a faint heartbeat pulse detectable through touch",
        "Wielder occasionally smells smoke or flowers that aren't present",
        "The item points north when held loosely",
        "Able to stand perfectly balanced on its edge indefinitely",
        "Produces a drop of liquid each morning — never identified"
    ],
    "magic_item_origins": [
        "Forged by a legendary artificer whose name is now forbidden",
        "Blessed by a dying god in their final moments",
        "Created from the crystallized essence of a planar tear",
        "Once belonged to a hero who died in a famous battle",
        "Dropped from the heavens during a divine war",
        "Grown in a magical grove over a century",
        "Stolen from a vault beneath an aboleth's lair",
        "Conjured spontaneously from raw magical catastrophe",
        "Commissioned by a paranoid king who then tried to destroy it",
        "Exists in two places at once — neither copy is the original",
        "Slowed time itself during creation — aged the maker decades in moments",
        "Made from the fused bones of two rival mages",
        "Pulled from the dreams of a sleeping dragon",
        "Forged in a volcano by a fire giant smith-god",
        "Existed as an ordinary object until a spell was cast on its dying owner"
    ],

    # -------------------------------------------------------------------------
    # CURSES & HEXES
    # -------------------------------------------------------------------------
    "minor_curses": [
        "All food tastes faintly of ash for one week",
        "Shadow grows 10 feet longer in all directions",
        "Dreams each night of a place the character has never been",
        "Every lock opened becomes visible to all for one hour",
        "Hair changes color to match the nearest light source",
        "Character's reflection appears 1 second delayed",
        "Left and right hands occasionally swap which is dominant",
        "A small mark appears somewhere on the body each morning",
        "Words occasionally颠倒 word order in speech",
        "All liquids poured drift slightly left before landing",
        "An item the character owns disappears each dawn, returns at dusk different",
        "Character occasionally speaks a language they don't know for 1d4 sentences",
        "Unconsciously draws small symbols in any dust or dirt touched",
        "Animals follow the character but keep their distance",
        "Character's voice echoes slightly when alone",
        "Sleeping always feels like it's happening somewhere else first"
    ],
    "major_curses": [
        "Alignment shifts one step toward evil each dawn",
        "Character slowly turns to stone from the feet up (reversible with wish)",
        "Every secret spoken aloud within earshot is immediately known to all within 60ft",
        "A duplicate of the character appears and mimics them for 1 hour each day",
        "All undead within 300ft are aware of the character's presence always",
        "Character cannot beheal damage but cannot be killed either (at 0 HP, unconscious)",
        "A cursed mark appears on someone close to the character each week",
        "Character ages 1 year each time they sleep",
        "Every spell cast has a random secondary effect within 10ft",
        "Character can only speak in questions",
        "All metallic objects within 10ft rust slowly but continuously",
        "Character leaves no footprints in any surface",
        "A ghostly whisper narrates the character's actions aloud",
        "All plants within 30ft wither when the character is near",
        "Character occasionally phases through solid objects for 1d4 rounds"
    ],
    "curse_removal_difficulties": [
        "Can only be broken by the caster's death",
        "Requires a wish spell and the blood of the original victim",
        "Attached to a specific artifact that must be destroyed",
        "Cursed to believe the curse doesn't exist — curse is invisible to them",
        "Triggers only when the character attempts to break it",
        "Shared between three willing bearers — all must agree to remove it",
        "Grows stronger each time it is attempted to be removed",
        "Requires the character to perform the original act of injustice in reverse",
        "Requires a god to willingly give up a portion of their power",
        "Attaches to the character's soul — cannot be removed even by death"
    ],

    # -------------------------------------------------------------------------
    # UNDERDARK, SWAMP, MOUNTAIN, DESERT, ARCTIC ENCOUNTERS
    # -------------------------------------------------------------------------
    "underdark_encounters": [
        "A patrol of drow elite hunters, interrogating prisoners",
        "A lone deep gnome scholar mapping tunnels with glowing ink",
        "A fungus farmer tending luminescent mushroom groves",
        "A disabled mind flayer, missing its elder brain connection, muttering prophecies",
        "Duergar slavers with three hobgoblin captives in iron cages",
        "A massive translucent cave fish, passively drifting in a underground lake",
        "A trading caravan of svirfneblin with pack lizards",
        "A section of tunnel where gravity points sideways",
        "A shrine to a forgotten god covered in pulsing bioluminescent moss",
        "An outcrop of crystal that broadcasts thoughts aloud across frequencies",
        "A rogue gibbering mouther leaving trails of digested stone",
        "A council of abolethskins arguing over territory",
        "A collapsed section revealing older ruins beneath the current tunnel",
        "A pool of strange liquid that reflects a different location",
        "A bone collector assembling a skeleton from fallen adventurers"
    ],
    "swamp_encounters": [
        "Will-o'-wisp leading travelers deeper into the mire",
        "A hag's hut on a small island, accessible only by stepping stones",
        "A tribe of lizardfolk performing a sacred ritual",
        "A sinking boat with survivors calling for help from a half-submerged cabin",
        "Giant insects swarming around something metallic glittering in the mud",
        "A druid shapeshifted into an alligator, watching silently",
        "A dead body caught in roots — not drowned, something else killed them",
        "Hooded figures collecting swamp plants under moonlight",
        "A massive snapping turtle the size of a cottage",
        "Lightning strikes a dead tree — the wood chars but doesn't burn",
        "A shrine to a nature deity, offerings of precious gems sinking into mud",
        "A band of bullywugs arguing with a merchant who's clearly lost",
        "Quicksand disguised by a thin layer of algae",
        "A spectral army marching beneath the water's surface"
    ],
    "mountain_encounters": [
        "A young dragon practicing territorial displays on a ledge",
        "Stone giants playing a game with boulder goals — the 'ball' is a screaming captive",
        "A hermit wizard with an observatory, obsessively charting the stars",
        "An avalanche in slow motion — the snow so gradual it's almost unnoticeable",
        "A griffon nest with fledglings — parents circling protectively",
        "Rockslides that are actually the movement of an earth elemental",
        "A monastery carved into the cliff face, monks silent and watchful",
        "A storm that produces hail the size of fists — shelter essential",
        "A merchant caravan roped together crossing a narrow pass",
        "Basilisk sunbathing on a warm stone outcrop",
        "A frozen corpse frozen mid-climb, fingers frozen to the rock",
        "A harpy chorus whose song is genuinely beautiful for once",
        "A cloud giant's floating island drifting slowly between peaks",
        "Ancient runes carved into a monolith — no one remembers by whom",
        "A narrow bridge of stone over a bottomless chasm — troll bridge conditions apply"
    ],
    "desert_encounters": [
        "A caravan of traveling merchants, one has a mysterious locked chest",
        "An undead guardian of an ancient tomb, bound to protect it",
        "A desert elf tribe performing a coming-of-age ritual",
        "A mirage that shows a bustling city — completely still when approached",
        "A blue dragon wyrmling learning to hunt in the dunes",
        "Tomb robbers caught mid-heist, one injured, begging for help",
        "A powerful sorcerer conducting an arcane experiment in a magical tent",
        "Quicksand disguised as solid ground near an oasis",
        "A sphinx with a riddle the party will want to answer — and one they won't",
        "The skeleton of a colossal creature half-buried in sand",
        "Dust mephits herding a salamander for sport",
        "A cursed oasis that grants wishes but twists them",
        "Ameteor strike crater — still smoking, metal debris scattered",
        "A dragon turtle in an underground oasis beneath the sands",
        "Local guides refusing to go further — 'the desert is angry'"
    ],
    "arctic_encounters": [
        "A yeti killing something. It's not clear what. It's not moving.",
        "Aurora borealis that forms words in an ancient language briefly",
        "An ice wizard's tower, door frozen shut, muffled sounds from within",
        "A wounded remorhaz, danger to everything nearby",
        "Polar bear and cubs — one cub has something shiny in its mouth",
        "An abandtheft camp with signs of struggle and claw marks",
        "A storm that moves with purpose — almost intelligently",
        "Frost giant raiders scouting from an ice ship",
        "A frozen lake with something visible beneath the ice — large, angular",
        "An ancient temple to a cold god, entrance hidden by perpetual snow",
        "A tribe of winter eladrin dancing a ritual dance",
        "Ice sculptures that look recent but depict events from centuries ago",
        "A walking ice cave — not elemental, something older",
        "The corpse of a creature that doesn't belong in this climate",
        "Wandering snow sprites building a castle from enchanted snow"
    ],
    "underwater_encounters": [
        "A kelpie disguised as a beautiful person waving from the shore",
        "A merrow (evil merfolk) hunting alone, injured, desperate",
        "A sunken trading vessel — the ship is intact, crew still at their posts",
        "A school of glowing fish forming patterns that almost make sense",
        "A sahuagin raid on a merfolk settlement",
        "An aboleth's probe — the party notices a strange clarity to their thoughts",
        "A water elemental and a fire elemental battling near a thermal vent",
        "Giant sea horses being used as mounts by an unknown faction",
        "A memorial to a lost navy — ghostly ships visible at dawn",
        "A shrine to a sea god at the base of a trench",
        "Jellyfish the size of sails drifting overhead",
        "A drowning swimmer from the surface world, confused and aggressive",
        "A kraken's tentacle briefly breaking the surface — gone before anyone acts",
        "A locathah merchant offering information for a seemingly absurd price"
    ],

    # -------------------------------------------------------------------------
    # DUNGEON ROOMS & FEATURES
    # -------------------------------------------------------------------------
    "dungeon_room_types": [
        "A banquet hall — long table still set, food turned to dust, chairs toppled",
        "A barracks — 20 stone bunks, footlockers, and old graffiti",
        "An alchemist's laboratory — broken vials, stained tables, a live ooze in a tank",
        "A library — bookshelves collapsed, scrolls everywhere, some still readable",
        "A meditation chamber — meditation cushions around a central brazier",
        "A guardroom — weapon rack (empty), gaming table, off-duty cots",
        "A treasury — empty except for one object that glimmers interestingly",
        "A temple — altar desecrated, pews overturned, but candles still burning",
        "A kitchen — massive hearth, hanging pots, smell of ancient spices",
        "A archives — genealogical records, lineage scrolls, one name circled repeatedly",
        "A trophy room — empty weapon mounts, faded tapestries, broken display cases",
        "A prison — cells with scratch marks, one with a skeleton still inside",
        "A throne room — grand but decayed, throne has a visible hidden compartment",
        "A garden — dead plants, withered trees, but a single flower still alive",
        "A well room — well is dry, but something scratches from below",
        "A summoning chamber — arcane circle still faintly glowing",
        "A treasury vault — door open, contents removed, but claw marks on floor",
        "A portrait gallery — portraits' eyes follow movement, one frame is empty"
    ],
    "dungeon_interesting_features": [
        "A mural that depicts a scene currently happening elsewhere",
        "A fountain that flows with a liquid that isn't water",
        "A statue that turns to face the last person who passed through",
        "A door that only opens when no one is looking at it",
        "A brazier that burns without fuel, heatless and smokeless",
        "A rug with a pressure plate underneath — wrong weight triggered it",
        "A music box in the corner, lid open, playing a lullaby",
        "A skeleton arranged as if it died laughing",
        "A mirror that shows the room as it was 100 years ago",
        "A tapestry depicting a map — an actual map to the treasury",
        "A chandelier with crystals that glow faintly in darkness",
        "A cracked bell — still rings if struck, attracts something each time",
        "A suit of empty armor that stands at attention when approached",
        "A clock that runs backward, hands moving counterclockwise",
        "A mosaic floor with one tile a different color — a code"
    ],

    # -------------------------------------------------------------------------
    # WILDERNESS & TRAVEL
    # -------------------------------------------------------------------------
    "travel_events": [
        "The party's supplies are raided by invisible creatures overnight",
        "A guide insists the path is this way — they're clearly lost but won't admit it",
        "Night sky is wrong somehow — constellations in the wrong position",
        "The party finds a campsite that is 1 day ahead of schedule somehow",
        "An animal follows the party for days, then vanishes at a crossroads",
        "A storm forces the party to shelter — in a cave that's already occupied",
        "The party's horses/n mounts refuse to go further, requiring a rest",
        "One party member swears they've had this exact conversation before",
        "A merchant offers to sell a map that shows a route that shouldn't exist",
        "The party's trail is found by someone following them — why?",
        "Wild magic surge causes all metal to glow faintly blue for an hour",
        "A ghost ship crosses the party's path on a landlocked road",
        "One night's rest feels like three days of sleep — unexplained vigor",
        "The party crosses a bridge and the name of someone in the party is carved into the railing"
    ],
    "wilderness_camps": [
        "A Druid's grove — stone circle, protective wards, no fire pit",
        "An abandoned hunter's blind — still has supplies cached inside",
        "A hermit's simple camp — bedroll, fishing line, meditation bell",
        "A Fey crossing — the grass forms a perfect circle, campfire burns silver",
        "A military tent — collapsed but the tent poles are mithral (valuable!)",
        "A stone circle used for summoning — scorch marks still visible",
        "A smuggler's cache — hidden under a cairn, barely concealed",
        "A noble's hunting camp — pavilion, servants' tents, fresh game hanging",
        "A Druid's Grove — ancient tree carved with warnings, protective aura",
        "A pilgrim's rest — small shrine, offerings, a bedroll left behind"
    ],
    "landmark_details": [
        "A standing stone circle — one stone is loose and can be rolled aside",
        "A petrified tree — all branches perfectly preserved in stone",
        "A hot spring — steam rising, minerals deposited in patterns",
        "A cliff face with ancient carved warnings in a forgotten language",
        "A crossroads shrine — offerings piled, most are very old",
        "A bridge of impossible construction — no mortar, stones fitted perfectly",
        "A natural arch of rock — wind through it makes a low moaning sound",
        "A split boulder — something forced it apart from within",
        "A natural pool — perfectly circular, unnaturally deep, clear to the bottom",
        "A field of flowers that only grows where something terrible happened"
    ],

    # -------------------------------------------------------------------------
    # CREATURE LAIRS
    # -------------------------------------------------------------------------
    "lair_features_goblin": [
        "Total chaos and disorder — nothing is where it should be",
        "Broken weapons used as cooking utensils",
        "A cage of captured rats being fattened for eating",
        "Worn toys from the surface — a child's doll, a wooden sword",
        "A throne made of broken weapons welded together",
        "Stolen holy symbols from a desecrated temple",
        "A gambling ring — goblins betting on beetle races",
        "A shrine to a goblin hero-god, offerings of stolen coins",
        "Furs stolen from caravans, rotting in piles",
        "A nest of young goblins with no adult supervision"
    ],
    "lair_features_dragon": [
        "Piles of coins sorted by type and age — obsessive organization",
        "A hoard of sentient magic items arguing amongst themselves",
        "Melted-down weapons reforged into decorative panels",
        "A museum of captured banners from fallen kingdoms",
        "Prisoners' skeletal remains arranged in posed displays",
        "A pool of liquid metal used as a bath — extreme heat",
        "Obsession with one specific non-valuable object — why?",
        "Stolen noble titles and land deeds — claims to lands long lost",
        "A library of stolen lore organized by the dragon's personal index",
        "Eggs — the dragon has offspring, hidden somewhere in the lair"
    ],
    "lair_features_undead": [
        "Everything is frozen in the moment of death — no decay, no dust",
        "Tomb walls covered in the names of everyone the necromancer ever killed",
        "Sacrificial altar with blood channels still faintly glistening",
        "Servants' quarters — undead servants, still performing their duties",
        "A garden of poisonous plants, carefully tended by undead gardeners",
        "Dining hall set for a feast that will never end",
        "Portrait gallery of the necromancer's victims, eyes that weep",
        "A summoning chamber — portals to negative energy plane still open",
        "Catacombs extending beyond mapped areas — much deeper than expected",
        "The necromancer's personal quarters — surprisingly ordinary"
    ],
    "lair_features_hags": [
        "Everything in threes — three candles, three chairs, three plates",
        "Preserved body parts in jars — labeled by what they grant",
        "A mirror that shows the viewer's greatest fear",
        "Children's toys — pristine, never played with, clearly not from this century",
        "A cauldron containing something that shouldn't exist in nature",
        "Riddles carved into every surface — answers needed to leave",
        "Dolls representing specific people — needles stuck through them",
        "A nursery that a creature sleeps in — why?",
        "Collected teeth from a thousand different creatures",
        "A music box that plays a different lullaby each time it's wound"
    ],

    # -------------------------------------------------------------------------
    # CRIME & INVESTIGATION
    # -------------------------------------------------------------------------
    "crime_weapons": [
        "A ceremonial dagger — used for a ritual killing",
        "Poison — specific rare herb not found locally",
        "A heavy book — death by blunt force trauma",
        "A garrote — silk cord, expensive, from a specific importer",
        "Bare hands — strength suggested, overkill for the victim",
        "A hairpin — slender, sharp, professional",
        "A blacksmith's tongs — heavy iron, clearly available locally",
        "A bow — arrows recovered, fletched with distinctive feathers",
        "Magic — residue of a spell that shouldn't exist anymore",
        "A wine bottle — broken neck used as a stabbing weapon"
    ],
    "crime_motives": [
        "Insurance — the victim was about to change their policy",
        "Affair — a spouse and a secret lover, jealousy escalated",
        "Inheritance — the victim was about to write a new will",
        "Blackmail — victim knew something dangerous about the killer",
        "Business rivalry — a competitor eliminating a market threat",
        "Revenge — a wrong committed years ago, the victim never remembered",
        "Politics — the victim was a messenger for a foreign power",
        "Jealousy over status — someone who felt humiliated by the victim",
        "Accidental — the killer was aiming for someone else",
        "A debt — the victim was owed money and the killer had no intention of paying"
    ],
    "crime_forensic_clues": [
        "The victim's pockets are untouched — not robbery",
        "The body was moved after death — why here specifically?",
        "A single witness heard arguing but no sounds of struggle",
        "The murder weapon is embedded in the wall — thrown with great force",
        "Footprints in mud — two sets, one running away, one stationary",
        "A perfume or cologne that doesn't belong to anyone present",
        "A scrap of fabric — doesn't match any victim's clothing",
        "The victim was killed elsewhere and the body was placed here",
        "A symbolic arrangement — hands crossed, coins on eyes — ritual",
        "The clock in the room stopped at the exact time of death"
    ],
    "crime_witness_statements": [
        "Saw a figure in a hood leaving the scene — too tall to be the suspects",
        "Heard classical music playing from the victim's room before the scream",
        "A servant who claims to have seen nothing — too afraid to speak",
        "A child who drew a picture of what they saw — unnervingly accurate",
        "A neighbor who heard loud arguing in a language they didn't recognize",
        "The victim was expecting someone — they left the door unlocked",
        "A coach driver who saw two figures enter but only one leave",
        "The victim's business partner was the last to visit — and left in a hurry",
        "A street vendor who remembers the victim's unusual mood that day",
        "A dog that won't stop howling since the incident — broke its leg in the chaos"
    ],

    # -------------------------------------------------------------------------
    # WILD MAGIC & POTION EFFECTS
    # -------------------------------------------------------------------------
    "wild_magic_surges": [
        "All plants within 60ft sprout tiny flowers that bloom and die in seconds",
        "The caster's hair changes to a random color for 1d4 hours",
        "Every metal object within 30ft rings like a struck bell",
        "A shower of butterflies fills the area — vanish after 1 minute",
        "The caster's voice echoes for the next 1d6 hours",
        "All liquids within 30ft briefly boil, then return to normal temperature",
        "The caster experiences the next 10 seconds twice — déjà vu",
        "A bright light flashes — everyone within 30ft is blinded for 1 round",
        "Small fires appear on surfaces and go out after 1 round — no damage",
        "The caster's clothes are briefly replaced with formal evening wear",
        "All nearby birds begin singing a melody that has never been composed",
        "The caster smells smoke and flowers alternately for 1d4 hours",
        "Everything within 30ft gains a shadow that moves independently",
        "A spectral hand writes something in the air that only the caster can read",
        "The caster's skin briefly becomes translucent — bones visible",
        "All nearby water freezes for 1 round then thaws instantly",
        "A clone of the caster appears, mimicks their next action, then vanishes",
        "Gravity briefly inverts — everything falls upward for 1 round",
        "The caster speaks all languages they know simultaneously for 1 minute",
        "Nearby plants grow visibly but don't change otherwise"
    ],
    "potion_miseffects": [
        "The drinker turns invisible but their shadow remains visible",
        "Potion causes hiccups that produce a different sound each time",
        "The drinker's hands age 100 years then recover over 1 hour",
        "Their reflection in any mirror waves back independently",
        "The drinker temporarily forgets one specific word — it's on the tip of their tongue",
        "Everything the drinker says for the next hour rhymes accidentally",
        "Their clothes shrink but don't constrict — they're just too small",
        "The drinker smells like their favorite food — continuously",
        "They grow a very small第三个 nipple — fades in 1d4 days",
        "Their voice becomes very loud for 1d4 hours, whispers are impossible",
        "The drinker sees floating numbers only they can see counting down something",
        "Their ears rotate 180 degrees independently for 10 minutes",
        "The drinker becomes briefly transparent — not invisible, just see-through",
        "All their hair falls out — regrows completely in 2d6 days",
        "They briefly see their own aura — colors that match their emotional state"
    ],

    # -------------------------------------------------------------------------
    # QUEST GENERATION
    # -------------------------------------------------------------------------
    "quest_types": [
        "Retrieve — recover an object from a dangerous location",
        "Rescue — extract a captive before they're moved or killed",
        "Investigate — uncover a conspiracy, cult, or hidden truth",
        "Deliver — escort a package or person to a destination",
        "Protect — defend a target from an inevitable attack",
        "Negotiate — broker a peace or resolve a dispute",
        "Destroy — eliminate a threat at its source",
        "Infiltrate — enter a secure location without being detected",
        "Purge — cleanse a location of a contamination or presence",
        "Retrieve — steal something from under heavy guard"
    ],
    "quest_complications": [
        "The target is being moved earlier than expected",
        "A trusted ally is actually a double agent",
        "The MacGuffin is cursed — handling it causes madness",
        "An innocent person is blamed for the crime being investigated",
        "The quest giver has their own hidden agenda",
        "A deadline that seemed reasonable is actually much sooner",
        "The location is magically sealed — needs a key from an enemy",
        "The target has been dead for days — new information changes everything",
        "A competing party is also after the same objective",
        "The reward promised isn't what it seemed — or the payment bounces",
        "Weather or disaster has made the route impassable",
        "The target doesn't want to be found — actively evading",
        "A spellcaster involved has been replaced by a doppelganger",
        "The quest conflicts with a personal promise made earlier",
        "Evidence at the scene points to one of the quest givers themselves"
    ],
    "quest_rewards": [
        "A magic item with a known flaw — too dangerous to use at full power",
        "A deed to land — a property with serious problems no one wanted",
        "A letter of credit from a bank that no longer exists",
        "Political favor from a minor noble — vaguely worded",
        "Training — access to a master's techniques for 1 month",
        "A rare ingredient that can be made into a powerful potion",
        "A secret — lore about something the party was investigating anyway",
        "Membership in an organization — with obligations attached",
        "A rare beast as a mount — bonded to the party but uncontrollable",
        "Forgiveness — for past crimes the party committed",
        "A title with no land — 'Baron of Nowhere', but it opens doors",
        "An enemy who will eventually return — alive, grateful, dangerous"
    ],
    "quest_givers": [
        "A dying soldier with their last breath and unfinished business",
        "A child who doesn't understand the danger of what they're asking",
        "A wealthy merchant worried about their reputation if this goes public",
        "A retired adventurer whose former party was destroyed by this threat",
        "A priest who has received a divine vision — but visions can be wrong",
        "A noble who cannot be seen to be involved in this matter personally",
        "A former enemy — the enemy of my enemy may still be an enemy",
        "A ghost who doesn't realize they're dead yet",
        "An adventuring rival who's sending the party to eliminate competition",
        "A librarian — the information is free, the danger is not",
        "A god speaking through a prophet — unclear if the god is benevolent",
        "An animal that somehow communicates the need for help",
        "A madman whose ravings describe the situation perfectly",
        "The victim themselves — someone dying, asking for justice",
        "A bureaucrat who needs 'unofficial' help with an unofficial problem"
    ],

    # -------------------------------------------------------------------------
    # NOBLES & ROYALTY
    # -------------------------------------------------------------------------
    "noble_intrigues": [
        "The heir is actually a changeling replaced in infancy",
        "The crown is cursed — every monarch dies violently within 10 years",
        "A council regent has been making decisions for a king in magical sleep",
        "The treasury is empty — the king has been secretly funding something",
        "A succession crisis — twins, one legitimate, one hidden",
        "The royal bloodline has a disease that manifests in violence",
        "The queen is actually three people rotating the role",
        "A foreign power has a hostage they won't release unless a treaty is signed",
        "The last three royal advisors died under suspicious circumstances",
        "A prophecy names an adventurer as the true heir — which one?"
    ],
    "noble_titles": [
        "Baron of the Misty Marches", "Count of Ashford", "Duke of the Northern Reaches",
        "Earl of the Silver Coast", "Grand Duke of the Heartlands", "Lady of the Eastern Shore",
        "Lord Protector of the Borderlands", "Marquis of the Iron Valley", "Prince of the Verdant Court",
        "Viscount of the Old Harbor", "Lord of the Gilded City", "Baroness of Thornwood",
        "Countess of the River Delta", "Duke of the Ashen Wastes", "Guardian of the Crystal Pass",
        "Keeper of the Western Sea", "Lord of the Sunken Kingdom", "Marchioness of the Shattered Coast",
        "Overlord of the Frozen North", "Sheriff of the King's Road", "Steward of the Eastern Valleys",
        "Voice of the Southern Isles", "Warden of the Black Forest", "Duke of the Crimson Throne",
        "Baron of the Whispering Plains", "Earl of the Amber Coast"
    ],

    # -------------------------------------------------------------------------
    # RELIGION & TEMPLES
    # -------------------------------------------------------------------------
    "temple_dedications": [
        "God of the sun, light, and truth — temples are bright and warm",
        "Goddess of the moon, mystery, and dreams — temples are dim and quiet",
        "God of war and honor — temples echo with distant battle hymns",
        "Goddess of knowledge and secrets — temples are libraries, guarded closely",
        "God of the forge and craft — temples ring with hammers even at midnight",
        "Goddess of nature and the harvest — temples blend into the wilderness",
        "God of death and the underworld — temples are beautiful, serene, not morbid",
        "Goddess of the sea and storms — temples smell of salt and sound of waves",
        "God of trickery and knowledge — temples are maze-like, entrances hard to find",
        "God of the hunt — temples are base camps, full of trophies and tracking gear"
    ],
    "temple_relics": [
        "A bone from the god's mortal form — glows in divine presence",
        "The god's weapon from the age of myth — currently sealed",
        "A book containing the god's true name — reading it is dangerous",
        "Blood that never dries — from the god's final battle",
        "A living flame that can't be extinguished by any means",
        "A预言 — a glimpse of the future etched into the temple walls",
        "The god's mount or companion, petrified but still alive inside",
        "A voice that answers one question per day — answers are cryptic",
        "A mirror that shows the god's current location and activity",
        "Clothing worn by the god when they walked the earth — still fits anyone"
    ],
    "religious_factions": [
        "The Orthodox — traditionalists who believe in strict adherence to doctrine",
        "The Reformers — believe the religion should evolve with the times",
        "The Separatists — broke away over a doctrinal disagreement centuries ago",
        "The Inquisition — dedicated to rooting out heresy and corruption",
        "The Seekers — theologians who chase theological mysteries",
        "The Pragmatists — focused on results, not doctrine",
        "The Mystics — focused on direct divine experience and visions",
        "The Rationalists — skeptical of miracles, focused on ethical teaching",
        "The Purists — only accept worship in the original ancient forms",
        "The Syncretists — blend elements from other faiths freely"
    ],

    # -------------------------------------------------------------------------
    # MORE NPC DETAILS
    # -------------------------------------------------------------------------
    "npc_ideals": [
        "Security — getting the next meal, staying alive, protecting what's theirs",
        "Power — control over others, political influence, magical might",
        "Knowledge — learning secrets, understanding the world, scientific truth",
        "Vengeance — settling scores, justice through violence",
        "Beauty — art, music, creating something that lasts",
        "Independence — no masters, no obligations, total freedom",
        "Family — blood bonds, sworn brotherhood, adopted kin",
        "Faith — devotion to a cause, deity, or ideology above all",
        "Wealth — gold, gems, property, the freedom money brings",
        "Glory — being remembered, songs sung in their name",
        "Community — protecting their village, guild, or city",
        "Truth — exposing lies, speaking plainly, uncomfortable honesty"
    ],
    "npc_flaws": [
        "Addiction — alcohol, gambling, substances, thrill-seeking",
        "Arrogance — believes they're better than everyone else",
        "Paranoia — trusts no one, sees conspiracies everywhere",
        "Greed — always wanting more, unwilling to share or spend",
        "Recklessness — acts without thinking of consequences",
        "Cruelty — enjoys inflicting pain, has no empathy",
        "Deceit — lies reflexively, even when the truth would serve better",
        "Envy — obsessed with what others have, destructive jealousy",
        "Cowardice — avoids confrontation even when they should act",
        "Obsession — fixated on one goal to the exclusion of all else",
        "Naivety — too trusting, easily manipulated",
        "Brutality — solves everything with violence, no subtlety"
    ],
    "npc_mannerisms": [
        "Always checks over their shoulder before speaking",
        "Touches their face constantly while talking",
        "Speaks in rhymes or verse without realizing it",
        "Never uses contractions — every word is deliberate",
        "Laughs at inappropriate moments",
        "Collects small objects, fidgets with them while listening",
        "Speaks in a voice slightly too loud for indoor conversation",
        "Narrates their own actions aloud — 'I open the door, I draw my sword'",
        "Paces while thinking, can't stay still",
        "Gazes into middle distance while responding, as if seeing something else",
        "Hesitates before every answer, as if selecting words carefully",
        "Finishes other people's sentences when they're too slow",
        "Says 'if you know what I mean' constantly, even when unnecessary",
        "Describes everything in terms of monetary value",
        "Refers to themselves as 'we' — are they royalty, mad, or plural?"
    ],
    "npc_speech_patterns": [
        "Speaks only in questions — even statements come as queries",
        "Uses nautical terminology for everything — 'landlubbers', 'port', 'starboard'",
        "Military cadence — short, clipped, clear directives",
        "Scholarly — long compound sentences, many qualifiers, sources cited",
        "Street slang — contracted, slang, changes depending on audience",
        "Formal archaic — 'thee', 'thou', 'wherefore', extremely proper",
        "Suspiciously polite — too many pleasantries, too agreeable",
        "Harsh and blunt — no softening, direct to the point of rudeness",
        "Storyteller — everything is a story, takes three minutes to answer yes",
        "Mumbles — half the words are incomprehensible, repeats important parts",
        "Poetic — speaks in metaphors, describes everything beautifully",
        "Technical jargon — assumes everyone understands their profession",
        "Constantly apologizing — 'sorry', 'pardon', 'forgive me'",
        "Brags constantly — their achievements, their connections, their plan",
        "Whispers — even in quiet rooms, makes others lean in to hear"
    ],
    "npc_fears": [
        "Heights — even climbing a ladder is a trial",
        "Water — can't swim, terrified of drowning",
        "Enclosed spaces — panic in tight areas",
        "The dark — carries a dozen light sources",
        "Fire — maintains distance, won't cook over open flame",
        "Spiders — any arachnid, even tiny ones, causes terror",
        "Authority — freezes in the presence of officials",
        "Being alone — will do anything to avoid isolation",
        "Failure — their reputation is all they have",
        "Magic — doesn't understand it, assumes it's always hostile",
        "The sea — won't set foot on a boat under any circumstances",
        "Insects — especially swarm behavior",
        "Disease — obsessive about cleanliness, terrified of contagion",
        "Death — not dying, but the process, the pain involved",
        "Their own power — terrified of what they might do"
    ],
    "npc_goals_short_term": [
        "Survive until tomorrow — just one more day",
        "Pay off a debt — the collector is getting impatient",
        "Find their missing sibling — last seen a month ago",
        "Get promoted — sabotaging a coworker to do it",
        "Win a bet — the stakes were higher than they should have been",
        "Get out of town — before the people they offended find them",
        "Finish a project — apprenticeship depends on it",
        "Eat a proper meal — haven't had one in days",
        "Find a buyer for something they shouldn't have",
        "Convince someone to trust them — for once"
    ],
    "npc_goals_long_term": [
        "Return home — after years away, following a failed dream",
        "Clear their family name — their parent's shame haunts them",
        "Build something that will outlast them — a legacy",
        "Find the person who destroyed their life — revenge",
        "Become powerful enough to never be helpless again",
        "Undo a past mistake — a spell gone wrong, a word unsaid",
        "Collect a debt owed to them — with interest, lots of interest",
        "Discover the truth about their origin — orphan, unknown parentage",
        "Achieve apotheosis — become something more than mortal",
        "Retire in comfort — but they keep getting pulled back in"
    ],

    # -------------------------------------------------------------------------
    # URBAN LOCATIONS & DETAILS
    # -------------------------------------------------------------------------
    "building_types": [
        "A coaching inn — carriages in back, stables, common room crowded",
        "A chandler's shop — smell of tallow and wax, windows sooty",
        "A bookbinder — stacks of pages, old leather, quiet work",
        "A tanner — stench from the works, hides stretching in the yard",
        "A boarding house — thin walls, thin doors, many exits",
        "A warehouse — locked at night, suspiciously busy at odd hours",
        "A bakery — warm at all hours, flour on the windowsill",
        "A bath house — steam rising, separate hours for men and women",
        "A moneychanger — scales, coins, very careful about counterfeit",
        "A gambling den — fronted as a tea house, back rooms very different",
        "A temple — alms for the poor, quiet reflection, confessional booths",
        "A guild hall — meeting room above, workshop below, apprentices everywhere",
        "A prison — cold stone, iron bars, and the sounds of the desperate",
        "A hospital — for the sick poor, run by religious order",
        "A school — children arriving in the morning, tutors arguing outside"
    ],
    "urban_problems": [
        "A serial thief is targeting a specific type of shop",
        "The water supply has been contaminated upstream",
        "A gang has been extorting the market vendors",
        "A fire last month burned three buildings — who's rebuilding?",
        "The lord's tax collector is bleeding the district dry",
        "A disease is spreading — alchemists are scrambling for a cure",
        "The bridge collapse has cut off half the city from markets",
        "A charismatic preacher is drawing crowds with apocalyptic warnings",
        "The official who's supposed to maintain the roads is pocketing funds",
        "Refugees from a distant war are straining city resources",
        "The underground sewer has become a home to something dangerous",
        "A rival city-state has spies operating openly in the merchant quarter",
        "The head of the guild was murdered — succession crisis",
        "A new cult is recruiting aggressively — mostly young people",
        "Someone has been forging documents — land deeds, credentials"
    ],
    "settlement_types": [
        "Farming village (pop 200-500) — everyone knows everyone, outsider novelty",
        "Fishing hamlet (pop 100-300) — smell of salt, nets, superstitions about the sea",
        "Mining town (pop 300-1000) — transient population, rough, drink-heavy",
        "Trading post (pop 200-600) — diverse, many languages, mercantile tension",
        "Fortress city (pop 1000-5000) — military hierarchy, fortified walls, barracks",
        "Religious center (pop 500-2000) — temple complex, pilgrims, theological politics",
        "University town (pop 1000-3000) — students, scholars, ideas spreading",
        "Port city (pop 3000-10000) — cosmopolitan, dangerous docks, smuggling",
        "Capital city (pop 10000+) — districts, politics, the seat of power",
        "Guild town (pop 500-2000) — one dominant guild controls everything",
        "Frontier settlement (pop 50-200) — log cabins, everyone armed, survival focus",
        "Ruins being rebuilt (pop 100-300) — skeletons in the basement, rebuild on top"
    ],

    # -------------------------------------------------------------------------
    # MORE SHOP TABLES
    # -------------------------------------------------------------------------
    "shop_food_drink": [
        "Fresh bread, still warm — 2 cp loaf",
        "A wheel of aged cheese — sharp smell, worth 5 gp",
        "Dried meat on the bone — 1 sp per piece",
        "A barrel of pickled herring — 1 gp for the barrel",
        "Honeycomb — 3 sp, also used in alchemy",
        "Exotic spices from distant ports — 2 gp per pouch",
        "A whole roasted pig — 5 gp, feeds a crowd",
        "Fresh fruit out of season — only affordable to the wealthy",
        "A recipe scroll for a regional dish — 10 gp",
        "A keg of famous local ale — 3 gp, highly sought after"
    ],
    "shop_clothing": [
        "Secondhand traveling clothes — 5 sp complete set",
        "A noble's cast-off gown — altered, barely recognizable — 10 gp",
        "Waterproofed cloak — 2 gp, essential for travel",
        "Reinforced boots — 3 gp, smithed for durability",
        "A healer's robes — embroidered with faded symbols — 4 gp",
        "Children's clothing — clearly outgrown, handed down — 1 sp",
        "A funeral shroud — barely used, technically a sign of wealth",
        "Furs from the north — real fur, not fake — 15 gp",
        "A performer's costume — flashy, torn, distinctive — 6 gp",
        "Military uniform — no insignia — 8 gp, slightly ominous"
    ],
    "shop_services": [
        "A guide to a local area — 5 sp, worth more to outsiders",
        "A courier service — 1 gp to send a letter to a distant city",
        "A legal advocate — 5 gp to represent you in magistrate's court",
        "A healer — 1 gp per healing, 5 gp per cure disease",
        "A scribe — 2 sp to copy a letter, 1 gp to forge a document",
        "A prostitute — prices vary, discretion guaranteed",
        "A fence — buys stolen goods, asks no questions, takes 40%",
        "A informer — sells secrets about local politics — price negotiable",
        "A locksmith — can open anything given time and money",
        "A mercenary for the day — 5 gp, no questions about the job"
    ],
    "shop_odds_ends": [
        "A taxidermied owl — glass eyes, slightly dusty — 3 gp",
        "A music box that plays three songs — 10 gp",
        "A map of a region that doesn't exist — clearly fake — 1 sp",
        "A set of dishes from a dead noble's estate — 8 gp for the set",
        "A telescope — works but the brass is tarnished — 12 gp",
        "A tax document from 50 years ago — why is this for sale? — 1 cp",
        "A mirror that doesn't reflect anything correctly — cursed? — 2 gp",
        "A very old baby rattle — someone died in the shop — 1 sp",
        "A complete (and very boring) history of the local region — 5 sp",
        "A mysterious key — no one knows what it opens — 10 gp"
    ],

    # -------------------------------------------------------------------------
    # FACTION & ORGANIZATION DETAILS
    # -------------------------------------------------------------------------
    "faction_types": [
        "Thieves' Guild — controls black market, info network, occasional murder",
        "Merchants' Consortium — trade monopoly, price fixing, political lobbying",
        "Religious Order — worship, charity, hidden agenda, or all three",
        "Adventurers' Guild — job board, vetting, takes a cut of loot",
        "Assassin's Syndicate — discreet, expensive, leaves no traces",
        "Mages' Tower — arcane research, potions, dangerous experiments",
        "Order of Knights — honor-bound, sworn to protect or serve",
        "Scholars' Academy — knowledge, books, academic politics",
        "Seafarers' Union — docks, ships, smuggling, strongarm tactics",
        "Crafters' Guild — quality control, apprenticeship, strikes"
    ],
    "faction_secrets": [
        "The leadership has been replaced by doppelgangers years ago",
        "They've been selling information to a rival faction",
        "The organization's treasury is empty — embezzled",
        "They're responsible for a famous crime everyone thinks someone else did",
        "A founding member is still alive — undead, running everything",
        "They've been hiding a creature that would destroy them if revealed",
        "The organization's leader is being blackmailed by a minor official",
        "They launder money for the crown's enemies — unknowingly",
        "A third of the membership are informants for different groups",
        "They've been experimenting with forbidden magic on members"
    ],
    "faction_reputation": [
        "Respected and trusted — people seek them out",
        "Feared — obeyed because of what they'll do",
        "Despised — publicly reviled, secretly used",
        "Ridiculed — seen as irrelevant, which makes them dangerous",
        "Mysterious — no one knows who or what they are",
        "Divided — internal factions tearing the group apart",
        "Rising — growing powerful, ambitious plans",
        "Declining — once great, now crumbling",
        "Neutral — tolerated because they're too useful to destroy",
        "Holy — blessed by the gods, untouchable to the faithful"
    ],

    # -------------------------------------------------------------------------
    # CREATURE VARIATIONS (beyond goblins and undead)
    # -------------------------------------------------------------------------
    "orc_appearance": [
        "Battle scars across the face — counting coups",
        "Elaborate tribal tattoos — each one marks a kill",
        "A missing tusk — lost in a ritual duel",
        "War paint that never washes off — made from crushed minerals",
        "A bone crest worn as a headdress — from a defeated enemy leader",
        "Jewelry made from ears — collected from the unworthy",
        "A shaman's mark — touched by the spirits, unpredictable",
        "An iron plate bolted to the skull — survived an execution attempt"
    ],
    "skeleton_appearance": [
        "Wearing ceremonial armor from a forgotten kingdom's army",
        "Still in rusted chainmail — the metal fused to bone",
        "Holding a scroll that disintegrates when touched",
        "Arranged in a sitting position as if waiting for something",
        "One bone replaced with bronze — clearly artificial",
        "A simple wedding ring still on one finger",
        "Writing on the ribcage — someone's last words",
        "A child — impossibly young for this place"
    ],
    "dragon_appearance": [
        "Old scars from battles with other dragons — territory disputes",
        "A missing scale revealing scarred flesh beneath",
        "A rider's saddle scars — they killed their former master",
        "Platinum scales dulled with age and tarnishing",
        "A forked tongue that flicks constantly — tasting the air",
        "Smoke curling from their nostrils at all times",
        "One wing held at an angle — old injury, healed wrong",
        "Hoarding gold coins in their scales — personal collection"
    ],
    "demon_appearance": [
        "Skin that seems to shift between two colors at the edges",
        "An unnatural heat radiating from their body",
        "Eyes that reflect firelight even in complete darkness",
        "A voice that echoes slightly, as if spoken by multiple mouths",
        "Markings that glow faintly when they lie",
        "Shadows cast in shapes that don't match the demon's form",
        "A smell of sulfur that intensifies with emotion",
        "Wounds that close and reopen in a cycle — not quite mortal"
    ],

    # -------------------------------------------------------------------------
    # DREAM VISIONS & PROPHECIES
    # -------------------------------------------------------------------------
    "dream_visitors": [
        "A version of themselves from an hour in the future",
        "The same person, but their face is wrong — who are they really?",
        "Someone they've never met who knows their name",
        "A dead relative — familiar mannerisms, too familiar",
        "A god, unmasked, eating something that might be a soul",
        "A child who speaks only in riddles that make sense later",
        "A version of the character from a past life — they died violently",
        "The character meets themselves — two copies of the same person",
        "A person who should be dead — the death was faked, they're watching",
        "An animal that speaks in perfect sentences — no one believes them"
    ],
    "prophetic_symbols": [
        "A crown of thorns — power through suffering",
        "A silver key — something locked away will be found",
        "Fire and water meeting — impossible peace",
        "A tree with roots in the sky — inversion of nature",
        "A door with no house — a choice without context",
        "A bridge made of hands — cooperation built from below",
        "A mirror that shows the viewer as they truly are",
        "A sword through a heart that still beats — love and betrayal",
        "A wolf in sheep's clothing, and another wolf beneath that",
        "A sun that rises at midnight — the impossible made real"
    ],

}


# ---------------------------------------------------------------------------
# TOOLS
# ---------------------------------------------------------------------------

def _get_table(name: str):
    """Get a table by name, with fuzzy matching."""
    if name in TABLES:
        return TABLES[name]
    # Try partial match
    matches = [k for k in TABLES if name.lower() in k.lower()]
    if len(matches) == 1:
        return TABLES[matches[0]]
    return None


def table_list() -> str:
    """
    List all available random tables.

    Returns:
        Formatted list of table names and entry counts.
    """
    lines = ["📋 Available random tables:"]
    # Group by category
    categories = {
        "Names": ["names_", "tavern_names", "city_", "tavern_districts"],
        "NPCs": ["npc_", "tavern_"],
        "Encounters": ["encounters", "_appearance"],
        "Dungeon": ["dungeon_", "traps", "dungeon_room", "lair_features"],
        "Treasure": ["treasures", "art_", "gemstones", "mundane_"],
        "Shops": ["shop_"],
        "Environment": ["weather_", "time_of_day", "festival_", "strange_", "wilderness_", "landmark"],
        "Magic Items": ["magic_item", "minor_curses", "major_curses", "curse_removal"],
        "Plot": ["plot_", "rumors", "secrets_", "quest_", "faction"],
        "Crime": ["crime_"],
        "Wild Magic": ["wild_magic", "potion_miseffects"],
        "Religion": ["temple_", "religious_"],
        "Nobles": ["noble_", "temple_dedications"],
        "Dreams": ["dream_", "prophetic_"],
        "Wilderness": ["travel_", "swamp_", "mountain_", "desert_", "arctic_", "underdark_", "underwater_"],
        "Organizations": ["faction_"],
    }

    for cat, prefixes in categories.items():
        cat_tables = []
        for prefix in prefixes:
            for name in TABLES:
                if name.startswith(prefix):
                    cat_tables.append(name)
        if cat_tables:
            lines.append(f"\n  [{cat}]")
            for t in sorted(cat_tables):
                lines.append(f"    {t} ({len(TABLES[t])} entries)")

    return "\n".join(lines)


def table_roll(table_name: str, count: int = 1, seed: int = None) -> str:
    """
    Roll on a named random table and return one or more results.

    Args:
        table_name: Table to roll on. Call table_list() to see available tables.
        count: Number of results to return (1-5). Default 1.
        seed: Optional integer seed for reproducibility (e.g. pass in a dice roll result).
              If not provided, uses system random.

    Returns:
        One or more randomly selected results from the table.
    """
    entries = _get_table(table_name)
    if not entries:
        close = [k for k in TABLES if table_name.lower() in k.lower()]
        suggestion = f"\nDid you mean: {', '.join(close[:5])}?" if close else "\nCall table_list() to see all options."
        return f"ERROR: Table '{table_name}' not found.{suggestion}"

    count = max(1, min(count, 5))

    rng = random.Random(seed) if seed is not None else random
    results = rng.sample(entries, min(count, len(entries)))

    if count == 1:
        return f"🎲 [{table_name}]: {results[0]}"

    lines = [f"🎲 [{table_name}] × {count}:"]
    for i, r in enumerate(results, 1):
        lines.append(f"  {i}. {r}")
    return "\n".join(lines)


def table_generate_npc(race: str = "human", gender: str = "random", include_quirks: bool = True) -> str:
    """
    Generate a complete quick NPC with name, occupation, appearance, and quirks.

    Args:
        race: Race for name table — human, elf, dwarf, halfling, tiefling, dragonborn, gnome, orc
        gender: Gender for names — male, female, or random
        include_quirks: Include appearance and quirk details

    Returns:
        Complete NPC description string.
    """
    race = race.lower()
    gender = gender.lower() if gender != "random" else random.choice(["male", "female"])

    # Get name table
    if race == "elf":
        name = random.choice(TABLES["names_elf"])
    elif race == "dwarf":
        name = random.choice(TABLES["names_dwarf"])
    elif race == "halfling":
        name = random.choice(TABLES["names_halfling"])
    elif race == "tiefling":
        name = random.choice(TABLES["names_tiefling"])
    elif race == "dragonborn":
        name = random.choice(TABLES["names_dragonborn"])
    elif race == "gnome":
        name = random.choice(TABLES["names_gnome"])
    elif race == "orcs" or race == "orc":
        name = random.choice(TABLES["names_orc"])
    else:  # human or default
        if gender == "male":
            name = random.choice(TABLES["names_human_male"])
        else:
            name = random.choice(TABLES["names_human_female"])
        surname = random.choice(TABLES["names_human_surname"])
        name = f"{name} {surname}"

    # Add surname for non-human if using human names
    if race == "human":
        pass  # already have full name
    else:
        name = name  # just first name for most fantasy races

    occupation = random.choice(TABLES["npc_occupations"])

    result = [
        f"🧑 NPC: {name}",
        f"  Race: {race.title()}",
        f"  Occupation: {occupation}"
    ]

    if include_quirks:
        appearance = random.choice(TABLES["npc_appearance"])
        quirk = random.choice(TABLES["npc_quirks"])
        result.append(f"  Appearance: {appearance}")
        result.append(f"  Quirk: {quirk}")

    return "\n".join(result)


def table_generate_tavern() -> str:
    """
    Generate a complete tavern description.

    Returns:
        Tavern name, ambiance, and notable regulars.
    """
    name = random.choice(TABLES["tavern_names"])
    ambiance = random.choice(TABLES["tavern_ambiance"])
    regular = random.choice(TABLES["tavern_regulars"])
    district = random.choice(TABLES["tavern_districts"])

    return (
        f"🍺 {name}\n"
        f"  Location: {district}\n"
        f"  Ambiance: {ambiance}\n"
        f"  Regular: {regular}"
    )


def table_generate_shop(shop_type: str = "general") -> str:
    """
    Generate a shop with inventory.

    Args:
        shop_type: Type of shop — general, weapons, armor, alchemist, bookstore, magic

    Returns:
        Shop inventory description.
    """
    shop_type = shop_type.lower()

    inventory_table = f"shop_{shop_type}"
    if inventory_table not in TABLES:
        inventory_table = "shop_general_goods"

    items = random.sample(TABLES[inventory_table], min(3, len(TABLES[inventory_table])))

    shop_name_prefix = random.choice(["The", "Iron", "Golden", "Silver", "Old", "New"])
    shop_item = random.choice(["Supplies", "Goods", "Wares", "Provisions", "Supplies"])

    return (
        f"🏪 {shop_name_prefix} {shop_item}\n"
        f"  Current inventory:\n"
        + "\n".join(f"    • {item}" for item in items)
    )


def table_generate_encounter(environment: str = "road") -> str:
    """
    Generate an encounter based on environment.

    Args:
        environment: Type of environment — road, forest, dungeon, urban

    Returns:
        Encounter description.
    """
    env = environment.lower()

    if env == "forest":
        table = "forest_encounters"
    elif env == "dungeon":
        table = "dungeon_encounters"
    elif env == "urban" or env == "city":
        table = "urban_encounters"
    else:
        table = "road_encounters"

    encounter = random.choice(TABLES[table])
    return f"⚔️ Encounter ({env}): {encounter}"


def table_generate_treasure(include_gems: bool = True) -> str:
    """
    Generate random treasure findings.

    Args:
        include_gems: Include gemstones in the find

    Returns:
        Treasure description.
    """
    mundane = random.choice(TABLES["mundane_treasures"])
    art = random.choice(TABLES["art_objects"])

    result = f"💰 Treasure:\n  • {mundane}\n  • {art}"

    if include_gems:
        gems = random.sample(TABLES["gemstones"], min(2, 3))
        result += "\n  • Gems: " + ", ".join(gems)

    return result


def table_generate_magic_item(item_type: str = "random") -> str:
    """
    Generate a magic item with a name, origin, and quirk.

    Args:
        item_type: Type of item — weapon, armor, wand, ring, scroll, potion, or random

    Returns:
        Complete magic item description.
    """
    prefixes = {
        "weapon": ["Sword", "Dagger", "Axe", "Mace", "Spear", "Bow", "Hammer"],
        "armor": ["Shield", "Helm", "Gauntlets", "Boots", "Cloak", "Bracers"],
        "wand": ["Wand", "Staff", "Rod"],
        "ring": ["Ring", "Amulet", "Talisman", "Circlet"],
        "scroll": ["Spellbook", "Tome", "Scroll", "Grimoire"],
        "potion": ["Potion", "Elixir", "Vial", "Draught"],
    }
    materials = ["Iron", "Silver", "Mithral", "Adamantine", "Bone", "Crystal", "Obsidian", "Brass", "Bronze"]
    effects = [
        "flames", "frost", "shadows", "light", "thorns", "storms",
        "whispers", "visions", "strength", "swiftness", "silence", "sight"
    ]

    if item_type == "random":
        category = random.choice(list(prefixes.keys()))
    else:
        category = item_type.lower()
        if category not in prefixes:
            category = "weapon"

    name = f"{random.choice(materials)} {random.choice(effects).title()} {random.choice(prefixes[category])}"
    quirk = random.choice(TABLES["magic_item_quirks"])
    origin = random.choice(TABLES["magic_item_origins"])

    return (
        f"✨ Magic Item: {name}\n"
        f"  Quirk: {quirk}\n"
        f"  Origin: {origin}"
    )


def table_generate_curse() -> str:
    """
    Generate a cursed magic item or effect.

    Returns:
        Curse description with removal difficulty.
    """
    minor = random.choice(TABLES["minor_curses"])
    major = random.choice(TABLES["major_curses"])
    removal = random.choice(TABLES["curse_removal_difficulties"])

    return (
        f"🔮 Curse:\n"
        f"  Minor: {minor}\n"
        f"  Major: {major}\n"
        f"  Removal: {removal}"
    )


def table_generate_lair(creature_type: str = "random") -> str:
    """
    Generate a creature lair with distinctive features.

    Args:
        creature_type: Type of creature — goblin, dragon, undead, hag, or random

    Returns:
        Lair description with features.
    """
    if creature_type == "random":
        creature_type = random.choice(["goblin", "dragon", "undead", "hag"])

    creature_type = creature_type.lower()
    if creature_type == "goblin":
        features = random.sample(TABLES["lair_features_goblin"], 3)
    elif creature_type == "dragon":
        features = random.sample(TABLES["lair_features_dragon"], 3)
    elif creature_type == "undead":
        features = random.sample(TABLES["lair_features_undead"], 3)
    elif creature_type == "hag":
        features = random.sample(TABLES["lair_features_hags"], 3)
    else:
        features = random.sample(TABLES["dungeon_interesting_features"], 3)

    feature_lines = "\n".join(f"  • {f}" for f in features)

    return (
        f"🏚️ {creature_type.title()} Lair:\n"
        f"{feature_lines}"
    )


def table_generate_dungeon_room() -> str:
    """
    Generate a dungeon room with a type and interesting feature.

    Returns:
        Complete room description.
    """
    room_type = random.choice(TABLES["dungeon_room_types"])
    feature = random.choice(TABLES["dungeon_interesting_features"])
    dressing = random.choice(TABLES["dungeon_dressing_atmosphere"])

    return (
        f"🚪 Dungeon Room:\n"
        f"  Type: {room_type}\n"
        f"  Feature: {feature}\n"
        f"  Atmosphere: {dressing}"
    )


def table_generate_wildmagic() -> str:
    """
    Generate a wild magic surge result.

    Returns:
        Wild magic surge description.
    """
    surge = random.choice(TABLES["wild_magic_surges"])
    return f"🌪️ Wild Magic Surge: {surge}"


def table_generate_potion_effect() -> str:
    """
    Generate a potion miseffect when something goes wrong with a potion.

    Returns:
        Potion miseffect description.
    """
    effect = random.choice(TABLES["potion_miseffects"])
    return f"⚗️ Potion Miseffect: {effect}"


TOOLS = [
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "table_list",
            "description": "List all available D&D random tables grouped by category. Call this first to discover table names before calling table_roll.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "table_roll",
            "description": "Roll on a named D&D random table and return one or more results. Use for NPC names, encounters, dungeon dressing, weather, rumors, treasure, and more. Call table_list() first to see available table names.",
            "parameters": {
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the table to roll on (e.g. 'road_encounters', 'npc_quirks', 'weather_temperate')"
                    },
                    "count": {
                        "type": "integer",
                        "description": "Number of results to return (1-5). Default 1."
                    },
                    "seed": {
                        "type": "integer",
                        "description": "Optional integer seed for reproducibility — pass in a prior dice roll result to get consistent output."
                    }
                },
                "required": ["table_name"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "table_generate_npc",
            "description": "Generate a complete quick NPC with name, race, occupation, appearance, and personality quirk. Use when the party meets a new character and you need details immediately.",
            "parameters": {
                "type": "object",
                "properties": {
                    "race": {
                        "type": "string",
                        "description": "Race for name generation: human, elf, dwarf, halfling, tiefling, dragonborn, gnome, orc. Default: human."
                    },
                    "gender": {
                        "type": "string",
                        "description": "Gender for names: male, female, or random. Default: random."
                    },
                    "include_quirks": {
                        "type": "boolean",
                        "description": "Include appearance and personality quirk details. Default: true."
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
            "name": "table_generate_tavern",
            "description": "Generate a complete tavern with name, district, ambiance description, and a notable regular patron. Use when the party enters a new inn or tavern.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "table_generate_shop",
            "description": "Generate a shop name and current inventory. Use when the party visits a merchant or store.",
            "parameters": {
                "type": "object",
                "properties": {
                    "shop_type": {
                        "type": "string",
                        "description": "Type of shop: general, weapons, armor, alchemist, bookstore, magic. Default: general."
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
            "name": "table_generate_encounter",
            "description": "Generate a random encounter suited to the environment. Use during travel or exploration when something unexpected happens.",
            "parameters": {
                "type": "object",
                "properties": {
                    "environment": {
                        "type": "string",
                        "description": "Environment type: road, forest, dungeon, urban. Default: road."
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
            "name": "table_generate_treasure",
            "description": "Generate random treasure findings including a mundane valuable, an art object, and optionally gemstones.",
            "parameters": {
                "type": "object",
                "properties": {
                    "include_gems": {
                        "type": "boolean",
                        "description": "Include gemstones in the find. Default: true."
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
            "name": "table_generate_magic_item",
            "description": "Generate a complete magic item with name, origin, and a unique quirk. Use when awarding loot or when the party finds a mysterious object.",
            "parameters": {
                "type": "object",
                "properties": {
                    "item_type": {
                        "type": "string",
                        "description": "Item category: weapon, armor, wand, ring, scroll, potion, or random. Default: random."
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
            "name": "table_generate_curse",
            "description": "Generate a curse with minor effect, major effect, and removal difficulty. Use when an item or location carries a hex.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "table_generate_lair",
            "description": "Generate a creature's lair with distinctive features and dressing. Use when the party enters the home of goblins, dragons, undead, or hags.",
            "parameters": {
                "type": "object",
                "properties": {
                    "creature_type": {
                        "type": "string",
                        "description": "Creature type: goblin, dragon, undead, hag, or random. Default: random."
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
            "name": "table_generate_dungeon_room",
            "description": "Generate a dungeon room with a room type, an interesting feature, and atmospheric dressing. Use when exploring a dungeon and needing a room on the fly.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "table_generate_wildmagic",
            "description": "Generate a wild magic surge result. Use when a spell triggers a wild magic surge or when in an area of wild magical energy.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "table_generate_potion_effect",
            "description": "Generate a potion miseffect when something goes wrong with potion creation or storage. Use when a potion has an unexpected or bizarre side effect.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
]


def execute(function_name, arguments, config):
    if function_name == 'table_list':
        return table_list(), True

    if function_name == 'table_roll':
        table_name = arguments.get('table_name', '')
        count = arguments.get('count', 1)
        seed = arguments.get('seed', None)
        return table_roll(table_name, count, seed), True

    if function_name == 'table_generate_npc':
        race = arguments.get('race', 'human')
        gender = arguments.get('gender', 'random')
        include_quirks = arguments.get('include_quirks', True)
        return table_generate_npc(race, gender, include_quirks), True

    if function_name == 'table_generate_tavern':
        return table_generate_tavern(), True

    if function_name == 'table_generate_shop':
        shop_type = arguments.get('shop_type', 'general')
        return table_generate_shop(shop_type), True

    if function_name == 'table_generate_encounter':
        environment = arguments.get('environment', 'road')
        return table_generate_encounter(environment), True

    if function_name == 'table_generate_treasure':
        include_gems = arguments.get('include_gems', True)
        return table_generate_treasure(include_gems), True

    if function_name == 'table_generate_magic_item':
        item_type = arguments.get('item_type', 'random')
        return table_generate_magic_item(item_type), True

    if function_name == 'table_generate_curse':
        return table_generate_curse(), True

    if function_name == 'table_generate_lair':
        creature_type = arguments.get('creature_type', 'random')
        return table_generate_lair(creature_type), True

    if function_name == 'table_generate_dungeon_room':
        return table_generate_dungeon_room(), True

    if function_name == 'table_generate_wildmagic':
        return table_generate_wildmagic(), True

    if function_name == 'table_generate_potion_effect':
        return table_generate_potion_effect(), True

    return f"Unknown function: {function_name}", False
