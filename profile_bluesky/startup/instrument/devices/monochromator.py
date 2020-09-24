"""
Monochromator motors
"""

__all__ = [
    'mono',
    ]

from ..session_logs import logger
logger.info(__file__)

from apstools.devices import KohzuSeqCtl_Monochromator
from ophyd import Component, EpicsSignalRO, EpicsMotor, EpicsSignal
from ..framework import sd

class Monochromator(KohzuSeqCtl_Monochromator):

    y1 = None

    x2 = Component(EpicsMotor,'m6',labels=('motor','monochromator'))
    y2 = Component(EpicsSignalRO,'KohzuYRdbkAI',labels=('motor','monochromator'))   # Kohzu Y2
    z2 = Component(EpicsSignalRO,'KohzuZRdbkAI',labels=('motor','monochromator'))  # Kohzu Z2

    thf2 = Component(EpicsMotor,'m4',labels=('motor','monochromator'))  # Kohzu Th2f
    chi2 = Component(EpicsMotor,'m5', labels=('motor','monochromator'))  # Kohzu Chi

    table_x = Component(EpicsMotor,'m7',labels=('motor','monochromator'))
    table_y = Component(EpicsMotor,'m8',labels=('motor','monochromator'))

    energy = Component(EpicsSignal, "BraggERdbkAO", write_pv="BraggEAO",
                       kind='hinted', put_complete = True)

mono = Monochromator('4idb:', name='monochromator')
mono.stage_sigs['mode'] = 1 #Ensure that mono is in auto before moving.
sd.baseline.append(mono)
