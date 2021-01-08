
"""
Configure matplotlib in interactive mode for IPython console
"""

__all__ = ['plt']

from ..session_logs import logger
import matplotlib.pyplot as plt

logger.info(__file__)
plt.ion()
