'''
Other motor/counters
'''

__all__ = ['kbic']

from ..session_logs import logger
logger.info(__file__)

from ophyd import Component, MotorBundle, EpicsMotor
from ..framework import sd


class KBIC(MotorBundle):
    y = Component(EpicsMotor, 'm34', labels=('motor', 'kbic'))  # KB IC Y
    x = Component(EpicsMotor, 'm33', labels=('motor', 'kbic'))  # KB IC X


kbic = KBIC('4iddx:', name='KBIC')
sd.baseline.append(kbic)

# TODO: Maybe other things that can be here? Like the motors for flags?
