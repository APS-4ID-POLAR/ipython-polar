'''
Other motor/counters
'''

__all__ = ['xbpm']

from ..session_logs import logger
logger.info(__file__)

from ophyd import Component, EpicsMotor, MotorBundle
from ..framework import sd


class XBPM(MotorBundle):
    y = Component(EpicsMotor, 'm20', labels=('motor', 'xbpm'))
    x = Component(EpicsMotor, 'm19', labels=('motor', 'xbpm'))


xbpm = XBPM('4iddx:', name='XBPM')
sd.baseline.append(xbpm)
