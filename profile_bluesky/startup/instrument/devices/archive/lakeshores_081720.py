"""
Lakeshore temperature controllers
"""

__all__ = ['lakeshore_336','lakeshore_340lt','lakeshore_340ht']

from instrument.session_logs import logger
logger.info(__file__)

from apstools.devices import ProcessController
from apstools.synApps.asyn import AsynRecord
from bluesky import plan_stubs as bps
from ophyd import Component, Device, DeviceStatus, Signal
from ophyd import EpicsSignal, EpicsSignalRO, EpicsSignalWithRBV
from ophyd import FormattedComponent
import time

# TODO: fixes bug in apstools/synApps/asyn.py
class MyAsynRecord(AsynRecord):
    binary_output_maxlength = Component(EpicsSignal, ".OMAX")

####### LAKESHORE 336 #########
class LS336_LoopBase(ProcessController):
    """
    One control loop on the LS336 temperature controller

    Each control loop is a separate process controller.
    """

    signal = FormattedComponent(EpicsSignalRO, "{self.prefix}IN{self.loop_number}")
    temperature = signal

    target = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}OUT{self.loop_number}:SP")
    units = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}IN{self.loop_number}:Units", kind="omitted")

    loop_name = FormattedComponent(EpicsSignalRO, "{self.prefix}IN{self.loop_number}:Name_RBV")

    control = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}OUT{self.loop_number}:Cntrl")
    manual = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}OUT{self.loop_number}:MOUT")
    mode = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}OUT{self.loop_number}:Mode")

    def __init__(self, *args, loop_number=None, **kwargs):
        self.controller_name = f"Lakeshore 336 Controller Loop {loop_number}"
        self.loop_number = loop_number
        super().__init__(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self.signal.get(*args, **kwargs)

class LS336_LoopMore(LS336_LoopBase):
    """
    Additional controls for loop1 and loop2: heater and pid
    """
    # only on loops 1 & 2
    heater = FormattedComponent(EpicsSignalRO, "{self.prefix}HTR{self.loop_number}")
    heater_range = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}HTR{self.loop_number}:Range")

    pid_P = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}P{self.loop_number}")
    pid_I = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}I{self.loop_number}")
    pid_D = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}D{self.loop_number}")
    ramp_rate = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}RampR{self.loop_number}")
    ramp_on = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}OnRamp{self.loop_number}")


class LS336Device(Device):
    """
    support for Lakeshore 336 temperature controller
    """
    loop1 = FormattedComponent(LS336_LoopMore, "{self.prefix}", loop_number=1)
    loop2 = FormattedComponent(LS336_LoopMore, "{self.prefix}", loop_number=2)
    loop3 = FormattedComponent(LS336_LoopBase, "{self.prefix}", loop_number=3)
    loop4 = FormattedComponent(LS336_LoopBase, "{self.prefix}", loop_number=4)

    # same names as apstools.synApps._common.EpicsRecordDeviceCommonAll
    scanning_rate = Component(EpicsSignal, "read.SCAN")
    process_record = Component(EpicsSignal, "read.PROC")

    read_all = Component(EpicsSignal, "readAll.PROC")
# TODO: serial = Component(AsynRecord, "serial")
    serial = Component(MyAsynRecord, "serial")

lakeshore_336 = LS336Device("4idd:LS336:TC3:", name="lakeshore 360", labels=["Lakeshore"])

####### LAKESHORE 340 #########
class LS340_LoopBase(ProcessController):

    target = FormattedComponent(EpicsSignal, "{self.prefix}SP{self.loop_number}",
                                write_pv='{self.prefix}wr_SP{self.loop_number}')

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

    def __init__(self, *args,loop_number=None, **kwargs):
        self.controller_name = f"Lakeshore 340 Controller"
        self.loop_number = loop_number
        super().__init__(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self.signal.get(*args, **kwargs)

class LS340_LoopSample(LS340_LoopBase):
    signal = FormattedComponent(EpicsSignalRO, "{self.prefix}Sample")
    temperature = signal
    sensor = FormattedComponent(EpicsSignal, "{self.prefix}Spl_sel")

class LS340_LoopControl(LS340_LoopBase):
    signal = FormattedComponent(EpicsSignalRO, "{self.prefix}Control")
    temperature = signal
    sensor = FormattedComponent(EpicsSignal, "{self.prefix}Ctl_sel")

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
