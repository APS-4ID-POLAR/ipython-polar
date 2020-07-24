"""
Slits
"""

__all__ = ['enslt']

from instrument.session_logs import logger
logger.info(__file__)

from ophyd import Device, EpicsMotor,EpicsSignal

class SlitDevice(Device):

    def __init__(self,PV,motorsDict,signalsDict,name,**kwargs):
        super().__init__(prefix=PV, name=name, **kwargs)

        for key in motorsDict.keys():
            setattr(self,key,EpicsMotor(PV+motorsDict[key], name=key,
                                        labels=('motor','slits'),parent=self))
        for key in signalsDict.keys():
            setattr(self,key,EpicsSignal(PV+signalsDict[key][0],
                                         write_pv = PV+signalsDict[key][1],
                                         name=key,
                                         labels=('slits'),parent=self))

# TODO: Do we need to change the "name" of these devices? Depends on how it
# is saved in the database.

enslt = SlitDevice('4iddx:',
                   {'top': 'm1','bot':'m2','out':'m3','inb':'m4'},
                   {'vcen': ['Slit1Vt2.D','Slit1Vcenter'],
                    'vsize':['Slit1Vt2.C','Slit1Vsize'],
                    'hcen': ['Slit1Ht2.D','Slit1Hcenter'],
                    'hsize':['Slit1Hsize','Slit1Hsize']},
                   'enslt')
