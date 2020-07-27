'''
Other motor/counters
'''

__all__ = [
    'uptab','kbic','xbpm'
    ]

from ..session_logs import logger
logger.info(__file__)

from ophyd import Component, Device, EpicsMotor

class UpTable(Device):
    y = Component(EpicsMotor, '4iddx:m10', labels=('motor','uptable'))  # Uptable Y
    x = Component(EpicsMotor, '4iddx:m9', labels=('motor','uptable'))  # Uptable Y

uptab = UpTable(name='uptable')

class KBIC(Device):
    y = Component(EpicsMotor, '4iddx:m34', labels=('motor','KBIC'))  # KB IC Y
    x = Component(EpicsMotor, '4iddx:m33', labels=('motor','KBIC'))  # KB IC X

kbic = KBIC(name='KBIC')


class XBPM(Device):
    y = Component(EpicsMotor, '4iddx:m20', labels=('motor','XBPM'))  # XBPM ver
    x = Component(EpicsMotor, '4iddx:m19', labels=('motor','XBPM'))  # XBPM hor

xbpm = XBPM(name='XBPM')
