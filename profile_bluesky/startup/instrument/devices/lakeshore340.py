"""
Lakeshore temperature controllers
"""

from instrument.session_logs import logger
logger.info(__file__)

from apstools.synApps.asyn import AsynRecord
from ophyd import Component, Device, Signal
from ophyd import EpicsSignal, EpicsSignalRO
from ophyd import FormattedComponent,PVPositioner
from ophyd import Kind
from ..utils import DoneSignal

class LS340_LoopBase(PVPositioner):

    # position
    readback = Component(Signal,value=0)
    setpoint = FormattedComponent(EpicsSignal, "{self.prefix}SP{self.loop_number}",
                                  write_pv='{self.prefix}wr_SP{self.loop_number}',
                                  kind=Kind.hinted)

    # status
    done = Component(DoneSignal,value=0,kind=Kind.omitted)
    done_value = 1

    # configuration
    # TODO: Check if this PV exist...
    units = Component(Signal,value='K', kind=Kind.config)
    #units = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}IN{self.loop_number}:Units",
    #                           kind="omitted")

    # TODO: Is there a manual input or mode PV? It's not in the MEDM screen.
    # manual = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}OUT{self.loop_number}:MOUT")
    # mode = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}OUT{self.loop_number}:Mode")

    pid_P = FormattedComponent(EpicsSignal, "{self.prefix}P{self.loop_number}",
                               write_pv='{self.prefix}setPID{self.loop_number}.AA',
                               kind=Kind.config)
    pid_I = FormattedComponent(EpicsSignal, "{self.prefix}I{self.loop_number}",
                               write_pv='{self.prefix}setPID{self.loop_number}.BB',
                               kind=Kind.config)
    pid_D = FormattedComponent(EpicsSignal, "{self.prefix}D{self.loop_number}",
                               write_pv='{self.prefix}setPID{self.loop_number}.CC',
                               kind=Kind.config)

    ramp_rate = FormattedComponent(EpicsSignal, "{self.prefix}Ramp{self.loop_number}",
                                   write_pv='{self.prefix}setRamp{self.loop_number}.BB',
                                   kind=Kind.config)
    ramp_on = FormattedComponent(EpicsSignal, "{self.prefix}Ramp{self.loop_number}_on",
                                 kind=Kind.config)


    def __init__(self, *args,loop_number=None,timeout=60*60*10,**kwargs):
        self.loop_number = loop_number
        super().__init__(*args,timeout=timeout,**kwargs)
        self._settle_time = 0
        self._tolerance = 1

        self.readback.subscribe(self.done.get)
        self.setpoint.subscribe(self.done.get)

    @property
    def settle_time(self):
        return self._settle_time

    @settle_time.setter
    def settle_time(self,value):
        if value < 0:
            raise ValueError('Settle value needs to be >= 0.')
        else:
            self._settle_time = value

    @property
    def tolerance(self):
        return self._tolerance

    @tolerance.setter
    def tolerance(self,value):
        if value < 0:
            raise ValueError('Tolerance needs to be >= 0.')
        else:
            self._tolerance = value
            _ = self.done.get()

    @property
    def egu(self):
        return self.units.get(as_string=True)

    def stop(self,*,success=False):
        if success is False:
            self.setpoint.put(self._position,wait=True)
        super().stop(success=success)

    def pause(self):
        self.setpoint.put(self._position,wait=True)

    @done.sub_value
    def _move_changed(self,**kwargs):
        super()._move_changed(**kwargs)

    def move(self,*args,**kwargs):
        self.done.put(0)
        return super().move(*args,**kwargs)

class LS340_LoopControl(LS340_LoopBase):

    readback = FormattedComponent(EpicsSignalRO, "{self.prefix}Control",
                                  kind=Kind.hinted)
    sensor = FormattedComponent(EpicsSignal, "{self.prefix}Ctl_sel",
                                kind=Kind.config)

class LS340_LoopSample(LS340_LoopBase):

    readback = FormattedComponent(EpicsSignalRO, "{self.prefix}Sample",
                                  kind=Kind.hinted)
    sensor = FormattedComponent(EpicsSignal, "{self.prefix}Spl_sel",
                                kind=Kind.config)

class LS340Device(Device):

    control = FormattedComponent(LS340_LoopControl, "{self.prefix}", loop_number=1)
    sample = FormattedComponent(LS340_LoopSample, "{self.prefix}", loop_number=2)

    heater = Component(EpicsSignalRO, "Heater")
    heater_range = Component(EpicsSignal, "HeatRg",write_pv="Rg_rdbk",
                             kind=Kind.omitted)


    read_pid = Component(EpicsSignal, "readPID.PROC", kind=Kind.omitted)

    # same names as apstools.synApps._common.EpicsRecordDeviceCommonAll
    scanning_rate = Component(EpicsSignal, "read.SCAN", kind=Kind.omitted)
    process_record = Component(EpicsSignal, "read.PROC", kind=Kind.omitted)

    # TODO: serial = Component(AsynRecord, "serial")
    serial = Component(AsynRecord, "serial", kind=Kind.omitted)

# TODO: include limits, Fix offset AttributeError
# TODO: lakeshore 340 won't show a status bar, I don't know why.
