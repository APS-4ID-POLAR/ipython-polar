"""
Slits
"""

__all__ = ['wbslt,''enslt','inslt','grdslt','detslt','magslt']

from instrument.session_logs import logger
logger.info(__file__)

from ophyd import Device, EpicsMotor,EpicsSignal

class SlitDevice(Device):

    def __init__(self,PV,motorsDict,signalsDict,name,slitnum = None,**kwargs):
        super().__init__(prefix=PV, name=name, **kwargs)

        for key in motorsDict.keys():
            setattr(self,key,EpicsMotor(PV+motorsDict[key], name=key,
                                        labels=('motor','slits'),parent=self))

        if signalsDict is None:
            if type(slitnum) != int:
                raise TypeError('slitnum has to be an integer!')
            else:
                prefix = 'Slit{}'.format(slitnum)
                signalsDict = {'vcen': [prefix+'Vt2.D',prefix+'Vcenter'],
                               'vsize':[prefix+'Vt2.C',prefix+'Vsize'],
                               'hcen': [prefix+'Ht2.D',prefix+'Hcenter'],
                               'hsize':[prefix+'Ht2.C',prefix+'Hsize']}

        for key in signalsDict.keys():
            setattr(self,key,EpicsSignal(PV+signalsDict[key][0],
                                         write_pv = PV+signalsDict[key][1],
                                         name=key,
                                         labels=('slits'),parent=self))

# TODO: Do we need to change the "name" of these devices? Depends on how it
# is saved in the database.

# TODO: There are PVs for the limits of the EpicsSignals, should I add them?
# Slit4Vsize.DRVH (high lim), .DRVL is low lim. Not clear how to set the PV name
# of the limits.


## White beam slit ##
wbslt = SlitDevice('4idb:',
                   {'top': 'm25','bot':'m26','out':'m27','inb':'m28'},
                   None,'wbslt',slitnum=1)

## Entrance slit ##
enslt = SlitDevice('4iddx:',
                   {'top': 'm1','bot':'m2','out':'m3','inb':'m4'},
                   None,'enslt',slitnum=1)

## 8C incident slit ##
inslt = SlitDevice('4iddx:',
                   {'top': 'm5','bot':'m6','out':'m7','inb':'m11'},
                   None,'inslt',slitnum=2)

## 2th guard slit ##
grdslt = SlitDevice('4iddx:',
                    {'top': 'm21','bot':'m22','out':'m23','inb':'m24'},
                    None,'grdslt',slitnum=3)

## 2th detector slit ##
detslt = SlitDevice('4iddx:',
                    {'top': 'm25','bot':'m26','out':'m27','inb':'m28'},
                    None,'detslt',slitnum=4)

## 2th detector slit ##
magslt = SlitDevice('4iddx:',
                    {'top': 'm29','bot':'m30','out':'m31','inb':'m32'},
                    None,'magslt',slitnum=5)
