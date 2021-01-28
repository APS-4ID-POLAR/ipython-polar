
"""
Configure matplotlib in interactive mode for Jupyter notebook
"""

__all__ = ['plt']

from ..session_logs import logger
logger.info(__file__)

import matplotlib.pyplot as plt
from IPython import get_ipython

# %matplotlib notebook
get_ipython().magic('matplotlib notebook')
plt.ion()
