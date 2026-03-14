"""
D&D 5e Spell Database

Covers ~80 of the most commonly used spells with full mechanics.
Fields: name, level, school, casting_time, range, components, duration,
        classes, description, higher_levels (if applicable)
"""

ENABLED = True
EMOJI = '📖'
AVAILABLE_FUNCTIONS = ['spell_lookup', 'spell_list']

SPELLS = [
    # ── Cantrips ──
    {"name":"Fire Bolt","level":0,"school":"Evocation","casting_time":"1 action","range":"120 feet","components":"V, S","duration":"Instantaneous","classes":["Sorcerer","Wizard"],"description":"Hurl a mote of fire. Make a ranged spell attack against target. On hit: 1d10 fire damage. Damage increases to 2d10 at 5th level, 3d10 at 11th, 4d10 at 17th."},
    {"name":"Eldritch Blast","level":0,"school":"Evocation","casting_time":"1 action","range":"120 feet","components":"V, S","duration":"Instantaneous","classes":["Warlock"],"description":"A beam of crackling energy strikes a target. Make a ranged spell attack. On hit: 1d10 force damage. Creates an additional beam at 5th level (2), 11th (3), 17th (4). Each beam targets the same or different creatures."},
    {"name":"Prestidigitation","level":0,"school":"Transmutation","casting_time":"1 action","range":"10 feet","components":"V, S","duration":"Up to 1 hour","classes":["Bard","Sorcerer","Warlock","Wizard"],"description":"Minor magical trick. Create a small sensory effect, light/snuff a candle, clean/soil an object, chill/warm/flavor 1 cubic foot of nonliving material, leave a mark, produce a small trinket."},
    {"name":"Mage Hand","level":0,"school":"Conjuration","casting_time":"1 action","range":"30 feet","components":"V, S","duration":"1 minute","classes":["Bard","Sorcerer","Warlock","Wizard"],"description":"A spectral hand appears that can manipulate objects, open doors/containers, stow/retrieve items, or pour liquids. Weight limit: 10 lb. Cannot attack or activate magic items."},
    {"name":"Minor Illusion","level":0,"school":"Illusion","casting_time":"1 action","range":"30 feet","components":"S, M (a bit of fleece)","duration":"1 minute","classes":["Bard","Sorcerer","Warlock","Wizard"],"description":"Create a sound or image. Sound: whisper to scream. Image: up to 5-foot cube, no sound/smell/light. Investigation check (DC = spell save DC) to determine illusion."},
    {"name":"Sacred Flame","level":0,"school":"Evocation","casting_time":"1 action","range":"60 feet","components":"V, S","duration":"Instantaneous","classes":["Cleric"],"description":"Flame descends on a creature you can see. Target must succeed DC [spell save] Dex save or take 1d8 radiant damage. No benefit from cover. Damage increases: 2d8 at 5th, 3d8 at 11th, 4d8 at 17th."},
    {"name":"Toll the Dead","level":0,"school":"Necromancy","casting_time":"1 action","range":"60 feet","components":"V, S","duration":"Instantaneous","classes":["Cleric","Warlock","Wizard"],"description":"A doleful sound and an image of death. Target must make Wis save. Fail: 1d8 necrotic (1d12 if missing HP). Damage increases: 2d8/2d12 at 5th, 3d8/3d12 at 11th, 4d8/4d12 at 17th."},
    {"name":"Shillelagh","level":0,"school":"Transmutation","casting_time":"1 bonus action","range":"Touch","components":"V, S, M (mistletoe, shamrock leaf, club or quarterstaff)","duration":"1 minute","classes":["Druid"],"description":"Wood of a club or quarterstaff becomes magical. Attacks with the weapon use your spellcasting ability modifier instead of STR, and deal 1d8 bludgeoning damage."},
    {"name":"Vicious Mockery","level":0,"school":"Enchantment","casting_time":"1 action","range":"60 feet","components":"V","duration":"Instantaneous","classes":["Bard"],"description":"Unleash a string of insults at a creature. Target must succeed Wisdom save or take 1d4 psychic damage and have disadvantage on the next attack roll it makes before the end of its next turn. Damage: 2d4 at 5th, 3d4 at 11th, 4d4 at 17th."},
    {"name":"Guidance","level":0,"school":"Divination","casting_time":"1 action","range":"Touch","components":"V, S","duration":"Concentration, up to 1 minute","classes":["Cleric","Druid"],"description":"Touch a willing creature. Once before the spell ends, the target can roll a d4 and add the result to one ability check of its choice. The spell then ends."},
    {"name":"Thaumaturgy","level":0,"school":"Transmutation","casting_time":"1 action","range":"30 feet","components":"V","duration":"Up to 1 minute","classes":["Cleric"],"description":"Manifest a minor wonder: amplify voice, cause flames to flicker/brighten/dim/change color, cause tremors, create instantaneous sound, open/close an unlocked door/window/shutter, alter eye appearance."},

    # ── 1st Level ──
    {"name":"Magic Missile","level":1,"school":"Evocation","casting_time":"1 action","range":"120 feet","components":"V, S","duration":"Instantaneous","classes":["Sorcerer","Wizard"],"description":"Create 3 glowing darts that each automatically hit a target and deal 1d4+1 force damage. Can hit the same or different targets.","higher_levels":"One additional dart per spell slot level above 1st."},
    {"name":"Cure Wounds","level":1,"school":"Evocation","casting_time":"1 action","range":"Touch","components":"V, S","duration":"Instantaneous","classes":["Bard","Cleric","Druid","Paladin","Ranger"],"description":"A creature you touch regains 1d8 + spellcasting ability modifier HP. No effect on undead or constructs.","higher_levels":"1d8 additional HP per slot level above 1st."},
    {"name":"Shield","level":1,"school":"Abjuration","casting_time":"1 reaction (when hit by attack or targeted by Magic Missile)","range":"Self","components":"V, S","duration":"1 round","classes":["Sorcerer","Wizard"],"description":"+5 bonus to AC until the start of your next turn, including against the triggering attack. Immune to Magic Missile for the duration."},
    {"name":"Thunderwave","level":1,"school":"Evocation","casting_time":"1 action","range":"Self (15-foot cube)","components":"V, S","duration":"Instantaneous","classes":["Bard","Cleric","Druid","Sorcerer","Wizard"],"description":"Each creature in a 15-foot cube originating from you must make Con save. Fail: 2d8 thunder damage, pushed 10 feet. Success: half damage. Unsecured objects pushed 10 feet. Audible up to 300 feet.","higher_levels":"2d8 additional thunder damage per slot level above 1st."},
    {"name":"Healing Word","level":1,"school":"Evocation","casting_time":"1 bonus action","range":"60 feet","components":"V","duration":"Instantaneous","classes":["Bard","Cleric","Druid"],"description":"A creature of your choice regains 1d4 + spellcasting ability modifier HP.","higher_levels":"1d4 additional HP per slot level above 1st."},
    {"name":"Sleep","level":1,"school":"Enchantment","casting_time":"1 action","range":"90 feet","components":"V, S, M (fine sand, rose petals, or cricket)","duration":"1 minute","classes":["Bard","Sorcerer","Wizard"],"description":"Roll 5d8; total is HP of creatures affected. Unconscious creatures first, then lowest HP. Humanoids only. Unconscious for duration. Creature wakes if damaged or shaken awake.","higher_levels":"2d8 additional HP of creatures affected per slot above 1st."},
    {"name":"Charm Person","level":1,"school":"Enchantment","casting_time":"1 action","range":"30 feet","components":"V, S","duration":"1 hour","classes":["Bard","Druid","Sorcerer","Warlock","Wizard"],"description":"Target humanoid must succeed Wisdom save (advantage if hostile) or be charmed. Regards you as friendly. Knows it was charmed when spell ends.","higher_levels":"One additional target per slot level above 1st."},
    {"name":"Detect Magic","level":1,"school":"Divination","casting_time":"1 action","range":"Self","components":"V, S","duration":"Concentration, up to 10 minutes","classes":["Bard","Cleric","Druid","Paladin","Ranger","Sorcerer","Wizard"],"description":"Sense presence of magic within 30 feet. See a faint aura around magical objects/creatures, and learn the school of magic if you spend an action to focus."},
    {"name":"Identify","level":1,"school":"Divination","casting_time":"1 minute (ritual)","range":"Touch","components":"V, S, M (pearl worth 100gp, owl feather)","duration":"Instantaneous","classes":["Bard","Wizard"],"description":"Learn a magic item's properties and how to use them, whether it requires attunement, and its remaining charges. Also learn if creature is under a spell."},
    {"name":"Mage Armor","level":1,"school":"Abjuration","casting_time":"1 action","range":"Touch","components":"V, S, M (cured leather)","duration":"8 hours","classes":["Sorcerer","Wizard"],"description":"Target willing creature not wearing armor. AC becomes 13 + Dex modifier. Ends if target dons armor."},
    {"name":"Bless","level":1,"school":"Enchantment","casting_time":"1 action","range":"30 feet","components":"V, S, M (holy water)","duration":"Concentration, up to 1 minute","classes":["Cleric","Paladin"],"description":"Up to 3 creatures of your choice add 1d4 to attack rolls and saving throws for the duration.","higher_levels":"One additional creature per slot level above 1st."},
    {"name":"Bane","level":1,"school":"Enchantment","casting_time":"1 action","range":"30 feet","components":"V, S, M (blood drop)","duration":"Concentration, up to 1 minute","classes":["Bard","Cleric"],"description":"Up to 3 creatures must succeed Charisma saves or subtract 1d4 from attack rolls and saving throws.","higher_levels":"One additional creature per slot level above 1st."},
    {"name":"Hunter's Mark","level":1,"school":"Divination","casting_time":"1 bonus action","range":"90 feet","components":"V","duration":"Concentration, up to 1 hour","classes":["Ranger"],"description":"Choose a creature; deal 1d6 extra damage with weapon attacks against it. Also advantage on Perception/Survival checks to track it. If target dies, move mark to new creature as bonus action.","higher_levels":"Duration: up to 8 hours (3rd+), 24 hours (5th+)."},
    {"name":"Hex","level":1,"school":"Enchantment","casting_time":"1 bonus action","range":"90 feet","components":"V, S, M (petrified eye of newt)","duration":"Concentration, up to 1 hour","classes":["Warlock"],"description":"Curse a creature. Deal extra 1d6 necrotic damage when you hit with attack. Choose one ability — target has disadvantage on checks using it. If target drops to 0 HP, move hex to new target as bonus action.","higher_levels":"Duration: up to 8 hours (3rd+), 24 hours (5th+)."},

    # ── 2nd Level ──
    {"name":"Misty Step","level":2,"school":"Conjuration","casting_time":"1 bonus action","range":"Self","components":"V","duration":"Instantaneous","classes":["Paladin (Oath of the Ancients)","Sorcerer","Warlock","Wizard"],"description":"Teleport up to 30 feet to an unoccupied space you can see, surrounded by silver mist."},
    {"name":"Hold Person","level":2,"school":"Enchantment","casting_time":"1 action","range":"60 feet","components":"V, S, M (iron bar)","duration":"Concentration, up to 1 minute","classes":["Bard","Cleric","Druid","Sorcerer","Warlock","Wizard"],"description":"Humanoid must make Wisdom save or be paralyzed. Repeats save each turn. While paralyzed: incapacitated, can't move/speak, auto-fails Str/Dex saves, attacks against it have advantage. Melee attacks within 5 feet are critical hits.","higher_levels":"One additional target per slot level above 2nd."},
    {"name":"Invisibility","level":2,"school":"Illusion","casting_time":"1 action","range":"Touch","components":"V, S, M (eyelash of bat)","duration":"Concentration, up to 1 hour","classes":["Bard","Sorcerer","Warlock","Wizard"],"description":"A creature you touch becomes invisible until the spell ends or it attacks or casts a spell.","higher_levels":"One additional target per slot level above 2nd."},
    {"name":"Mirror Image","level":2,"school":"Illusion","casting_time":"1 action","range":"Self","components":"V, S","duration":"1 minute","classes":["Sorcerer","Warlock","Wizard"],"description":"3 illusory duplicates appear. When attacked, roll d20: 6+ (3 images), 8+ (2 images), 11+ (1 image) = duplicate is hit instead and destroyed. Duplicates share your AC."},
    {"name":"Shatter","level":2,"school":"Evocation","casting_time":"1 action","range":"60 feet","components":"V, S, M (mica chip)","duration":"Instantaneous","classes":["Bard","Sorcerer","Warlock","Wizard"],"description":"10-foot radius sphere of thunderous sound. Creatures must make Con save. Fail: 3d8 thunder. Success: half. Disadvantage for inorganic creatures (crystal, metal, stone). Unattended objects take full damage automatically.","higher_levels":"1d8 additional damage per slot level above 2nd."},
    {"name":"Spiritual Weapon","level":2,"school":"Evocation","casting_time":"1 bonus action","range":"60 feet","components":"V, S","duration":"1 minute","classes":["Cleric"],"description":"Create floating spectral weapon. Bonus action: move up to 20 feet and attack (+spellcasting mod to hit, 1d8+spellcasting mod force damage). Doesn't require concentration.","higher_levels":"1d8 additional damage per slot level above 2nd (2 levels)."},
    {"name":"Scorching Ray","level":2,"school":"Evocation","casting_time":"1 action","range":"120 feet","components":"V, S","duration":"Instantaneous","classes":["Sorcerer","Wizard"],"description":"Create 3 rays. Make a ranged spell attack for each. On hit: 2d6 fire damage. Can target same or different creatures.","higher_levels":"One additional ray per slot level above 2nd."},
    {"name":"Web","level":2,"school":"Conjuration","casting_time":"1 action","range":"60 feet","components":"V, S, M (spider web)","duration":"Concentration, up to 1 hour","classes":["Sorcerer","Wizard"],"description":"20-foot cube of webbing. Difficult terrain. Creatures starting turn in webs or entering them make Dex save or become restrained. Restrained creature can use action to escape (Str check vs spell save DC). Highly flammable."},
    {"name":"Suggestion","level":2,"school":"Enchantment","casting_time":"1 action","range":"30 feet","components":"V, M (snake tongue, honeycomb/sweet oil)","duration":"Concentration, up to 8 hours","classes":["Bard","Sorcerer","Warlock","Wizard"],"description":"Suggest a reasonable course of action to one creature. Must make Wisdom save or follow the suggestion. Ends if harmed by caster or compelled to do something obviously harmful."},
    {"name":"Silence","level":2,"school":"Illusion","casting_time":"1 action","range":"120 feet","components":"V, S","duration":"Concentration, up to 10 minutes","classes":["Bard","Cleric","Ranger"],"description":"20-foot radius sphere of magical silence. No sound can be created within or pass through it. Creatures are deafened. Spells with verbal components can't be cast inside."},

    # ── 3rd Level ──
    {"name":"Fireball","level":3,"school":"Evocation","casting_time":"1 action","range":"150 feet","components":"V, S, M (bat guano and sulfur)","duration":"Instantaneous","classes":["Sorcerer","Wizard"],"description":"A bright streak explodes into a 20-foot radius sphere. Creatures must make Dex save. Fail: 8d6 fire. Success: half. Fire spreads around corners, ignites flammable objects.","higher_levels":"1d6 additional fire damage per slot level above 3rd."},
    {"name":"Lightning Bolt","level":3,"school":"Evocation","casting_time":"1 action","range":"Self (100-foot line)","components":"V, S, M (fur and glass/crystal rod)","duration":"Instantaneous","classes":["Sorcerer","Wizard"],"description":"100-foot × 5-foot line of lightning. Creatures in line make Dex save. Fail: 8d6 lightning. Success: half. Bounces off solid obstacles.","higher_levels":"1d6 additional lightning damage per slot level above 3rd."},
    {"name":"Counterspell","level":3,"school":"Abjuration","casting_time":"1 reaction (when creature within 60 feet casts spell)","range":"60 feet","components":"S","duration":"Instantaneous","classes":["Sorcerer","Warlock","Wizard"],"description":"Attempt to interrupt a spell being cast. Automatically counters spells of 3rd level or lower. Higher level spells: make ability check (DC 10 + spell level). On fail, the spell proceeds.","higher_levels":"Automatically counter spells of a level equal to or lower than the slot used."},
    {"name":"Hypnotic Pattern","level":3,"school":"Illusion","casting_time":"1 action","range":"120 feet","components":"S, M (glowing stick of incense or crystal vial)","duration":"Concentration, up to 1 minute","classes":["Bard","Sorcerer","Warlock","Wizard"],"description":"Create a twisting 30-foot cube pattern. Creatures who can see it make Wis save or are charmed: incapacitated and have speed 0. Effect ends if creature is harmed or someone uses action to snap them out."},
    {"name":"Mass Healing Word","level":3,"school":"Evocation","casting_time":"1 bonus action","range":"60 feet","components":"V","duration":"Instantaneous","classes":["Cleric"],"description":"Up to 6 creatures each regain 1d4 + spellcasting ability modifier HP.","higher_levels":"1d4 additional HP per slot level above 3rd."},
    {"name":"Dispel Magic","level":3,"school":"Abjuration","casting_time":"1 action","range":"120 feet","components":"V, S","duration":"Instantaneous","classes":["Bard","Cleric","Druid","Paladin","Sorcerer","Warlock","Wizard"],"description":"Ends spells of 3rd level or lower on target. Spells of 4th level or higher: make ability check (DC 10 + spell level) to dispel.","higher_levels":"Automatically end spells of a level equal to or lower than the slot used."},
    {"name":"Fly","level":3,"school":"Transmutation","casting_time":"1 action","range":"Touch","components":"V, S, M (wing feather from any bird)","duration":"Concentration, up to 10 minutes","classes":["Sorcerer","Warlock","Wizard"],"description":"Target gains flying speed of 60 feet for the duration. If concentration ends while in the air, target falls.","higher_levels":"One additional target per slot level above 3rd."},
    {"name":"Haste","level":3,"school":"Transmutation","casting_time":"1 action","range":"30 feet","components":"V, S, M (shaving of licorice root)","duration":"Concentration, up to 1 minute","classes":["Sorcerer","Wizard"],"description":"Target's speed doubled, +2 AC, advantage on Dex saves, gains an additional action each turn (attack once, Dash, Disengage, Hide, or Use Object). When spell ends, target can't move or take actions until after its next turn."},
    {"name":"Animate Dead","level":3,"school":"Necromancy","casting_time":"1 minute","range":"10 feet","components":"V, S, M (drop of blood, flesh, bone)","duration":"Instantaneous","classes":["Cleric","Wizard"],"description":"Create a zombie or skeleton from corpse or pile of bones. Under your control for 24 hours. Use bonus action to command up to 4 undead. Recast spell within 24 hours to extend control.","higher_levels":"Two additional undead per slot level above 3rd."},

    # ── 4th Level ──
    {"name":"Banishment","level":4,"school":"Abjuration","casting_time":"1 action","range":"60 feet","components":"V, S, M (abjuration item)","duration":"Concentration, up to 1 minute","classes":["Cleric","Paladin","Sorcerer","Warlock","Wizard"],"description":"Creature makes Charisma save. Fail: sent to harmless demiplane incapacitated. If concentration maintained for 1 minute, creature is permanently banished (native extraplanar) or returns 10 feet from where it was.","higher_levels":"One additional target per slot level above 4th."},
    {"name":"Polymorph","level":4,"school":"Transmutation","casting_time":"1 action","range":"60 feet","components":"V, S, M (caterpillar cocoon)","duration":"Concentration, up to 1 hour","classes":["Bard","Druid","Sorcerer","Wizard"],"description":"Transform a creature into a new form. Unwilling creature makes Wis save. Limited to beast form with CR ≤ target's level/CR. Uses beast's statistics, retains alignment and personality. Reverts if HP drops to 0."},
    {"name":"Greater Invisibility","level":4,"school":"Illusion","casting_time":"1 action","range":"Touch","components":"V, S","duration":"Concentration, up to 1 minute","classes":["Bard","Sorcerer","Wizard"],"description":"Target becomes invisible whether or not it attacks or casts spells. Attacks against it have disadvantage; its attacks have advantage."},
    {"name":"Wall of Fire","level":4,"school":"Evocation","casting_time":"1 action","range":"120 feet","components":"V, S, M (bit of phosphorous)","duration":"Concentration, up to 1 minute","classes":["Druid","Sorcerer","Wizard"],"description":"Create a wall up to 60 ft long, 20 ft high, 1 ft thick — or a 20-ft-diameter ring. Choose inner or outer side to deal damage. Creatures entering or starting turn on that side: 5d8 fire (Dex save, half on success).","higher_levels":"1d8 additional fire damage per slot level above 4th."},
    {"name":"Ice Storm","level":4,"school":"Evocation","casting_time":"1 action","range":"300 feet","components":"V, S, M (dusting of powdered ice)","duration":"Instantaneous","classes":["Druid","Sorcerer","Wizard"],"description":"20-foot radius, 40-foot high cylinder of hail. Creatures make Dex save. Fail: 2d8 bludgeoning + 4d6 cold. Success: half. Ground in area is difficult terrain until end of next turn.","higher_levels":"1d8 additional bludgeoning per slot level above 4th."},

    # ── 5th Level ──
    {"name":"Fireball (5th slot)","level":5,"school":"Evocation","casting_time":"See Fireball","range":"See Fireball","components":"See Fireball","duration":"See Fireball","classes":["Sorcerer","Wizard"],"description":"Fireball cast at 5th level deals 10d6 fire damage."},
    {"name":"Cone of Cold","level":5,"school":"Evocation","casting_time":"1 action","range":"Self (60-foot cone)","components":"V, S, M (drop of water or ice)","duration":"Instantaneous","classes":["Sorcerer","Wizard"],"description":"A 60-foot cone of cold air. Creatures make Con save. Fail: 8d8 cold. Success: half. Killed creatures become frozen statues — shatter on hit for 3d6 piercing to adjacent creatures.","higher_levels":"1d8 additional cold damage per slot level above 5th."},
    {"name":"Wall of Force","level":5,"school":"Evocation","casting_time":"1 action","range":"120 feet","components":"V, S, M (pinch of powder from disintegrated clear gem)","duration":"Concentration, up to 10 minutes","classes":["Wizard"],"description":"An invisible wall of force up to 10 10-foot × 10-foot panels or a sphere up to 10-foot radius. Immune to all damage, can't be dispelled (dispel magic has no effect), can be targeted by Disintegrate."},
    {"name":"Teleportation Circle","level":5,"school":"Conjuration","casting_time":"1 minute","range":"10 feet","components":"V, M (rare chalks and inks, 50gp)","duration":"1 round","classes":["Bard","Sorcerer","Wizard"],"description":"A shimmering circle appears that teleports up to 9 willing creatures to a permanent teleportation circle whose sigil sequence you know."},
    {"name":"Mass Cure Wounds","level":5,"school":"Evocation","casting_time":"1 action","range":"60 feet","components":"V, S","duration":"Instantaneous","classes":["Bard","Cleric","Druid"],"description":"Up to 6 creatures each regain 3d8 + spellcasting modifier HP. No effect on undead or constructs.","higher_levels":"1d8 additional HP per slot level above 5th."},
    {"name":"Hold Monster","level":5,"school":"Enchantment","casting_time":"1 action","range":"90 feet","components":"V, S, M (small iron bar)","duration":"Concentration, up to 1 minute","classes":["Bard","Sorcerer","Warlock","Wizard"],"description":"Like Hold Person but works on any creature (not just humanoids). Target makes Wis save or is paralyzed. Repeats save each turn.","higher_levels":"One additional target per slot level above 5th."},

    # ── 6th+ Level ──
    {"name":"Disintegrate","level":6,"school":"Transmutation","casting_time":"1 action","range":"60 feet","components":"V, S, M (lodestone and dust)","duration":"Instantaneous","classes":["Sorcerer","Wizard"],"description":"Target makes Dex save. Fail: 10d6 + 40 force damage. If this reduces target to 0 HP, it disintegrates — everything it's wearing/carrying except magic items. Large or smaller nonmagical objects also disintegrate.","higher_levels":"3d6 additional force damage per slot level above 6th."},
    {"name":"Chain Lightning","level":6,"school":"Evocation","casting_time":"1 action","range":"150 feet","components":"V, S, M (fur, amber/glass rod, silver wire)","duration":"Instantaneous","classes":["Sorcerer","Wizard"],"description":"A bolt of lightning jumps to 4 targets (within 30 feet of each other). Each makes Dex save: 10d8 lightning on fail, half on success.","higher_levels":"One additional target per slot level above 6th."},
    {"name":"Heal","level":6,"school":"Evocation","casting_time":"1 action","range":"60 feet","components":"V, S","duration":"Instantaneous","classes":["Cleric","Druid"],"description":"Target regains 70 HP. Also ends blindness, deafness, and any diseases on target. No effect on constructs or undead.","higher_levels":"10 additional HP per slot level above 6th."},

    {"name":"Finger of Death","level":7,"school":"Necromancy","casting_time":"1 action","range":"60 feet","components":"V, S","duration":"Instantaneous","classes":["Sorcerer","Warlock","Wizard"],"description":"Target makes Con save. Fail: 7d8 + 30 necrotic. Success: half. A humanoid killed this way rises the next turn as a zombie permanently under your control."},
    {"name":"Power Word Kill","level":9,"school":"Enchantment","casting_time":"1 action","range":"60 feet","components":"V","duration":"Instantaneous","classes":["Sorcerer","Warlock","Wizard"],"description":"Utter a word of power that instantly kills a creature with 100 HP or fewer. No saving throw."},
    {"name":"Wish","level":9,"school":"Conjuration","casting_time":"1 action","range":"Self","components":"V","duration":"Instantaneous","classes":["Sorcerer","Wizard"],"description":"The most powerful spell. Duplicate any spell of 8th level or lower without material components. Or create one of many listed effects. Or describe a wish — DM interprets it. Risk: 33% chance to never cast Wish again if used for something other than duplicating a spell."},
    {"name":"Meteor Swarm","level":9,"school":"Evocation","casting_time":"1 action","range":"1 mile","components":"V, S","duration":"Instantaneous","classes":["Sorcerer","Wizard"],"description":"Four 40-foot radius spheres centered on chosen points (must be on ground, at least 40 ft apart). Creatures in area make Dex save. Fail: 20d6 fire + 20d6 bludgeoning. Success: half. Sheds bright light 40 ft, dim 40 ft. Duration: 1 round."},
]

TOOLS = [
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "spell_lookup",
            "description": "Look up a D&D 5e spell's full mechanics, components, damage, and description. Use whenever a player casts a spell and you need accurate rules, or to answer questions about how a spell works.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Spell name, e.g. 'Fireball', 'Cure Wounds', 'Counterspell'"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "spell_list",
            "description": "List available spells, optionally filtered by class or level.",
            "parameters": {
                "type": "object",
                "properties": {
                    "class_name": {"type": "string", "description": "Filter by class, e.g. 'Wizard', 'Cleric', 'Warlock'"},
                    "level":      {"type": "integer", "description": "Filter by spell level (0 = cantrips)"}
                },
                "required": []
            }
        }
    }
]


def execute(function_name, arguments, config):
    if function_name == "spell_lookup":
        query = arguments.get("name", "").lower().strip()
        matches = [s for s in SPELLS if query in s["name"].lower()]
        if not matches:
            names = ", ".join(s["name"] for s in SPELLS[:20])
            return f"Spell '{arguments.get('name','')}' not found. Sample spells: {names}...", False

        s = matches[0]
        school_level = f"Level {s['level']} {s['school']}" if s['level'] > 0 else f"Cantrip ({s['school']})"
        result = (
            f"📖 **{s['name']}**\n"
            f"{school_level}\n"
            f"**Casting Time:** {s['casting_time']}\n"
            f"**Range:** {s['range']}\n"
            f"**Components:** {s['components']}\n"
            f"**Duration:** {s['duration']}\n"
            f"**Classes:** {', '.join(s['classes'])}\n\n"
            f"{s['description']}"
        )
        if s.get("higher_levels"):
            result += f"\n\n**At Higher Levels:** {s['higher_levels']}"
        return result, True

    elif function_name == "spell_list":
        class_filter = arguments.get("class_name", "").lower()
        level_filter = arguments.get("level", None)

        results = SPELLS[:]
        if class_filter:
            results = [s for s in results if any(class_filter in c.lower() for c in s["classes"])]
        if level_filter is not None:
            results = [s for s in results if s["level"] == level_filter]

        if not results:
            return "No spells found matching those filters.", True

        by_level = {}
        for s in results:
            by_level.setdefault(s["level"], []).append(s["name"])

        lines = []
        for lvl in sorted(by_level.keys()):
            label = "Cantrips" if lvl == 0 else f"Level {lvl}"
            lines.append(f"**{label}:** {', '.join(sorted(by_level[lvl]))}")
        return "\n".join(lines), True

    return f"Unknown function: {function_name}", False
