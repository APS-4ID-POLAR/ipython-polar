
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

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self._tracking = False
        self._offset = 0

    @property
    def tracking(self):
        return self._tracking

    @tracking.setter
    def tracking(self,value):
        if type(value) != bool:
            raise ValueError('tracking is boolean, it can only be True or False.')
        else:
            self._tracking = value

        if value == True:
            while True:
                offset = input("Undulator offset: ")
                try:
                    self._offset = offset
                    break  # if valid entry we break the loop
                except ValueError:
                    # or else we get here, print message and ask again
                    print("The undulator offset has to be a number.")

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self,value):
        self._offset = float(value)

# TODO: Not sure where to put the tracking.....
# undulator = apstools.devices.ApsUndulator("ID04", name="undulator")
undulator = MyUndulator("ID04", name="undulator")
sd.baseline.append(undulator)
