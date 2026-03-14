"""
dnd-voice-polish — post_llm OOC Filter

Fires after the LLM responds but before it's saved or spoken.

Local models like Qwen 3.5 occasionally break character with
out-of-character comments like:
  "As an AI I should note..."
  "I'll now describe the scene as the DM..."
  "Note: this is a fictional scenario..."
  "[DM narration begins]"

This hook strips those lines silently so the player never
hears Remmi break immersion.

Also cleans up common local model artifacts:
  - Orphaned tool call markers that leaked into the response
  - Repeated "As the DM..." framing lines
  - Trailing asterisk stage directions (*rolls dice*, *checks notes*)
    when they appear as standalone lines rather than inline flavor
"""

import re

# Lines to strip if they appear as a full line (case-insensitive)
STRIP_LINE_PATTERNS = [
    r"^as an ai\b",
    r"^i('m| am) an ai\b",
    r"^note:\s*(this is a fictional|this is just|remember that)",
    r"^\*?as the (dungeon master|dm)[,:]?\*?$",
    r"^\[dm narration",
    r"^\[tool (call|result)",
    r"^i'll (now )?(describe|narrate|continue)",
    r"^let me (describe|continue|narrate)",
    r"^\*clears throat\*",
    r"^\*checks (notes|map|sheet)\*$",
    r"^as remmi,?\s*(i |the dm )",
]

COMPILED = [re.compile(p, re.IGNORECASE) for p in STRIP_LINE_PATTERNS]


def post_llm(event):
    text = event.response or ""
    if not text:
        return

    lines     = text.split("\n")
    filtered  = []
    stripped  = 0

    for line in lines:
        stripped_line = line.strip()
        if any(p.match(stripped_line) for p in COMPILED):
            stripped += 1
            continue
        filtered.append(line)

    if stripped > 0:
        # Remove any double blank lines left behind
        result = "\n".join(filtered)
        result = re.sub(r"\n{3,}", "\n\n", result).strip()
        event.response = result
