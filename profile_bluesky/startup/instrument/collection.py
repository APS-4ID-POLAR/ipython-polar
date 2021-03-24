
"""
configure for data collection in a console session
"""

from .session_logs import logger
logger.info(__file__)

from . import mpl

logger.info("bluesky framework")

from .framework import *
from .devices import *
from .callbacks import *
from .plans import *
from .utils import *

from apstools.utils import *

from IPython import get_ipython
from .utils.local_magics import LocalMagics
get_ipython().register_magics(LocalMagics)
