"""
APD detector
"""

__all__ = ['cyberstar_mag_parameters', 'cyberstar_8c_parameters']

from ..session_logs import logger
logger.info(__file__)

from ophyd import Component, Device, EpicsSignal, EpicsSignalRO
from ..framework import sd


class CyberstarDevice(Device):

    hv_readback = Component(EpicsSignalRO, 'HV.VAL', kind='config',
                            labels=('cyberstar'))
    hv_setpoint = Component(EpicsSignal, 'SetHV.A', kind='omitted',
                            labels=('cyberstar'))
    remote_on = Component(EpicsSignal, 'Remote.VAL', kind='config',
                          labels=('cyberstar'))

    gain_readback = Component(EpicsSignalRO, 'Gain.VAL', kind='config',
                              labels=('cyberstar'))
    gain_setpoint = Component(EpicsSignal, 'SetGain.VAL', kind='omitted',
                              labels=('cyberstar'))

    peak_time_readback = Component(EpicsSignalRO, 'Pktime.VAL', kind='config',
                                   labels=('cyberstar'))
    peak_time_setpoint = Component(EpicsSignal, 'SetPktime.VAL',
                                   kind='omitted', labels=('cyberstar'))

    sca_low_readback = Component(EpicsSignalRO, 'SCAlo.VAL', kind='config',
                                 labels=('cyberstar'))
    sca_low_setpoint = Component(EpicsSignal, 'SetSCAlo.VAL', kind='omitted',
                                 labels=('cyberstar'))

    sca_window_readback = Component(EpicsSignalRO, 'SCAhi.VAL', kind='config',
                                    labels=('cyberstar'))
    sca_window_setpoint = Component(EpicsSignal, 'SetSCAhi.VAL',
                                    kind='omitted', labels=('cyberstar'))


cyberstar_mag_parameters = CyberstarDevice('4idd:x1k:2:', name='cyberstar_mag')
cyberstar_8c_parameters = CyberstarDevice('4idd:x1k:1:', name='cyberstar_8c')
sd.baseline.append(cyberstar_8c_parameters)
sd.baseline.append(cyberstar_mag_parameters)
