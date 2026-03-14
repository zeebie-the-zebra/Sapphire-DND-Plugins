"""
dnd-recap — Prompt Inject Hook

Injects the session recap at the VERY TOP of every system prompt.
Priority 25 — fires before everything else.

This is the core of the memory fix:
  - Compressed summaries sit at the top of context (highest attention)
  - They replace the raw history that would otherwise drift into the middle
  - The model reads dense facts, not a wall of dialogue it will ignore

The injected block looks like:

  [SESSION HISTORY — READ THIS FIRST]
  PREVIOUS SESSION: The party escaped the collapsing mine and made
  it to Saltmarsh. They learned a noble house is funding the bandits.

  EARLIER THIS SESSION: They bribed dock guard Cobb for info on ship
  schedules. Sylva found a coded letter. Aldric questioned the
  harbormaster who was nervous and evasive.

  RECENT EVENTS:
  • The party decoded the letter — it implicates Duke Harrowmere
  • Brother Tomm cast Detect Evil near the docks — got a strong ping
  • The party is now heading to The Rusty Flagon to regroup
"""


def prompt_inject(event):
    try:
        from core.plugin_loader import plugin_loader

        # Check if D&D mode is active before injecting recap
        dnd_active = False
        try:
            toggle_state = plugin_loader.get_plugin_state("dnd-toggle")
            if toggle_state:
                dnd_active = toggle_state.get("dnd_active", False)
        except Exception:
            pass  # dnd-toggle not installed

        # Skip injection if D&D mode is off
        if not dnd_active:
            return

        state = plugin_loader.get_plugin_state("dnd-recap")
        data  = state.get("recap") or {}

        last_session = data.get("last_session")
        summaries    = data.get("summaries", [])
        raw_events   = data.get("raw_events", [])

        # Nothing to inject yet
        if not last_session and not summaries and not raw_events:
            return

        lines = ["[SESSION HISTORY — READ THIS FIRST]"]

        if last_session:
            lines.append(f"PREVIOUS SESSION: {last_session}")

        if summaries:
            lines.append("")
            if len(summaries) == 1:
                lines.append(f"EARLIER THIS SESSION: {summaries[0]}")
            else:
                lines.append("EARLIER THIS SESSION:")
                for s in summaries:
                    lines.append(f"  {s}")

        if raw_events:
            lines.append("")
            lines.append("RECENT EVENTS:")
            for e in raw_events:
                lines.append(f"  • {e}")

        event.context_parts.insert(0, "\n".join(lines))
        # Insert at position 0 so it appears at the very top

    except Exception:
        pass
