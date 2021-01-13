"""
Filters
"""
__all__ = ['filter_pre8c', 'filter_tth']

from ..session_logs import logger
logger.info(__file__)

from ophyd import Component, Device, EpicsSignal
from ..framework import sd


class FilterBank(Device):

    slot1_name = Component(EpicsSignal, 'bo1.DESC', kind='config',
                           labels=('Filters'))
    slot1_position = Component(EpicsSignal, 'bo1.VAL', kind='config',
                               labels=('filters',))

    slot2_name = Component(EpicsSignal, 'bo2.DESC', kind='config',
                           labels=('filters',))
    slot2_position = Component(EpicsSignal, 'bo2.VAL', kind='config',
                               labels=('filters',))

    slot3_name = Component(EpicsSignal, 'bo3.DESC', kind='config',
                           labels=('filters',))
    slot3_position = Component(EpicsSignal, 'bo3.VAL', kind='config',
                               labels=('filters',))

    slot4_name = Component(EpicsSignal, 'bo4.DESC', kind='config',
                           labels=('filters',))
    slot4_position = Component(EpicsSignal, 'bo4.VAL', kind='config',
                               labels=('filters',))


filter_pre8c = FilterBank('4idd:PCFfilter:1:', name='filter_pre8c')
filter_tth = FilterBank('4idd:PCFfilter:2:', name='filter_tth')

sd.baseline.append(filter_pre8c)
sd.baseline.append(filter_tth)
