"""
Filters
"""
__all__ = ['filter_pre8c', 'filter_tth']

from ophyd import Component, Device, EpicsSignal
from ..framework import sd

from ..session_logs import logger
logger.info(__file__)


class FilterBank(Device):

    slot1_name = Component(EpicsSignal, 'bo1.DESC', labels=('Filters'))
    slot1_position = Component(EpicsSignal, 'bo1.VAL', auto_monitor=True,
                               labels=('filters',))

    slot2_name = Component(EpicsSignal, 'bo2.DESC', labels=('filters',))
    slot2_position = Component(EpicsSignal, 'bo2.VAL', auto_monitor=True,
                               labels=('filters',))

    slot3_name = Component(EpicsSignal, 'bo3.DESC', labels=('filters',))
    slot3_position = Component(EpicsSignal, 'bo3.VAL', auto_monitor=True,
                               labels=('filters',))

    slot4_name = Component(EpicsSignal, 'bo4.DESC', labels=('filters',))
    slot4_position = Component(EpicsSignal, 'bo4.VAL', auto_monitor=True,
                               labels=('filters',))


filter_pre8c = FilterBank('4idd:PCFfilter:1:', name='filter_pre8c')
filter_tth = FilterBank('4idd:PCFfilter:2:', name='filter_tth')

sd.baseline.append(filter_pre8c)
sd.baseline.append(filter_tth)
