"""
Phase retarders
"""

__all__ = [
    'pr1','pr2','pr3'
    ]

from ..session_logs import logger
logger.info(__file__)

from ophyd import Device, EpicsMotor, FormattedComponent

class PRDevice(Device):

    x = FormattedComponent(EpicsMotor,'{self.prefix}:{_motorsDict[x]}',
                           labels=('motor','phase retarders'))

    y = FormattedComponent(EpicsMotor,'{self.prefix}:{_motorsDict[y]}',
                           labels=('motor','phase retarders'))

    th = FormattedComponent(EpicsMotor,'{self.prefix}:{_motorsDict[th]}',
                            labels=('motor','phase retarders'))

    def __init__(self,prefix,name,motorsDict,**kwargs):
        self._motorsDict = motorsDict
        super().__init__(prefix=prefix, name=name, **kwargs)

pr1 = PRDevice('4idb','pr1',{'x':'m10','y':'m11','th':'m13'})
pr2 = PRDevice('4idb','pr2',{'x':'m15','y':'m16','th':'m18'})
pr3 = PRDevice('4idb','pr3',{'x':'m19','y':'m20','th':'m21'})

# TODO: add other stuff to pr's, like lock-in PVS, and screen position.
