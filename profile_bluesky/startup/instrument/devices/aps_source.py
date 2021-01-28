
"""
APS only: connect with facility information
"""

__all__ = ['aps', 'undulator']

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
                       put_complete=True, kind='hinted', labels=('undulator',))

    deadband = Component(Signal, value=0.002, kind='config',
                         labels=('undulator',))
    backlash = Component(Signal, value=0.25, kind='config',
                         labels=('undulator',))
    offset = Component(Signal, value=0, kind='config', labels=('undulator',))
    tracking = Component(TrackingSignal, value=False, kind='config',
                         labels=('undulator',))

    def undulator_setup(self):
        """Interactive setup of usual undulator parameters."""
        while True:
            msg = "Do you want to track the undulator energy? (yes/no): "
            _tracking = input(msg)
            if _tracking == 'yes':
                self.tracking.put(True)
                break
            elif _tracking == 'no':
                self.tracking.put(False)
            else:
                print("Only yes or no are valid answers.")

        if _tracking == 'yes':
            while True:
                msg = "Undulator offset (keV) ({:0.3f}): "
                _offset = input(msg.format(self.offset.get()))
                try:
                    self.offset.put(float(_offset))
                    break
                except ValueError:
                    if _offset == '':
                        msg = 'Using offset = {:0.3f} keV'
                        print(msg.format(self.offset.get()))
                        break
                    else:
                        print("The undulator offset has to be a number.")


class MyDualUndulator(Device):
    upstream = None
    downstream = Component(MyUndulator, 'ds:')


undulator = MyDualUndulator("ID04", name="undulator")
sd.baseline.append(undulator)
