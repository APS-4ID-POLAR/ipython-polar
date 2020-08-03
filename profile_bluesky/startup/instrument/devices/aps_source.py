
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

class MyUndulator(apstools.devices.ApsUndulator):

    deadband = 0.002
    backlash = 0.25

    def __init__(self,pv,**kwargs):
        super().__init__(pv,**kwargs)
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
                offset = input("Undulator offset (keV) ({}): ".format(self._offset))
                try:
                    self._offset = float(offset)
                    break
                except ValueError:
                    if offset == '':
                        print('Using offset = {} keV'.format(self._offset))
                        break
                    print("The undulator offset has to be a number.")

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self,value):
        self._offset = float(value)

class MyDualUndulator(Devices):
    upstream = None
    downstream = Component(MyUndulator,'ds:')

# TODO: Not sure where to put the tracking.....
# undulator = apstools.devices.ApsUndulator("ID04", name="undulator")

undulator = MyDualUndulator("ID04", name="undulator")
sd.baseline.append(undulator)
