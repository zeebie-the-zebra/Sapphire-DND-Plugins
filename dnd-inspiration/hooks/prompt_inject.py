"""
dnd-inspiration — prompt_inject hook

Injects active inspiration state into every prompt so Remmi always
knows who has inspiration and can flag dramatic moments.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from inspiration import inspiration_prompt


def hook(prompt, context=None, **kwargs):
    insp = inspiration_prompt()
    if insp:
        prompt = f"{prompt}\n\n{insp}"
    return prompt
