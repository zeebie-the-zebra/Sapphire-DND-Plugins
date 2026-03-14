"""
D&D NPC Generator & Roster

Generates fully-fleshed NPCs with:
  - Name, race, gender, age, occupation, faction
  - Physical appearance (3 traits)
  - Personality traits, ideal, bond, flaw (PHB backgrounds style)
  - Attitude toward party (friendly/neutral/hostile/unknown)
  - Voice/speech mannerism
  - Secret (optional)
  - Persistent storage — NPCs remembered across sessions
"""

import random

ENABLED = True
EMOJI = '🧑'
AVAILABLE_FUNCTIONS = ['npc_generate', 'npc_save', 'npc_get', 'npc_list', 'npc_update', 'npc_delete']

# ── Name tables ────────────────────────────────────────────────────────────────
NAMES = {
    "Human": {
        "male":   ["Aldric","Brennan","Caius","Darian","Edmund","Falk","Garrett","Hadrian","Ivan","Jasper",
                   "Kelvin","Lucan","Marcus","Nathaniel","Owen","Percival","Quintin","Roland","Stefan","Tobias"],
        "female": ["Adela","Brynn","Celia","Dara","Elara","Fiona","Gwendolyn","Hilda","Isolde","Jana",
                   "Kira","Lyra","Mira","Nora","Ophelia","Petra","Quinn","Reva","Sylvia","Tara"],
        "surname":["Ashwood","Blackstone","Crane","Drake","Fairweather","Greymantle","Holloway","Ironfist",
                   "Kettlewell","Lorne","Moorfield","Nightwood","Oldbury","Pilgrim","Ravenscroft","Stonewall"]
    },
    "Elf": {
        "male":   ["Aelindra","Caladrel","Daecalan","Erevan","Faral","Galaeron","Haemir","Iliphar","Jhaeros",
                   "Kethaan","Leshanna","Maekar","Naeltar","Peren","Quarion","Rolen","Soveliss","Thamior"],
        "female": ["Adrie","Althaea","Anastrianna","Caelynna","Drusilia","Enna","Felosial","Iefyr","Jelenneth",
                   "Keyleth","Luvon","Mialee","Naivara","Quelenna","Sariel","Talaitha","Valenae","Xanaphia"],
        "surname":["Amakiir","Amastacia","Galanodel","Holimion","Ilphelkiir","Liadon","Meliamne","Naïlo",
                   "Siannodel","Xiloscient"]
    },
    "Dwarf": {
        "male":   ["Adrik","Alberich","Baran","Barendd","Brottor","Bruenor","Dain","Darrak","Delg","Eberk",
                   "Einkil","Fargrim","Flint","Gardain","Harbek","Kildrak","Morgran","Orsik","Oskar","Rangrim"],
        "female": ["Amber","Artin","Audhild","Bardryn","Dagnal","Diesa","Eldeth","Falkrunn","Finellen",
                   "Gunnloda","Gurdis","Helja","Hlin","Kathra","Kristryd","Mardred","Riswynn","Sannl"],
        "surname":["Balderk","Dankil","Gorunn","Holderhek","Loderr","Lutgehr","Rumnaheim","Strakeln","Torunn","Ungart"]
    },
    "Halfling": {
        "male":   ["Alton","Ander","Bernie","Bobbin","Cade","Corrin","Eldon","Errich","Finnan","Garret",
                   "Lindal","Lyle","Merric","Milo","Osborn","Perrin","Reed","Roscoe","Wellby"],
        "female": ["Andry","Bree","Callie","Cora","Euphemia","Jillian","Kithri","Lavinia","Lidda","Merla",
                   "Nedda","Paela","Portia","Seraphina","Shaena","Trym","Vani","Verna","Wella"],
        "surname":["Brushgather","Goodbarrel","Greenbottle","High-hill","Hilltopple","Leagallow","Tealeaf","Thorngage","Tosscobble","Underbough"]
    },
}
DEFAULT_NAMES = NAMES["Human"]

RACES = ["Human","Human","Human","Human","Elf","Elf","Dwarf","Dwarf","Halfling","Half-Orc","Gnome","Tiefling","Dragonborn"]
GENDERS = ["male","female","male","female","nonbinary"]

OCCUPATIONS = [
    "Blacksmith","Innkeeper","Merchant","Farmer","Guard","Soldier (retired)","Scholar","Priest","Herbalist",
    "Sailor","Carpenter","Tailor","Cook","Stable master","Miner","Fisherman","Cartographer","Apothecary",
    "Scribe","Bounty hunter","Fence (black market)","Spy","Cult member","Noble's steward","Bandit captain",
    "Bard","Traveling circus performer","Alchemist","Gravedigger","Tax collector","Wandering monk",
]

FACTIONS = ["None","None","None","None","The Merchant's Guild","The Town Watch","The Temple of Light",
            "The Thieves' Guild","The Mages' Circle","The Harpers","The Zhentarim","The Order of the Gauntlet",
            "The Emerald Enclave","The Lords' Alliance","A local noble house","A secretive cult"]

# ── Trait tables ───────────────────────────────────────────────────────────────
PERSONALITY_TRAITS = [
    "I'm always polite, even to people who don't deserve it.",
    "I quote (or misquote) sacred texts in almost every situation.",
    "I'm confident in my own abilities and love a good challenge.",
    "I'm suspicious of strangers and expect the worst of them.",
    "I let my actions speak for themselves.",
    "I bluntly say what others are merely thinking.",
    "I have a crude sense of humor.",
    "I face problems head-on. A simple direct solution is the best.",
    "I'm always picking things up, fiddling with them, examining them.",
    "I'm haunted by memories I can't share with anyone.",
    "I misuse long words in an attempt to sound smarter.",
    "I get bored easily and often stir up trouble to pass the time.",
    "I enjoy a good insult, even if aimed at me.",
    "I am always calm, even in dire situations. I never raise my voice.",
    "I'd rather make a new friend than a new enemy.",
    "I have a weakness for vices and am easily tempted.",
    "I like to keep trinkets and small curiosities on me at all times.",
    "Everything I do is for the greater good.",
    "I start too many projects and rarely finish them.",
    "I speak very slowly and choose my words with great care.",
]

IDEALS = [
    ("Tradition","The ancient traditions must be preserved.","Lawful"),
    ("Charity","I always try to help those in need.",  "Good"),
    ("Power","I want to become the most powerful person in the world.","Evil"),
    ("Freedom","Everyone should be free to do what they want.","Chaotic"),
    ("Honesty","I never lie, not even a white one.","Lawful"),
    ("Aspiration","I work hard to be the best at my craft.","Any"),
    ("Redemption","There's a spark of good in everyone.","Good"),
    ("Self-Reliance","I rely only on myself, no one else.","Neutral"),
    ("Knowledge","The path to power is through knowledge.","Neutral"),
    ("Greater Good","Personal gain comes second to helping others.","Good"),
    ("Greed","I'll do whatever it takes to get rich.","Evil"),
    ("Live and Let Live","I don't butt into other people's business.","Neutral"),
]

BONDS = [
    "I owe everything to my mentor — I will repay that debt.",
    "I will do anything to protect my hometown.",
    "I have a family member who needs my help.",
    "My most prized possession is a letter from someone I loved.",
    "I want to find the person who wronged my family.",
    "I protect those who cannot protect themselves.",
    "My guild is my true family.",
    "I'm trying to pay off a massive debt.",
    "I owe my life to someone in this group.",
    "My holy symbol means everything to me.",
    "There is a secret I would kill to protect.",
    "I am searching for a lost artifact of great importance.",
]

FLAWS = [
    "I have trouble trusting anyone — even myself.",
    "I'm quick to assume that others are trying to cheat me.",
    "I have a hard time admitting when I'm wrong.",
    "My pride will likely get me killed someday.",
    "I am painfully slow to trust anyone.",
    "I let my greed override my better judgment.",
    "Once I set my mind on something, I am nearly impossible to dissuade.",
    "I talk too much and share too many secrets.",
    "I am terrified of something specific (spiders, fire, undead...).",
    "I hold a grudge for a very long time.",
    "I am obsessed with wealth and status.",
    "I will say anything to avoid conflict.",
]

APPEARANCE = {
    "build":  ["lean and wiry","stocky and broad-shouldered","tall and willowy","short and stout",
               "heavily muscled","slight and delicate","average build","hunched with age"],
    "hair":   ["close-cropped grey hair","long braided auburn hair","wild white hair","a shaved head",
               "neat black hair","disheveled brown hair","silver-streaked hair","a dark topknot",
               "no hair at all","curly red hair","iron-grey stubble"],
    "eyes":   ["piercing blue eyes","warm brown eyes","cold grey eyes","bright green eyes",
               "deep-set dark eyes","mismatched eyes (one blue, one green)","hazel eyes",
               "pale amber eyes","eyes that always seem to be calculating"],
    "notable":["a prominent scar across the chin","calloused hands from years of work","ink-stained fingers",
               "a tattoo barely visible at the collar","an elaborate signet ring","missing two fingers on the left hand",
               "moves with a slight but notable limp","wears a hood even indoors",
               "always smells faintly of pipe smoke","a nervous habit of tapping fingers",
               "never makes eye contact","unusually good posture","several small burn scars on the forearm"]
}

SPEECH_MANNERISMS = [
    "speaks in short, clipped sentences",
    "uses a lot of old-fashioned idioms",
    "has a thick regional accent",
    "laughs nervously at inappropriate times",
    "speaks very quietly, forcing others to lean in",
    "frequently uses the wrong word but never realizes it",
    "pauses dramatically before answering any question",
    "refers to themselves in the third person",
    "uses a lot of profanity, then immediately apologizes",
    "answers questions with questions",
    "always ends sentences with '...you understand?'",
    "has a habit of trailing off mid-sentence",
    "speaks extremely formally, even to friends",
    "hums quietly while thinking",
    "frequently interrupts themselves to add more details",
]

SECRETS = [
    "is secretly in debt to a dangerous organization",
    "witnessed a crime they've never reported",
    "is not who they claim to be — using a false name",
    "is an informant for a rival faction",
    "has a hidden stash of stolen goods somewhere nearby",
    "knows the location of something powerful or valuable",
    "is fleeing from someone or something",
    "has a forbidden love they must keep hidden",
    "was once in the party's position — and made the wrong choice",
    "is dying and doesn't want anyone to know",
    "knows something about one of the party members' pasts",
    "is working against the party's interests, but conflicted about it",
]

ATTITUDES = ["Friendly","Friendly","Neutral","Neutral","Neutral","Suspicious","Hostile"]


def _get_state():
    from core.plugin_loader import plugin_loader
    return plugin_loader.get_plugin_state("dnd-npcs")

def _load_all() -> dict:
    return _get_state().get("npcs") or {}

def _save_all(npcs: dict):
    _get_state().save("npcs", npcs)

def _find(name: str, npcs: dict):
    key = name.lower().strip()
    for k, v in npcs.items():
        if k.lower() == key:
            return k, v
    return None, None

def _generate_npc(race=None, gender=None, occupation=None):
    race   = race or random.choice(RACES)
    gender = gender or random.choice(GENDERS)

    name_table = NAMES.get(race, DEFAULT_NAMES)
    if gender == "nonbinary":
        first = random.choice(name_table.get("male", []) + name_table.get("female", []))
    else:
        first = random.choice(name_table.get(gender, name_table.get("male", ["Unknown"])))
    surname = random.choice(name_table.get("surname", [""]))
    full_name = f"{first} {surname}".strip()

    occupation = occupation or random.choice(OCCUPATIONS)
    faction    = random.choice(FACTIONS)
    age_range  = random.choice(["young (early 20s)", "young adult (late 20s)", "middle-aged", "middle-aged", "older (50s)", "elderly"])

    ideal = random.choice(IDEALS)

    appearance = (
        f"{random.choice(APPEARANCE['build'])}, "
        f"{random.choice(APPEARANCE['hair'])}, "
        f"{random.choice(APPEARANCE['eyes'])}, "
        f"{random.choice(APPEARANCE['notable'])}"
    )

    npc = {
        "name":        full_name,
        "race":        race,
        "gender":      gender,
        "age":         age_range,
        "occupation":  occupation,
        "faction":     faction,
        "appearance":  appearance,
        "personality": random.choice(PERSONALITY_TRAITS),
        "ideal":       f"{ideal[0]}: {ideal[1]} ({ideal[2]})",
        "bond":        random.choice(BONDS),
        "flaw":        random.choice(FLAWS),
        "speech":      random.choice(SPEECH_MANNERISMS),
        "attitude":    random.choice(ATTITUDES),
        "secret":      random.choice(SECRETS),
        "notes":       "",
    }
    return npc

def _npc_card(npc: dict) -> str:
    lines = [
        f"🧑 **{npc['name']}**",
        f"{npc.get('age','').capitalize()} {npc['race']} {npc['gender']} | {npc['occupation']}"
        + (f" | {npc['faction']}" if npc.get('faction') and npc['faction'] != 'None' else ""),
        f"",
        f"**Appearance:** {npc['appearance']}",
        f"**Speech:** {npc['speech']}",
        f"",
        f"**Personality:** {npc['personality']}",
        f"**Ideal:** {npc['ideal']}",
        f"**Bond:** {npc['bond']}",
        f"**Flaw:** {npc['flaw']}",
        f"",
        f"**Attitude toward party:** {npc['attitude']}",
        f"**Secret:** *(DM only)* {npc['secret']}",
    ]
    if npc.get("notes"):
        lines.append(f"**Notes:** {npc['notes']}")
    return "\n".join(lines)


TOOLS = [
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "npc_generate",
            "description": "Generate a new NPC with full personality, appearance, and backstory. Use when the party encounters a new character or you need to populate a location with people.",
            "parameters": {
                "type": "object",
                "properties": {
                    "race":       {"type": "string",  "description": "NPC race (Human, Elf, Dwarf, Halfling, etc.) — random if omitted"},
                    "gender":     {"type": "string",  "description": "male, female, or nonbinary — random if omitted"},
                    "occupation": {"type": "string",  "description": "Job or role, e.g. 'Innkeeper', 'Guard'. Random if omitted."},
                    "save":       {"type": "boolean", "description": "Save this NPC to the roster (default true)"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "npc_save",
            "description": "Save or update an NPC in the persistent roster. Use to remember important NPCs across sessions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name":       {"type": "string", "description": "NPC name"},
                    "race":       {"type": "string", "description": "Race"},
                    "gender":     {"type": "string", "description": "Gender"},
                    "occupation": {"type": "string", "description": "Occupation"},
                    "appearance": {"type": "string", "description": "Physical description"},
                    "personality":{"type": "string", "description": "Key personality trait"},
                    "attitude":   {"type": "string", "description": "Attitude toward party"},
                    "notes":      {"type": "string", "description": "Any additional notes"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "npc_get",
            "description": "Look up a saved NPC by name. Use before roleplaying a returning character to remember their traits.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "NPC name"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "npc_list",
            "description": "List all saved NPCs with brief summaries.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "npc_update",
            "description": "Update notes or attitude for an existing NPC (e.g. party helped them, now friendly).",
            "parameters": {
                "type": "object",
                "properties": {
                    "name":     {"type": "string", "description": "NPC name"},
                    "attitude": {"type": "string", "description": "New attitude: Friendly, Neutral, Suspicious, Hostile"},
                    "notes":    {"type": "string", "description": "New notes to append or set"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "npc_delete",
            "description": "Remove an NPC from the roster.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "NPC name"}
                },
                "required": ["name"]
            }
        }
    }
]


def execute(function_name, arguments, config):
    npcs = _load_all()

    if function_name == "npc_generate":
        npc = _generate_npc(
            race=arguments.get("race"),
            gender=arguments.get("gender"),
            occupation=arguments.get("occupation"),
        )
        save = arguments.get("save", True)
        if save:
            npcs[npc["name"]] = npc
            _save_all(npcs)
            saved_note = " *(saved to roster)*"
        else:
            saved_note = " *(not saved)*"
        return _npc_card(npc) + f"\n\n{saved_note}", True

    elif function_name == "npc_save":
        name = arguments.get("name", "").strip()
        if not name:
            return "NPC name is required.", False
        key, existing = _find(name, npcs)
        if existing:
            npc = existing
        else:
            npc = _generate_npc()
            npc["name"] = name
        for field in ["race","gender","occupation","appearance","personality","attitude","notes","faction","age","ideal","bond","flaw","speech","secret"]:
            if field in arguments:
                npc[field] = arguments[field]
        npc["name"] = name
        npcs[name] = npc
        _save_all(npcs)
        return f"✅ {name} saved to NPC roster.\n\n{_npc_card(npc)}", True

    elif function_name == "npc_get":
        name = arguments.get("name", "")
        key, npc = _find(name, npcs)
        if not npc:
            return f"No NPC named '{name}' found. Use npc_list to see all saved NPCs.", False
        return _npc_card(npc), True

    elif function_name == "npc_list":
        if not npcs:
            return "No NPCs saved yet. Use npc_generate to create some.", True
        lines = ["**NPC Roster:**"]
        for npc in npcs.values():
            att = npc.get("attitude", "Unknown")
            att_emoji = {"Friendly":"🟢","Neutral":"🟡","Suspicious":"🟠","Hostile":"🔴"}.get(att, "⚪")
            lines.append(f"{att_emoji} **{npc['name']}** — {npc.get('race','')} {npc.get('occupation','')} | {att}")
        return "\n".join(lines), True

    elif function_name == "npc_update":
        name = arguments.get("name", "")
        key, npc = _find(name, npcs)
        if not npc:
            return f"No NPC named '{name}' found.", False
        if "attitude" in arguments:
            npc["attitude"] = arguments["attitude"]
        if "notes" in arguments:
            existing_notes = npc.get("notes", "")
            new_note = arguments["notes"]
            npc["notes"] = (existing_notes + " | " + new_note).strip(" | ") if existing_notes else new_note
        npcs[key] = npc
        _save_all(npcs)
        return f"✅ {key} updated.\n\n{_npc_card(npc)}", True

    elif function_name == "npc_delete":
        name = arguments.get("name", "")
        key, npc = _find(name, npcs)
        if not npc:
            return f"No NPC named '{name}' found.", False
        del npcs[key]
        _save_all(npcs)
        return f"🗑️ '{key}' removed from roster.", True

    return f"Unknown function: {function_name}", False
