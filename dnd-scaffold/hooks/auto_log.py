"""
dnd-scaffold/hooks/auto_log.py — merged from dnd-recap + dnd-logger + state_auditor post_chat

post_chat: captures game events, stores in recap log, and detects expected tool calls.
"""

import re
from datetime import datetime


# ── State auditor patterns (for _detect_expected_calls) ────────────────────────

AUD_ITEM_ACQUIRE_VERBS = {"takes", "finds", "picks up", "receives", "gets", "grabs", "loots", "obtains", "acquires", "picks up"}
AUD_ITEM_LOSS_VERBS = {"sells", "loses", "drops", "destroys", "consumes", "gives away", "stolen", "parts with"}
AUD_HP_DAMAGE_WORDS = {"takes", "damage", "hit", "wounded", "strikes", "deals", "suffers"}
AUD_HP_HEAL_WORDS = {"heals", "recovers", "restores", "cures"}
AUD_CONDITION_WORDS = {"poisoned", "blinded", "stunned", "paralyzed", "charmed", "frightened", "unconscious", "incapacitated", "restrained", "grappled", "invisible", "petrified", "prone"}
AUD_SPELL_CAST_WORDS = {"casts", "cast", "spell"}
AUD_RESOURCE_WORDS = {"rage", "ki", "wild shape", "channel divinity", "second wind", "action surge", "lay on hands", "sorcery points", "mystic arcanum", "inspiration"}
AUD_XP_WORDS = {"xp", "experience points", "experience"}


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


def _detect_expected_calls(text):
    """
    Parse narrative text and return list of expected tool calls.
    These are events narrated but not yet confirmed as tool calls.
    """
    expected = []
    text_lower = text.lower()
    words = set(text_lower.split())

    # ── Item acquisition ───────────────────────────────────────────────────────
    item_acquire_patterns = [
        r'(?:' + '|'.join(AUD_ITEM_ACQUIRE_VERBS) + r')\s+(?:a|an|the)\s+([a-z][a-z\s\-]{1,40})',
        r'(?:hands?|gives?)\s+you\s+(?:a|an|the)?\s*([a-z][a-z\s\-]{1,40})',
        r'(?:chest|room|body|loot|treasure)\s+(?:contains?|holds?|reveals?)\s+(?:a|an|the)?\s*([a-z][a-z\s\-]{1,40})',
    ]
    for pattern in item_acquire_patterns:
        for m in re.finditer(pattern, text_lower):
            item = m.group(1).strip()
            if item and len(item) > 1 and len(item) < 50:
                if item not in ("way", "hand", "handed", "it", "them", "something", "nothing", "time"):
                    expected.append({
                        "tool": "character_add_item",
                        "item": item,
                        "raw": m.group(0),
                        "category": "item_acquire",
                    })

    # ── Gold ──────────────────────────────────────────────────────────────────
    gold_patterns = [
        r'(\d+)\s*gp\b',
        r'(\d+)\s*gold\s*pieces?',
        r'(\d+)\s*pieces?\s*of\s*gold',
    ]
    for pattern in gold_patterns:
        for m in re.finditer(pattern, text_lower):
            amount = int(m.group(1))
            if 1 <= amount <= 1000000:
                expected.append({
                    "tool": "character_add_item",
                    "item": "Gold (gp)",
                    "quantity": amount,
                    "raw": m.group(0),
                    "category": "gold",
                })

    # ── Item loss/removal ─────────────────────────────────────────────────────
    for verb in AUD_ITEM_LOSS_VERBS:
        idx = text_lower.find(verb)
        if idx != -1:
            start = max(0, idx - 5)
            end = min(len(text), idx + 50)
            snippet = text_lower[start:end]
            expected.append({
                "tool": "character_remove_item",
                "verb": verb,
                "snippet": snippet,
                "raw": snippet,
                "category": "item_loss",
            })

    # ── HP damage ─────────────────────────────────────────────────────────────
    hp_damage_patterns = [
        r'([A-Z][a-z]+)\s+(?:takes?|suffers?|loses?)\s+(\d+)\s*(?:\s+damage)?',
        r'(?:deals?|dealt)\s+(\d+)\s*(?:\s+damage)?\s+(?:to|on)\s+([A-Z][a-z]+)',
        r'([A-Z][a-z]+)\s+(?:is\s+)?(?:hit|struck)\s+(?:for\s+)?(\d+)',
    ]
    for pattern in hp_damage_patterns:
        for m in re.finditer(pattern, text):
            if m.lastindex >= 2:
                char = m.group(1).strip()
                amount = m.group(2).strip()
                if char and amount and char.lower() not in ("the", "a", "an"):
                    expected.append({
                        "tool": "character_damage",
                        "character": char,
                        "amount": int(amount),
                        "raw": m.group(0),
                        "category": "hp_damage",
                    })

    # ── HP healing ────────────────────────────────────────────────────────────
    for word in AUD_HP_HEAL_WORDS:
        if word in words or word in text_lower:
            heal_match = re.search(r'([A-Z][a-z]+)\s+(?:heals?|recovers?|restores?)\s+(\d+)', text)
            if heal_match:
                char = heal_match.group(1).strip()
                amount = heal_match.group(2).strip()
                expected.append({
                    "tool": "character_heal",
                    "character": char,
                    "amount": int(amount),
                    "raw": heal_match.group(0),
                    "category": "hp_heal",
                })
            break

    # ── Conditions ───────────────────────────────────────────────────────────
    for cond in AUD_CONDITION_WORDS:
        if cond in words:
            cond_match = re.search(rf'([A-Z][a-z]+)\s+(?:is\s+)?(?:now\s+)?(?:{cond}|becomes?{cond})', text)
            if cond_match:
                char = cond_match.group(1).strip()
                expected.append({
                    "tool": "character_set_condition",
                    "character": char,
                    "condition": cond,
                    "active": True,
                    "raw": cond_match.group(0),
                    "category": "condition",
                })

    # ── Spell casting ───────────────────────────────────────────────────────
    for word in AUD_SPELL_CAST_WORDS:
        if word in words:
            spell_match = re.search(r'([A-Z][a-z]+)\s+casts?\s+(?:a\s+)?(?:(\d+)(?:st|nd|rd|th)\s+)?(?:level\s+)?([A-Za-z\s]+?)(?:\s+spell|\s+at|,|\.|!|\n|$)', text)
            if spell_match:
                char = spell_match.group(1).strip()
                level = spell_match.group(2) or "1"
                expected.append({
                    "tool": "character_use_spell_slot",
                    "character": char,
                    "level": int(level),
                    "raw": spell_match.group(0),
                    "category": "spell_cast",
                })

    # ── Resource usage ───────────────────────────────────────────────────────
    for word in AUD_RESOURCE_WORDS:
        if word in text_lower:
            resource_match = re.search(r'([A-Z][a-z]+)\s+(?:uses?|activates?|enters?|spends?)\s+(?:their?)?\s*([A-Za-z\s]+)', text)
            if resource_match:
                char = resource_match.group(1).strip()
                resource = resource_match.group(2).strip()
                expected.append({
                    "tool": "resource_use",
                    "character": char,
                    "resource": resource,
                    "raw": resource_match.group(0),
                    "category": "resource",
                })
            break

    # ── XP awards ────────────────────────────────────────────────────────────
    for word in AUD_XP_WORDS:
        if word in text_lower:
            xp_match = re.search(r'(\d+)\s*xp\b', text_lower)
            if xp_match:
                xp = int(xp_match.group(1))
                if 1 <= xp <= 1000000:
                    expected.append({
                        "tool": "xp_add",
                        "xp": xp,
                        "raw": xp_match.group(0),
                        "category": "xp",
                    })
            break

    return expected


def post_chat(event):
    """Log chat exchanges to session recap, detect expected tool calls."""
    try:
        from core.plugin_loader import plugin_loader

        # Check if D&D mode is active before logging
        dnd_active = False
        try:
            toggle_state = plugin_loader.get_plugin_state("dnd-scaffold")
            if toggle_state:
                dnd_active = toggle_state.get("dnd_active", False)
        except Exception:
            pass

        if not dnd_active:
            return

        player_msg = (event.input or "").strip()
        dm_response = (event.response or "").strip()
        if not player_msg or not dm_response:
            return

        state = plugin_loader.get_plugin_state("dnd-scaffold")

        session_log = state.get("session_log") or []
        turn_count = state.get("turn_count") or 0
        session_num = state.get("session_num") or 1

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        session_log.append({
            "turn": turn_count + 1,
            "player": player_msg[:500],
            "dm": dm_response[:1000],
            "timestamp": timestamp,
        })
        turn_count += 1

        state.save("session_log", session_log[-200:])
        state.save("turn_count", turn_count)

        # Auto-increment session number on first turn of a new day
        last_date = state.get("last_date") or ""
        today = datetime.now().strftime("%Y-%m-%d")
        if last_date and last_date != today and turn_count == 1:
            state.save("session_num", session_num + 1)
        state.save("last_date", today)

        # ── State auditor: detect and store expected tool calls ──────────────
        if dm_response and len(dm_response) > 30:
            expected_calls = _detect_expected_calls(dm_response)
            if expected_calls:
                state.save("pending_expected_calls", expected_calls)
                state.save("pending_check_turn", turn_count)
                state.save("pending_response_preview", dm_response[:500])

    except Exception:
        pass
