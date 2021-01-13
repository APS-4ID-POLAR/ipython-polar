"""
Wavefunction generator.
"""

__all__ = ['wavefunc_gen']


from ..session_logs import logger
logger.info(__file__)

from ophyd import Device, EpicsSignal, Kind, Component
from ..framework import sd


class SRS340(Device):

    frequency = Component(EpicsSignal, 'FREQ.VAL', write_pv='SetFREQ.A',
                          kind=Kind.config, labels=('phase retarders'))

    amplitude = Component(EpicsSignal, 'AMPL.VAL', write_pv='SetAMPL.A',
                          kind=Kind.config, labels=('phase retarders'))

    offset = Component(EpicsSignal, 'OFFS.VAL', write_pv='SetOFFS.A',
                       kind=Kind.config, labels=('phase retarders'))

    function = Component(EpicsSignal, 'FUNC.SVAL', write_pv='FUNCs.VAL',
                         kind=Kind.config, labels=('phase retarders'))


wavefunc_gen = SRS340('4idd:SRS340:1:', name='wavefunction_generator')
sd.baseline.append(wavefunc_gen)
