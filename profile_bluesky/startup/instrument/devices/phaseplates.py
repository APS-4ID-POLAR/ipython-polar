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

    x = None
    y = None
    th = None

    def __init__(PV,motorsPVdict,**kwargs):
        super().__init__(PV,**kwargs)
        self.make_motors(motorsPVdict)

    def make_motors(self,motorsPVdict):
        for key in motorsPVdict.keys():
            pv,name  = motorsPVdict[key]
            setattr(self,key,Component(EpicsMotor,pv, name=name,
                                       labels=('motor','phase retarder')))

pr1 = PRDevice('4idb',{'x':'m10','y':'m11','th':'m13'},name='pr1')
pr2 = PRDevice('4idb',{'x':'m15','y':'m16','th':'m18'},name='pr2')
pr3 = PRDevice('4idb',{'x':'m19','y':'m20','th':'m21'},name='pr3')

# TODO: add other stuff to pr's, like lock-in PVS, and screen position.
