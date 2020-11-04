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

    hv_setpoint = Component(EpicsSignal, 'SetHV.A', kind='omitted',
                            labels=('apd'))
    hv_readback = Component(EpicsSignalRO, 'HV.VAL', kind='config',
                            labels=('apd'))
    hv_on = Component(EpicsSignal, 'HVOnOff.VAL', kind='config',
                      labels=('apd'))

    sca_mode = Component(EpicsSignal, 'SetSCAMode.VAL', kind='config',
                         labels=('apd'))
    sca_outtime = Component(EpicsSignal, 'SetOutTime.VAL', kind='config',
                            labels=('apd'))
    sca_low_setpoint = Component(EpicsSignal, 'SetSCALevel.A', kind='omitted',
                                 labels=('apd'))
    sca_low_readback = Component(EpicsSignalRO, 'SCAlow.VAL', kind='config',
                                 labels=('apd'))
    sca_window_readback = Component(EpicsSignalRO, 'SCAwin.VAL', kind='config',
                                    labels=('apd'))
    sca_window_setpoint = Component(EpicsSignal, 'SetSCALevel.B',
                                    kind='omitted', labels=('apd'))


apd_parameters = APDDevice('4idd:apd:1:', name='apd')
sd.baseline.append(apd_parameters)
