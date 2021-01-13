"""
Energy scans
"""

from ..session_logs import logger
logger.info(__file__)

__all__ = ['moveE', 'Escan', 'Escan_list', 'qxscan', 'undscan']

from bluesky.plan_stubs import mv, trigger_and_read
from bluesky.preprocessors import stage_decorator, run_decorator
from bluesky.utils import Msg, short_uid
from ..devices import undulator, mono, qxscan_params, pr1, pr2, pr3
from numpy import linspace, array, arcsin, pi
from scipy.constants import speed_of_light, Planck


def undscan(detectors, energy_0, energy_f, steps, md=None):

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

    @stage_decorator(decorators)
    def _inner_moveE():
        for args in args_list:
            yield from mv(*args, group=group)

    if len(args_list[0]) > 0:
        return (yield from _inner_moveE())
    else:
        return None


def Escan_list(detectors, energy_list, factor_list=None, md=None):

    _positioners = [mono.energy]
    if undulator.downstream.tracking:
        _positioners.append(undulator.downstream.energy)

    if factor_list is None:
        factor_list = [1 for i in range(len(energy_list))]
    else:
        if len(factor_list) != len(energy_list):
            raise ValueError('The size of factor_list cannot be different \
                              from the size of the energy_list')

    _md = {'detectors': [det.name for det in detectors],
           'positioners': [pos.name for pos in _positioners],
           'num_points': len(energy_list),
           'num_intervals': len(energy_list) - 1,
           'plan_args': {'detectors': list(map(repr, detectors)),
                         'energy_list': list(map(repr, energy_list))},
           'plan_name': 'Escan_list',
           'hints': {},
           }

    _md.update(md or {})

    _md['hints'] = {'dimensions': [(['monochromator_energy'], 'primary')]}
    _md['hints'].update(md.get('hints', {}) or {})

    # Collects current monitor count for each detector
    dets_preset = []
    for detector in detectors:
        dets_preset.append(detector.preset_monitor.get())

    @run_decorator(md=_md)
    def _inner_Escan_list():
        for energy, factor in zip(energy_list, factor_list):
            grp = short_uid('set')
            yield Msg('checkpoint')

            # Change counting time
            for detector, original_preset in zip(detectors, dets_preset):
                yield from detector.SetCountTimePlan(factor*original_preset,
                                                     group=grp)

            # Move and scan
            yield from moveE(energy, group=grp)
            yield from trigger_and_read(list(detectors)+_positioners)

        # Put counting time back to original
        for detector, original_preset in zip(detectors, dets_preset):
            yield from detector.SetCountTimePlan(original_preset)

    return (yield from _inner_Escan_list())


def Escan(detectors, energy_0, energy_f, steps, md=None):
    _md = {'plan_args': {'detectors': list(map(repr, detectors)),
                         'initial_energy': repr(energy_0),
                         'final_energy': repr(energy_f),
                         'steps': repr(steps)},
           'plan_name': 'Escan',
           'hints': {'x': ['mono_energy']},
           }

    _md.update(md or {})
    energy_list = linspace(energy_0, energy_f, steps)
    return (yield from Escan_list(detectors, energy_list, md=_md))


def qxscan(detectors, edge_energy, md=None):

    _md = {'plan_args': {'detectors': list(map(repr, detectors)),
                         'edge_energy': repr(edge_energy)},
           'plan_name': 'qxscan',
           'hints': {},
           }

    _md.update(md or {})
    energy_list = array(qxscan_params.energy_list.get())+edge_energy
    return (yield from Escan_list(detectors, energy_list,
                                  factor_list=qxscan_params.factor_list.get(),
                                  md=_md))
