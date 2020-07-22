"""
Slits
"""

__all__ = ['si1', 'si2', 'si3', 'si4', 'si5', 'sipink']

from instrument.session_logs import logger
logger.info(__file__)

from ophyd import Component, Device, EpicsMotor

class SlitDevice(Device):

    def __init__(self,name,motors,pvs):
        """ General slit Device
        """
        super().__init__(name=name, **kwargs)
        self.motors = motors
        self.pvs = pvs

    in = EpicsMotor(self.motors['in'], name='inb', labels=('motor',))
    out = EpicsMotor(self.motors['out'], name='outb', labels=('motor',))
    top = EpicsMotor(self.motors['top'], name='top', labels=('motor',))
    bot = EpicsMotor(self.motors['bot'], name='bot', labels=('motor',))
    vsize = Component(EpicsMotor, self.pvs['vsize'], labels=["motor",])
    vcen = Component(EpicsMotor, self.pvs['vscen'], labels=["motor",])
    hsize = Component(EpicsMotor, self.pvs['hsize'], labels=["motor",])
    hcen = Component(EpicsMotor, self.pvs['hcen'], labels=["motor",])

# entrance Slits
motors = {'top': '4iddx:m1','bot': '4iddx:m2',
          'out': '4iddx:m3','in': '4iddx:m4'}
pvs = {'hsize': '4iddx:Slit1Hsize','hcen': '4iddx:Slit1Hcenter',
       'vsize': '4iddx:Slit1Vsize','vcen': '4iddx:Slit1Vcenter'}

enslt = SlitDevice(name='enslt',motors,pvs)
