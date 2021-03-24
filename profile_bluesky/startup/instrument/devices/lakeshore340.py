"""
Lakeshore temperature controllers
"""

from apstools.synApps.asyn import AsynRecord
from ophyd import Component, Device, Signal, Staged
from ophyd import EpicsSignal, EpicsSignalRO
from ophyd import FormattedComponent, PVPositioner
from ..utils import DoneSignal, TrackingSignal
from time import sleep

from instrument.session_logs import logger
logger.info(__file__)


class SetpointSignal(EpicsSignal):

    def __init__(self, *args, max_iteractions=5, sleep_default=0.02,
                 ramp_attr='ramp_on', **kwargs):
        super().__init__(*args, **kwargs)
        self.max_iteractions = max_iteractions
        self.sleep_default = sleep_default
        self.ramp_attr = ramp_attr

    def put(self, value, **kwargs):
        super().put(value, **kwargs)
        ramp = getattr(self.parent, self.ramp_attr).get()
        counter = 0
        while abs(value - self._readback) > self.tolerance:
            if counter == self.max_iteractions:
                # Checks that it is not ramping.
                if ramp == 0:
                    raise RuntimeError('Setpoint was not updated after '
                                       f'{self.max_iteractions} attempts.')
                else:
                    break
            sleep(self.sleep_default)
            super().put(value, **kwargs)
            counter += 1


class LS340_LoopBase(PVPositioner):

    # position
    readback = Component(Signal, value=0)
    setpoint = FormattedComponent(SetpointSignal, "{prefix}SP{loop_number}",
                                  write_pv="{prefix}wr_SP{loop_number}",
                                  kind="normal", put_complete=True)

    # This is here only because of ramping, because then setpoint will change
    # slowly.
    target = Component(Signal, value=0, kind="omitted")

    # status
    done = Component(DoneSignal, value=0, setpoint_attr='target',
                     kind="omitted")
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

    def pause(self):
        self.setpoint.put(self._position, wait=True)

    @done.sub_value
    def _move_changed(self, **kwargs):
        super()._move_changed(**kwargs)

    def move(self, position, **kwargs):

        # TODO: This is an area that may be problematic. Need to test at
        # beamline when doing scan and when just moving.

        # This will apply only when we are moving, not scanning. In the later,
        # the stage/unstage will run before/after the scan.
        if self._staged == Staged.no:
            self.stage()
            self.subscribe(self.unstage, event_type=self._SUB_REQ_DONE)
        self.done.put(0)
        self.target.put(position)
        return super().move(position, **kwargs)

    def stage(self):
        self.readback.subscribe(self.done.get, event_type='value')
        self.setpoint.subscribe(self.done.get, event_type='value')
        super().stage()

    def unstage(self, **kwargs):
        self.readback.clear_subs(self.done.get)
        self.setpoint.clear_subs(self.done.get)
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
    heater_range = Component(EpicsSignal, "Rg_rdbk", write_pv="HeatRg",
                             kind="normal", put_complete=True)

    auto_heater = Component(TrackingSignal, value=False, kind="config")

    read_pid = Component(EpicsSignal, "readPID.PROC", kind="omitted")

    # same names as apstools.synApps._common.EpicsRecordDeviceCommonAll
    scanning_rate = Component(EpicsSignal, "read.SCAN", kind="omitted")
    process_record = Component(EpicsSignal, "read.PROC", kind="omitted")

    serial = Component(AsynRecord, "serial", kind="omitted")

    # This must be modified either here, or before using auto_heater.
    _auto_ranges = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # TODO: I don't know why this has to be done, otherwise it gets hinted.
        self.control.readback.kind = "normal"

    @auto_heater.sub_value
    def _subscribe_auto_heater(self, value=None, **kwargs):
        if value:
            self.control.setpoint.subscribe(self._switch_heater,
                                            event_type='value')
        else:
            self.control.setpoint.clear_subs(self._switch_heater)

    def _switch_heater(self, value=None, **kwargs):
        # TODO: Find a better way to do this, perhaps with an array?
        for _heater_range, _temp_range in self._auto_ranges.items():
            if _temp_range:
                if _temp_range[0] < value <= _temp_range[1]:
                    self.heater_range.put(_heater_range)

    @property
    def auto_ranges(self):
        return self._auto_ranges

    @auto_ranges.setter
    def auto_ranges(self, value):
        if not isinstance(value, dict):
            raise TypeError('auto_ranges must be a dictionary.')

        for _heater_range, _temp_range in value.items():
            if _heater_range not in self.heater_range.enum_strs:
                raise ValueError("The input dictionary keys must be one of "
                                 f"these: {self.heater_range.enum_strs}, but "
                                 f"{_heater_range} was entered.")

            if _temp_range is not None and len(_temp_range) != 2:
                raise ValueError(f"The value {_temp_range} is invalid! It "
                                 "must be either None or an iterable with two "
                                 "items.")

            self._auto_ranges = value
