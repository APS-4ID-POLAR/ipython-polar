"""
Magnet motors
"""

__all__ = ['mag6t']

from ophyd import Component, Device, EpicsMotor
from ..framework import sd

from ..session_logs import logger
logger.info(__file__)


class Magnet6T(Device):

    # Motors
    tabth = Component(EpicsMotor, 'm53', labels=('motor', 'magnet'))
    tabx = Component(EpicsMotor, 'm49', labels=('motor', 'magnet'))
    taby = Component(EpicsMotor, 'm50', labels=('motor', 'magnet'))

    tabth2 = Component(EpicsMotor, 'm56', labels=('motor', 'magnet'))
    tabz2 = Component(EpicsMotor, 'm51', labels=('motor', 'magnet'))
    tabx2 = Component(EpicsMotor, 'm52', labels=('motor', 'magnet'))

    sampy = Component(EpicsMotor, 'm63', labels=('motor', 'magnet'))
    sampth = Component(EpicsMotor, 'm58', labels=('motor', 'magnet'))

    Tvaporizer = None
    Tsample = None


mag6t = Magnet6T('4iddx:', name='6T_magnet')
sd.baseline.append(mag6t)
