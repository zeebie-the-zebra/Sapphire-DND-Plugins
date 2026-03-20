"""
dnd-homebrew — prompt_inject hook

Injects a brief summary of the campaign's homebrew library into context.
Only fires when there are actual homebrew entries to surface.
"""


def prompt_inject(event):
    try:
        from core.plugin_loader import plugin_loader

        campaign_state = plugin_loader.get_plugin_state("dnd-campaign")
        campaign_id = campaign_state.get("active_campaign", "default")

        homebrew_state = plugin_loader.get_plugin_state("dnd-homebrew")
        data = homebrew_state.get(f"homebrew:{campaign_id}") or {}

        if not data:
            return  # Nothing to inject

        monsters = [(eid, e) for eid, e in data.items() if e.get("type") == "monster"]
        items = [(eid, e) for eid, e in data.items() if e.get("type") == "item"]
        spells = [(eid, e) for eid, e in data.items() if e.get("type") == "spell"]

        parts = []
        if monsters:
            names = ", ".join(e.get("name", "??") for _, e in monsters[:10])
            if len(monsters) > 10:
                names += f" (+{len(monsters) - 10} more)"
            parts.append(f"Homebrew Monsters ({len(monsters)}): {names}")
        if items:
            names = ", ".join(e.get("name", "??") for _, e in items[:10])
            if len(items) > 10:
                names += f" (+{len(items) - 10} more)"
            parts.append(f"Homebrew Items ({len(items)}): {names}")
        if spells:
            names = ", ".join(e.get("name", "??") for _, e in spells[:10])
            if len(spells) > 10:
                names += f" (+{len(spells) - 10} more)"
            parts.append(f"Homebrew Spells ({len(spells)}): {names}")

        if not parts:
            return

        context = (
            "[HOME BREW LIBRARY]\n"
            + "\n".join(parts)
            + "\n\nUse the homebrew_get tool to retrieve full details on any entry above."
        )
        event.context_parts.append(context)

    except Exception:
        pass
