"""
SRS 810 Lock-in
"""

__all__ = ['lockin']

from ..session_logs import logger
logger.info(__file__)

from ophyd import Component, Device, EpicsSignal, EpicsSignalRO
from ..framework import sd


class LockinDevice(Device):

    # Time constant
    time_multiplier = Component(EpicsSignal, 'TC1', kind='omitted',
                                label=('lockin'))
    time_decade = Component(EpicsSignal, 'TC2', kind='omitted',
                            label=('lockin'))
    time_unit = Component(EpicsSignal, 'TC3', kind='config', label=('lockin'))
    time_filter = Component(EpicsSignal, 'FiltCh', kind='omitted',
                            label=('lockin'))
    time_readback = Component(EpicsSignalRO, 'TC.SVAL', kind='config',
                              label=('lockin'))

    # Gain
    gain_multiplier = Component(EpicsSignal, 'Sens1', kind='omitted',
                                label=('lockin'))
    gain_decade = Component(EpicsSignal, 'Sens2', kind='omitted',
                            label=('lockin'))
    gain_unit = Component(EpicsSignal, 'Sens3', kind='config',
                          label=('lockin'))
    gain_readback = Component(EpicsSignalRO, 'Sens.SVAL', kind='config',
                              label=('lockin'))

    # Reserve
    reserve = Component(EpicsSignal, 'ResvCh', kind='config',
                        label=('lockin'))

    # Reference
    reference_freq = Component(EpicsSignalRO, 'Freq.SVAL', kind='config',
                               label=('lockin'))
    reference_phase = Component(EpicsSignalRO, 'Phas.SVAL', kind='config',
                                label=('lockin'))
    reference_phase_set = Component(EpicsSignal, 'Phas.SVAL', kind='omitted',
                                    label=('lockin'))

    # Channel 1 outputs
    chan1_x = Component(EpicsSignalRO, 'X.SVAL', kind='hinted',
                        label=('lockin'))
    chan1_y = Component(EpicsSignalRO, 'Y.SVAL', kind='hinted',
                        label=('lockin'))
    chan1_r = Component(EpicsSignalRO, 'R.SVAL', kind='hinted',
                        label=('lockin'))
    chan1_q = Component(EpicsSignalRO, 'Th.SVAL', kind='hinted',
                        label=('lockin'))


lockin = LockinDevice('4idd:SRS810:1:', name='lockin')
sd.baseline.append(lockin)
# TODO: There are a bunch of "read" buttons should I add them here?
# TODO: Channel2 outputs?
