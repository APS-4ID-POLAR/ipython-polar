
"""
our motors
"""

__all__ = [
    'diffractometer',
    ]

from ..session_logs import logger
logger.info(__file__)

from ophyd import Component, Device, EpicsMotor

class CryoStage(Device):
    x = Component(EpicsMotor, '4iddx:m14', labels=('motor', 'cryo'))  # Cryo X
    y = Component(EpicsMotor, '4iddx:m15', labels=('motor', 'cryo'))  # Cryo Y
    z = Component(EpicsMotor, '4iddx:m16', labels=('motor', 'cryo'))  # Cryo Z


class Diffractometer(Device):
    cryo = Component(CryoStage)
    # scaler = ScalerCH( ... )
    # filters = 
    # magnets = 


diffractometer = Diffractometer(name="diffractometer")
