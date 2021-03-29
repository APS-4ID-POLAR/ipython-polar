"""
GE pressure controllers
"""

__all__ = ['ge_applyP', 'ge_releaseP']

from ophyd import Component
from ophyd import EpicsSignalRO, EpicsSignalWithRBV
from ophyd import FormattedComponent, PVPositioner
from ophyd import Kind
from .extra_signals import DoneSignal
from ..framework import sd
from ..session_logs import logger
logger.info(__file__)


class GEController(PVPositioner):
    """ General controller as a PVPositioner """

    # position
    readback = FormattedComponent(EpicsSignalRO, "{self.prefix}Pressure_RBV",
                                  auto_monitor=True, kind=Kind.hinted)
    setpoint = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}Setpoint",
                                  auto_monitor=True, kind=Kind.normal)

    # status
    done = Component(DoneSignal, value=0, kind=Kind.omitted)
    done_value = 1

    # configuration
    units = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}Units",
                               kind=Kind.config)

    control = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}Control",
                                 kind=Kind.config)

    slew_mode = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}SlewMode",
                                   kind=Kind.config)

    slew = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}Slew",
                              kind=Kind.config)

    effort = FormattedComponent(EpicsSignalRO, "{self.prefix}Effort_RBV",
                                auto_monitor=True, kind=Kind.config)

    def __init__(self, *args, loop_number=None, timeout=60*60*10, **kwargs):
        self.loop_number = loop_number
        super().__init__(*args, timeout=timeout, **kwargs)
        self._settle_time = 0
        self._tolerance = 0.01

        self.readback.subscribe(self.done.get)
        self.setpoint.subscribe(self.done.get)

    @property
    def settle_time(self):
        return self._settle_time

    @settle_time.setter
    def settle_time(self, value):
        if value < 0:
            raise ValueError('Settle value needs to be >= 0.')
        else:
            self._settle_time = value

    @property
    def tolerance(self):
        return self._tolerance

    @tolerance.setter
    def tolerance(self, value):
        if value < 0:
            raise ValueError('Tolerance needs to be >= 0.')
        else:
            self._tolerance = value
            _ = self.done.get()

    @property
    def egu(self):
        return self.units.get(as_string=True)

    def stop(self, *, success=False):
        if success is False:
            self.setpoint.put(self._position)
        super().stop(success=success)

    def pause(self):
        self.setpoint.put(self._position)

    @done.sub_value
    def _move_changed(self, **kwargs):
        super()._move_changed(**kwargs)

    def move(self, *args, **kwargs):
        # TODO: This self.done.put(0) is for the cases where the end point is
        # within self.tolerance. Is it needed? Or is there a better way to do
        # this?
        self.done.put(0)
        return super().move(*args, **kwargs)


ge_applyP = GEController("4idd:PC1:", name="ge_applyP",
                         labels=('ge_controller',))
ge_releaseP = GEController("4idd:PC2:", name="ge_releaseP",
                           labels=('ge_controller',))

sd.baseline.append(ge_applyP)
sd.baseline.append(ge_releaseP)
