"""
Slits
"""

__all__ = ['enslt']

from instrument.session_logs import logger
logger.info(__file__)

from ophyd import Component, Device, EpicsMotor,EpicsSignal

class SlitDevice(Device):


    top = Component(EpicsMotor,':m1', name='inb', labels=('motor','slits'))
    bot = Component(EpicsMotor,':m2', name='inb', labels=('motor','slits'))
    out = Component(EpicsMotor,':m3', name='inb', labels=('motor','slits'))
    inb = Component(EpicsMotor,':m4', name='inb', labels=('motor','slits'))

    vsize = None
    vcen  = None
    hsize = None
    hcen  = None

    def __init__(PV,slitPV,**kwargs):
        super().__init__(PV,**kwargs)
        self.make_centers_sizes(slitPV)

    def make_centers_sizes(self,slitPV):
        self.vsize = Component(EpicsSignal,slitPV+'Vsize', labels=['slits'])
        self.vcen  = Component(EpicsSignal,slitPV+'Vcenter', labels=['slits'])
        self.hsize = Component(EpicsSignal,slitPV+'Hsize', labels=['slits'])
        self.hcen  = Component(EpicsSignal,slitPV+'Hcenter', labels=['slits'])

    # TODO: these read, but can't scan, options:
    # This may be fine. We just need to do create a plan to that scans the center.
    # or use: from ophyd import PVPositioner, PseudoPositioner ??

enslt = SlitDevice('4iddx:',':Slit1',name='enslt')
