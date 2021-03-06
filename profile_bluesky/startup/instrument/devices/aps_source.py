"""
APS only: connect with facility information
"""

__all__ = ['aps', 'undulator']

from apstools.devices import ApsMachineParametersDevice, ApsUndulator
from ..framework import sd
from .extra_signals import TrackingSignal, DoneSignal
from ophyd import (Device, Component, Signal, EpicsSignal, EpicsSignalRO,
                   PVPositioner)
from ophyd.status import Status, AndStatus, wait as status_wait

from ..session_logs import logger
logger.info(__file__)

aps = ApsMachineParametersDevice(name="aps")
sd.baseline.append(aps)


class UndulatorEnergy(PVPositioner):
    """
    Undulator energy positioner.

    Main purpose this being a PVPositioner is to handle the undulator backlash.
    """

    # Position
    readback = Component(EpicsSignalRO, 'Energy', kind='hinted',
                         auto_monitor=True)
    setpoint = Component(EpicsSignal, 'EnergySet', put_complete=True,
                         auto_monitor=True, kind='normal')

    # Configuration
    deadband = Component(Signal, value=0.002, kind='config')
    backlash = Component(Signal, value=0.25, kind='config')
    offset = Component(Signal, value=0, kind='config')

    done = Component(DoneSignal, value=0, kind='omitted')
    done_value = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tolerance = 0.002
        self.readback.subscribe(self.done.get)
        self.setpoint.subscribe(self.done.get)

    @deadband.sub_value
    def _change_tolerance(self, value=None, **kwargs):
        if value:
            self.tolerance = value

    @done.sub_value
    def _move_changed(self, **kwargs):
        super()._move_changed(**kwargs)

    def move(self, position, wait=True, **kwargs):

        # If position is in the the deadband -> do nothing.
        if abs(position - self.readback.get()) <= self.tolerance:
            status = Status(self)
            status.set_finished()
        # Otherwise -> let's move!
        else:

            # Applies backlash if needed.
            if position > self.readback.get():
                # Go to backlash position, wait until it gets there.
                # TODO: is there a way to run these two actions without
                # blocking? The undulator would still move to the backlash
                # position, then final position, but the user would be able to
                # use the terminal.

                first_pos_status = super().move(position + self.backlash.get(),
                                                wait=False, **kwargs)
                first_click_status = self.parent.start_button.set(1)
                first_status = AndStatus(first_pos_status, first_click_status)
                status_wait(first_status)

            timeout = kwargs.pop('timeout', 120)
            pos_status = super().move(position, wait=False, timeout=timeout,
                                      **kwargs)
            click_status = self.parent.start_button.set(1)
            status = AndStatus(pos_status, click_status)

        self.done.get()
        if wait:
            status_wait(status)

        return status


class MyUndulator(ApsUndulator):
    """
    Undulator setup.

    Differences from `apstools` standard:
    - energy is a PVPositioner.
    - Has a flag used to track the mono energy.
    - Has an interactive undulator_setup.
    """

    energy = Component(UndulatorEnergy, '')
    tracking = Component(TrackingSignal, value=False, kind='config')

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
    """ 4-ID has two undulators, we use only the downstream. """
    upstream = None
    downstream = Component(MyUndulator, 'ds:')


undulator = MyDualUndulator("ID04", name="undulator")
sd.baseline.append(undulator)
