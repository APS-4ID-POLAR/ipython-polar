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
    y = Component(EpicsMotor, 'm10', labels=('motor','uptable'))  # Uptable Y
    x = Component(EpicsMotor, 'm9', labels=('motor','uptable'))  # Uptable Y

uptab = UpTable('4iddx:',name='uptable')

class KBIC(Device):
    y = Component(EpicsMotor, 'm34', labels=('motor','kbic'))  # KB IC Y
    x = Component(EpicsMotor, 'm33', labels=('motor','kbic'))  # KB IC X

kbic = KBIC('4iddx:',name='KBIC')


class XBPM(Device):
    y = Component(EpicsMotor, 'm20', labels=('motor','XBPM'))  # XBPM ver
    x = Component(EpicsMotor, 'm19', labels=('motor','XBPM'))  # XBPM hor

xbpm = XBPM('4iddx:',name='XBPM')

# TODO: Maybe other things that can be here? Like the motors for flags?
