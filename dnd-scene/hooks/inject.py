"""
dnd-scene v2 — Prompt Inject Hook

Injects scene state into every prompt.
For KNOWN locations: injects the saved permanent layout.
For NEW locations: prompts Remmi to define and save it.

The key line Remmi reads:
  "SAVED LAYOUT (do not change this):"
  followed by the exact description that was saved on first visit.

This means returning to the Rusty Flagon always shows:
  "bar on north wall, boar head, kitchen door behind bar..."
regardless of how many sessions have passed.
"""


def prompt_inject(event):
    try:
        from core.plugin_loader import plugin_loader

        # Check if D&D mode is active before injecting scene
        dnd_active = False
        try:
            toggle_state = plugin_loader.get_plugin_state("dnd-toggle")
            if toggle_state:
                dnd_active = toggle_state.get("dnd_active", False)
        except Exception:
            pass  # dnd-toggle not installed

        if not dnd_active:
            return

        state   = plugin_loader.get_plugin_state("dnd-scene")
        data    = state.get("scene") or {}
        current = data.get("current", {})
        library = data.get("library", {})

        if not current:
            event.context_parts.append(
                "[SCENE] No location set. Call scene_move() when the party arrives somewhere."
            )
            return

        name   = current.get("name", "Unknown")
        key    = name.strip().lower()
        is_new = current.get("is_new", True)
        saved  = library.get(key, {})

        lines = ["[CURRENT SCENE]"]
        lines.append(f"  Location: {name}")

        time     = current.get("time", "")
        lighting = current.get("lighting") or saved.get("lighting_default", "")
        mood     = current.get("mood", "")

        if time:     lines.append(f"  Time: {time}")
        if lighting: lines.append(f"  Lighting: {lighting}")
        if mood:     lines.append(f"  Mood: {mood}")

        if is_new:
            lines.append("  ⚠️  NEW LOCATION — not visited before.")
            lines.append("  Describe it now, then call scene_set() to save the layout permanently.")
        else:
            visits = saved.get("visit_count", 1)
            lines.append(f"  (Known location — visited {visits} time{'s' if visits != 1 else ''})")
            if saved.get("description"):
                lines.append(f"  SAVED LAYOUT (do not change this — it is established canon):")
                lines.append(f"    {saved['description']}")
            if saved.get("notes"):
                lines.append(f"  Notes: {saved['notes']}")
            if saved.get("change_log"):
                lines.append(f"  Changes: {' | '.join(saved['change_log'][-2:])}")

        present = current.get("present", [])
        lines.append(f"  Present now: {', '.join(present) if present else '(nobody)'}")

        if current.get("visit_notes"):
            lines.append(f"  This visit: {current['visit_notes']}")

        lines.append(
            "  scene_move() loads saved layout | scene_update() changes this visit only | "
            "scene_update_location() changes the room permanently"
        )

        event.context_parts.append("\n".join(lines))

    except Exception:
        pass
