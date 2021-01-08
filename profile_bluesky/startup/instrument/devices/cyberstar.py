"""
APD detector
"""
__all__ = ['cyberstar_mag_parameters', 'cyberstar_8c_parameters']

from ..session_logs import logger
logger.info(__file__)

from ophyd import Component, Device, EpicsSignal
from ..framework import sd


class CyberstarDevice(Device):

    hv = Component(EpicsSignal, 'HV.VAL', write_pv='SetHV.A',
                   kind='config', labels=('cyberstar',))

    remote_on = Component(EpicsSignal, 'Remote.VAL', kind='config',
                          labels=('cyberstar',))

    gain = Component(EpicsSignal, 'Gain.VAL', write_pv='SetGain.VAL',
                     kind='config', labels=('cyberstar',))

    peak_time = Component(EpicsSignal, 'Pktime.VAL', write_pv='SetPktime.VAL',
                          kind='config', labels=('cyberstar',))

    sca_low = Component(EpicsSignal, 'SCAlo.VAL', write_pv='SetSCAlo.VAL',
                        kind='config', labels=('cyberstar',))

    sca_window = Component(EpicsSignal, 'SCAhi.VAL', write_pv='SetSCAhi.VAL',
                           kind='config', labels=('cyberstar',))


cyberstar_mag_parameters = CyberstarDevice('4idd:x1k:2:', name='cyberstar_mag')
cyberstar_8c_parameters = CyberstarDevice('4idd:x1k:1:', name='cyberstar_8c')
sd.baseline.append(cyberstar_8c_parameters)
sd.baseline.append(cyberstar_mag_parameters)
