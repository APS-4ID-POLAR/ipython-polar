
"""
our motors
"""

__all__ = [
    'diffractometer',
    ]

from ..session_logs import logger
logger.info(__file__)

from ophyd.sim import motor
from ophyd import Component,Device

class CryoStage(Device):
    x = motor  # Cryo X
    y = motor # Cryo Y
    z = motor # Cryo Z


class Diffractometer(Device):
    cryo = Component(CryoStage)
    # scaler = ScalerCH( ... )
    # filters =
    # magnets =


diffractometer = Diffractometer(name="diffractometer")
