"""
Monochromator motors
"""

__all__ = [
    'mono',
    ]

from ..session_logs import logger
logger.info(__file__)

from ophyd import Component, Device, EpicsMotor


class Monochromator(Device):
    th = EpicsMotor('4idb:m1', name='mono', labels=('motor',))  # Kohzu Theta # home_slew_rate=0
    y = EpicsMotor('4idb:m2', name='mon_y', labels=('motor',))  # Kohzu Y2
    # 2: MOT002 =    NONE:0/3   2000  1  2000  200   50  125    0 0x003    mon_z  Kohzu Z2  # Kohzu Z2
    thf = EpicsMotor('4idb:m4', name='mon_thf', labels=('motor',))  # Kohzu Th2f
    chi = EpicsMotor('4idb:m5', name='mon_chi', labels=('motor',))  # Kohzu Chi

mono = Monochromator(name='mono')

# TODO: Define Z motor!
# TODO: Look at TODO/fourc.py --> May be better to implement that way?
