"""
dnd-facts — Prompt Inject Hook

Stamps all established world facts into every system prompt.
Grouped by category for readability.
Fires at priority 30 — before campaign context (40) so facts
appear near the top of the injected block.
"""


def prompt_inject(event):
    try:
        from core.plugin_loader import plugin_loader

        # Check if D&D mode is active before injecting facts
        dnd_active = False
        try:
            toggle_state = plugin_loader.get_plugin_state("dnd-toggle")
            if toggle_state:
                dnd_active = toggle_state.get("dnd_active", False)
        except Exception:
            pass  # dnd-toggle not installed

        if not dnd_active:
            return

        state = plugin_loader.get_plugin_state("dnd-facts")
        facts = state.get("facts") or {}

        if not facts:
            return  # Nothing to inject yet

        # Group by category
        by_cat = {}
        for key, data in facts.items():
            cat = data.get("category", "general")
            by_cat.setdefault(cat, []).append((key, data.get("value", "")))

        # Order categories for readability
        CAT_ORDER = ["locations", "npcs", "secrets", "clues", "promises", "items", "lore", "general"]
        ordered_cats = sorted(by_cat.keys(), key=lambda c: CAT_ORDER.index(c) if c in CAT_ORDER else 99)

        lines = ["[ESTABLISHED FACTS — NEVER CONTRADICT THESE]"]
        for cat in ordered_cats:
            lines.append(f"  {cat.upper()}:")
            for key, value in sorted(by_cat[cat]):
                lines.append(f"    • {key}: {value}")

        event.context_parts.append("\n".join(lines))

    except Exception:
        pass
