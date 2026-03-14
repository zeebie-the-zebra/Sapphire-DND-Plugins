"""
dnd-threads — Prompt Inject Hook

Injects open narrative threads into every system prompt.
Only injects open threads — resolved ones are archived.
High urgency threads are listed first and flagged clearly.

Fires at priority 38 — just before campaign context (40).
"""


URGENCY_EMOJI = {"high": "🔴", "medium": "🟡", "low": "🟢"}
TYPE_EMOJI    = {
    "consequence": "⚡",
    "promise":     "🤝",
    "clue":        "🔍",
    "threat":      "⚠️",
    "opportunity": "✨",
    "revelation":  "💡",
}
URGENCY_ORDER = {"high": 0, "medium": 1, "low": 2}


def prompt_inject(event):
    try:
        from core.plugin_loader import plugin_loader

        # Check if D&D mode is active before injecting threads
        dnd_active = False
        try:
            toggle_state = plugin_loader.get_plugin_state("dnd-toggle")
            if toggle_state:
                dnd_active = toggle_state.get("dnd_active", False)
        except Exception:
            pass  # dnd-toggle not installed

        if not dnd_active:
            return

        state = plugin_loader.get_plugin_state("dnd-threads")
        data  = state.get("threads") or {}
        items = data.get("items", [])

        open_threads = [t for t in items if t.get("status") == "open"]

        if not open_threads:
            return  # Nothing to inject

        # Sort: high first
        open_threads = sorted(
            open_threads,
            key=lambda t: (URGENCY_ORDER.get(t.get("urgency", "medium"), 1), t.get("id", 0))
        )

        high   = [t for t in open_threads if t.get("urgency") == "high"]
        medium = [t for t in open_threads if t.get("urgency") == "medium"]
        low    = [t for t in open_threads if t.get("urgency") == "low"]

        lines = [f"[OPEN NARRATIVE THREADS — {len(open_threads)} unresolved]"]

        if high:
            lines.append("  ⚠️  SURFACE SOON (high urgency):")
            for t in high:
                emoji = TYPE_EMOJI.get(t.get("type", ""), "•")
                tag   = f" [{t['tag']}]" if t.get("tag") else ""
                lines.append(f"    #{t['id']} {emoji}{tag} {t['description']}")

        if medium:
            lines.append("  MEDIUM:")
            for t in medium:
                emoji = TYPE_EMOJI.get(t.get("type", ""), "•")
                lines.append(f"    #{t['id']} {emoji} {t['description']}")

        if low:
            lines.append("  LOW (background):")
            for t in low:
                emoji = TYPE_EMOJI.get(t.get("type", ""), "•")
                lines.append(f"    #{t['id']} {emoji} {t['description']}")

        lines.append(
            "  When a thread plays out or is resolved, call thread_resolve(thread_id). "
            "Weave high-urgency threads into the current scene naturally."
        )

        event.context_parts.append("\n".join(lines))

    except Exception:
        pass
