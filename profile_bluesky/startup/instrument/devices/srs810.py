"""
SRS 810 Lock-in
"""

__all__ = ['lockin']

from ophyd import Component, Device, EpicsSignal, EpicsSignalRO
from ..framework import sd

from ..session_logs import logger
logger.info(__file__)


class LockinDevice(Device):

    # Time constant
    time_multiplier = Component(EpicsSignal, 'TC1', kind='omitted',
                                labels=('lockin',))
    time_decade = Component(EpicsSignal, 'TC2', kind='omitted',
                            labels=('lockin',))
    time_unit = Component(EpicsSignal, 'TC3', kind='config',
                          labels=('lockin',))
    time_filter = Component(EpicsSignal, 'FiltCh', kind='omitted',
                            labels=('lockin',))
    time_readback = Component(EpicsSignalRO, 'TC.SVAL', kind='config',
                              labels=('lockin',))

    # Gain
    gain_multiplier = Component(EpicsSignal, 'Sens1', kind='omitted',
                                labels=('lockin',))
    gain_decade = Component(EpicsSignal, 'Sens2', kind='omitted',
                            labels=('lockin',))
    gain_unit = Component(EpicsSignal, 'Sens3', kind='config',
                          labels=('lockin',))
    gain_readback = Component(EpicsSignalRO, 'Sens.SVAL', kind='config',
                              labels=('lockin',))

    # Reserve
    reserve = Component(EpicsSignal, 'ResvCh', kind='config',
                        labels=('lockin',))

    # Reference
    reference_freq = Component(EpicsSignalRO, 'Freq.SVAL', kind='config',
                               labels=('lockin',))
    reference_phase = Component(EpicsSignal, 'Phas.SVAL', write_pv='Phas.SVAL',
                                kind='config', labels=('lockin',))

    # Channel 1 outputs
    chan1_x = Component(EpicsSignalRO, 'X.SVAL', kind='hinted',
                        labels=('lockin',))
    chan1_y = Component(EpicsSignalRO, 'Y.SVAL', kind='hinted',
                        labels=('lockin',))
    chan1_r = Component(EpicsSignalRO, 'R.SVAL', kind='hinted',
                        labels=('lockin',))
    chan1_q = Component(EpicsSignalRO, 'Th.SVAL', kind='hinted',
                        labels=('lockin',))


lockin = LockinDevice('4idd:SRS810:1:', name='lockin')
sd.baseline.append(lockin)
# TODO: There are a bunch of "read" buttons should I add them here?
# TODO: Channel2 outputs?
