"""
Monochromator motors
"""

__all__ = ['mono']

from apstools.devices import KohzuSeqCtl_Monochromator
from ophyd import EpicsMotor, EpicsSignal, EpicsSignalRO
from ophyd import Component, Device, FormattedComponent
from ..framework import sd

from ..session_logs import logger
logger.info(__file__)


class MonoFeedback(Device):
    """ Mono feedback reading """

    readback = Component(EpicsSignalRO, 'mono_pid2.CVAL', kind='config',
                         labels=('mono',))
    setpoint = Component(EpicsSignal, 'mono_pid2.VAL', kind='config',
                         put_complete=True, labels=('mono',))
    onoff = Component(EpicsSignal, 'mono_pid2.FBON', kind='config',
                      labels=('mono',), put_complete=True)


class Monochromator(KohzuSeqCtl_Monochromator):
    """ Tweaks from apstools mono """

    # No y1 at 4-ID-D
    y1 = None

    x2 = Component(EpicsMotor, 'm6', labels=('motors', 'mono'))
    y2 = Component(EpicsSignalRO, 'KohzuYRdbkAI',
                   labels=('motors', 'mono'))
    z2 = Component(EpicsSignalRO, 'KohzuZRdbkAI',
                   labels=('motors', 'mono'))

    thf2 = Component(EpicsMotor, 'm4', labels=('motors', 'mono'))
    chi2 = Component(EpicsMotor, 'm5', labels=('motors', 'mono'))

    table_x = Component(EpicsMotor, 'm7', labels=('motors', 'mono'))
    table_y = Component(EpicsMotor, 'm8', labels=('motors', 'mono'))

    energy = Component(EpicsSignal, "BraggERdbkAO", write_pv="BraggEAO",
                       put_complete=True, labels=('mono',))

    feedback = FormattedComponent(MonoFeedback, '4id:')

    def calibrate_energy(self, value):
        """Calibrate the mono energy.

        Parameters
        ----------
        value: float
            New energy for the current monochromator position.
        """
        self.use_set.put('Set', use_complete=True)
        self.energy.put(value)
        self.use_set.put('Use', use_complete=True)


mono = Monochromator('4idb:', name='mono')
mono.stage_sigs['mode'] = 1  # Ensure that mono is in auto before moving.
sd.baseline.append(mono)
