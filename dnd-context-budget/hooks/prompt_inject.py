"""
dnd-context-budget — prompt_inject hook

Runs at priority 950 (after all other D&D plugins have injected).
Measures total injected context size and trims from the bottom of the
context_parts list if over budget — lowest-priority items append last,
so trimming from the tail removes the least critical context first.

Priority injection order assumed (highest → lowest):
  1. Combat state / active threads (dnd-encounters, dnd-threads — high urgency)
  2. Character state / conditions (dnd-characters, dnd-resources)
  3. Scene / location (dnd-scene, dnd-time)
  4. Campaign / quests (dnd-campaign)
  5. Recap / facts / NPCs (dnd-recap, dnd-facts, dnd-npcs)
  6. Weather / misc flavour (dnd-weather)

Items toward the end of context_parts are trimmed first.
"""

from core.plugin_loader import plugin_loader
import logging

logger = logging.getLogger("dnd-context-budget")

# Absolute floor — never trim below this many context_parts
MIN_PARTS = 3


def prompt_inject(event):
    config = event.config
    state = plugin_loader.get_plugin_state("dnd-context-budget")

    # Read settings — fall back to defaults if not configured
    try:
        char_budget = int(getattr(config, "dnd_context_budget_char_budget", 6000))
        warn_at_percent = int(getattr(config, "dnd_context_budget_warn_at_percent", 80))
    except Exception:
        char_budget = 6000
        warn_at_percent = 80

    parts = event.context_parts
    if not parts:
        return

    total_chars = sum(len(p) for p in parts)
    warn_threshold = int(char_budget * (warn_at_percent / 100))

    if total_chars <= warn_threshold:
        # Well within budget — nothing to do
        state.save("last_total_chars", total_chars)
        state.save("last_trimmed", 0)
        return

    if total_chars <= char_budget:
        # Over warn threshold but under hard limit — log only
        logger.warning(
            f"[context-budget] Injected context at {total_chars} chars "
            f"({round(total_chars/char_budget*100)}% of {char_budget} budget). "
            f"Consider reducing plugin injection verbosity."
        )
        state.save("last_total_chars", total_chars)
        state.save("last_trimmed", 0)
        return

    # Over hard budget — trim from the tail until within budget
    trimmed_count = 0
    trimmed_chars = 0

    while sum(len(p) for p in parts) > char_budget and len(parts) > MIN_PARTS:
        removed = parts.pop()
        trimmed_count += 1
        trimmed_chars += len(removed)

    final_total = sum(len(p) for p in parts)

    logger.warning(
        f"[context-budget] TRIMMED {trimmed_count} context section(s) "
        f"({trimmed_chars} chars removed). "
        f"Final: {final_total}/{char_budget} chars. "
        f"Increase char_budget in settings if important context is being lost."
    )

    # Append a note at the END of context so the model knows trimming occurred
    parts.append(
        f"[context-budget] ⚠️ {trimmed_count} lower-priority context section(s) were "
        f"omitted to stay within the {char_budget}-char injection budget."
    )

    state.save("last_total_chars", final_total)
    state.save("last_trimmed", trimmed_count)
    event.context_parts = parts
