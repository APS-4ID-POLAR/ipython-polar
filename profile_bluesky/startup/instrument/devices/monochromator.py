"""
Monochromator motors
"""

__all__ = [
    'mono',
    ]

from ..session_logs import logger
logger.info(__file__)

from apstools.devices import KohzuSeqCtl_Monochromator
from ophyd import Component, EpicsMotor, EpicsSignal

class Monochromator(KohzuSeqCtl_Monochromator):

    th = Component(EpicsMotor,'m1', labels=('motor','monochromator'))  # Kohzu Theta # home_slew_rate=0
    y = Component(EpicsMotor,'m2', labels=('motor','monochromator'))  # Kohzu Y2
    z = Component(EpicsMotor,'m3', labels=('motor','monochromator'))  # Kohzu Z2
    thf = Component(EpicsMotor,'m4',labels=('motor','monochromator'))  # Kohzu Th2f
    chi = Component(EpicsMotor,'m5', labels=('motor','monochromator'))  # Kohzu Chi


mono = Monochromator('4idb:', name='monochromator')
mono.mode.put('auto') #Switch mono to "auto".
mono.stage_sigs['mode'] = 1 #Ensure that mono is in auto before moving.
