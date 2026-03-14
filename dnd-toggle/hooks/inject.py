"""
dnd-toggle — prompt_inject hook

Priority 5 — fires FIRST, before all other D&D plugins.

When D&D mode is OFF:
  Injects a hard override at the very top of the system prompt telling
  the model to ignore the D&D tools and persona injected by other plugins.

  The other D&D hooks still fire (facts, scene, threads, campaign) but
  this override sits above them all and tells the model to disregard them.
  A well-instructed model will follow the first clear instruction it sees.

When D&D mode is ON (or never set):
  Injects nothing — all other D&D plugins run normally.
"""


def prompt_inject(event):
    try:
        from core.plugin_loader import plugin_loader

        state      = plugin_loader.get_plugin_state("dnd-toggle")
        dnd_active = state.get("dnd_active")

        # Default to OFF if never been set — user has to explicitly say "game on"
        # Change to `True` below if you want D&D mode on by default
        if dnd_active is None:
            dnd_active = False

        if not dnd_active:
            # Insert at position 0 — this must be the very first thing the model reads
            event.context_parts.insert(0,
                "[MODE: NORMAL CHAT — D&D MODE IS OFF]\n"
                "You are a helpful AI assistant. You are NOT acting as a Dungeon Master.\n"
                "Ignore all D&D campaign state, character sheets, scene data, and DM "
                "instructions that may appear below. Do not call any D&D tools.\n"
                "Respond normally to whatever the user says.\n"
                "If the user says 'game on' or 'start game', D&D mode will activate."
            )

    except Exception:
        pass
