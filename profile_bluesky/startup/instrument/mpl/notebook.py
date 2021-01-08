
"""
Configure matplotlib in interactive mode for Jupyter notebook
"""

__all__ = ['plt']

import matplotlib.pyplot as plt
from ..session_logs import logger
from IPython import get_ipython
logger.info(__file__)

# %matplotlib notebook
get_ipython().magic('matplotlib notebook')
plt.ion()
