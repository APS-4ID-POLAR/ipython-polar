
"""
Diffractometer motors
"""

__all__ = ['fourc']

from ophyd import Component, FormattedComponent
from ophyd import PseudoSingle
from ophyd import EpicsSignal, EpicsSignalRO, EpicsMotor, Signal
from bluesky.suspenders import SuspendBoolLow
from ..framework import RE
from ..framework import sd
import gi
gi.require_version('Hkl', '5.0')
# MUST come before `import hkl`
from hkl.geometries import E4CV
from ..session_logs import logger
logger.info(__file__)


class FourCircleDiffractometer(E4CV):
    """
    E4CV: huber diffractometer in 4-circle vertical geometry with energy.

    4-ID-D setup.
    """

    # HKL and 4C motors
    h = Component(PseudoSingle, '', labels=("hkl", "fourc"))
    k = Component(PseudoSingle, '', labels=("hkl", "fourc"))
    l = Component(PseudoSingle, '', labels=("hkl", "fourc"))

    theta = Component(EpicsMotor, 'm65', labels=("motor", "fourc"))
    chi = Component(EpicsMotor, 'm67', labels=("motor", "fourc"))
    phi = Component(EpicsMotor, 'm68', labels=("motor", "fourc"))
    tth = Component(EpicsMotor, 'm66', labels=("motor", "fourc"))

    th_tth_min = Component(EpicsSignal, "userCalc1.C",
                           labels=('fourc', 'limits'),
                           kind='config')
    th_tth_permit = Component(EpicsSignal, "userCalc1.VAL",
                              labels=('fourc', 'limits'),
                              kind='config')

    # Explicitly selects the real motors
    _real = ['theta', 'chi', 'phi', 'tth']

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
    energy_update_calc_flag = Component(Signal, value=1)
    energy_offset = Component(Signal, value=0)

    @property
    def _calc_energy_update_permitted(self):
        """return boolean `True` if permitted."""
        acceptable_values = (1, "Yes", "locked", "OK", True, "On")
        return self.energy_update_calc_flag.get() in acceptable_values

    def _energy_changed(self, value=None, **kwargs):
        '''
        Callback indicating that the energy signal was updated.
        .. note::
            The `energy` signal is subscribed to this method
            in the :meth:`Diffractometer.__init__()` method.
        '''
        if not self.connected:
            logger.warning(
                "%s not fully connected, %s.calc.energy not updated",
                self.name, self.name)
            return

        if self._calc_energy_update_permitted:
            self._update_calc_energy(value)

    def _update_calc_energy(self, value=None, **kwargs):
        '''
        writes self.calc.energy from value or self.energy.
        '''
        if not self.connected:
            logger.warning(
                "%s not fully connected, %s.calc.energy not updated",
                self.name, self.name)
            return

        # use either supplied value or get from signal
        value = value or self.energy.get()

        # energy_offset has same units as energy
        new_calc_energy = value + self.energy_offset.get()
        self.calc.energy = new_calc_energy
        self._update_position()


fourc = FourCircleDiffractometer('4iddx:', name='fourc')
fourc.calc.physical_axis_names = {'omega': 'theta',
                                  'chi': 'chi',
                                  'phi': 'phi',
                                  'tth': 'tth'}
sus = SuspendBoolLow(fourc.th_tth_permit)
RE.install_suspender(sus)

# TODO: This is a rough workaround...
for attr in ("x", "y", "z", "baseth", "basetth", "ath", "achi", "atth",
             "tablex", "tabley"):
    getattr(fourc, attr).kind = "normal"
fourc.energy.kind = "omitted"

sd.baseline.append(fourc)
