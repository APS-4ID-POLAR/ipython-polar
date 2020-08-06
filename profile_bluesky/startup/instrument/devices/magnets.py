"""
Magnet motors
"""

__all__ = [
    'mag6t',
    ]

from ..session_logs import logger
logger.info(__file__)

from ophyd import Component, Device, EpicsMotor, FormattedComponent
from .lakeshore import LS336_LoopMore

## Magnet and sample motors ##
class Magnet6T(Device):

    ## Motors ##
    tabth = Component(EpicsMotor,'m53', labels=('motor','6T magnet'))  # 4T Mag Th
    tabx = Component(EpicsMotor,'m49', labels=('motor','6T magnet'))  # 4T MagTab X
    taby = Component(EpicsMotor,'m50', labels=('motor','6T magnet'))  # 4T MagTab Y

    tabth2 = Component(EpicsMotor,'m56', labels=('motor','6T magnet'))  # AMIMagnetPhi
    tabz2 = Component(EpicsMotor,'m51', labels=('motor','6T magnet'))  # AMIMagnetZ
    tabx2 = Component(EpicsMotor,'m52', labels=('motor','6T magnet'))  # AMIMagenetX

    sampy = Component(EpicsMotor,'m63', labels=('motor','6T magnet'))  # CIATRA
    sampth = Component(EpicsMotor,'m58', labels=('motor','6T magnet'))  # CIA ROT

    Tvaporizer = FormattedComponent(LS336_LoopMore, "4idd:LS336:TC3", loop_number=1)
    Tsample = FormattedComponent(LS336_LoopMore, "4idd:LS336:TC3", loop_number=2)


mag6t = Magnet6T('4iddx:',name='6T magnet')

# TODO: should we add the magnet field controls here?
