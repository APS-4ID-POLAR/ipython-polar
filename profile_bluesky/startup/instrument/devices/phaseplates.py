"""
Phase retarders
"""

__all__ = [
    'pr1','pr2','pr3','wavefunc_gen'
    ]

from ..session_logs import logger
logger.info(__file__)

from ophyd import Device, EpicsMotor
from ophyd import Component,FormattedComponent
from ophyd import EpicsSignal, EpicsSignalRO, Signal
from ophyd import Kind

## Phase Plates ##
class PRPzt(Device):
    remote_setpoint = Component(EpicsSignal,'set_microns.VAL',kind=Kind.omitted)
    remote_readback = Component(EpicsSignalRO,'microns')

    # TODO: LocalDC readback is usually a bit different from the setpoint,
    # check if tolerance = 0.01 is good.
    localDC = Component(EpicsSignal,'DC_read_microns',
                        write_pv='DC_read_microns.VAL',auto_monitor=True,
                        kind=Kind.hinted,tolerance=0.01)

    center = Component(EpicsSignal,'AC_put_center.A',kind=Kind.config)
    offset = Component(EpicsSignal,'AC_put_offset.A',kind=Kind.config)

    servoOn = Component(EpicsSignal,'servo_ON.PROC',kind=Kind.omitted)
    servoOff = Component(EpicsSignal,'servo_OFF.PROC',kind=Kind.omitted)
    servoStatus = Component(EpicsSignalRO,'svo',kind=Kind.config)

    selectDC = FormattedComponent(EpicsSignal,
                                  '4idb:232DRIO:1:OFF_ch{_prnum}.PROC',
                                  kind=Kind.omitted)

    selectAC = FormattedComponent(EpicsSignal,
                                  '4idb:232DRIO:1:ON_ch{_prnum}.PROC',
                                  kind=Kind.omitted)

    ACstatus = FormattedComponent(EpicsSignalRO,'4idb:232DRIO:1:status',
                                  kind=Kind.config)

    def __init__(self,prefix,prnum,**kwargs):
        self._prnum = prnum
        super().__init__(prefix=prefix,**kwargs)


class PRDeviceBase(Device):

    x = FormattedComponent(EpicsMotor,'{self.prefix}:{_motorsDict[x]}',
                           labels=('motor','phase retarders'))

    y = FormattedComponent(EpicsMotor,'{self.prefix}:{_motorsDict[y]}',
                           labels=('motor','phase retarders'))

    th = FormattedComponent(EpicsMotor,'{self.prefix}:{_motorsDict[th]}',
                            labels=('motor','phase retarders'))

    tracking = Component(Signal,value=False)

    conversion_factor = Component(Signal,value=0.0)

    def __init__(self,prefix,name,motorsDict,**kwargs):
        self._motorsDict = motorsDict
        super().__init__(prefix=prefix, name=name, **kwargs)

class PRDevice(PRDeviceBase):

    pzt = FormattedComponent(PRPzt,'{self.prefix}:E665:{_prnum}:','{_prnum}')

    def __init__(self,prefix,name,motorsDict,prnum,**kwargs):
        self._prnum = prnum
        super().__init__(prefix, name, motorsDict, **kwargs)


pr1 = PRDevice('4idb','pr1',1,{'x':'m10','y':'m11','th':'m13'})
pr1.conversion_factor.put(0.001636)

pr2 = PRDevice('4idb','pr2',2,{'x':'m15','y':'m16','th':'m18'})
pr2.conversion_factor.put(0.0019324)

pr3 = PRDeviceBase('4idb','pr3',{'x':'m19','y':'m20','th':'m21'})
pr3.conversion_factor.put(0.0019324)

## Wavefunction Generator ##
class SRS340(Device):
    frequency = Component(EpicsSignal,'FREQ.VAL',write_pv='SetFREQ.A',
                          kind=Kind.config, labels=('phase retarders'))

    amplitude = Component(EpicsSignal,'AMPL.VAL',write_pv='SetAMPL.A',
                          kind=Kind.config, labels=('phase retarders'))

    offset = Component(EpicsSignal,'OFFS.VAL',write_pv='SetOFFS.A',
                       kind=Kind.config, labels=('phase retarders'))

    function = Component(EpicsSignal,'FUNC.SVAL',write_pv='FUNCs.VAL',
                         kind=Kind.config, labels=('phase retarders'))

wavefunc_gen = SRS340('4idd:SRS340:1:',name='wavefunction generator')

# TODO: add other stuff to pr's, like lock-in PVS, and screen position.
