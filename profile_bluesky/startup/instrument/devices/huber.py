
"""
Diffractometer motors
"""

__all__ = [
    'cryo',
    'huber'
    ]

from ..session_logs import logger
logger.info(__file__)

from ophyd import Component, Device, EpicsMotor

## Cryo carrier ##
class CryoStage(Device):
    x = Component(EpicsMotor, '4iddx:m14', labels=('motor', 'cryo'))  # Cryo X
    y = Component(EpicsMotor, '4iddx:m15', labels=('motor', 'cryo'))  # Cryo Y
    z = Component(EpicsMotor, '4iddx:m16', labels=('motor', 'cryo'))  # Cryo Z

cryo = CryoStage(name='cryo')

## 8c rotations ##
class Diffractometer(Device):
    th = EpicsMotor('4iddx:m65', name='th', labels=('motor',))  # Theta # slop=2
    tth = EpicsMotor('4iddx:m66', name='tth', labels=('motor',))  # Two Theta
    phi = EpicsMotor('4iddx:m68', name='phi', labels=('motor',))  # Phi
    chi = EpicsMotor('4iddx:m67', name='chi', labels=('motor',))  # Chi
    bth = EpicsMotor('4iddx:m69', name='bth', labels=('motor',))  # Base Th
    btth = EpicsMotor('4iddx:m70', name='btth', labels=('motor',))  # Base tth
    ath = EpicsMotor('4iddx:m77', name='ath', labels=('motor',))  # Ana Theta
    achi = EpicsMotor('4iddx:m79', name='achi', labels=('motor',))  # Ana Chi
    atth = EpicsMotor('4iddx:m78', name='atth', labels=('motor',))  # Ana 2Theta
    x = EpicsMotor('4iddx:m18', name='hcirc', labels=('motor',))  # 8C horiz
    y = EpicsMotor('4iddx:m17', name='vcirc', labels=('motor',))  # 8C verical

huber = Diffractometer(name='huber')

# TODO: look at todo folder. Use hklpy when setting these up, so that we
#       can create fourc and sixc

# TODO: discuss the extend of which we want to add classes like the one below
#class Diffractometer(Device):
#   cryo = Component(CryoStage)
#   scaler = ScalerCH( ... )
#   filters =
#   magnets =
#diffractometer = Diffractometer(name="diffractometer")
