"""
dnd-mystery — prompt_inject hook

Injects active mystery state into every prompt so Remmi always
knows what mysteries are active and can surface forgotten leads.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mystery import mystery_prompt


def hook(prompt, context=None, **kwargs):
    m = mystery_prompt()
    if m:
        prompt = f"{prompt}\n\n{m}"
    return prompt
