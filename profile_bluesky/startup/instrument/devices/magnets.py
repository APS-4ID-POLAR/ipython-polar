"""
Magnet motors
"""

__all__ = [
    'mag6t',
    ]

from ..session_logs import logger
logger.info(__file__)

from ophyd import Component, Device, EpicsMotor

## Magnet and sample motors ##
class Magnet6T(Device):
    tabth = EpicsMotor('4iddx:m53', name='th', labels=('motor',))  # 4T Mag Th
    tabx = EpicsMotor('4iddx:m49', name='x', labels=('motor',))  # 4T MagTab X
    taby = EpicsMotor('4iddx:m50', name='y', labels=('motor',))  # 4T MagTab Y

    tabth2 = EpicsMotor('4iddx:m56', name='th2', labels=('motor',))  # AMIMagnetPhi
    tabz2 = EpicsMotor('4iddx:m51', name='z2', labels=('motor',))  # AMIMagnetZ
    tabx2 = EpicsMotor('4iddx:m52', name='x2', labels=('motor',))  # AMIMagenetX

    sampy = EpicsMotor('4iddx:m63', name='sampy', labels=('motor',))  # CIATRA
    sampth = EpicsMotor('4iddx:m58', name='sampth', labels=('motor',))  # CIA ROT

mag6t = Magnet6T(name='magnet')

# TODO: should we add the magnet field controls here?
