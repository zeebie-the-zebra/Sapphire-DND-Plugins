"""
Dice Roller — D&D / tabletop RPG dice rolling tool.

Supports:
  - Standard notation: 2d6, 1d20, 4d4+3, 1d8-1
  - Named dice: d4, d6, d8, d10, d12, d20, d100 (percentile)
  - Advantage / disadvantage (roll 2d20, keep highest/lowest)
  - Multiple separate rolls in one call (e.g. "1d20 for attack, 2d6+3 for damage")
  - Roll history tracking via plugin state
"""

import random
import re
from datetime import datetime

ENABLED = True
EMOJI = '🎲'
AVAILABLE_FUNCTIONS = ['dice_roll', 'dice_history']

TOOLS = [
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "dice_roll",
            "description": (
                "Roll dice for D&D or any tabletop RPG. Use whenever the user asks to roll dice, "
                "make an attack roll, check a skill, roll for damage, or any game action involving "
                "randomness. Supports standard dice notation like '1d20', '2d6+3', '4d4-1'. "
                "Also supports multiple dice groups like '2d6+2d6+4' for combined rolls like sneak attack. "
                "Supports advantage/disadvantage for D&D 5e d20 rolls. "
                "Can handle multiple rolls at once (e.g. attack roll + damage roll)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "rolls": {
                        "type": "array",
                        "description": (
                            "List of dice rolls to perform. Each entry is an object with 'notation' "
                            "(e.g. '2d6+3') and optional 'label' (e.g. 'Fireball damage'). "
                            "Always include at least one entry."
                        ),
                        "items": {
                            "type": "object",
                            "properties": {
                                "notation": {
                                    "type": "string",
                                    "description": "Dice notation, e.g. '1d20', '2d6+3', '1d8-1', 'd100'"
                                },
                                "label": {
                                    "type": "string",
                                    "description": "Optional label for this roll, e.g. 'Attack roll', 'Stealth check'"
                                },
                                "advantage": {
                                    "type": "string",
                                    "description": "For d20 rolls: 'advantage' (roll twice, take higher) or 'disadvantage' (roll twice, take lower). Omit for normal rolls."
                                }
                            },
                            "required": ["notation"]
                        }
                    }
                },
                "required": ["rolls"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "dice_history",
            "description": (
                "Show the recent dice roll history for this session. Use when the user asks "
                "'what did I roll earlier', 'show my last rolls', or similar recall questions."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "How many recent rolls to return (default 10, max 50)"
                    }
                },
                "required": []
            }
        }
    }
]


# ── Dice rolling logic ─────────────────────────────────────────────────────────

VALID_SIDES = {4, 6, 8, 10, 12, 20, 100}

# Matches a single dice group: "2d6", "d6", "2d6+3", "d8-1"
_DICE_GROUP_RE = re.compile(
    r'^(\d+)?d(\d+)([+-]\d+)?$',
    re.IGNORECASE
)


def _parse_notation(notation: str):
    """
    Parse dice notation like '2d6+3', '1d20', 'd8', 'd100-1'.
    Also supports multiple dice groups: '2d6+2d6+4', '1d8+1d6+3'.
    Returns (total_count, total_sides, total_modifier, breakdown) or raises ValueError.
    """
    notation = notation.strip().lower().replace(' ', '')

    # First try single-group pattern
    m = _DICE_GROUP_RE.match(notation)
    if m:
        count   = int(m.group(1)) if m.group(1) else 1
        sides   = int(m.group(2))
        mod_str = m.group(3)
        modifier = int(mod_str) if mod_str else 0

        _validate_dice(count, sides, modifier)
        return count, sides, modifier, None

    # Multi-group: split by '+' and parse each part
    # Handle both positive and negative modifiers
    # "2d6+2d6+4" → ["2d6", "2d6", "4"]
    # "1d8+1d6+3" → ["1d8", "1d6", "3"]
    # "2d6+2d6-1" → ["2d6", "2d6-1"]
    parts = notation.split('+')

    if len(parts) > 1:
        total_count = 0
        total_sides = 0
        flat_modifier = 0  # Track flat modifiers separately from dice group modifiers
        breakdown = []

        for part in parts:
            part = part.strip()
            if not part:
                continue

            # Check if this part contains dice notation
            if 'd' in part:
                m = _DICE_GROUP_RE.match(part)
                if not m:
                    raise ValueError(f"Invalid dice notation: '{part}' in '{notation}'")

                count   = int(m.group(1)) if m.group(1) else 1
                sides   = int(m.group(2))
                mod_str = m.group(3)
                modifier = int(mod_str) if mod_str else 0

                _validate_dice(count, sides, modifier)

                if total_sides == 0:
                    total_sides = sides
                total_count += count
                flat_modifier += modifier

                breakdown.append({
                    'notation': part,
                    'count': count,
                    'sides': sides,
                    'modifier': modifier
                })
            else:
                # It's just a number (flat modifier)
                try:
                    flat_modifier += int(part)
                except ValueError:
                    raise ValueError(f"Invalid number in dice notation: '{part}'")

        return total_count, total_sides, flat_modifier, breakdown

    # If we get here, it's invalid
    raise ValueError(f"Invalid dice notation: '{notation}'. Use format like '2d6+3' or '1d20'.")


def _validate_dice(count: int, sides: int, modifier: int):
    """Validate dice parameters."""
    if count < 1 or count > 100:
        raise ValueError(f"Dice count must be 1–100, got {count}")
    if sides not in VALID_SIDES:
        raise ValueError(
            f"d{sides} is not a standard die. Valid: d4, d6, d8, d10, d12, d20, d100"
        )
    if modifier < -100 or modifier > 100:
        raise ValueError(f"Modifier must be between -100 and +100")


def _roll_dice(count: int, sides: int):
    """Roll `count` dice with `sides` faces. Returns list of individual results."""
    return [random.randint(1, sides) for _ in range(count)]


def _format_roll_result(notation: str, label: str | None, advantage: str | None) -> dict:
    """
    Perform a single roll and return a structured result dict.
    Handles advantage/disadvantage for d20 rolls.
    Handles multiple dice groups (e.g., 2d6+2d6+4).
    """
    count, sides, modifier, breakdown = _parse_notation(notation)

    adv = (advantage or "").lower().strip()
    use_advantage    = adv == "advantage"
    use_disadvantage = adv == "disadvantage"

    # Handle multi-group rolls (e.g., 2d6+2d6+4)
    if breakdown:
        return _handle_multi_group_roll(notation, label, breakdown, modifier)

    # Single dice group - original logic
    if (use_advantage or use_disadvantage) and sides == 20 and count == 1:
        # Roll two d20s, keep highest or lowest
        roll_a = _roll_dice(1, 20)[0]
        roll_b = _roll_dice(1, 20)[0]
        chosen = max(roll_a, roll_b) if use_advantage else min(roll_a, roll_b)
        total  = chosen + modifier

        adv_label = "advantage" if use_advantage else "disadvantage"
        dice_str  = f"[{roll_a}, {roll_b}] → kept {chosen} ({adv_label})"
        if modifier != 0:
            sign = "+" if modifier > 0 else ""
            dice_str += f" {sign}{modifier}"

        return {
            "label":    label or notation,
            "notation": notation,
            "rolls":    [roll_a, roll_b],
            "kept":     chosen,
            "modifier": modifier,
            "total":    total,
            "detail":   dice_str,
            "is_nat20": chosen == 20 and sides == 20,
            "is_nat1":  chosen == 1  and sides == 20,
        }

    else:
        rolls   = _roll_dice(count, sides)
        subtotal = sum(rolls)
        total    = subtotal + modifier

        # Build readable detail string
        if count == 1:
            dice_str = str(rolls[0])
        else:
            dice_str = f"[{', '.join(str(r) for r in rolls)}] = {subtotal}"

        if modifier != 0:
            sign = "+" if modifier > 0 else ""
            dice_str += f" {sign}{modifier}"

        return {
            "label":    label or notation,
            "notation": notation,
            "rolls":    rolls,
            "modifier": modifier,
            "total":    total,
            "detail":   dice_str,
            "is_nat20": count == 1 and sides == 20 and rolls[0] == 20,
            "is_nat1":  count == 1 and sides == 20 and rolls[0] == 1,
        }


def _handle_multi_group_roll(notation: str, label: str | None, breakdown: list, total_modifier: int) -> dict:
    """
    Handle multiple dice groups in one notation (e.g., 2d6+2d6+4).
    breakdown contains the dice groups, total_modifier contains flat modifiers.
    """
    all_rolls = []
    dice_subtotal = 0
    detail_parts = []

    for group in breakdown:
        count = group['count']
        sides = group['sides']
        mod = group['modifier']

        rolls = _roll_dice(count, sides)
        all_rolls.extend(rolls)

        group_sum = sum(rolls)
        dice_subtotal += group_sum + mod  # Include each group's own modifier

        if count == 1:
            part_str = str(rolls[0])
        else:
            part_str = f"[{', '.join(str(r) for r in rolls)}]"

        if mod != 0:
            sign = "+" if mod > 0 else ""
            part_str += f" {sign}{mod}"

        detail_parts.append(f"{group['notation']}={part_str}")

    # Add flat modifiers that weren't part of any dice group
    # Only show flat modifier separately if it wasn't already included in breakdown
    detail_str = " + ".join(detail_parts)
    total = dice_subtotal + total_modifier

    # Only append flat modifier if it's separate from breakdown
    # (total_modifier already includes modifiers from breakdown)
    if total_modifier != 0 and abs(total_modifier) <= 100:
        # Check if we need to show it - but actually the breakdown already has all modifiers
        # So we don't need to show total_modifier separately
        pass

    return {
        "label":    label or notation,
        "notation": notation,
        "rolls":    all_rolls,
        "modifier": total_modifier,
        "total":    total,
        "detail":   detail_str,
        "is_nat20": False,
        "is_nat1":  False,
    }


def _result_to_text(r: dict) -> str:
    """Format a single roll result as a readable string."""
    label = r["label"]
    detail = r["detail"]
    total  = r["total"]

    line = f"**{label}**: {detail} = **{total}**"

    if r.get("is_nat20"):
        line += " 🎯 *Natural 20!*"
    elif r.get("is_nat1"):
        line += " 💀 *Critical Fail (Nat 1)*"

    return line


# ── History helpers ────────────────────────────────────────────────────────────

def _load_history():
    try:
        from core.plugin_loader import plugin_loader
        state = plugin_loader.get_plugin_state("dnd-dice-roller")
        return state.get("history") or []
    except Exception:
        return []


def _save_history(history: list):
    try:
        from core.plugin_loader import plugin_loader
        state = plugin_loader.get_plugin_state("dnd-dice-roller")
        # Keep last 50 entries
        state.save("history", history[-50:])
    except Exception:
        pass


# ── execute() dispatcher ───────────────────────────────────────────────────────

def execute(function_name, arguments, config):
    if function_name == "dice_roll":
        rolls_input = arguments.get("rolls", [])

        if not rolls_input:
            return "No dice specified. Provide at least one roll.", False

        results     = []
        errors      = []
        history     = _load_history()
        timestamp   = datetime.now().strftime("%H:%M:%S")

        for entry in rolls_input:
            notation   = entry.get("notation", "").strip()
            label      = entry.get("label", None)
            advantage  = entry.get("advantage", None)

            if not notation:
                errors.append("Empty notation skipped.")
                continue

            try:
                result = _format_roll_result(notation, label, advantage)
                results.append(result)

                history.append({
                    "time":     timestamp,
                    "label":    result["label"],
                    "notation": notation,
                    "total":    result["total"],
                    "detail":   result["detail"],
                })
            except ValueError as e:
                errors.append(str(e))

        _save_history(history)

        if not results and errors:
            return "Dice roll failed:\n" + "\n".join(errors), False

        lines = [_result_to_text(r) for r in results]

        if errors:
            lines.append("\n⚠️ Some rolls were skipped: " + "; ".join(errors))

        return "\n".join(lines), True

    elif function_name == "dice_history":
        limit   = min(int(arguments.get("limit", 10)), 50)
        history = _load_history()

        if not history:
            return "No dice rolls recorded yet this session.", True

        recent = history[-limit:][::-1]  # newest first
        lines  = ["**Recent Rolls** (newest first):"]
        for entry in recent:
            lines.append(
                f"• [{entry['time']}] **{entry['label']}** ({entry['notation']}) → **{entry['total']}**"
            )

        return "\n".join(lines), True

    return f"Unknown function: {function_name}", False
