"""
dnd-time — Persistent Time Tracking

Tracks:
  - Time of day (morning, afternoon, evening, night, midnight)
  - Game clock (hour, minute)
  - Day count
  - Elapsed time since session start

Tools:
  time_set()      — set the current time
  time_advance()   — advance time by hours/minutes
  time_get()       — get current time info
  time_set_day()   — set the day number
  time_reset()     — reset to session start (for new sessions)
"""

from datetime import datetime, timedelta

ENABLED = True
EMOJI = '🕐'
AVAILABLE_FUNCTIONS = [
    'time_set', 'time_advance', 'time_get', 'time_set_day', 'time_reset'
]

TOOLS = [
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "time_set",
            "description": (
                "Set the current in-game time. Use this when the party wakes up, rests, "
                "or when time explicitly changes. This time persists across turns."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "time_of_day": {
                        "type": "string",
                        "description": "Time period: 'morning', 'afternoon', 'evening', 'night', 'midnight', 'dawn', 'dusk'"
                    },
                    "hour": {
                        "type": "integer",
                        "description": "Hour (0-23), e.g. 6 for 6 AM, 18 for 6 PM"
                    },
                    "minute": {
                        "type": "integer",
                        "description": "Minute (0-59), default 0"
                    },
                    "day": {
                        "type": "integer",
                        "description": "Day number (optional — defaults to current)"
                    },
                    "notes": {
                        "type": "string",
                        "description": "Optional notes about this time setting"
                    }
                },
                "required": ["time_of_day"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "time_advance",
            "description": (
                "Advance the game clock by a duration. Use after travel, long conversations, "
                "battles, or any scene where time passes. The new time is injected every turn."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "hours": {
                        "type": "integer",
                        "description": "Hours to advance (0-24)"
                    },
                    "minutes": {
                        "type": "integer",
                        "description": "Minutes to advance (0-59)"
                    },
                    "event": {
                        "type": "string",
                        "description": "What happened during this time (optional, for log)"
                    }
                },
                "required": ["hours"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "time_get",
            "description": "Get the current in-game time, day, and time period.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "time_set_day",
            "description": "Set the current day number (e.g. Day 1, Day 12).",
            "parameters": {
                "type": "object",
                "properties": {
                    "day": {"type": "integer", "description": "Day number"}
                },
                "required": ["day"]
            }
        }
    },
    {
        "type": "function",
        "is_local": True,
        "function": {
            "name": "time_reset",
            "description": (
                "Reset time to the start of a new session. Sets time to morning, day 1, "
                "clears the elapsed tracker. Use when starting a fresh play session."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "day": {"type": "integer", "description": "Starting day number (default 1)"}
                },
                "required": []
            }
        }
    }
]

DEFAULT_CAMPAIGN_ID = "default"


def _get_state():
    from core.plugin_loader import plugin_loader
    return plugin_loader.get_plugin_state("dnd-scaffold")


def _get_campaign_id(config=None) -> str:
    """Get current campaign ID, defaulting to 'default' for backward compatibility."""
    from core.plugin_loader import plugin_loader

    try:
        campaign_state = plugin_loader.get_plugin_state("dnd-campaign")
        campaign_id = campaign_state.get("active_campaign", DEFAULT_CAMPAIGN_ID)
        if campaign_id:
            return campaign_id
    except Exception:
        pass

    return DEFAULT_CAMPAIGN_ID


def _migrate_if_needed(campaign_id: str):
    """Migrate legacy time data to campaign scope if needed."""
    state = _get_state()
    migration_key = f"_legacy_migrated_{campaign_id}"

    if state.get(migration_key):
        return

    legacy = state.get("time")
    if legacy:
        state.save(f"time:{campaign_id}", legacy)
        state.save(migration_key, True)


def _load(config=None):
    """Load time data for the current campaign."""
    campaign_id = _get_campaign_id(config)
    state = _get_state()

    _migrate_if_needed(campaign_id)

    campaign_time = state.get(f"time:{campaign_id}")
    if campaign_time:
        return campaign_time

    return state.get("time") or {
        "time_of_day": "morning",
        "hour": 8,
        "minute": 0,
        "day": 1,
        "session_start": datetime.now().isoformat(),
        "elapsed_minutes": 0,
        "last_updated": datetime.now().isoformat()
    }


def _save(data, config=None):
    """Save time data to the current campaign's storage."""
    campaign_id = _get_campaign_id(config)
    data["last_updated"] = datetime.now().isoformat()
    _get_state().save(f"time:{campaign_id}", data)


def _time_period(hour):
    """Determine time period from hour."""
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 20:
        return "evening"
    elif 20 <= hour < 24 or 0 <= hour < 2:
        return "night"
    elif 2 <= hour < 5:
        return "midnight"
    elif hour == 12:
        return "noon"
    elif hour == 0:
        return "midnight"
    return "night"


def _format_time(hour, minute):
    """Format time as '8:00 AM' style."""
    if hour == 0:
        return "12:00 AM (midnight)"
    elif hour == 12:
        return "12:00 PM (noon)"
    elif hour < 12:
        return f"{hour}:{minute:02d} AM"
    else:
        return f"{hour-12}:{minute:02d} PM"


def execute(function_name, arguments, config):
    data = _load(config)

    # ── time_set ─────────────────────────────────────────────────────────
    if function_name == "time_set":
        time_of_day = arguments.get("time_of_day", "").lower().strip()
        hour = arguments.get("hour")
        minute = arguments.get("minute", 0)
        day = arguments.get("day")
        notes = arguments.get("notes", "").strip()

        # Map time_of_day to hour if not provided
        hour_map = {
            "morning": 8, "dawn": 6, "noon": 12,
            "afternoon": 14, "dusk": 18, "evening": 19,
            "night": 21, "midnight": 0
        }

        if hour is None:
            hour = hour_map.get(time_of_day, 8)

        data["time_of_day"] = time_of_day
        data["hour"] = hour
        data["minute"] = minute

        if day:
            data["day"] = day

        _save(data, config)

        time_str = _format_time(hour, minute)
        day_str = f"Day {data['day']}"
        msg = f"🕐 Time set to: {time_str} ({time_of_day}), {day_str}"
        if notes:
            msg += f"\nNote: {notes}"
        return msg, True

    # ── time_advance ─────────────────────────────────────────────────────
    elif function_name == "time_advance":
        hours = arguments.get("hours", 0)
        minutes = arguments.get("minutes", 0)
        event = arguments.get("event", "").strip()

        if hours == 0 and minutes == 0:
            return "Error: specify hours and/or minutes to advance.", False

        # Calculate new time
        current_hour = data.get("hour", 8)
        current_minute = data.get("minute", 0)
        current_day = data.get("day", 1)

        # Add duration
        total_minutes = current_hour * 60 + current_minute + hours * 60 + minutes

        # Handle day overflow
        days_passed = total_minutes // (24 * 60)
        remaining_minutes = total_minutes % (24 * 60)
        new_hour = remaining_minutes // 60
        new_minute = remaining_minutes % 60

        data["hour"] = new_hour
        data["minute"] = new_minute
        data["day"] = current_day + days_passed
        data["time_of_day"] = _time_period(new_hour)
        data["elapsed_minutes"] = data.get("elapsed_minutes", 0) + hours * 60 + minutes

        _save(data, config)

        time_str = _format_time(new_hour, new_minute)
        elapsed = data.get("elapsed_minutes", 0)
        hours_elapsed = elapsed // 60
        mins_elapsed = elapsed % 60
        elapsed_str = f"{hours_elapsed}h {mins_elapsed}m this session"

        msg = f"⏱️ Time advanced {hours}h {minutes}m"
        msg += f"\nNow: {time_str} ({data['time_of_day']}), Day {data['day']}"
        msg += f"\nElapsed: {elapsed_str}"

        if event:
            msg += f"\nEvent: {event}"

        return msg, True

    # ── time_get ─────────────────────────────────────────────────────────
    elif function_name == "time_get":
        hour = data.get("hour", 8)
        minute = data.get("minute", 0)
        day = data.get("day", 1)
        time_of_day = data.get("time_of_day", "morning")
        elapsed = data.get("elapsed_minutes", 0)

        time_str = _format_time(hour, minute)
        hours_elapsed = elapsed // 60
        mins_elapsed = elapsed % 60

        lines = [
            f"🕐 **CURRENT TIME**",
            f"  {time_str} ({time_of_day})",
            f"  Day {day}",
            f"  Elapsed this session: {hours_elapsed}h {mins_elapsed}m"
        ]

        return "\n".join(lines), True

    # ── time_set_day ─────────────────────────────────────────────────────
    elif function_name == "time_set_day":
        day = arguments.get("day", 1)

        if day < 1:
            return "Day must be 1 or greater.", False

        old_day = data.get("day", 1)
        data["day"] = day
        _save(data, config)

        return f"📅 Day set: {old_day} → {day}", True

    # ── time_reset ───────────────────────────────────────────────────────
    elif function_name == "time_reset":
        day = arguments.get("day", 1)

        data = {
            "time_of_day": "morning",
            "hour": 8,
            "minute": 0,
            "day": day,
            "session_start": datetime.now().isoformat(),
            "elapsed_minutes": 0,
            "last_updated": datetime.now().isoformat()
        }
        _save(data, config)

        return f"🔄 Time reset — {day}, 8:00 AM (morning). Ready for a new session!", True

    return f"Unknown function: {function_name}", False
