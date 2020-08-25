"""
Monochromator motors
"""

__all__ = [
    'mono',
    ]

from ..session_logs import logger
logger.info(__file__)

from apstools.devices import KohzuSeqCtl_Monochromator
from ophyd import Component, EpicsMotor, FormattedComponent
from epics import caget

class Monochromator(KohzuSeqCtl_Monochromator):
    
    th = FormattedComponent(EpicsMotor,'{self._theta_pv}',
                            labels=('motor','monochromator'))  # Kohzu Theta
    
    y = FormattedComponent(EpicsMotor,'{self._y_pv}',
                            labels=('motor','monochromator'))   # Kohzu Y2
    
    z = FormattedComponent(EpicsMotor,'{self._z_pv}',
                            labels=('motor','monochromator'))  # Kohzu Z2
    
    thf = Component(EpicsMotor,'m4',labels=('motor','monochromator'))  # Kohzu Th2f
    chi = Component(EpicsMotor,'m5', labels=('motor','monochromator'))  # Kohzu Chi
    
    def __init__(self,prefix,*args,**kwargs):
        
        self._theta_pv = caget(prefix+'KohzuThetaPvSI')
        self._y_pv = caget(prefix+'KohzuYPvSI')
        self._z_pv = caget(prefix+'KohzuZPvSI')
        
        super().__init__(prefix,*args,**kwargs)
        


mono = Monochromator('4idb:', name='monochromator')
mono.mode.put('Auto') #Switch mono to "auto".
mono.stage_sigs['mode'] = 1 #Ensure that mono is in auto before moving.
