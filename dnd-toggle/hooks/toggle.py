"""
dnd-toggle — pre_chat hook

Listens for trigger phrases and flips D&D mode on or off.
Bypasses the LLM entirely for the toggle itself — instant response.

TRIGGER PHRASES:
  ON:  "game on", "start game", "dnd on", "d&d on", "dm mode on",
       "remmi on", "start session", "begin session"
  OFF: "game off", "stop game", "dnd off", "d&d off", "dm mode off",
       "remmi off", "end session", "pause game"

When OFF:
  - prompt_inject injects a hard instruction telling the model to
    ignore all D&D tools and act as a normal assistant
  - All other D&D plugin prompt_inject hooks still fire, but the
    override instruction at the top of context overrides them

When ON:
  - prompt_inject injects nothing (all other D&D plugins run normally)
  - Remmi persona and tools are fully active
"""

ON_PHRASES = {
    "game on", "start game", "dnd on", "d&d on", "dm mode on",
    "remmi on", "start session", "begin session", "start dnd",
    "begin dnd", "play dnd", "play d&d"
}

OFF_PHRASES = {
    "game off", "stop game", "dnd off", "d&d off", "dm mode off",
    "remmi off", "end session", "pause game", "stop dnd",
    "end dnd", "exit dnd", "exit game", "leave game"
}


def _get_state():
    from core.plugin_loader import plugin_loader
    return plugin_loader.get_plugin_state("dnd-toggle")


def pre_chat(event):
    text = (event.input or "").strip().lower()

    # Strip punctuation for matching
    clean = text.rstrip("!.,?").strip()

    if clean in ON_PHRASES:
        _get_state().save("dnd_active", True)
        event.skip_llm = True
        event.ephemeral = True
        event.response = (
            "⚔️ Game on. Remmi is active — all D&D tools enabled.\n"
            "I'll run your campaign from here. What would you like to do?"
        )
        event.stop_propagation = True
        return

    if clean in OFF_PHRASES:
        _get_state().save("dnd_active", False)
        event.skip_llm = True
        event.ephemeral = True
        event.response = (
            "🔇 Game off. D&D mode paused — back to normal chat.\n"
            "Say 'game on' whenever you're ready to resume."
        )
        event.stop_propagation = True
        return
