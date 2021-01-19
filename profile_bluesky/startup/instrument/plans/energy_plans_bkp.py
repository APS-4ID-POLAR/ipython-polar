"""
Energy scans
"""

__all__ = ['moveE', 'Escan', 'Escan_list', 'qxscan']

from bluesky.plan_stubs import mv, trigger_and_read
from bluesky.preprocessors import stage_decorator, run_decorator
from bluesky.utils import Msg, short_uid
from ..devices import undulator, mono, qxscan_params, pr1, pr2, pr3
from ..devices import pr_setup
from numpy import linspace, array
from .local_preprocessors import stage_dichro_decorator
from ..utils import local_rd


def moveE(energy, group=None):
    """
    Move beamline energy.

    It reads the tracking flags of the undulator and phase retarders.

    Parameters
    ----------
    energy : float
        Target energy
    group : string, optional
        Used to mark these as a unit to be waited on.

    See Also
    --------
    :func:`bluesky.plan_stubs.mv`
    :func:`Escan`
    """
    args = ()
    decorators = []

    # Move mono if motion is larger than tolerance.
    _mono_energy = yield from local_rd(mono.energy)
    if abs(energy - _mono_energy) > mono.energy.tolerance:
        args += (mono.energy, energy)
        decorators.append(mono)

    # Move PRs that are tracking.
    for pr in [pr1, pr2, pr3]:
        _pr_tracking = yield from local_rd(pr.tracking)
        if _pr_tracking is True:
            args += (pr.energy, energy)
            decorators.append(pr)

    # Move undulator if tracking.
    _und_tracking = yield from local_rd(undulator.downstream.tracking)
    if _und_tracking is True:
        _und_offset = yield from local_rd(undulator.downstream.energy.offset)
        args += (undulator.downstream.energy, energy + _und_offset)
        decorators.append(undulator.downstream.energy)

    @stage_decorator(decorators)
    def _inner_moveE():
        yield from mv(*args, group=group)

    return (yield from _inner_moveE())


def Escan_list(detectors, energy_list, factor_list=None, md=None,
               dichro=False, lockin=False):
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

    _und_tracking = yield from local_rd(undulator.downstream.tracking)
    if _und_tracking:
        _positioners.append(undulator.downstream.energy)

    for pr in [pr1, pr2, pr3]:
        _pr_tracking = yield from local_rd(pr.tracking)
        if _pr_tracking is True:
            _positioners.append(pr.th)
            _positioners.append(pr.energy)

    # Controls the time per point.
    if factor_list is None:
        factor_list = [1 for i in range(len(energy_list))]
    else:
        if len(factor_list) != len(energy_list):
            raise ValueError('The size of factor_list cannot be different \
                              from the size of the energy_list')

    # Metadata
    _md = {'detectors': [det.name for det in detectors],
           'positioners': [pos.name for pos in _positioners],
           'num_points': len(energy_list),
           'num_intervals': len(energy_list) - 1,
           'plan_args': {'detectors': list(map(repr, detectors)),
                         'energy_list': list(map(repr, energy_list))},
           'plan_name': 'Escan_list',
           'hints': {'x': ['mono_energy']},
           }

    _md.update(md or {})

    _md['hints'] = {'dimensions': [(['monochromator_energy'], 'primary')]}
    _md['hints'].update(md.get('hints', {}) or {})

    # Collects current monitor count for each detector
    dets_preset = []
    for detector in detectors:
        dets_preset.append(detector.preset_monitor.get())

    # Setup dichro
    if dichro:
        _positioners.append(pr_setup.positioner)

    pos_cache = defaultdict(lambda: None)  # where last position is stashed
    
    @stage_dichro_decorator(dichro, lockin)
    @run_decorator(md=_md)
    def _inner_Escan_list():
        yield from moveE(energy_list[0]+0.001)
        for energy, factor in zip(energy_list, factor_list):
            grp = short_uid('set')
            yield Msg('checkpoint')

            # Change counting time
            for detector, original_preset in zip(detectors, dets_preset):
                yield from detector.SetCountTimePlan(factor*original_preset,
                                                     group=grp)

            # Move and scan
            yield from moveE(energy, group=grp)
            if dichro:
                pr_pos = yield from local_rd(pr_setup.positioner)
                offset = yield from local_rd(pr_setup.offset)
                for sign in [1, -1, -1, 1]:
                    yield from mv(pr_setup.positioner, pr_pos + sign*offset)
                    yield from trigger_and_read(list(detectors)+_positioners)
                yield from mv(pr_setup.positioner, pr_pos)
            else:
                yield from trigger_and_read(list(detectors)+_positioners)

        # Put counting time back to original
        for detector, original_preset in zip(detectors, dets_preset):
            yield from detector.SetCountTimePlan(original_preset)

    return (yield from _inner_Escan_list())


def Escan(detectors, energy_0, energy_f, steps, md=None, dichro=False,
          lockin=False):
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
    _md = {'plan_args': {'detectors': list(map(repr, detectors)),
                         'initial_energy': repr(energy_0),
                         'final_energy': repr(energy_f),
                         'steps': repr(steps)},
           'plan_name': 'Escan',
           'hints': {'x': ['mono_energy']},
           }

    _md.update(md or {})
    energy_list = linspace(energy_0, energy_f, steps)
    return (yield from Escan_list(detectors, energy_list, md=_md,
                                  dichro=dichro, lockin=lockin))


def qxscan(detectors, edge_energy, md=None, dichro=False, lockin=False):
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
    _md = {'plan_args': {'detectors': list(map(repr, detectors)),
                         'edge_energy': repr(edge_energy),
                         'dichro': dichro,
                         'lockin': lockin},
           'plan_name': 'qxscan',
           'hints': {'x': ['mono_energy']},
           }

    _md.update(md or {})

    energy_list = yield from local_rd(qxscan_params.energy_list)
    energy_list = array(energy_list) + edge_energy

    _factor_list = yield from local_rd(qxscan_params.factor_list)

    return (yield from Escan_list(detectors, energy_list,
                                  factor_list=_factor_list, md=_md,
                                  dichro=dichro, lockin=lockin))