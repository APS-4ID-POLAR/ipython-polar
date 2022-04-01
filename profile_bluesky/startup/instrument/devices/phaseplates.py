"""
Phase retarders.
"""

__all__ = ['pr1', 'pr2', 'pr3', 'pr_setup']

from ..framework import sd
from ophyd import Device, EpicsMotor, PseudoPositioner, PseudoSingle
from ophyd import Component, FormattedComponent
from ophyd import EpicsSignal, EpicsSignalRO, Signal, DerivedSignal
from ophyd.pseudopos import pseudo_position_argument, real_position_argument
from scipy.constants import speed_of_light, Planck
from numpy import arcsin, pi, sin
from .util_components import TrackingSignal, PVPositionerSoftDone
from ..session_logs import logger

# This is here because PRDevice.select_pr has a micron symbol that utf-8
# cannot read. See: https://github.com/bluesky/ophyd/issues/930
from epics import utils
utils.EPICS_STR_ENCODING = "latin-1"

logger.info(__file__)


class MicronsSignal(DerivedSignal):
    '''A signal that converts the offset from degrees to microns'''

    def __init__(self, parent_attr, *, parent=None, **kwargs):
        degrees_signal = getattr(parent, parent_attr)
        super().__init__(derived_from=degrees_signal, parent=parent, **kwargs)

    def describe(self):
        desc = super().describe()
        desc[self.name]['units'] = 'microns'
        return desc

    def inverse(self, value):
        '''Compute original signal value -> derived signal value'''
        return value / self.parent.conversion_factor.get()

    def forward(self, value):
        '''Compute derived signal value -> original signal value'''
        return value * self.parent.conversion_factor.get()


class PRPzt(Device):
    """ Phase retarder PZT """

    remote_setpoint = Component(EpicsSignal, 'set_microns.VAL')
    remote_readback = Component(EpicsSignalRO, 'microns')

    localdc = Component(PVPositionerSoftDone, "",
                        readback_pv="DC_read_microns",
                        setpoint_pv="DC_set_microns", tolerance=0.01)

    center = Component(EpicsSignal, 'AC_put_center.A', kind='config')
    offset_degrees = Component(EpicsSignal, 'AC_put_offset.A',
                               kind='config')

    offset_microns = Component(MicronsSignal, parent_attr='offset_degrees',
                               kind='config')

    servoon = Component(EpicsSignal, 'servo_ON.PROC', kind='omitted')
    servooff = Component(EpicsSignal, 'servo_OFF.PROC', kind='omitted')
    servostatus = Component(EpicsSignalRO, 'svo', kind='config')

    selectDC = FormattedComponent(EpicsSignal,
                                  '4idb:232DRIO:1:OFF_ch{_prnum}.PROC',
                                  kind='omitted', put_complete=True)

    selectAC = FormattedComponent(EpicsSignal,
                                  '4idb:232DRIO:1:ON_ch{_prnum}.PROC',
                                  kind='omitted', put_complete=True)

    ACstatus = FormattedComponent(EpicsSignalRO, '4idb:232DRIO:1:status',
                                  kind='config')

    conversion_factor = Component(Signal, value=0.1, kind='config')

    def __init__(self, PV, *args, **kwargs):
        self._prnum = PV.split(':')[-2]
        super().__init__(PV, *args, **kwargs)


class PRDeviceBase(PseudoPositioner):

    energy = Component(PseudoSingle, limits=(2.7, 20))
    th = FormattedComponent(EpicsMotor, '{prefix}:{_motorsDict[th]}',
                            labels=('motors', 'phase_retarders'))

    # Explicitly selects the real motor
    _real = ['th']

    x = FormattedComponent(EpicsMotor, '{prefix}:{_motorsDict[x]}',
                           labels=('motors', 'phase_retarders'))

    y = FormattedComponent(EpicsMotor, '{prefix}:{_motorsDict[y]}',
                           labels=('motors', 'phase_retarders'))

    d_spacing = Component(Signal, value=0, kind='config',
                          labels=('phase_retarders',))

    # This offset is used when the motor is used to switch polarization
    offset_degrees = Component(Signal, value=0.0, kind='config',
                               labels=('phase_retarders',))

    tracking = Component(TrackingSignal, value=False, kind='config',
                         labels=('phase_retarders',))

    def __init__(self, PV, name, motorsDict, **kwargs):
        self._motorsDict = motorsDict
        super().__init__(prefix=PV, name=name, **kwargs)
        self._energy_cid = None

    def convert_energy_to_theta(self, energy):
        # lambda in angstroms, theta in degrees, energy in keV
        lamb = speed_of_light*Planck*6.241509e15*1e10/energy
        theta = arcsin(lamb/2/self.d_spacing.get())*180./pi
        return theta

    def convert_theta_to_energy(self, theta):
        # lambda in angstroms, theta in degrees, energy in keV
        lamb = 2*self.d_spacing.get()*sin(theta*pi/180)
        energy = speed_of_light*Planck*6.241509e15*1e10/lamb
        return energy

    @pseudo_position_argument
    def forward(self, pseudo_pos):
        '''Run a forward (pseudo -> real) calculation'''
        return self.RealPosition(
            th=self.convert_energy_to_theta(pseudo_pos.energy)
            )

    @real_position_argument
    def inverse(self, real_pos):
        '''Run an inverse (real -> pseudo) calculation'''
        return self.PseudoPosition(
            energy=self.convert_theta_to_energy(real_pos.th)
            )

    def set_energy(self, energy):
        # energy in keV, theta in degrees.
        theta = self.convert_energy_to_theta(energy)
        self.th.set_current_position(theta)


class PRDevice(PRDeviceBase):

    pzt = FormattedComponent(PRPzt, '{prefix}:E665:{_prnum}:',
                             labels=('phase_retarders',))
    select_pr = FormattedComponent(EpicsSignal, '{prefix}:PRA{_prnum}',
                                   string=True, auto_monitor=True,
                                   kind='config', labels=('phase_retarders',))

    def __init__(self, prefix, name, prnum, motorsDict, **kwargs):
        self._prnum = prnum
        super().__init__(prefix, name, motorsDict, **kwargs)

    @select_pr.sub_value
    def _set_d_spacing(self, **kwargs):
        value = self.select_pr.get()
        spacing_dictionary = {'111': 2.0595, '220': 1.26118}
        plane = value.split('(')[1].split(')')[0]
        self.d_spacing.put(spacing_dictionary[plane])


class PRSetup():

    positioner = None
    offset = None
    dichro_steps = [1, -1, -1, 1]

    def __repr__(self):

        tracked = ""
        for pr in [pr1, pr2, pr3]:
            if pr.tracking.get():
                tracked += f"{pr.name} "

        oscillate = self.positioner.name if self.positioner else "None"
        offset = self.offset.name if self.offset else "None"
        try:
            pzt_center = self.offset.parent.center.get()
        except AttributeError:
            pzt_center = "None"

        return ("Phase retarder settings\n"
                f"  Tracking PRs = {tracked}\n"
                f"  Oscillating PR = {oscillate}\n"
                f"  Offset positioner = {offset}\n"
                f"  Offset value = {self.offset.get()}\n"
                f"  PZT center = {pzt_center}\n"
                f"  Steps for dichro scan = {self.dichro_steps}\n")

    def __str__(self):
        return self.__repr__()

    def __call__(self):

        print('Setup of the phase retarders for dichro scans.')
        print('Note that you can only oscillate one phase retarder stack.')

        _positioner = None

        for pr, label in zip([pr1, pr2, pr3], ["PR1", "PR2", "PR3"]):

            _current = {}
            _current['track'] = "yes" if pr.tracking.get() else "no"
            for key in ['oscillate', 'method', 'offset', 'center']:
                _current[key] = None

            if self.positioner and not _positioner:
                _current['oscillate'] = (
                    "yes" if self.positioner.root.name == label.lower()
                    else "no"
                    )
                _current['method'] = ("pzt" if "pzt" in self.positioner.name
                                      else "motor")

                _current["offset"] = self.positioner.parent.offset_degrees.\
                    get()

                if _current['method'] == "pzt":
                    _current["center"] = self.positioner.parent.center.get()

            print(" ++ {} ++ ".format(label))

            # Track the energy?
            while True:
                track = input(f"\tTrack? ({_current['track']}): ")
                if track == '':
                    track = str(_current['track'])

                if track.lower() == "yes":
                    pr.tracking.put(True)
                    break
                elif track.lower() == "no":
                    pr.tracking.put(False)
                    break
                else:
                    print("Only yes or no are acceptable answers.")

            # If no positioner has been selected to oscillate, we will ask.
            # This assumes that we only oscillate one PR, which is tracked.
            if _positioner is None and track == "yes":
                # Oscillate this PR?
                while True:
                    oscillate = input(f"\tOscillate? ({_current['oscillate']})"
                                      ": ")

                    if oscillate == '':
                        oscillate = str(_current['oscillate'])
                    # If this will oscillate, need to determine the positioner
                    # to use and its parameters.
                    if oscillate.lower() == "yes":
                        # PR3 doesn't have a PZT.
                        if pr == pr3:
                            method = "motor"
                            _positioner = pr.th
                        else:
                            while True:
                                method = input("\tUse motor or PZT? "
                                               f"({_current['method']}): ")
                                if method == '':
                                    method = str(_current['method'])
                                if method.lower() == 'motor':
                                    _positioner = pr.th
                                    break
                                elif method.lower() == 'pzt':
                                    _positioner = pr.pzt.localdc
                                    break
                                else:
                                    print("Only motor or pzt are acceptable "
                                          "answers.")

                        # Get offset
                        while True:
                            try:
                                msg = "\tOffset (in degrees)"
                                msg += f"({_current['offset']}): "
                                offset = input(msg)
                                if offset == '':
                                    offset = str(_current['offset'])
                                _positioner.parent.offset_degrees.put(
                                        float(offset)
                                        )
                                break
                            except ValueError:
                                print('Must be a number.')

                        # if PZT is used, then get the center.
                        if method.lower() == "pzt":
                            # Get offset signal
                            self.offset = _positioner.parent.offset_microns
                            # Get the PZT center.
                            while True:
                                try:
                                    center = input(
                                            "\tPZT center in microns "
                                            f"({_current['center']}): ")
                                    if center == '':
                                        center = str(_current['center'])
                                    _positioner.parent.center.put(
                                            float(center))
                                    break
                                except ValueError:
                                    print('Must be a number.')
                        else:
                            # Get offset signal
                            self.offset = _positioner.parent.offset_degrees
                        break
                    elif oscillate.lower() == 'no':
                        break
                    else:
                        print("Only yes or no are acceptable answers.")

            else:
                if _positioner and track == 'yes':
                    print('\tYou already selected {} to oscillate.'.format(
                          _positioner.name))

        self.positioner = _positioner


pr1 = PRDevice('4idb', 'pr1', 1, {'x': 'm10', 'y': 'm11', 'th': 'm13'})
pr1.pzt.conversion_factor.put(0.001636)
pr1._set_d_spacing()

pr2 = PRDevice('4idb', 'pr2', 2, {'x': 'm15', 'y': 'm16', 'th': 'm18'})
pr2.pzt.conversion_factor.put(0.0019324)
pr2._set_d_spacing()

pr3 = PRDeviceBase('4idb', 'pr3', {'x': 'm19', 'y': 'm20', 'th': 'm21'})
pr3.d_spacing.put(3.135)

pr_setup = PRSetup()

sd.baseline.append(pr1)
sd.baseline.append(pr2)
sd.baseline.append(pr3)
