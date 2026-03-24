"""
dnd-scaffold/hooks/prompt_inject.py — consolidated D&D state injection

Merged from dnd-active-conditions prompt_inject + all D&D plugin state injection.

Injects into every prompt:
1. Active conditions (loud in combat, quiet out of combat)
2. Inspiration state
3. Travel/exploration state
4. High-urgency narrative threads
"""

from core.plugin_loader import plugin_loader
import logging

logger = logging.getLogger("dnd-scaffold")


# ── State auditor helpers for prompt_inject cross-check ────────────────────────

def _aud_get_state():
    from core.plugin_loader import plugin_loader
    return plugin_loader.get_plugin_state("dnd-scaffold")


def _aud_is_dnd_active():
    try:
        state = _aud_get_state()
        return state.get("dnd_active", False)
    except Exception:
        return False


def _aud_get_recent_tool_calls(state, count=10):
    """Get recent tool calls from audit log."""
    try:
        audit_log = state.get("audit_log") or []
        return audit_log[-count:]
    except Exception:
        return []


def _aud_get_turn_count(state):
    """Get current turn count."""
    try:
        return state.get("turn_count") or 0
    except Exception:
        return 0

DEFAULT_CAMPAIGN_ID = "default"

# Mechanical effects for condition injection — mirrors dnd-rules condition_lookup
CONDITION_EFFECTS = {
    "blinded":        "can't see; auto-fails sight checks; attack rolls have disadvantage; attackers have advantage",
    "charmed":        "can't attack charmer; charmer has advantage on social checks vs this creature",
    "deafened":       "can't hear; auto-fails hearing checks",
    "exhaustion_1":   "disadvantage on ability checks",
    "exhaustion_2":   "disadvantage on ability checks; speed halved",
    "exhaustion_3":   "disadvantage on ability checks and attack rolls and saving throws",
    "exhaustion_4":   "disadvantage on ability checks, attacks, saves; max HP halved",
    "exhaustion_5":   "all above + speed = 0",
    "exhaustion_6":   "death",
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
    "concentration":   "maintaining concentration — damage triggers DC 10 or half-damage CON save or spell ends",
    "death_saves":     "at 0 HP — tracking death saving throws",
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
        chars = char_state.get(f"characters:{campaign_id}") or {}
        if not chars:
            chars = char_state.get("characters") or {}
        return list(chars.values()) if chars else []
    except Exception as e:
        logger.debug(f"[prompt_inject] Could not read characters: {e}")
        return []


def _is_combat_active():
    """Check if combat is currently running via dnd-encounters state."""
    try:
        campaign_id = _get_campaign_id()
        enc_state = plugin_loader.get_plugin_state("dnd-encounters")
        combat = enc_state.get(f"combat:{campaign_id}")
        if not combat:
            combat = enc_state.get("combat")
        return bool(combat)
    except Exception:
        return False


def _get_inspiration_state():
    """Get active inspiration awards for the campaign."""
    try:
        campaign_id = _get_campaign_id()
        insp_state = plugin_loader.get_plugin_state("dnd-inspiration")
        awards = insp_state.get(f"awards:{campaign_id}") or []
        if not awards:
            awards = insp_state.get("awards") or []
        return awards
    except Exception:
        return []


def _get_travel_state():
    """Get current travel state if any."""
    try:
        campaign_id = _get_campaign_id()
        travel_state = plugin_loader.get_plugin_state("dnd-travel")
        travel = travel_state.get(f"travel_state:{campaign_id}")
        if not travel:
            travel = travel_state.get("travel_state")
        return travel or {}
    except Exception:
        return {}


def _get_high_urgency_threads():
    """Get threads marked as high urgency."""
    try:
        campaign_id = _get_campaign_id()
        thread_state = plugin_loader.get_plugin_state("dnd-threads")
        threads = thread_state.get(f"threads:{campaign_id}") or {}
        if not threads:
            threads = thread_state.get("threads") or {}
        urgent = []
        for t in threads.values():
            if t.get("urgency") in ("high", "critical"):
                urgent.append(t.get("title", "Unnamed thread"))
        return urgent
    except Exception:
        return []


def prompt_inject(event):
    """
    Fires on every prompt. Injects D&D game state:
    - D&D mode OFF override (if game not active) — runs FIRST
    - Active conditions (combat = loud, non-combat = quiet)
    - Inspiration state
    - Travel/exploration state
    - High-urgency threads
    """
    # ── D&D mode OFF override — fires first ──────────────────────────────────
    try:
        state = plugin_loader.get_plugin_state("dnd-scaffold")
        dnd_active = state.get("dnd_active")
        if dnd_active is None:
            dnd_active = False
        if not dnd_active:
            event.context_parts.insert(0,
                "[MODE: NORMAL CHAT — D&D MODE IS OFF]\n"
                "You are a helpful AI assistant. You are NOT acting as a Dungeon Master.\n"
                "Ignore all D&D campaign state, character sheets, scene data, and DM "
                "instructions that may appear below. Do not call any D&D tools.\n"
                "Respond normally to whatever the user says.\n"
                "If the user says 'game on' or 'start game', D&D mode will activate."
            )
            return  # Skip all D&D injection when mode is off
    except Exception:
        pass

    # ── Commit gate correction injection ────────────────────────────────────
    # If pre_tts blocked TTS, inject the mandatory correction prompt.
    # Sets correction_active so post_llm knows to clear flags once resolved.
    try:
        state = plugin_loader.get_plugin_state("dnd-scaffold")
        if state.get("tts_blocked", False):
            correction_prompt = state.get("correction_prompt", "")
            if correction_prompt:
                event.context_parts.insert(1, correction_prompt)
                event.context_parts.insert(2,
                    "You must resolve all pending violations before continuing. "
                    "Call the missing state-change tools NOW to synchronize game state."
                )
            # Mark correction as active — post_llm will clear flags once resolved
            state.save("correction_active", True)
            state.save("tts_blocked", False)
    except Exception:
        pass

    # ── Conditions ────────────────────────────────────────────────────────────
    characters = _get_all_characters()
    afflicted = []
    if characters:
        for char in characters:
            conditions = char.get("conditions", [])
            if conditions:
                name = char.get("name", "Unknown")
                afflicted.append((name, conditions))

    in_combat = _is_combat_active()

    if afflicted:
        if in_combat:
            lines = ["⚠️ ACTIVE CONDITIONS — APPLY THESE MECHANICS NOW:"]
            for name, conditions in afflicted:
                lines.append(f"\n  {name.upper()}:")
                for cond in conditions:
                    effect = CONDITION_EFFECTS.get(cond.lower(), "see rules reference")
                    lines.append(f"    • {cond.upper()}: {effect}")
            lines.append("\nDo NOT skip or forget these modifiers. Check before every roll.")
            event.context_parts.append("\n".join(lines))
        else:
            summaries = []
            for name, conditions in afflicted:
                readable = [c.replace("_", " ") for c in conditions]
                summaries.append(f"{name} [{', '.join(readable)}]")
            event.context_parts.append(
                f"⚠️ Ongoing conditions: {'; '.join(summaries)}. "
                f"These persist until cured or the condition expires."
            )

    # ── Inspiration ──────────────────────────────────────────────────────────
    awards = _get_inspiration_state()
    if awards:
        names = [a.get("character_name", "?") for a in awards]
        reasons = [a.get("reason", "unspecified") for a in awards]
        event.context_parts.append(
            f"💫 ACTIVE INSPIRATION: {', '.join(names)}. "
            f"Reasons: {'; '.join(reasons)}. "
            f"Inspiration grants advantage on ONE roll — use it wisely."
        )

    # ── Travel state ──────────────────────────────────────────────────────────
    travel = _get_travel_state()
    if travel:
        pace = travel.get("pace", "normal")
        distance = travel.get("distance_traveled", 0)
        destination = travel.get("destination", "unknown")
        event.context_parts.append(
            f"🗺️ Travel: {distance} miles traveled toward {destination} at {pace} pace."
        )

    # ── High-urgency threads ───────────────────────────────────────────────────
    urgent_threads = _get_high_urgency_threads()
    if urgent_threads:
        event.context_parts.append(
            f"⚡ URGENT THREADS: {'; '.join(urgent_threads)}. "
            f"Address these promptly — failure may have consequences."
        )

    # ── State synchronization cross-check ─────────────────────────────────────
    try:
        state = _aud_get_state()
    except Exception:
        state = None

    if state and _aud_is_dnd_active():
        current_turn = _aud_get_turn_count(state)
        check_turn = state.get("pending_check_turn", -1)
        expected = state.get("pending_expected_calls", [])

        if current_turn > 0 and expected and check_turn == current_turn - 1:
            recent_calls = _aud_get_recent_tool_calls(state, count=15)
            actual_tools = {entry.get("fn", "") for entry in recent_calls}

            missing = []
            for exp in expected:
                tool = exp["tool"]
                if tool not in actual_tools:
                    missing.append(exp)

            if missing:
                warning_lines = [
                    "\n\n⚠️ **STATE SYNCHRONIZATION WARNING**",
                    "Your previous response narrated events that should have been recorded.",
                    "Checking expected tool calls against actual calls made...\n",
                ]

                by_category = {}
                for m in missing:
                    cat = m.get("category", "unknown")
                    by_category.setdefault(cat, []).append(m)

                for cat, items in by_category.items():
                    if cat == "item_acquire":
                        items_list = ", ".join(f"'{i.get('item', '?')}'" for i in items[:3])
                        warning_lines.append(f"  • Item(s) acquired but not recorded: {items_list} → call character_add_item")
                    elif cat == "gold":
                        total = sum(i.get("quantity", 0) for i in items)
                        warning_lines.append(f"  • Gold awarded ({total} gp) but not recorded → call character_add_item for gold")
                    elif cat == "item_loss":
                        warning_lines.append(f"  • Item(s) lost/disposed but not recorded → call character_remove_item")
                    elif cat == "hp_damage":
                        chars = list(set(i.get("character", "?") for i in items[:3]))
                        warning_lines.append(f"  • Damage to {', '.join(chars)} but not recorded → call character_damage")
                    elif cat == "hp_heal":
                        warning_lines.append(f"  • Healing described but not recorded → call character_heal")
                    elif cat == "condition":
                        conds = list(set(i.get("condition", "?") for i in items[:3]))
                        warning_lines.append(f"  • Condition(s) applied ({', '.join(conds)}) but not recorded → call character_set_condition")
                    elif cat == "spell_cast":
                        warning_lines.append(f"  • Spell(s) cast but spell slot(s) not expended → call character_use_spell_slot")
                    elif cat == "resource":
                        warning_lines.append(f"  • Class resource(s) used but not recorded → call resource_use")
                    elif cat == "xp":
                        xp_total = sum(i.get("xp", 0) for i in items)
                        warning_lines.append(f"  • {xp_total} XP awarded but not recorded → call xp_add")
                    else:
                        warning_lines.append(f"  • {cat}: expected tool not called → call {items[0].get('tool', '?')}")

                warning_lines.extend([
                    "",
                    "**Rule:** Narrating an event is NOT the same as recording it.",
                    "Call the missing tools NOW to synchronize game state.",
                    "State must match narrative — no exceptions.\n",
                ])

                event.context_parts.append("\n".join(warning_lines))

            # Clear pending
            state.save("pending_expected_calls", [])
            state.save("pending_check_turn", -1)