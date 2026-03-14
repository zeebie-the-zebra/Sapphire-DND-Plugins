"""
dnd-resources — prompt_inject hook

Injects current resource status for all party members.
Only shows resources that are partially or fully spent so the
context block stays concise when everything is full.
Always shows empty resources as a warning.
"""


def prompt_inject(event):
    try:
        from core.plugin_loader import plugin_loader

        state = plugin_loader.get_plugin_state("dnd-resources")
        data  = state.get("resources") or {}

        if not data:
            return

        lines    = []
        warnings = []

        for name, char_data in data.items():
            resources = char_data.get("resources", [])
            spent     = []
            empty     = []

            for r in resources:
                rc = r.get("recharge", "")
                if rc in ("passive", "reaction"):
                    continue
                current = r.get("current", 0)
                maximum = r.get("max", 0)
                try:
                    if isinstance(current, int) and isinstance(maximum, int):
                        if current == 0 and maximum > 0:
                            empty.append(f"{r['name']} EMPTY")
                        elif current < maximum:
                            spent.append(f"{r['name']}: {current}/{maximum}")
                except Exception:
                    pass

            if spent or empty:
                char_line = f"  {name}:"
                if spent:
                    char_line += " " + ", ".join(spent)
                if empty:
                    warnings.append(f"  ⚠️ {name}: {', '.join(empty)}")
                    char_line += "  ⚠️ " + ", ".join(empty)
                lines.append(char_line)

        if lines:
            event.context_parts.append(
                "[CLASS RESOURCES — partially or fully spent]\n" + "\n".join(lines)
            )

    except Exception:
        pass
