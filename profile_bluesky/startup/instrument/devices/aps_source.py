
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
from ophyd import Device, Component, Signal, EpicsSignal

aps = apstools.devices.ApsMachineParametersDevice(name="aps")
sd.baseline.append(aps)


class MyUndulator(apstools.devices.ApsUndulator):

    energy = Component(EpicsSignal, "Energy", write_pv="EnergySet",
                       put_complete=True, kind='hinted')

    deadband = Component(Signal, value=0.002, kind='config')
    backlash = Component(Signal, value=0.25, kind='config')
    offset = Component(Signal, value=0, kind='config')
    _tracking = Component(Signal, value=False, kind='config')

    @property
    def tracking(self):
        return self._tracking.get()

    @tracking.setter
    def tracking(self, value):
        if type(value) != bool:
            raise ValueError('tracking is boolean, it can only be True or False.')
        else:
            self._tracking.put(value)

        if value:
            while True:
                offset = input("Undulator offset (keV) ({}): ".format(self._offset.get()))
                try:
                    self._offset.put(float(offset))
                    break
                except ValueError:
                    if offset == '':
                        print('Using offset = {} keV'.format(self._offset.get()))
                        break
                    print("The undulator offset has to be a number.")


class MyDualUndulator(Device):
    upstream = None
    downstream = Component(MyUndulator,'ds:')


undulator = MyDualUndulator("ID04", name="undulator")
undulator.downstream.tracking = False
sd.baseline.append(undulator)
