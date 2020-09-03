"""
Magnet motors
"""

__all__ = [
    'mag6t',
    ]

from ..session_logs import logger
logger.info(__file__)

from ophyd import Component, Device, EpicsMotor
from ..framework import sd

## Magnet and sample motors ##
class Magnet6T(Device):

    ## Motors ##
    tabth = Component(EpicsMotor,'m53', labels=('motor','6T_magnet'))  # 4T Mag Th
    tabx = Component(EpicsMotor,'m49', labels=('motor','6T_magnet'))  # 4T MagTab X
    taby = Component(EpicsMotor,'m50', labels=('motor','6T_magnet'))  # 4T MagTab Y

    tabth2 = Component(EpicsMotor,'m56', labels=('motor','6T_magnet'))  # AMIMagnetPhi
    tabz2 = Component(EpicsMotor,'m51', labels=('motor','6T_magnet'))  # AMIMagnetZ
    tabx2 = Component(EpicsMotor,'m52', labels=('motor','6T_magnet'))  # AMIMagenetX

    sampy = Component(EpicsMotor,'m63', labels=('motor','6T_magnet'))  # CIATRA
    sampth = Component(EpicsMotor,'m58', labels=('motor','6T_magnet'))  # CIA ROT

    Tvaporizer = None
    Tsample = None


mag6t = Magnet6T('4iddx:',name='6T_magnet')
sd.baseline.append(mag6t)
# Tvaporizer = lakeshore_336.loop1
# Tsample = lakeshore_336.loop2

# TODO: Is it ok to add the lakeshores here?
# TODO: should we add the magnet field controls here?
