"""
LM 510 Level Monitor
"""

__all__ = ['cryolevels']

from ..session_logs import logger
logger.info(__file__)

from ophyd import Component, Device, EpicsSignal, EpicsSignalRO
from ..framework import sd


class CryoLevelMonitor(Device):


    # Cryo_1 LHe
    level_he = Component(EpicsSignalRO, 'cryo_1:LEVEL', kind='hinted',
                                labels=('cryolevels'))
    alarm_threshold_he = Component(EpicsSignalRO, 'cryo_1:HALARM', kind='omitted',
                                labels=('cryolevels'))
    alarm_threshold__he_set = Component(EpicsSignal, 'cryo_1:SETHALARM', kind='omitted',
                                labels=('cryolevels'))
    low_threshold_he = Component(EpicsSignalRO, 'cryo_1:LOW', kind='omitted',
                                labels=('cryolevels'))
    low_threshold_he_set = Component(EpicsSignal, 'cryo_1:SETLOW', kind='omitted',
                                labels=('cryolevels'))
    high_threshold_he = Component(EpicsSignalRO, 'cryo_1:HIGH', kind='omitted',
                                labels=('cryolevels'))
    high_threshold_he_set = Component(EpicsSignal, 'cryo_1:SETHIGH', kind='omitted',
                                labels=('cryolevels'))
    automated_refill_he = Component(EpicsSignalRO, 'cryo_1:CTRL', kind='config',
                                labels=('cryolevels'))
    automated_refill_he_set = Component(EpicsSignal, 'cryo_1:SETCTRL', kind='config',
                                labels=('cryolevels'))
    scan_he = Component(EpicsSignal, 'cryo_1:scanSeq.SCAN', kind='config',
                                labels=('cryolevels'))

    # Cryo_2 LN2 
    level_n2 = Component(EpicsSignalRO, 'cryo_2:LEVEL', kind='hinted',
                                labels=('cryolevels'))
    alarm_threshold_n2 = Component(EpicsSignalRO, 'cryo_2:HALARM', kind='omitted',
                                labels=('cryolevels'))
    alarm_threshold_n2_set = Component(EpicsSignal, 'cryo_2:SETHALARM', kind='omitted',
                                labels=('cryolevels'))
    low_threshold_n2 = Component(EpicsSignalRO, 'cryo_2:LOW', kind='omitted',
                                labels=('cryolevels'))
    low_threshold_n2_set = Component(EpicsSignal, 'cryo_2:SETLOW', kind='omitted',
                                labels=('cryolevels'))
    high_threshold_n2 = Component(EpicsSignalRO, 'cryo_2:HIGH', kind='omitted',
                                labels=('cryolevels'))
    high_threshold_n2_set = Component(EpicsSignal, 'cryo_2:SETHIGH', kind='omitted',
                                labels=('cryolevels'))
    automated_refill_n2 = Component(EpicsSignalRO, 'cryo_2:CTRL', kind='config',
                                labels=('cryolevels'))
    automated_refill_n2_set = Component(EpicsSignal, 'cryo_2:SETCTRL', kind='config',
                                labels=('cryolevels'))


levels = CryoLevelMonitor('4idd:', name='cryolevels')
sd.baseline.append(levels)
