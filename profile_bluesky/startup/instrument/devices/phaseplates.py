"""
Phase retarders
"""

__all__ = [
    'pr1','pr2','pr3'
    ]

from ..session_logs import logger
logger.info(__file__)

from ophyd import Component, Device, EpicsMotor

class PRDevice(Device):

    def __init__(PV,motorsPVdict,name,**kwargs):
        super().__init__(prefix=PV, name=name, **kwargs)

        for key in motorsPVDict.keys():
            setattr(self,key,EpicsMotor(PV+motorsDict[key], name=key,
                                        labels=('motor','phase retarders'),parent=self))

pr1 = PRDevice('4idb:',{'x':'m10','y':'m11','th':'m13'},'pr1')
pr2 = PRDevice('4idb:',{'x':'m15','y':'m16','th':'m18'},'pr2')
pr3 = PRDevice('4idb:',{'x':'m19','y':'m20','th':'m21'},'pr3')

# TODO: add other stuff to pr's, like lock-in PVS, and screen position.
