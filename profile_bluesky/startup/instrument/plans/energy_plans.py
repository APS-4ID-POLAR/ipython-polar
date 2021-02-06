"""
Energy scans
"""

__all__ = ['moveE', 'Escan', 'Escan_list', 'qxscan', 'undscan']

from bluesky.plan_stubs import mv, trigger_and_read, rd
from bluesky.preprocessors import stage_decorator, run_decorator
from bluesky.utils import Msg, short_uid
from ..devices import (undulator, mono, qxscan_params, pr1, pr2, pr3, scalerd,
                       counters)
from numpy import linspace, array, arcsin, pi
from scipy.constants import speed_of_light, Planck
from .local_preprocessors import (stage_dichro_decorator,
                                  configure_counts_decorator)
from .local_scans import dichro_steps

from ..session_logs import logger
logger.info(__file__)


def undscan(detectors, energy_0, energy_f, steps, time=None, md=None):
    """
    Scan the undulator energy.
    Due to the undulator backlash, it is recommended that energy_0 > energy_f.
    Parameters
    ----------
    detectors : list
        list of 'readable' objects
    energy_0 : float
        Initial energy in keV
    energy_f : float
        Final energy in keV
    steps : integer
        Number of steps
    md : dict, optional
        metadata
    See Also
    --------
    :func:`moveE`
    :func:`Escan`
    """
    energy_list = linspace(energy_0, energy_f, steps)

    _md = {'detectors': [det.name for det in detectors],
           'positioners': [undulator.downstream.energy.name],
           'num_points': len(energy_list),
           'num_intervals': len(energy_list) - 1,
           'plan_args': {'detectors': list(map(repr, detectors)),
                         'initial_energy': repr(energy_0),
                         'final_energy': repr(energy_f),
                         'steps': repr(steps)},
           'plan_name': 'undscan',
           'hints': {'x': ['undulator_downstream_energy']},
           }

    _md.update(md or {})

    @configure_counts_decorator(detectors, time)
    @run_decorator(md=_md)
    def _inner_undscan():
        for energy in energy_list:
            grp = short_uid('set')
            yield Msg('checkpoint')
            yield from moveE(energy, undscan=True, group=grp)
            yield from trigger_and_read(list(detectors) +
                                        [undulator.downstream.energy])

    return (yield from _inner_undscan())


def moveE(energy, undscan=False, group=None):
    """
    Move beamline energy.

    It reads the tracking flags of the undulator and phase retarders.

    Parameters
    ----------
    energy : float
        Target energy
    undscan : boolean, optional
        If True, it moves only the undulator energy
    group : string, optional
        Used to mark these as a unit to be waited on.

    See Also
    --------
    :func:`bluesky.plan_stubs.mv`
    :func:`undscan`
    :func:`Escan`
    """
    args_list = [()]
    decorators = []

    _offset = undulator.downstream.offset.get()
    _tracking = undulator.downstream.tracking.get()

    if undscan is False:
        if abs(energy-mono.energy.get()) > mono.energy.tolerance:
            args_list[0] += ((mono.energy, energy))
            decorators.append(mono)

        for pr in [pr1, pr2, pr3]:
            if pr.tracking.get() is True:
                _lambda = speed_of_light*Planck*6.241509e15*1e10/energy
                theta = arcsin(_lambda/2/pr.d_spacing.get())*180./pi
                args_list.append((pr.th, theta))
                decorators.append(pr)
    else:
        _offset = 0.0
        _tracking = True

    if _tracking is True:

        decorators.append(undulator.downstream.energy)

        target_energy = _offset + energy
        current_energy = undulator.downstream.energy.get()

        if abs(target_energy-current_energy) > \
                undulator.downstream.deadband.get():
            if current_energy < target_energy:
                args_list[0] += (undulator.downstream.energy,
                                 target_energy +
                                 undulator.downstream.backlash.get())
                args_list[0] += (undulator.downstream.start_button, 1)

                args_list.append((undulator.downstream.energy, target_energy))
                args_list[-1] += (undulator.downstream.start_button, 1)

            else:
                args_list[0] += (undulator.downstream.energy, target_energy)
                args_list[0] += (undulator.downstream.start_button, 1)

    for pr in [pr1, pr2, pr3]:
        if pr.tracking is True:
            lamb = speed_of_light*Planck*6.241509e15*1e10/energy
            theta = arcsin(lamb/2/pr.d_spacing.get())*180./pi
            args_list.append((pr.th, theta))

    @stage_decorator(decorators)
    def _inner_moveE():
        for args in args_list:
            yield from mv(*args, group=group)

    if len(args_list[0]) > 0:
        return (yield from _inner_moveE())
    else:
        return None


def Escan_list(detectors, energy_list, count_time=None, *, factor_list=None,
               md=None, dichro=False, lockin=False):
    """
    Scan the beamline energy using a list of energies.

    Due to the undulator backlash, it is recommended for energy_list to be in
    descending order.

    Parameters
    ----------
    detectors : list
        list of 'readable' objects
    energy_list : iterable
        List of energies to be used
    factor_list: iterable, optional
        Controls the time per point by multiplying the initial count time by
        this factor. Needs to have the same length as energy_list.
    md : dict, optional
        metadata
    dichro : boolean, optional
        Flag to run a dichro energy scan. Please run pr_setup.config() prior to
        a dichro scan. Note that this will switch the x-ray polarization at
        every point using the +, -, -, + sequence, thus increasing the number
        of points, and time per energy, by a factor of 4
    lockin : boolean, optional
        Flag to run a lockin energy scan. Please run pr_setup.config() prior to
        a lockin scan.

    See Also
    --------
    :func:`moveE`
    :func:`Escan`
    :func:`qxscan`
    """
    # Create positioners list
    _positioners = [mono.energy]

    if (yield from rd(undulator.downstream.tracking)):
        _positioners.append(undulator.downstream.energy)
    for pr in [pr1, pr2, pr3]:
        if pr.tracking.get():
            _positioners.append(pr.th)

    for pr in [pr1, pr2, pr3]:
        if (yield from rd(pr.tracking)):
            _positioners.append(pr.th)
            _positioners.append(pr.energy)

    # Controls the time per point.
    if factor_list is None:
        factor_list = [1 for i in range(len(energy_list))]
    else:
        if len(factor_list) != len(energy_list):
            raise ValueError("The size of factor_list cannot be different "
                             "from the size of the energy_list")

    # Metadata
    _md = {'detectors': [det.name for det in detectors],
           'positioners': [pos.name for pos in _positioners],
           'num_points': len(energy_list),
           'num_intervals': len(energy_list) - 1,
           'plan_args': {'detectors': list(map(repr, detectors)),
                         'energy_list': list(map(repr, energy_list))},
           'plan_name': 'Escan_list',
           'hints': {'dimensions': [(['monochromator_energy'], 'primary')]},
           }

    _md.update(md or {})

    # Collects current monitor count for each detector
    dets_preset = []
    for detector in detectors:
        if count_time:
            value = abs(count_time)
        else:
            value = yield from rd(detector.preset_monitor)
        dets_preset.append(value)

    @stage_dichro_decorator(dichro, lockin)
    @configure_counts_decorator(detectors, count_time)
    @run_decorator(md=_md)
    def _inner_Escan_list():
        yield from moveE(energy_list[0]+0.001)
        for energy, factor in zip(energy_list, factor_list):

            # Change counting time
            for detector, original_preset in zip(detectors, dets_preset):
                yield from mv(detector.preset_monitor, factor*original_preset)

            # Move and scan
            grp = short_uid('set')
            yield Msg('checkpoint')
            yield from moveE(energy, group=grp)
            if dichro:
                yield from dichro_steps(detectors, _positioners,
                                        trigger_and_read)
            else:
                yield from trigger_and_read(list(detectors)+_positioners)

    return (yield from _inner_Escan_list())


def Escan(energy_0, energy_f, steps, time=None, *, detectors=None,
          md=None, dichro=False, lockin=False):
    """
    Scan the beamline energy using a fixed step size.

    Due to the undulator backlash, it is recommended that
    energy_0 > energy_f.

    Parameters
    ----------
    detectors : list
        list of 'readable' objects
    energy_0 : float
        Initial energy in keV
    energy_f : float
        Final energy in keV
    steps : integer
        Number of steps
    md : dict, optional
        metadata
    dichro : boolean, optional
        Flag to run a dichro energy scan. Please run pr_setup.config() prior to
        a dichro scan. Note that this will switch the x-ray polarization at
        every point using the +, -, -, + sequence, thus increasing the number
        of points, and time per energy, by a factor of 4
    lockin : boolean, optional
        Flag to run a lockin energy scan. Please run pr_setup.config() prior to
        a lockin scan.

    See Also
    --------
    :func:`moveE`
    :func:`Escan_list`
    :func:`qxscan`
    """

    if not detectors:
        detectors = counters.detectors

    # Scalerd is always selected.
    if scalerd not in detectors:
        scalerd.select_plot_channels([])
        detectors += [scalerd]

    _md = {'plan_args': {'detectors': list(map(repr, detectors)),
                         'initial_energy': repr(energy_0),
                         'final_energy': repr(energy_f),
                         'steps': repr(steps)},
           'plan_name': 'Escan',
           }

    _md.update(md or {})
    energy_list = linspace(energy_0, energy_f, steps)
    return (yield from Escan_list(detectors, energy_list, time, md=_md,
                                  dichro=dichro, lockin=lockin))


def qxscan(edge_energy, time=None, *, detectors=None, md=None,
           dichro=False, lockin=False):
    """
    Scan the beamline energy using variable step size.

    It reads the `qxscan_params` device. Prior to this scan, please run
    `qxscan_params.setup` or load setttings using
    `qxscan_params.load_params_json`.

    Parameters
    ----------
    detectors : list
        list of 'readable' objects
    edge_energy : float
        Energy of the absorption edge.
    md : dict, optional
        metadata
    dichro : boolean, optional
        Flag to run a dichro energy scan. Please run pr_setup.config() prior to
        a dichro scan. Note that this will switch the x-ray polarization at
        every point using the +, -, -, + sequence, thus increasing the number
        of points, and time per energy, by a factor of 4
    lockin : boolean, optional
        Flag to run a lockin energy scan. Please run pr_setup.config() prior to
        a lockin scan.

    See Also
    --------
    :func:`moveE`
    :func:`Escan_list`
    :func:`Escan`
    """

    if not detectors:
        detectors = counters.detectors

    # Scalerd is always selected.
    if scalerd not in detectors:
        scalerd.select_plot_channels([])
        detectors += [scalerd]

    _md = {'plan_args': {'detectors': list(map(repr, detectors)),
                         'edge_energy': repr(edge_energy),
                         'dichro': dichro,
                         'lockin': lockin},
           'plan_name': 'qxscan'
           }

    _md.update(md or {})

    energy_list = yield from rd(qxscan_params.energy_list)
    energy_list = array(energy_list) + edge_energy

    _factor_list = yield from rd(qxscan_params.factor_list)

    return (yield from Escan_list(detectors, energy_list, time,
                                  factor_list=_factor_list, md=_md,
                                  dichro=dichro, lockin=lockin))
