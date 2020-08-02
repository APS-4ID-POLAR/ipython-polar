"""
Monochromator motors
"""

__all__ = [
    'mono',
    ]

from ..session_logs import logger
logger.info(__file__)

from apsutils.devices import KohzuSeqCtl_Monochromator
from ophyd import Component, Device, EpicsMotor, EpicsSignal
from .aps_source import undulator

class Monochromator(KohzuSeqCtl_Monochromator):

    th = Component(EpicsMotor,':m1', labels=('motor','monochromator'))  # Kohzu Theta # home_slew_rate=0
    y = Component(EpicsMotor,':m2', labels=('motor','monochromator'))  # Kohzu Y2
    z = Component(EpicsMotor,':m3', labels=('motor','monochromator'))  # Kohzu Z2
    thf = Component(EpicsMotor,':m4',labels=('motor','monochromator'))  # Kohzu Th2f
    chi = Component(EpicsMotor,':m5', labels=('motor','monochromator'))  # Kohzu Chi


mono = Monochromator('4idb', name='monochromator')

# TODO: We should add the undulator tracking within this function as a
# @property of the energy setter.
# TODO: How to handle an epics PV that has options? The KohzuSeqCtl has to be
# in "auto" mode, but it changes to "manual" if spec moves the energy.
