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

    x2 = Component(EpicsMotor, 'm6', labels=('motor', 'mono'))
    y2 = Component(EpicsSignalRO, 'KohzuYRdbkAI', labels=('motor',  'mono'))
    z2 = Component(EpicsSignalRO, 'KohzuZRdbkAI', labels=('motor', 'mono'))

    thf2 = Component(EpicsMotor, 'm4', labels=('motor', 'mono'))
    chi2 = Component(EpicsMotor, 'm5', labels=('motor', 'mono'))

    table_x = Component(EpicsMotor, 'm7', labels=('motor', 'mono'))
    table_y = Component(EpicsMotor, 'm8', labels=('motor', 'mono'))

    feedback = FormattedComponent(MonoFeedback, '4id:')


mono = Monochromator('4idb:', name='mono')
mono.stage_sigs['mode'] = 1  # Ensure that mono is in auto before moving.
sd.baseline.append(mono)
