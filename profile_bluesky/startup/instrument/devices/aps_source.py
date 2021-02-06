
"""
APS only: connect with facility information
"""

from ..session_logs import logger
logger.info(__file__)

import apstools.devices
from ..framework import sd
from ..utils import TrackingSignal, DoneSignal
from ophyd import (Device, Component, Signal, EpicsSignal, EpicsSignalRO,
                   PVPositioner)
from ophyd.status import Status, AndStatus, wait as status_wait

aps = apstools.devices.ApsMachineParametersDevice(name="aps")
sd.baseline.append(aps)


class UndulatorEnergy(PVPositioner):
  
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
            _tracking = input("Do you want to track the undulator energy? "
                              "(yes/no): ")
            if _tracking == 'yes':
                self.tracking.put(True)
                break
            elif _tracking == 'no':
                self.tracking.put(False)
            else:
                print("Only yes or no are valid answers.")

        if _tracking == 'yes':
            while True:
                _offset = input("Undulator offset (keV) ({:0.3f}): ".format(
                    self.energy.offset.get()))
                try:
                    self.energy.offset.put(float(_offset))
                    break
                except ValueError:
                    if _offset == '':
                        print('Using offset = {:0.3f} keV'.format(
                            self.energy.offset.get()))
                        break
                    else:
                        print("The undulator offset has to be a number.")


class MyDualUndulator(Device):
    upstream = None
    downstream = Component(MyUndulator, 'ds:')


undulator = MyDualUndulator("ID04", name="undulator")
sd.baseline.append(undulator)
