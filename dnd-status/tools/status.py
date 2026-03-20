"""
dnd-status — tools

Single-call full game state aggregator. Reads from all active D&D
plugin states and produces a formatted snapshot. Use to reorient
the model after confusion, at the start of a session, or after a
long pause in play.

Reads from (best-effort, gracefully skips missing plugins):
  - dnd-characters
  - dnd-campaign
  - dnd-scene
  - dnd-time
  - dnd-encounters
  - dnd-threads
  - dnd-resources
  - dnd-weather
  - dnd-npc-relations

Supports multi-campaign: reads campaign-scoped data from plugins.
"""

from core.plugin_loader import plugin_loader
import json
import logging

logger = logging.getLogger("dnd-status")

DEFAULT_CAMPAIGN_ID = "default"


def _get_campaign_id(config=None) -> str:
    """Get current campaign ID, defaulting to 'default' for backward compatibility."""
    try:
        campaign_state = plugin_loader.get_plugin_state("dnd-campaign")
        campaign_id = campaign_state.get("active_campaign", DEFAULT_CAMPAIGN_ID)
        if campaign_id:
            return campaign_id
    except Exception:
        pass
    return DEFAULT_CAMPAIGN_ID


def _get(plugin_name: str, key: str, default=None, campaign_id: str = None):
    """Safe plugin state getter — returns default if plugin missing or key absent.
    If campaign_id is provided, tries campaign-scoped key first.
    """
    try:
        state = plugin_loader.get_plugin_state(plugin_name)
        # Try campaign-scoped key first if provided
        if campaign_id:
            scoped_key = f"{key}:{campaign_id}" if not key.startswith(f"{plugin_name}:") else key
            val = state.get(scoped_key)
            if val is not None:
                if isinstance(val, str):
                    try:
                        return json.loads(val)
                    except Exception:
                        return val
                return val
        # Fall back to global key
        val = state.get(key)
        if val is None:
            return default
        if isinstance(val, str):
            try:
                return json.loads(val)
            except Exception:
                return val
        return val
    except Exception:
        return default


def _section(title: str, lines: list) -> str:
    """Format a named section."""
    return f"\n{'─'*40}\n{title}\n" + "\n".join(f"  {l}" for l in lines)


def status_get_all(include_npcs: bool = False) -> str:
    """
    Get a full snapshot of the current game state across all D&D plugins.

    Args:
        include_npcs: If True, includes NPC/faction attitude summary from
                      dnd-npc-relations (can be verbose — off by default).

    Returns:
        Formatted full game state snapshot.
    """
    campaign_id = _get_campaign_id()

    sections = []
    sections.append("═" * 40)
    sections.append("  GAME STATE SNAPSHOT")
    sections.append("═" * 40)

    # ── CAMPAIGN ──────────────────────────────────────────────────────────────
    try:
        camp = _get("dnd-campaign", f"campaign:{campaign_id}", campaign_id=campaign_id) or {}
        if not camp:
            camp = _get("dnd-campaign", "campaign", campaign_id=None) or {}
        if camp:
            lines = [
                f"Campaign: {camp.get('name', '(unset)')}",
                f"Chapter:  {camp.get('chapter', '(unset)')}",
                f"Location: {camp.get('location', '(unset)')}",
                f"Mode:     {camp.get('dm_mode', 'in_character')}",
            ]
            if camp.get("world_notes"):
                lines.append(f"Notes:    {str(camp['world_notes'])[:120]}")
            sections.append(_section("📜 CAMPAIGN", lines))
    except Exception as e:
        logger.debug(f"status: campaign read failed: {e}")

    # ── TIME ──────────────────────────────────────────────────────────────────
    try:
        time_data = _get("dnd-time", f"time:{campaign_id}", campaign_id=campaign_id) or {}
        if not time_data:
            time_data = _get("dnd-time", "time", campaign_id=None) or {}
        if time_data:
            day = time_data.get("day", "?")
            tod = time_data.get("time_of_day", "?")
            hour = time_data.get("hour", "")
            hour_str = f" ({hour}:00)" if hour != "" else ""
            sections.append(_section("🕰️  TIME", [f"Day {day} — {tod}{hour_str}"]))
    except Exception as e:
        logger.debug(f"status: time read failed: {e}")

    # ── SCENE ─────────────────────────────────────────────────────────────────
    try:
        scene = _get("dnd-scene", f"scene:{campaign_id}", campaign_id=campaign_id) or {}
        if not scene:
            scene = _get("dnd-scene", "scene", campaign_id=None) or {}
        current = scene.get("current", {}) if isinstance(scene, dict) else {}
        if current:
            lines = [f"Location: {current.get('name', '(unknown)')}"]
            if current.get("mood"):
                lines.append(f"Mood:     {current['mood']}")
            if current.get("present"):
                present = current["present"]
                if isinstance(present, list):
                    lines.append(f"Present:  {', '.join(present)}")
            sections.append(_section("📍 SCENE", lines))
    except Exception as e:
        logger.debug(f"status: scene read failed: {e}")

    # ── WEATHER ───────────────────────────────────────────────────────────────
    try:
        wx = _get("dnd-weather", "weather_state") or {}
        if wx:
            cond = wx.get("condition", "unknown")
            desc = wx.get("description", "")
            mechanics = wx.get("mechanics", "")
            line = cond
            if desc:
                line += f" — {desc[:80]}"
            lines = [line]
            if mechanics:
                lines.append(mechanics)
            sections.append(_section("🌤️  WEATHER", lines))
    except Exception as e:
        logger.debug(f"status: weather read failed: {e}")

    # ── PARTY ─────────────────────────────────────────────────────────────────
    try:
        char_state = plugin_loader.get_plugin_state("dnd-characters")

        # Try campaign-scoped data first
        chars = char_state.get(f"characters:{campaign_id}") or {}
        if not chars:
            chars = char_state.get("characters") or {}

        char_lines = []

        for char in chars.values() if isinstance(chars, dict) else []:
            hp = char.get("hp_current", "?")
            hp_max = char.get("hp_max", "?")
            ac = char.get("ac", "?")
            conditions = char.get("conditions", [])
            cond_str = f" [{', '.join(conditions)}]" if conditions else ""
            death_saves = char.get("death_saves", {})
            ds_str = ""
            if death_saves:
                succ = death_saves.get("successes", 0)
                fail = death_saves.get("failures", 0)
                if succ > 0 or fail > 0:
                    ds_str = f" ⚰️ DS {succ}S/{fail}F"
            char_lines.append(
                f"{char.get('name', '?')}: HP {hp}/{hp_max} | AC {ac}{cond_str}{ds_str}"
            )

        if char_lines:
            sections.append(_section("👥 PARTY", char_lines))
    except Exception as e:
        logger.debug(f"status: party read failed: {e}")

    # ── RESOURCES ─────────────────────────────────────────────────────────────
    try:
        res_state = plugin_loader.get_plugin_state("dnd-resources")
        res_index_raw = res_state.get(f"resource_index:{campaign_id}")
        if not res_index_raw:
            res_index_raw = res_state.get("resource_index")

        if res_index_raw:
            res_index = json.loads(res_index_raw) if isinstance(res_index_raw, str) else res_index_raw
            res_lines = []
            for char_key in res_index:
                # Try campaign-scoped resource key
                raw = res_state.get(f"resources:{campaign_id}:{char_key}")
                if not raw:
                    raw = res_state.get(char_key)
                if not raw:
                    continue
                char_res = json.loads(raw) if isinstance(raw, str) else raw
                char_name = char_res.get("name", char_key)
                spent = []
                for res_name, res_data in char_res.get("resources", {}).items():
                    current = res_data.get("current", 0)
                    maximum = res_data.get("max", 0)
                    if current < maximum:
                        spent.append(f"{res_name}: {current}/{maximum}")
                if spent:
                    res_lines.append(f"{char_name}: {', '.join(spent)}")
            if res_lines:
                sections.append(_section("⚡ SPENT RESOURCES", res_lines))
    except Exception as e:
        logger.debug(f"status: resources read failed: {e}")

    # ── COMBAT ────────────────────────────────────────────────────────────────
    try:
        enc_state = plugin_loader.get_plugin_state("dnd-encounters")

        # Try campaign-scoped combat data first
        combat = enc_state.get(f"combat:{campaign_id}")
        if not combat:
            combat = enc_state.get("combat")

        if combat:
            lines = ["⚔️ COMBAT IS ACTIVE"]
            current_turn = combat.get("current_turn", "?")
            round_num = combat.get("round", "?")
            lines.append(f"Round {round_num} — Current turn: {current_turn}")
            combatants = combat.get("combatants", [])
            for c in combatants:
                hp_str = f"HP {c.get('hp', '?')}" if "hp" in c else ""
                marker = "▶ " if c.get("name") == current_turn else "  "
                conds = c.get("conditions", [])
                cond_str = f" [{', '.join(conds)}]" if conds else ""
                lines.append(
                    f"{marker}{c.get('name', '?')} (init {c.get('initiative', '?')}) {hp_str}{cond_str}"
                )
            sections.append(_section("⚔️  COMBAT", lines))
    except Exception as e:
        logger.debug(f"status: combat read failed: {e}")

    # ── THREADS ───────────────────────────────────────────────────────────────
    try:
        thread_raw = _get("dnd-threads", f"threads:{campaign_id}", campaign_id=campaign_id) or []
        if not thread_raw:
            thread_raw = _get("dnd-threads", "threads", campaign_id=None) or []
        open_threads = [t for t in thread_raw if t.get("status") != "resolved"] if isinstance(thread_raw, list) else []
        if open_threads:
            high = [t for t in open_threads if t.get("urgency") == "high"]
            other = [t for t in open_threads if t.get("urgency") != "high"]
            lines = []
            for t in high:
                lines.append(f"🔴 [HIGH] {t.get('description', '?')[:100]}")
            for t in other[:5]:  # limit to 5 medium/low to avoid bloat
                lines.append(f"⚪ [{t.get('urgency', 'medium').upper()}] {t.get('description', '?')[:100]}")
            if open_threads:
                sections.append(_section("🧵 OPEN THREADS", lines))
    except Exception as e:
        logger.debug(f"status: threads read failed: {e}")

    # ── QUESTS ────────────────────────────────────────────────────────────────
    try:
        camp_data = _get("dnd-campaign", f"campaign:{campaign_id}", campaign_id=campaign_id)
        if not camp_data:
            camp_data = _get("dnd-campaign", "campaign", campaign_id=None)
        camp_quests = []
        if camp_data and isinstance(camp_data, dict):
            camp_quests = camp_data.get("quests", [])
        active_quests = [q for q in camp_quests if q.get("status") == "active"]
        if active_quests:
            lines = [f"• {q.get('title', '?')}: {q.get('description', '')[:80]}" for q in active_quests[:5]]
            sections.append(_section("📌 ACTIVE QUESTS", lines))
    except Exception as e:
        logger.debug(f"status: quests read failed: {e}")

    # ── NPC RELATIONS (optional) ──────────────────────────────────────────────
    if include_npcs:
        try:
            rel_state = plugin_loader.get_plugin_state("dnd-npc-relations")
            rel_raw = rel_state.get(f"relations_index:{campaign_id}")
            if not rel_raw:
                rel_raw = rel_state.get("relations_index")
            if rel_raw:
                rel_data = json.loads(rel_raw) if isinstance(rel_raw, str) else rel_raw
                non_neutral = {k: v for k, v in rel_data.items() if v.get("attitude_score", 0) != 0}
                if non_neutral:
                    lines = []
                    for e in sorted(non_neutral.values(), key=lambda x: x.get("attitude_score", 0)):
                        lines.append(f"{e['name']}: {e['attitude'].upper()}")
                    sections.append(_section("🧭 NPC ATTITUDES", lines))
        except Exception as e:
            logger.debug(f"status: npc-relations read failed: {e}")

    sections.append("\n" + "═" * 40)
    return "\n".join(sections)


def status_party() -> str:
    """
    Quick party HP and conditions snapshot only.

    Returns:
        Compact party status — name, HP, AC, active conditions.
    """
    try:
        campaign_id = _get_campaign_id()
        char_state = plugin_loader.get_plugin_state("dnd-characters")

        # Try campaign-scoped data first
        chars = char_state.get(f"characters:{campaign_id}") or {}
        if not chars:
            chars = char_state.get("characters") or {}

        if not chars:
            return "No characters found. Create characters with character_create."

        lines = ["👥 Party status:"]
        for char in chars.values() if isinstance(chars, dict) else []:
            hp = char.get("hp_current", "?")
            hp_max = char.get("hp_max", "?")
            ac = char.get("ac", "?")
            level = char.get("level", "?")
            class_name = char.get("class_name", "?")
            conditions = char.get("conditions", [])
            cond_str = f" ⚠️ {', '.join(conditions)}" if conditions else ""
            hp_bar = "🟢" if isinstance(hp, int) and isinstance(hp_max, int) and hp > hp_max * 0.5 else "🔴" if isinstance(hp, int) and isinstance(hp_max, int) and hp <= hp_max * 0.25 else "🟡"
            lines.append(
                f"  {hp_bar} {char.get('name', '?')} (Lv{level} {class_name}): "
                f"HP {hp}/{hp_max} | AC {ac}{cond_str}"
            )

        return "\n".join(lines)
    except Exception as e:
        return f"Could not read party status: {e}"


TOOLS = [
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "status_get_all",
            "description": "Get a full snapshot of the current game state across all D&D plugins — campaign, time, scene, weather, party HP, conditions, resources, combat, threads, quests, and optionally NPC attitudes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "include_npcs": {"type": "boolean", "description": "If True, includes NPC/faction attitude summary from dnd-npc-relations (can be verbose). Default: False"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "status_party",
            "description": "Quick party HP and conditions snapshot only. Returns compact party status — name, HP, AC, active conditions.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
]


def execute(function_name, arguments, config):
    if function_name == 'status_get_all':
        return status_get_all(include_npcs=arguments.get('include_npcs', False)), True

    if function_name == 'status_party':
        return status_party(), True

    return f"Unknown function: {function_name}", False
