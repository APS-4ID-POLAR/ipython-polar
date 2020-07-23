
"""
our diffractometer
"""

__all__ = [
    'scaler1',
    'scaler2',
    ]

from ..session_logs import logger
logger.info(__file__)

from ophyd.sim import SynGauss,SynSignal,motor
from ophyd import Device,Component,Signal,Kind
from ..utils import simScalerCH

scaler1 = SynGauss('scaler1', motor, 'motor', center=0, Imax=1, sigma=1)
setattr(scaler1,'preset_time',1)

channels = ['time','ic1','ic2','ic3',
            'ic4','ic5','APD']

for i in range(len(channels)):
    label = 'chan{:02d}'.format(i+1)
    setattr(scaler1,label,SynGauss(label, motor, 'motor', center=0, Imax=1, sigma=1))
    setattr(getattr(scaler1,label),'chname',channels[i])

# TODO: While this runs, it does not behave like a scaler.

scaler2 = simScalerCH(name='scaler2')
