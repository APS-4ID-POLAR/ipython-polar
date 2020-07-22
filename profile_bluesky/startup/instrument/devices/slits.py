"""
Slits
"""

__all__ = ['enslt']

from instrument.session_logs import logger
logger.info(__file__)

from ophyd import Component, Device, EpicsMotor,EpicsSignal

class EntranceSlitDevice(Device):

    in = EpicsMotor('4iddx:m4', name='inb', labels=('motor',))
    out = EpicsMotor('4iddx:m3', name='outb', labels=('motor',))
    top = EpicsMotor('4iddx:m1', name='top', labels=('motor',))
    bot = EpicsMotor('4iddx:m2', name='bot', labels=('motor',))
    #vsize = Component(EpicsSignal, '4iddx:Slit1Vsize', labels=["motor",])
    #vcen = Component(EpicsSignal, '4iddx:Slit1Vcenter', labels=["motor",])
    #hsize = Component(EpicsSignal, '4iddx:Slit1Hsize', labels=["motor",])
    #hcen = Component(EpicsSignal, '4iddx:Slit1Hcenter', labels=["motor",])
    # TODO: these read, but can't scan.

enslt = EntranceSlitDevice(name='enslt')
