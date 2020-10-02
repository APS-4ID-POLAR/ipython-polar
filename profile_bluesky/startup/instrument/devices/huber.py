
"""
Diffractometer motors
"""

__all__ = [
    'fourc',
    ]

from ..session_logs import logger
logger.info(__file__)


import gi
gi.require_version('Hkl', '5.0')
# MUST come before `import hkl`
from hkl.diffract import E4CV
from ophyd import Component, FormattedComponent
from ophyd import PseudoSingle
from ophyd import EpicsSignal, EpicsSignalRO, EpicsMotor, Signal
from bluesky.suspenders import SuspendBoolLow
import pint
from apstools.diffractometer import Constraint
from apstools.diffractometer import DiffractometerMixin
from ..framework import RE
from ..framework import sd


class FourCircleDiffractometer(DiffractometerMixin, E4CV):
    """
    E4CV: kappa diffractometer in 4-circle geometry with energy.

    4-ID-D setup.
    """

    # HKL and 4C motors
    h = Component(PseudoSingle, '', labels=("hkl", "fourc"), kind="hinted")
    k = Component(PseudoSingle, '', labels=("hkl", "fourc"), kind="hinted")
    l = Component(PseudoSingle, '', labels=("hkl", "fourc"), kind="hinted")

    omega = Component(EpicsMotor, 'm65', labels=("motor", "fourc"),
                      kind="hinted")
    chi = Component(EpicsMotor, 'm67', labels=("motor", "fourc"),
                    kind="hinted")
    phi = Component(EpicsMotor, 'm68', labels=("motor", "fourc"),
                    kind="hinted")
    tth = Component(EpicsMotor, 'm66', labels=("motor", "fourc"),
                    kind="hinted")

    th_tth_min = Component(EpicsSignal, "userCalc1.C",
                           labels=('diffractometer', 'limits'),
                           kind='config')
    th_tth_permit = Component(EpicsSignal, "userCalc1.VAL",
                              labels=('diffractometer', 'limits'),
                              kind='config')

    # Cryo carrier
    x = Component(EpicsMotor, 'm14', labels=('motor', 'fourc'))  # Cryo X
    y = Component(EpicsMotor, 'm15', labels=('motor', 'fourc'))  # Cryo Y
    z = Component(EpicsMotor, 'm16', labels=('motor', 'fourc'))  # Cryo Z

    # Base motors
    baseth = Component(EpicsMotor, 'm69', labels=('motor', 'fourc'))
    basetth = Component(EpicsMotor, 'm70', labels=('motor', 'fourc'))

    tablex = Component(EpicsMotor, 'm18', labels=('motor', 'fourc'))
    tabley = Component(EpicsMotor, 'm17', labels=('motor', 'fourc'))

    # Analyzer motors
    ath = Component(EpicsMotor, 'm77', labels=('motor', 'fourc'))
    achi = Component(EpicsMotor, 'm79', labels=('motor', 'fourc'))
    atth = Component(EpicsMotor, 'm78', labels=('motor', 'fourc'))

    # Energy
    energy = FormattedComponent(EpicsSignalRO, "4idb:BraggERdbkAO",
                                kind='omitted')
    # energy_EGU = Component(EpicsSignal, "optics:energy.EGU")
    energy_update_calc = Component(Signal, value=1)
    energy_offset = Component(Signal, value=0)

    def _energy_changed(self, value=None, **kwargs):
        '''
        Callback indicating that the energy signal was updated.
        '''
        if not self.connected:
            logger.warning("%s not fully connected, %s.calc.energy not updated",
                           self.name, self.name)
            return
        if self.energy_update_calc.get() in (1, "Yes", "locked", "OK"):
            # energy_offset has same units as energy
            local_energy = value + self.energy_offset.get()

            # TODO: I think we don't need this. It's always keV.
            # # either get units from control system
            # units = self.energy_EGU.get()
            # # or define as a constant here
            # # units = "eV"
            #
            # keV = pint.Quantity(local_energy, units).to("keV")
            # logger.debug("setting %s.calc.energy = %f (keV)", self.name,
            #              keV.magnitude)

            self._calc.energy = local_energy
            self._update_position()


fourc = FourCircleDiffractometer(prefix='4iddx:', name='fourc')
sus = SuspendBoolLow(fourc.th_tth_permit)
RE.install_suspender(sus)
sd.baseline.append(fourc)
