"""
Phase retarders
"""

__all__ = ['pr1', 'pr2', 'pr3', 'wavefunc_gen']

from ..framework import sd
from ophyd import Device, EpicsMotor
from ophyd import Component, FormattedComponent
from ophyd import EpicsSignal, EpicsSignalRO, Signal
from ophyd import Kind
from scipy.constants import speed_of_light, Planck
from numpy import arcsin, pi

from ..session_logs import logger
logger.info(__file__)


# Phase Plates
class PRPzt(Device):
    remote_setpoint = Component(EpicsSignal, 'set_microns.VAL',
                                kind=Kind.omitted)
    remote_readback = Component(EpicsSignalRO, 'microns')

    # TODO: LocalDC readback is usually a bit different from the setpoint,
    # check if tolerance = 0.01 is good.
    # TODO: The value doesnt change in the MEDM screen, not sure why.
    localDC = Component(EpicsSignal, 'DC_read_microns',
                        write_pv='DC_read_microns.VAL', auto_monitor=True,
                        kind=Kind.hinted, tolerance=0.01)

    center = Component(EpicsSignal, 'AC_put_center.A', kind=Kind.config)
    offset = Component(EpicsSignal, 'AC_put_offset.A', kind=Kind.config)

    servoOn = Component(EpicsSignal, 'servo_ON.PROC', kind=Kind.omitted)
    servoOff = Component(EpicsSignal, 'servo_OFF.PROC', kind=Kind.omitted)
    servoStatus = Component(EpicsSignalRO, 'svo', kind=Kind.config)

    selectDC = FormattedComponent(EpicsSignal,
                                  '4idb:232DRIO:1:OFF_ch{_prnum}.PROC',
                                  kind=Kind.omitted)

    selectAC = FormattedComponent(EpicsSignal,
                                  '4idb:232DRIO:1:ON_ch{_prnum}.PROC',
                                  kind=Kind.omitted)

    ACstatus = FormattedComponent(EpicsSignalRO, '4idb:232DRIO:1:status',
                                  kind=Kind.config)

    def __init__(self, prefix, prnum, **kwargs):
        self._prnum = prnum
        super().__init__(prefix=prefix, **kwargs)


class PRDeviceBase(Device):

    x = FormattedComponent(EpicsMotor, '{prefix}:{_motorsDict[x]}',
                           labels=('motor', 'phase retarders'))

    y = FormattedComponent(EpicsMotor, '{prefix}:{_motorsDict[y]}',
                           labels=('motor', 'phase retarders'))

    th = FormattedComponent(EpicsMotor, '{prefix}:{_motorsDict[th]}',
                            labels=('motor', 'phase retarders'))

    _tracking = Component(Signal, value=False)
    d_spacing = Component(Signal, value=0)
    conversion_factor = Component(Signal, value=0.0)

    def __init__(self, prefix, name, motorsDict, **kwargs):
        self._motorsDict = motorsDict
        super().__init__(prefix=prefix, name=name, **kwargs)

    @property
    def tracking(self):
        return self._tracking.get()

    @tracking.setter
    def tracking(self, value):
        if type(value) != bool:
            raise ValueError('tracking is boolean, it can only be True or \
                False')
        else:
            self._tracking.put(value)

    def set_energy(self, energy):
        # energy in keV!

        # lamb in angstroms
        lamb = speed_of_light*Planck*6.241509e15*1e10/energy

        # theta in degrees
        theta = arcsin(lamb/2/self.d_spacing.get())*180./pi

        self.th.set_current_position(theta)


class PRDevice(PRDeviceBase):

    pzt = FormattedComponent(PRPzt, '{prefix}:E665:{_prnum}:',
                             prnum='{_prnum}')

    def __init__(self, prefix, name, prnum, motorsDict, **kwargs):
        self._prnum = prnum
        super().__init__(prefix, name, motorsDict, **kwargs)


pr1 = PRDevice('4idb', 'pr1', 1, {'x': 'm10', 'y': 'm11', 'th': 'm13'})
pr1.conversion_factor.put(0.001636)
pr1.d_spacing.put(2.0595)
# TODO: pr1 #3 says (220) in the MEDM screen, is it correct?

pr2 = PRDevice('4idb', 'pr2', 2, {'x': 'm15', 'y': 'm16', 'th': 'm18'})
pr2.conversion_factor.put(0.0019324)
pr2.d_spacing.put(2.0595)

pr3 = PRDeviceBase('4idb', 'pr3', {'x': 'm19', 'y': 'm20', 'th': 'm21'})
pr3.conversion_factor.put(0.0019324)
pr3.d_spacing.put(3.135)


# Wavefunction Generator
class SRS340(Device):
    frequency = Component(EpicsSignal, 'FREQ.VAL', write_pv='SetFREQ.A',
                          kind=Kind.config, labels=('phase retarders',))

    amplitude = Component(EpicsSignal, 'AMPL.VAL', write_pv='SetAMPL.A',
                          kind=Kind.config, labels=('phase retarders',))

    offset = Component(EpicsSignal, 'OFFS.VAL', write_pv='SetOFFS.A',
                       kind=Kind.config, labels=('phase retarders',))

    function = Component(EpicsSignal, 'FUNC.SVAL', write_pv='FUNCs.VAL',
                         kind=Kind.config, labels=('phase retarders',))


sd.baseline.append(pr1)
sd.baseline.append(pr2)
sd.baseline.append(pr3)

wavefunc_gen = SRS340('4idd:SRS340:1:', name='wavefunction generator')
