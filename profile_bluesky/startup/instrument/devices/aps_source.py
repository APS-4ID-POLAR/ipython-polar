
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
from ..utils import TrackingSignal
from ophyd import Device, Component, Signal, EpicsSignal

aps = apstools.devices.ApsMachineParametersDevice(name="aps")
sd.baseline.append(aps)


class MyUndulator(apstools.devices.ApsUndulator):

    energy = Component(EpicsSignal, "Energy", write_pv="EnergySet",
                       put_complete=True, kind='hinted')

    deadband = Component(Signal, value=0.002, kind='config')
    backlash = Component(Signal, value=0.25, kind='config')
    offset = Component(Signal, value=0, kind='config')
    tracking = Component(TrackingSignal, value=False, kind='config')

    @tracking.sub_value
    def _ask_for_offset(self, value=False, **kwargs):
        if value:
            while True:
                offset = input("Undulator offset (keV) ({}): ".format(self.offset.get()))
                try:
                    self.offset.put(float(offset))
                    break
                except ValueError:
                    if offset == '':
                        print('Using offset = {} keV'.format(self.offset.get()))
                        break
                    print("The undulator offset has to be a number.")


class MyDualUndulator(Device):
    upstream = None
    downstream = Component(MyUndulator, 'ds:')


undulator = MyDualUndulator("ID04", name="undulator")
undulator.downstream.tracking = False
sd.baseline.append(undulator)
