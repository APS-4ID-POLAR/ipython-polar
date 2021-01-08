"""
Lakeshore temperature controllers
"""

from apstools.synApps.asyn import AsynRecord
from ophyd import Component, Device
from ophyd import EpicsSignal, EpicsSignalRO, EpicsSignalWithRBV
from ophyd import FormattedComponent, PVPositioner
from ophyd import Kind
from ..utils import DoneSignal

from instrument.session_logs import logger
logger.info(__file__)


class LS336_LoopControl(PVPositioner):

    # position
    readback = FormattedComponent(EpicsSignalRO, "{prefix}IN{loop_number}",
                                  auto_monitor=True, kind=Kind.hinted)
    setpoint = FormattedComponent(EpicsSignal, "{prefix}OUT{loop_number}:SP",
                                  auto_monitor=True, put_complete=True,
                                  kind=Kind.omitted)
    setpointRO = FormattedComponent(EpicsSignalRO,
                                    "{prefix}OUT{loop_number}:SP_RBV",
                                    kind=Kind.normal)
    heater = FormattedComponent(EpicsSignalRO, "{prefix}HTR{loop_number}",
                                auto_monitor=True, kind=Kind.normal)

    # status
    done = Component(DoneSignal, value=0, kind=Kind.omitted)
    done_value = 1

    # configuration
    units = FormattedComponent(EpicsSignalWithRBV,
                               "{prefix}IN{loop_number}:Units",
                               kind=Kind.config)
    pid_P = FormattedComponent(EpicsSignalWithRBV,
                               "{prefix}P{loop_number}",
                               kind=Kind.config)
    pid_I = FormattedComponent(EpicsSignalWithRBV,
                               "{prefix}I{loop_number}",
                               kind=Kind.config)
    pid_D = FormattedComponent(EpicsSignalWithRBV,
                               "{prefix}D{loop_number}",
                               kind=Kind.config)
    ramp_rate = FormattedComponent(EpicsSignalWithRBV,
                                   "{prefix}RampR{loop_number}",
                                   kind=Kind.config)
    ramp_on = FormattedComponent(EpicsSignalWithRBV,
                                 "{prefix}OnRamp{loop_number}",
                                 kind=Kind.config)

    loop_name = FormattedComponent(EpicsSignalRO,
                                   "{prefix}IN{loop_number}:Name_RBV",
                                   kind=Kind.config)
    control = FormattedComponent(EpicsSignalWithRBV,
                                 "{prefix}OUT{loop_number}:Cntrl",
                                 kind=Kind.config)
    manual = FormattedComponent(EpicsSignalWithRBV,
                                "{prefix}OUT{loop_number}:MOUT",
                                kind=Kind.config)
    mode = FormattedComponent(EpicsSignalWithRBV,
                              "{prefix}OUT{loop_number}:Mode",
                              kind=Kind.config)
    heater_range = FormattedComponent(EpicsSignalWithRBV,
                                      "{prefix}HTR{loop_number}:Range",
                                      kind=Kind.config, auto_monitor=True)

    def __init__(self, *args, loop_number=None, timeout=60*60*10, **kwargs):
        self.loop_number = loop_number
        super().__init__(*args, timeout=timeout, **kwargs)
        self._settle_time = 0
        self._tolerance = 1

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
        # within self.tolerance.
        # Is it needed? Or is there a better way to do this?
        self.done.put(0)
        return super().move(*args, **kwargs)


class LS336_LoopRO(Device):
    """
    Additional controls for loop3 and loop4: heater and pid
    """
    # Set this to normal because we don't use it.
    readback = FormattedComponent(EpicsSignalRO,
                                  "{prefix}IN{loop_number}",
                                  kind=Kind.normal)
    units = FormattedComponent(EpicsSignalWithRBV,
                               "{prefix}IN{loop_number}:Units",
                               kind=Kind.omitted)
    loop_name = FormattedComponent(EpicsSignalRO,
                                   "{prefix}IN{loop_number}:Name_RBV",
                                   kind=Kind.omitted)

    def __init__(self, *args, loop_number=None, **kwargs):
        self.loop_number = loop_number
        super().__init__(*args, **kwargs)


class LS336Device(Device):
    """
    support for Lakeshore 336 temperature controller
    """
    loop1 = FormattedComponent(LS336_LoopControl, "{prefix}",
                               loop_number=1)
    loop2 = FormattedComponent(LS336_LoopControl, "{prefix}",
                               loop_number=2)
    loop3 = FormattedComponent(LS336_LoopRO, "{prefix}",
                               loop_number=3)
    loop4 = FormattedComponent(LS336_LoopRO, "{prefix}", loop_number=4)

    # same names as apstools.synApps._common.EpicsRecordDeviceCommonAll
    scanning_rate = Component(EpicsSignal, "read.SCAN", kind=Kind.omitted)
    process_record = Component(EpicsSignal, "read.PROC", kind=Kind.omitted)

    read_all = Component(EpicsSignal, "readAll.PROC", kind=Kind.omitted)
    # TODO: serial = Component(AsynRecord, "serial")
    serial = Component(AsynRecord, "serial", kind=Kind.omitted)
