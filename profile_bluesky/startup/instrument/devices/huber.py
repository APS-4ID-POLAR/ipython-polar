
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
    x = Component(EpicsMotor, 'm14', labels=('motor', 'cryo'))  # Cryo X
    y = Component(EpicsMotor, 'm15', labels=('motor', 'cryo'))  # Cryo Y
    z = Component(EpicsMotor, 'm16', labels=('motor', 'cryo'))  # Cryo Z

cryo = CryoStage(prefix='4iddx:',name='cryo')

## 8c rotations ##
class Diffractometer(Device):
    th = Component(EpicsMotor,'m65', labels=('motor','diffractometer'))  # Theta # slop=2
    tth = Component(EpicsMotor,'m66', labels=('motor','diffractometer'))  # Two Theta
    phi = Component(EpicsMotor,'m68', labels=('motor','diffractometer'))  # Phi
    chi = Component(EpicsMotor,'m67', labels=('motor','diffractometer'))  # Chi
    bth = Component(EpicsMotor,'m69', labels=('motor','diffractometer'))  # Base Th
    btth = Component(EpicsMotor,'m70', labels=('motor','diffractometer'))  # Base tth
    ath = Component(EpicsMotor,'m77', labels=('motor','diffractometer'))  # Ana Theta
    achi = Component(EpicsMotor,'m79', labels=('motor','diffractometer'))  # Ana Chi
    atth = Component(EpicsMotor,'m78', labels=('motor','diffractometer'))  # Ana 2Theta
    x = Component(EpicsMotor,'m18', labels=('motor','diffractometer'))  # 8C horiz
    y = Component(EpicsMotor,'m17', labels=('motor','diffractometer'))  # 8C verical

huber = Diffractometer(prefix='4iddx:',name='huber')

# TODO: look at todo folder. Use hklpy when setting these up, so that we
#       can create fourc and sixc

# TODO: discuss the extend of which we want to add classes like the one below
#class Diffractometer(Device):
#   cryo = Component(CryoStage)
#   scaler = ScalerCH( ... )
#   filters =
#   magnets =
#diffractometer = Diffractometer(name="diffractometer")
