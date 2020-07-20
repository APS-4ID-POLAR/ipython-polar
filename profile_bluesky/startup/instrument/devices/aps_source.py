
"""
APS only: connect with facility information
"""

__all__ = [
    'aps', 
    'undulator',
    ]

from ..session_logs import logger
logger.info(__file__)

import apstools.devices
from ..framework import sd

aps = apstools.devices.ApsMachineParametersDevice(name="aps")
sd.baseline.append(aps)

class MyUndulator(apstools.devices.ApsUndulatorDual):
    upstream = None

# undulator = apstools.devices.ApsUndulator("ID04", name="undulator")
undulator = MyUndulator("ID04", name="undulator")
sd.baseline.append(undulator)
