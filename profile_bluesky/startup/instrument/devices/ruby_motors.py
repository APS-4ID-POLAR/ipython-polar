"""
Ruby spectrometer motors.
"""
__all__ = [
    'ruby_mot'
    ]

from ..session_logs import logger
logger.info(__file__)

from ophyd import Component, MotorBundle, EpicsMotor
from ..framework import sd


class RubyMotors(MotorBundle):
    focus = Component(EpicsMotor, 'm37', labels=('motor', 'ruby'))
    y = Component(EpicsMotor, 'm38', labels=('motor', 'ruby'))
    z = Component(EpicsMotor, 'm39', labels=('motor', 'ruby'))
    zoom = Component(EpicsMotor, 'm40', labels=('motor', 'ruby'))


ruby_mot = RubyMotors('4iddx:', name='ruby_motors')
sd.baseline.append(ruby_mot)
