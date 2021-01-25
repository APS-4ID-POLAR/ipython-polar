"""
Monochromator motors
"""

__all__ = ['mono']

from apstools.devices import KohzuSeqCtl_Monochromator
from ophyd import EpicsMotor, EpicsSignal, EpicsSignalRO
from ophyd import Component, Device, FormattedComponent
from ..framework import sd
from ..utils import TrackingSignal

from ..session_logs import logger
logger.info(__file__)


class MonoFeedback(Device):

    readback = Component(EpicsSignalRO, 'mono_pid2.CVAL', kind='config',
                         labels=('mono',))
    setpoint = Component(EpicsSignal, 'mono_pid2.VAL', kind='config',
                         put_complete=True, labels=('mono',))
    onoff = Component(EpicsSignal, 'mono_pid2.FBON', kind='config',
                      labels=('mono',), put_complete=True)


class Monochromator(KohzuSeqCtl_Monochromator):

    y1 = None

    x2 = Component(EpicsMotor, 'm6', labels=('motor', 'mono'))
    y2 = Component(EpicsSignalRO, 'KohzuYRdbkAI',
                   labels=('motor', 'mono'))
    z2 = Component(EpicsSignalRO, 'KohzuZRdbkAI',
                   labels=('motor', 'mono'))

    thf2 = Component(EpicsMotor, 'm4', labels=('motor', 'mono'))
    chi2 = Component(EpicsMotor, 'm5', labels=('motor', 'mono'))

    table_x = Component(EpicsMotor, 'm7', labels=('motor', 'mono'))
    table_y = Component(EpicsMotor, 'm8', labels=('motor', 'mono'))

    energy = Component(EpicsSignal, "BraggERdbkAO", write_pv="BraggEAO",
                       put_complete=True, labels=('mono',))

    tracking = Component(TrackingSignal, value=True, kind="config",
                         labels=('mono',))

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


mono = Monochromator('4idb:', name='monochromator')
mono.stage_sigs['mode'] = 1  # Ensure that mono is in auto before moving.
sd.baseline.append(mono)
