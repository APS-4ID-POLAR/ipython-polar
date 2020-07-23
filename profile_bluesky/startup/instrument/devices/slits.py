"""
Slits
"""

__all__ = ['enslt']

from instrument.session_logs import logger
logger.info(__file__)

from ophyd import Component, Device, EpicsMotor,EpicsSignal

class SlitDevice(Device):

    # top = None
    # bot = None
    # out = None
    # inb = None
    # vsize = None
    # vcen  = None
    # hsize = None
    # hcen  = None

    def __init__(PV,motorsDict,signalsDict,**kwargs):
        super().__init__(PV,**kwargs)

        name = ''
        if 'name' in kwargs.keys():
            if kwargs['name'] is not None:
                name = kwargs['name']+'.'

        for key in motorsDict.keys():
            setattr(self,key,Component(EpicsMotor, motorsDict[key],
                                       name = name+key, labels=('motor','slits')))

        for key in signalsDict.keys():
            setattr(self,key,Component(EpicsSignal, signalsDict[key],
                                       name = name+key, labels=('slits')))

            # self.make_centers_sizes(slitPV)

    # def make_centers_sizes(self,slitPV):
        # self.vsize = Component(EpicsSignal,slitPV+'Vsize', labels=['slits'])
        # self.vcen  = Component(EpicsSignal,slitPV+'Vcenter', labels=['slits'])
        # self.hsize = Component(EpicsSignal,slitPV+'Hsize', labels=['slits'])
        # self.hcen  = Component(EpicsSignal,slitPV+'Hcenter', labels=['slits'])

    # TODO: these read, but can't scan, options:
    # This may be fine. We just need to do create a plan to that scans the center.
    # or use: from ophyd import PVPositioner, PseudoPositioner ??

enslt = SlitDevice('4iddx:',
                   {'top': ':m1','bot',':m2','out':':m3','inb':':m4'},
                   {'vcen': ':Slit1Vcenter','vsize': ':Slit1Vsize',
                    'hcen': ':Slit1Hcenter','hsize': ':Slit1Hsize'},
                   name='enslt')
