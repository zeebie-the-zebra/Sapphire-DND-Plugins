"""
dnd-levelup — prompt_inject hook

Injects a brief XP status block each turn.
If anyone is ready to level up, puts a loud flag at the top so Remmi
can't miss it and immediately calls levelup_guide.
"""


def prompt_inject(event):
    try:
        from core.plugin_loader import plugin_loader

        lv_state  = plugin_loader.get_plugin_state("dnd-levelup")
        xp_data   = lv_state.get("xp_data") or {}
        char_state = plugin_loader.get_plugin_state("dnd-characters")
        chars     = char_state.get("characters") or {}

        if not chars or not xp_data:
            return

        ready = []
        for key, char in chars.items():
            data    = xp_data.get(key, {})
            xp      = data.get("xp", 0)
            level   = 1
            for lvl, threshold in sorted({
                1:0, 2:300, 3:900, 4:2700, 5:6500, 6:14000, 7:23000, 8:34000,
                9:48000, 10:64000, 11:85000, 12:100000, 13:120000, 14:140000,
                15:165000, 16:195000, 17:225000, 18:265000, 19:305000, 20:355000
            }.items()):
                if xp >= threshold:
                    level = lvl
            next_threshold = {
                1:300,2:900,3:2700,4:6500,5:14000,6:23000,7:34000,8:48000,
                9:64000,10:85000,11:100000,12:120000,13:140000,14:165000,
                15:195000,16:225000,17:265000,18:305000,19:355000
            }.get(level)
            if next_threshold and xp >= next_threshold:
                ready.append((key, level + 1))

        if ready:
            names = ", ".join(f"{n} (→ L{lv})" for n, lv in ready)
            event.context_parts.append(
                f"⬆️ LEVEL UP READY: {names}\n"
                f"Call levelup_guide() for each character listed above BEFORE continuing the story."
            )

    except Exception:
        pass
