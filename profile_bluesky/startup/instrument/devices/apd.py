"""
APD detector
"""

__all__ = ['apd_parameters']

from ..session_logs import logger
logger.info(__file__)

from ophyd import Component, Device, EpicsSignal, EpicsSignalRO
from ..framework import sd


class APDDevice(Device):

    source = Component(EpicsSignal, 'SetCSRC', kind='config', labels=('apd'))
    read_scan = Component(EpicsSignal, 'ReadCounts.SCAN', kind='config',
                          labels=('apd'))
    count_time = Component(EpicsSignal, 'CountTime.A', kind='config',
                           labels=('apd'))

    hv = Component(EpicsSignalRO, 'HV.VAL', write_pv='SetHV.A',
                   kind='config', labels=('apd'))
    hv_on = Component(EpicsSignal, 'HVOnOff.VAL', kind='config',
                      labels=('apd'))

    sca_mode = Component(EpicsSignal, 'SetSCAMode.VAL', kind='config',
                         labels=('apd'))
    sca_outtime = Component(EpicsSignal, 'SetOutTime.VAL', kind='config',
                            labels=('apd'))
    sca_low = Component(EpicsSignalRO, 'SCAlow.VAL', write_pv='SetSCALevel.A',
                        kind='config', labels=('apd'))
    sca_window = Component(EpicsSignalRO, 'SCAwin.VAL',
                           write_pv='SetSCALevel.B', kind='config',
                           labels=('apd'))


apd_parameters = APDDevice('4idd:apd:1:', name='apd')
sd.baseline.append(apd_parameters)
