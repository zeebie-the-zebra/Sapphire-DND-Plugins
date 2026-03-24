"""
dnd-scaffold — Consolidated D&D 5e plugin for Sapphire

Imports all tool modules and exposes them via get_all_tools() and register_tools().
"""

import importlib
import logging
import os

logger = logging.getLogger("dnd-scaffold")

# All known tool modules in the tools/ directory
TOOL_MODULES = [
    "campaign",
    "characters",
    "dice",
    "encounter",
    "facts",
    "homebrew",
    "inspiration",
    "levelup",
    "mystery",
    "npcs",
    "recap",
    "relations",
    "resources",
    "rest",
    "reset",
    "rules",
    "scene",
    "shop",
    "spells",
    "status",
    "tables",
    "threads",
    "time",
    "travel",
    "weather",
]

# Modules that exist in tools/ (checked at import time)
_existing_modules = []
_failed_modules = []

for module_name in TOOL_MODULES:
    try:
        importlib.import_module(f"tools.{module_name}")
        _existing_modules.append(module_name)
    except ImportError:
        _failed_modules.append(module_name)

if _failed_modules:
    logger.debug(f"[dnd-scaffold] Some tool modules not available: {_failed_modules}")

# Build combined TOOLS list from all existing modules
_all_tools = []
for module_name in _existing_modules:
    try:
        module = importlib.import_module(f"tools.{module_name}")
        tools = getattr(module, "TOOLS", None)
        if tools:
            _all_tools.extend(tools)
    except Exception as e:
        logger.debug(f"[dnd-scaffold] Could not load tools from {module_name}: {e}")


def get_all_tools():
    """Return the combined list of all D&D tool classes."""
    return list(_all_tools)


def register_tools():
    """Register all D&D tools with the plugin system."""
    try:
        from core.plugin_loader import plugin_loader
        for tool in _all_tools:
            plugin_loader.register_tool(tool)
        logger.debug(f"[dnd-scaffold] Registered {len(_all_tools)} tools")
    except Exception as e:
        logger.debug(f"[dnd-scaffold] Could not register tools: {e}")


# Expose TOOLS at module level for plugin discovery
TOOLS = list(_all_tools)
