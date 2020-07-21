
"""
safe name for ophyd object
"""

__all__ = [
    'safeOphydName',
    ]

from ..session_logs import logger
logger.info(__file__)

import re

def safeOphydName(text):
    """
    make text safe to be used as an ophyd object name
    Given some input text string, return a clean version.
    Remove troublesome characters, perhaps other cleanup as well.
    This is best done with regular expression pattern matching.
    """
    pattern = "[a-zA-Z0-9_]"

    def mapper(c):
        if re.match(pattern, c) is not None:
            return c
        return "_"

    return "".join([mapper(c) for c in text])
