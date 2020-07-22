
"""
configure for data collection in a console session
"""

from .session_logs import logger
logger.info(__file__)

from . import mpl

logger.info("bluesky framework")

from .sim_framework import *
#from .framework import *

#from .sim_devices import *
from .devices import *
# TODO: add a condition to import either

from .callbacks import *
from .plans import *
from .utils import *

from apstools.utils import *
