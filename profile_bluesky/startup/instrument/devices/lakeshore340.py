"""
Lakeshore temperature controllers
"""

from instrument.session_logs import logger
logger.info(__file__)

from apstools.synApps.asyn import AsynRecord
from ophyd import Component, Device, Signal
from ophyd import EpicsSignal, EpicsSignalRO
from ophyd import FormattedComponent, PVPositioner
from ..utils import DoneSignal, TrackingSignal


class LS340_LoopBase(PVPositioner):

    # position
    readback = Component(Signal, value=0)
    setpoint = FormattedComponent(EpicsSignal,
                                  '{prefix}wr_SP{loop_number}',
                                  kind="omitted", put_complete=True)
    setpointRO = FormattedComponent(EpicsSignal,
                                    "{prefix}SP{loop_number}",
                                    kind="normal")

    # status
    done = Component(DoneSignal, value=0, kind="omitted")
    done_value = 1

    # configuration
    units = Component(Signal, value='K', kind="config")

    pid_P = FormattedComponent(EpicsSignal, "{prefix}P{loop_number}",
                               write_pv='{prefix}setPID{loop_number}.AA',
                               kind="config")
    pid_I = FormattedComponent(EpicsSignal, "{prefix}I{loop_number}",
                               write_pv='{prefix}setPID{loop_number}.BB',
                               kind="config")
    pid_D = FormattedComponent(EpicsSignal, "{prefix}D{loop_number}",
                               write_pv='{prefix}setPID{loop_number}.CC',
                               kind="config")

    ramp_rate = FormattedComponent(EpicsSignal,
                                   "{prefix}Ramp{loop_number}",
                                   write_pv='{prefix}setRamp{loop_number}.BB',
                                   kind="config")
    ramp_on = FormattedComponent(EpicsSignal,
                                 "{prefix}Ramp{loop_number}_on",
                                 kind="config")

    def __init__(self, *args, loop_number=None, timeout=60*60*10, **kwargs):
        self.loop_number = loop_number
        super().__init__(*args, timeout=timeout, **kwargs)
        self._settle_time = 0
        self._tolerance = 1

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

    @property
    def egu(self):
        return self.units.get(as_string=True)

    def stop(self, *, success=False):
        if success is False:
            self.setpoint.put(self._position, wait=True)
        super().stop(success=success)

    def pause(self):
        self.setpoint.put(self._position, wait=True)

    @done.sub_value
    def _move_changed(self, **kwargs):
        super()._move_changed(**kwargs)

    def move(self, *args, **kwargs):
        self.done.put(0)
        return super().move(*args, **kwargs)

    def stage(self):
        self.readback.subscribe(self.done.get)
        self.setpoint.subscribe(self.done.get)
        super().stage()

    def unstage(self):
        self.readback.unsubscribe(self.done.get)
        self.setpoint.unsubscribe(self.done.get)
        super().unstage()


class LS340_LoopControl(LS340_LoopBase):

    readback = FormattedComponent(EpicsSignalRO, "{prefix}Control",
                                  kind="normal")
    sensor = FormattedComponent(EpicsSignal, "{prefix}Ctl_sel",
                                kind="config")


class LS340_LoopSample(LS340_LoopBase):

    readback = FormattedComponent(EpicsSignalRO, "{prefix}Sample",
                                  kind="hinted")
    sensor = FormattedComponent(EpicsSignal, "{prefix}Spl_sel",
                                kind="config")


class LS340Device(Device):

    control = FormattedComponent(LS340_LoopControl, "{prefix}",
                                 loop_number=1)
    sample = FormattedComponent(LS340_LoopSample, "{prefix}",
                                loop_number=2)

    heater = Component(EpicsSignalRO, "Heater")
    heater_range = Component(EpicsSignal, "HeatRg", write_pv="Rg_rdbk",
                             kind="normal", put_complete=True)

    auto_heater = Component(TrackingSignal, value=False, kind="config")

    read_pid = Component(EpicsSignal, "readPID.PROC", kind="omitted")

    # same names as apstools.synApps._common.EpicsRecordDeviceCommonAll
    scanning_rate = Component(EpicsSignal, "read.SCAN", kind="omitted")
    process_record = Component(EpicsSignal, "read.PROC", kind="omitted")

    serial = Component(AsynRecord, "serial", kind="omitted")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # TODO: I don't know why this has to be done, otherwise it gets hinted.
        self.control.readback.kind = "normal"
        self._auto_ranges = {
            '10 mA': (0, 10),
            '33 mA': None,
            '100 mA': (10, 30),
            '333 mA': None,
            '1 A': (30, 305),
        }

    @auto_heater.sub_value
    def _subscribe_auto_heater(self, value=None, **kwargs):
        if value:
            self.control.setpointRO.subscribe(self._switch_heater,
                                              event_type='value')
        else:
            self.control.setpointRO.unsubscribe(self._switch_heater)

    def _switch_heater(self, value=None, **kwargs):
        # TODO: Find a better way to do this, perhaps with an array?
        for _heater_range, _temp_range in self._auto_ranges.items():
            if _temp_range:
                if _temp_range[0] < value <= _temp_range[1]:
                    self.heater_range.put(_heater_range)
