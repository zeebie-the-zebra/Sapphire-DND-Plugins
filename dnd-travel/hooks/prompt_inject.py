"""
dnd-travel — prompt_inject hook

Injects active travel state into every prompt so Remmi always
knows where the party is traveling and their current travel status.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from travel import travel_prompt


def hook(prompt, context=None, **kwargs):
    t = travel_prompt()
    if t:
        prompt = f"{prompt}\n\n{t}"
    return prompt
