"""
Lakeshore temperature controllers
"""



__all__ = ['lakeshore_336','lakeshore_340lt','lakeshore_340ht']

from instrument.session_logs import logger
logger.info(__file__)

from apstools.synApps.asyn import AsynRecord
from ophyd import Component, Device, Signal
from ophyd import EpicsSignal, EpicsSignalRO, EpicsSignalWithRBV
from ophyd import FormattedComponent,PVPositioner
from ophyd.signal import SignalRO

# TODO: fixes bug in apstools/synApps/asyn.py
class MyAsynRecord(AsynRecord):
    binary_output_maxlength = Component(EpicsSignal, ".OMAX")

####### LAKESHORE 336 #########
class DoneSignal(SignalRO):
    def get(self,**kwargs):
        readback = self.parent.readback.get()
        setpoint = self.parent.setpoint.get()
        tolerance = self.parent.tolerance

        if abs(readback-setpoint) <= tolerance:
            self._readback = 1
        else:
            self._readback = 0

        return self._readback

class LS336_LoopControl(PVPositioner):

    readback = FormattedComponent(EpicsSignalRO, "{self.prefix}IN{self.loop_number}")
    setpoint = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}OUT{self.loop_number}:SP")

    done = Component(DoneSignal,value=0)
    done_value = 1

    units = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}IN{self.loop_number}:Units", kind="omitted")

    loop_name = FormattedComponent(EpicsSignalRO, "{self.prefix}IN{self.loop_number}:Name_RBV")

    control = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}OUT{self.loop_number}:Cntrl")
    manual = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}OUT{self.loop_number}:MOUT")
    mode = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}OUT{self.loop_number}:Mode")

    heater = FormattedComponent(EpicsSignalRO, "{self.prefix}HTR{self.loop_number}")
    heater_range = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}HTR{self.loop_number}:Range")

    pid_P = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}P{self.loop_number}")
    pid_I = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}I{self.loop_number}")
    pid_D = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}D{self.loop_number}")
    ramp_rate = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}RampR{self.loop_number}")
    ramp_on = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}OnRamp{self.loop_number}")

    def __init__(self, *args,loop_number=None,timeout=60*60*10,**kwargs):
        self.loop_number = loop_number
        super().__init__(*args,timeout=timeout,**kwargs)
        self._settle_time = 0
        self._tolerance = 0

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

    def egu(self):
        return self.units.get()

    def get(self, *args, **kwargs):
        return self.readback.get(*args, **kwargs)

    def set(self,*args,**kwargs):
        return self.move(*args,wait=True,timeout=self._timeout,**kwargs)

    def put(self,*args,**kwargs):
        return self.move(*args,wait=False,timeout=self._timeout,**kwargs)

    def stop(self,*,success=False):
        self.put(self.get())
        super().stop(success=success)

class LS336_LoopRO(Device):
    """
    Additional controls for loop1 and loop2: heater and pid
    """
    readback = FormattedComponent(EpicsSignalRO, "{self.prefix}IN{self.loop_number}")
    units = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}IN{self.loop_number}:Units", kind="omitted")
    loop_name = FormattedComponent(EpicsSignalRO, "{self.prefix}IN{self.loop_number}:Name_RBV")

    def __init__(self, *args,loop_number=None,**kwargs):
        self.loop_number = loop_number
        super().__init__(*args,**kwargs)

class LS336Device(Device):
    """
    support for Lakeshore 336 temperature controller
    """
    loop1 = FormattedComponent(LS336_LoopControl, "{self.prefix}", loop_number=1)
    loop2 = FormattedComponent(LS336_LoopControl, "{self.prefix}", loop_number=2)
    loop3 = FormattedComponent(LS336_LoopRO, "{self.prefix}", loop_number=3)
    loop4 = FormattedComponent(LS336_LoopRO, "{self.prefix}", loop_number=4)

    # same names as apstools.synApps._common.EpicsRecordDeviceCommonAll
    scanning_rate = Component(EpicsSignal, "read.SCAN")
    process_record = Component(EpicsSignal, "read.PROC")

    read_all = Component(EpicsSignal, "readAll.PROC")
# TODO: serial = Component(AsynRecord, "serial")
    serial = Component(MyAsynRecord, "serial")

lakeshore_336 = LS336Device("4idd:LS336:TC3:", name="lakeshore 360", labels=["Lakeshore"])

####### LAKESHORE 340 #########

class LS340_LoopBase(PVPositioner):

    readback = Component(Signal,value=0)
    setpoint = FormattedComponent(EpicsSignal, "{self.prefix}SP{self.loop_number}",
                                    write_pv='{self.prefix}wr_SP{self.loop_number}')

    done = Component(DoneSignal,value=0)
    done_value = 1

    # TODO: Check if this PV exist...
    units = Component(Signal,value='Kelvin')
    #units = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}IN{self.loop_number}:Units",
    #                           kind="omitted")

    # TODO: Is there a manual input or mode PV? It's not in the MEDM screen.
    # manual = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}OUT{self.loop_number}:MOUT")
    # mode = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}OUT{self.loop_number}:Mode")

    pid_P = FormattedComponent(EpicsSignal, "{self.prefix}P{self.loop_number}",
                               write_pv='{self.prefix}setPID{self.loop_number}.AA')
    pid_I = FormattedComponent(EpicsSignal, "{self.prefix}I{self.loop_number}",
                               write_pv='{self.prefix}setPID{self.loop_number}.BB')
    pid_D = FormattedComponent(EpicsSignal, "{self.prefix}D{self.loop_number}",
                               write_pv='{self.prefix}setPID{self.loop_number}.CC')

    ramp_rate = FormattedComponent(EpicsSignal, "{self.prefix}Ramp{self.loop_number}",
                                   write_pv='{self.prefix}setRamp{self.loop_number}.BB')
    ramp_on = FormattedComponent(EpicsSignal, "{self.prefix}Ramp{self.loop_number}_on")

    def __init__(self, *args,loop_number=None,timeout=60*60*10,**kwargs):
        self.loop_number = loop_number
        super().__init__(*args,timeout=timeout,**kwargs)
        self._settle_time = 0
        self._tolerance = 0

    @property
    def egu(self):
        return self.units.get()

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

    def get(self, *args, **kwargs):
        return self.readback.get(*args, **kwargs)

    def set(self,*args,**kwargs):
        return self.move(*args,wait=True,timeout=self._timeout,**kwargs)

    def put(self,*args,**kwargs):
        return self.move(*args,wait=False,timeout=self._timeout,**kwargs)

    def stop(self,*,success=False):
        self.put(self.get())
        super().stop(success=success)

class LS340_LoopControl(LS340_LoopBase):

    readback = FormattedComponent(EpicsSignalRO, "{self.prefix}Control")
    sensor = FormattedComponent(EpicsSignal, "{self.prefix}Ctl_sel")

class LS340_LoopSample(LS340_LoopBase):

    readback = FormattedComponent(EpicsSignalRO, "{self.prefix}Sample")
    sensor = FormattedComponent(EpicsSignal, "{self.prefix}Spl_sel")

class LS340Device(Device):

    control = FormattedComponent(LS340_LoopControl, "{self.prefix}", loop_number=1)
    sample = FormattedComponent(LS340_LoopSample, "{self.prefix}", loop_number=2)

    heater = FormattedComponent(EpicsSignalRO, "{self.prefix}Heater")
    heater_range = FormattedComponent(EpicsSignal, "{self.prefix}HeatRg",
                                      write_pv="{self.prefix}Rg_rdbk" )


    read_pid = FormattedComponent(EpicsSignal, "{self.prefix}readPID.PROC")

    # same names as apstools.synApps._common.EpicsRecordDeviceCommonAll
    scanning_rate = Component(EpicsSignal, "read.SCAN")
    process_record = Component(EpicsSignal, "read.PROC")

    # TODO: serial = Component(AsynRecord, "serial")
    serial = Component(MyAsynRecord, "serial")

lakeshore_340lt = LS340Device('4idd:LS340:TC1:',name="lakeshore 340 - low temperature",
                              labels=("Lakeshore"))

lakeshore_340ht = LS340Device('4idd:LS340:TC2:',name="lakeshore 340 - high temperature",
                              labels=("Lakeshore"))

# TODO: PVPositioner has a .settle_time that should wait after reached temperature.
# Need to think about the best way to implement it, should it be defaulted to zero,
# and modified in a plan?

# TODO: Test how to implement "watcher" options. It's under MoveStatus, so it may not
# be trivial. Perhaps this would be done through callbacks? I suspect the best effort
# callback will already add something.
