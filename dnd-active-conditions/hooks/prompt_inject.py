"""
dnd-active-conditions — prompt_inject hook

Reads character condition state from dnd-characters plugin storage and
injects a loud, formatted conditions block into every prompt when any
character has active conditions.

Only injects during active combat (reads dnd-encounters state).
During non-combat scenes, injects a quieter one-liner summary instead
(e.g. "Thorin is still poisoned — disadvantage on attacks and ability checks.")

Supports multi-campaign: reads from the active campaign's character and combat data.
"""

from core.plugin_loader import plugin_loader
import logging

logger = logging.getLogger("dnd-active-conditions")

DEFAULT_CAMPAIGN_ID = "default"

# Mechanical effects for injection — mirrors dnd-rules condition_lookup
# but pre-baked to avoid a tool call inside a hook
CONDITION_EFFECTS = {
    "blinded":        "can't see; auto-fails sight checks; attack rolls have disadvantage; attackers have advantage",
    "charmed":        "can't attack charmer; charmer has advantage on social checks vs this creature",
    "deafened":       "can't hear; auto-fails hearing checks",
    "exhaustion_1":   "disadvantage on ability checks",
    "exhaustion_2":   "disadvantage on ability checks; speed halved",
    "exhaustion_3":   "disadvantage on ability checks and attack rolls and saving throws",
    "exhaustion_4":   "disadvantage on ability checks, attacks, saves; max HP halved",
    "exhaustion_5":   "all above + speed = 0",
    "frightened":     "disadvantage on ability checks and attack rolls while source is in sight; can't move toward source",
    "grappled":       "speed = 0",
    "incapacitated":  "can't take actions or reactions",
    "invisible":      "can't be seen; attack rolls have advantage; attackers have disadvantage",
    "paralyzed":      "incapacitated; can't move or speak; auto-fails Str/Dex saves; attacks have advantage; hits within 5ft are crits",
    "petrified":      "transformed to stone; incapacitated; resistant to all damage; immune to poison/disease",
    "poisoned":       "DISADVANTAGE on attack rolls; DISADVANTAGE on ability checks",
    "prone":          "can only crawl; disadvantage on attacks; attackers within 5ft have advantage; ranged attackers have disadvantage",
    "restrained":     "speed = 0; attack rolls have disadvantage; attackers have advantage; disadvantage on Dex saves",
    "stunned":        "incapacitated; can't move; can only speak falteringly; auto-fails Str/Dex saves; attackers have advantage",
    "unconscious":    "incapacitated; drops everything; falls prone; auto-fails Str/Dex saves; attackers have advantage; hits within 5ft are crits",
    "concentration":  "maintaining concentration — damage triggers DC 10 or half-damage CON save or spell ends",
    "death_saves":    "at 0 HP — tracking death saving throws",
}


def _get_campaign_id():
    """Get current campaign ID from dnd-campaign state."""
    try:
        campaign_state = plugin_loader.get_plugin_state("dnd-campaign")
        return campaign_state.get("active_campaign", DEFAULT_CAMPAIGN_ID)
    except Exception:
        return DEFAULT_CAMPAIGN_ID


def _get_all_characters():
    """Read all characters from dnd-characters plugin state for the current campaign."""
    try:
        campaign_id = _get_campaign_id()
        char_state = plugin_loader.get_plugin_state("dnd-characters")

        # Try campaign-scoped data first
        chars = char_state.get(f"characters:{campaign_id}") or {}

        # Fall back to legacy data for backward compatibility
        if not chars:
            chars = char_state.get("characters") or {}

        return list(chars.values()) if chars else []
    except Exception as e:
        logger.debug(f"[active-conditions] Could not read characters: {e}")
        return []


def _is_combat_active():
    """Check if combat is currently running via dnd-encounters state for the current campaign."""
    try:
        campaign_id = _get_campaign_id()
        enc_state = plugin_loader.get_plugin_state("dnd-encounters")

        # Try campaign-scoped combat data first
        combat = enc_state.get(f"combat:{campaign_id}")

        # Fall back to legacy data for backward compatibility
        if not combat:
            combat = enc_state.get("combat")

        return bool(combat)
    except Exception:
        return False


def prompt_inject(event):
    characters = _get_all_characters()
    if not characters:
        return

    # Collect all characters with active conditions
    afflicted = []
    for char in characters:
        conditions = char.get("conditions", [])
        if not conditions:
            continue
        name = char.get("name", "Unknown")
        afflicted.append((name, conditions))

    if not afflicted:
        return

    in_combat = _is_combat_active()

    if in_combat:
        # LOUD combat-mode injection — every active condition with mechanics
        lines = ["⚠️ ACTIVE CONDITIONS — APPLY THESE MECHANICS NOW:"]
        for name, conditions in afflicted:
            lines.append(f"\n  {name.upper()}:")
            for cond in conditions:
                effect = CONDITION_EFFECTS.get(cond.lower(), "see rules reference")
                lines.append(f"    • {cond.upper()}: {effect}")
        lines.append("\nDo NOT skip or forget these modifiers. Check before every roll.")
        event.context_parts.append("\n".join(lines))
    else:
        # Quiet out-of-combat summary
        summaries = []
        for name, conditions in afflicted:
            readable = [c.replace("_", " ") for c in conditions]
            summaries.append(f"{name} [{', '.join(readable)}]")
        event.context_parts.append(
            f"⚠️ Ongoing conditions: {'; '.join(summaries)}. "
            f"These persist until cured or the condition expires."
        )
