"""
Slits
"""

__all__ = ['wbslt','enslt','inslt','grdslt','detslt','magslt']

from instrument.session_logs import logger
logger.info(__file__)

from ophyd import Device, EpicsMotor, EpicsSignal, FormattedComponent

class SlitDevice(Device):

    ## Setting motors ##
    top = FormattedComponent(EpicsMotor,'{self.prefix}:{_motorsDict[top]}',
                             labels=('motor','slit'))

    bot = FormattedComponent(EpicsMotor,'{self.prefix}:{_motorsDict[bot]}',
                             labels=('motor','slit'))

    out = FormattedComponent(EpicsMotor,'{self.prefix}:{_motorsDict[out]}',
                             labels=('motor','slit'))

    inb = FormattedComponent(EpicsMotor,'{self.prefix}:{_motorsDict[inb]}',
                             labels=('motor','slit'))

    ## Setting pseudo positioners ##
    vcen = FormattedComponent(EpicsSignal,'{self.prefix}:{_signalsDict[vcen][0]}',
                              write_pv = '{self.prefix}:{_signalsDict[vcen][1]}',
                              labels=('slit'))

    hcen = FormattedComponent(EpicsSignal,'{self.prefix}:{_signalsDict[hcen][0]}',
                              write_pv = '{self.prefix}:{_signalsDict[hcen][1]}',
                              labels=('slit'))

    vsize = FormattedComponent(EpicsSignal,'{self.prefix}:{_signalsDict[vsize][0]}',
                               write_pv = '{self.prefix}:{_signalsDict[vsize][1]}',
                               labels=('slit'))

    hsize = FormattedComponent(EpicsSignal,'{self.prefix}:{_signalsDict[hsize][0]}',
                               write_pv = '{self.prefix}:{_signalsDict[hsize][1]}',
                               labels=('slit'))


    def __init__(self,PV,name,motorsDict,slitnum = None, signalsDict = None,**kwargs):

        self._motorsDict = motorsDict

        if signalsDict is None:
            if type(slitnum) != int:
                raise TypeError('If signalsDict is None, then slitnum has to be an integer!')
            else:
                prefix = 'Slit{}'.format(slitnum)
                self._signalsDict = {'vcen': [prefix+'Vt2.D',prefix+'Vcenter'],
                                     'vsize':[prefix+'Vt2.C',prefix+'Vsize'],
                                     'hcen': [prefix+'Ht2.D',prefix+'Hcenter'],
                                     'hsize':[prefix+'Ht2.C',prefix+'Hsize']}
        else:
            self._signalsDict = signalsDict

        super().__init__(prefix=PV, name=name, **kwargs)

## White beam slit ##
wbslt = SlitDevice('4idb','wbslt',
                   {'top': 'm25','bot':'m26','out':'m27','inb':'m28'},
                   slitnum=1)

## Entrance slit ##
enslt = SlitDevice('4iddx','enslt',
                   {'top': 'm1','bot':'m2','out':'m3','inb':'m4'},
                   slitnum=1)

## 8C incident slit ##
inslt = SlitDevice('4iddx','inslt',
                   {'top': 'm5','bot':'m6','out':'m7','inb':'m11'},
                   slitnum=2)

## 2th guard slit ##
grdslt = SlitDevice('4iddx','grdslt',
                    {'top': 'm21','bot':'m22','out':'m23','inb':'m24'},
                    slitnum=3)

## 2th detector slit ##
detslt = SlitDevice('4iddx','detslt',
                    {'top': 'm25','bot':'m26','out':'m27','inb':'m28'},
                    slitnum=4)

## Magnet incident slit ##
magslt = SlitDevice('4iddx','magslt',
                    {'top': 'm29','bot':'m30','out':'m31','inb':'m32'},
                    slitnum=5)

# TODO: Test limits on EpicsSignal.
