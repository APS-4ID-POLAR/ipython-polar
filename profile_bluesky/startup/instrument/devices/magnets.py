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
    tabth = Compoent(EpicsMotor,':m53', labels=('motor',))  # 4T Mag Th
    tabx = Compoent(EpicsMotor,':m49', labels=('motor',))  # 4T MagTab X
    taby = Compoent(EpicsMotor,':m50', labels=('motor',))  # 4T MagTab Y

    tabth2 = Compoent(EpicsMotor,':m56', labels=('motor',))  # AMIMagnetPhi
    tabz2 = Compoent(EpicsMotor,':m51', labels=('motor',))  # AMIMagnetZ
    tabx2 = Compoent(EpicsMotor,':m52', labels=('motor',))  # AMIMagenetX

    sampy = Compoent(EpicsMotor,':m63', labels=('motor',))  # CIATRA
    sampth = Compoent(EpicsMotor,':m58', labels=('motor',))  # CIA ROT

mag6t = Magnet6T('4iddx',name='magnet')

# TODO: should we add the magnet field controls here?
