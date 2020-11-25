"""
Monochromator motors
"""

__all__ = [
    'mono',
    ]

from ..session_logs import logger
logger.info(__file__)

from apstools.devices import KohzuSeqCtl_Monochromator
from ophyd import EpicsMotor, EpicsSignal, EpicsSignalRO
from ophyd import Component, FormattedComponent, Device
from ..framework import sd


class MonoFeedback(Device):

    readback = Component(EpicsSignalRO, 'mono_pid2.CVAL', kind='normal',
                         labels=('mono'))
    setpoint = Component(EpicsSignal, 'mono_pid2.VAL', kind='config',
                         labels=('mono'))
    onoff = Component(EpicsSignal, 'mono_pid2.FBON', kind='config',
                      labels=('mono'))

 
class Monochromator(KohzuSeqCtl_Monochromator):

    y1 = None
    
    x2 = Component(EpicsMotor, 'm6', labels=('motor', 'monochromator'))
    y2 = Component(EpicsSignalRO, 'KohzuYRdbkAI',
                   labels=('motor', 'monochromator'))
    z2 = Component(EpicsSignalRO, 'KohzuZRdbkAI',
                   labels=('motor', 'monochromator'))

    thf2 = Component(EpicsMotor, 'm4', labels=('motor', 'monochromator'))
    chi2 = Component(EpicsMotor, 'm5', labels=('motor', 'monochromator'))

    table_x = Component(EpicsMotor, 'm7', labels=('motor', 'monochromator'))
    table_y = Component(EpicsMotor, 'm8', labels=('motor', 'monochromator'))

    energy = Component(EpicsSignal, "BraggERdbkAO", write_pv="BraggEAO",
                       kind='hinted', put_complete=True)

    def calibrate_energy(self, value):
        """Calibrate the mono energy.

        Parameters
        ----------
        value: float
            New energy for the current monochromator position.
        """
        self.use_set.put('Set')
        self.energy.put(value)
        self.use_set.put('Use')


mono = Monochromator('4idb:', name='monochromator')
mono.stage_sigs['mode'] = 1  # Ensure that mono is in auto before moving.
sd.baseline.append(mono)
