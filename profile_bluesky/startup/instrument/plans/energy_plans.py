"""
Energy scans
"""

__all__ = ['moveE', 'Escan', 'Escan_list', 'qxscan', 'undscan']

from bluesky.plan_stubs import mv, trigger_and_read
from bluesky.plans import list_scan
from bluesky.preprocessors import stage_decorator, run_decorator
from bluesky.utils import Msg, short_uid
from ..devices import undulator, mono, qxscan_params
from numpy import linspace


def undscan(detectors, energy_0, energy_f, steps, md=None):
    _md = {'plan_args': {'detectors': list(map(repr, detectors)),
                         'initial_energy': repr(energy_0),
                         'final_energy': repr(energy_f),
                         'steps': repr(steps)},
           'plan_name': 'undscan',
           'hints': {'x': ['undulator_downstream_energy']},
           }

    _md.update(md or {})
    energy_list = linspace(energy_0, energy_f, steps)
    start_list = [1 for i in range(steps)]
    return (yield from list_scan(detectors,
                                 undulator.downstream.energy, energy_list,
                                 undulator.downstream.start_button, start_list,
                                 md=_md))


def moveE(energy, group=None):
    args_list = []

    args_list.append((mono.energy, energy))

    if undulator.downstream.tracking is True:

        target_energy = undulator.downstream.offset + energy
        current_energy = undulator.downstream.energy.get() + undulator.downstream.deadband

        if current_energy < target_energy:
            args_list[0] += (undulator.downstream.energy,
                             target_energy+undulator.downstream.backlash)
            args_list[0] += (undulator.downstream.start_button, 1)

            args_list.append((undulator.downstream.energy, target_energy))
            args_list[-1] += (undulator.downstream.start_button, 1)

        else:
            args_list[0] += (undulator.downstream.energy, target_energy)
            args_list[0] += (undulator.downstream.start_button, 1)

    @stage_decorator([mono, undulator.downstream])
    def _inner_moveE():
        for args in args_list:
            yield from mv(*args, group=group)

    return (yield from _inner_moveE())


def Escan_list(detectors, energy_list, md = None):

    _positioners = [mono.energy]
    if undulator.downstream.tracking:
        _positioners.append(undulator.downstream.energy)

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

    @run_decorator(md=_md)
    def _inner_Escan_list():
        for energy in energy_list:
            grp = short_uid('set')
            yield Msg('checkpoint')
            yield from moveE(energy, group=grp)
            yield from trigger_and_read(list(detectors)+_positioners)

    return (yield from _inner_Escan_list())


def Escan(detectors, energy_0, energy_f, steps, md = None):
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


def qxscan(detectors, edge_energy, md = None):

    _md = {'plan_args': {'detectors': list(map(repr, detectors)),
                         'edge_energy': repr(edge_energy),
                         'qx_setup': qxscan_params._make_params_dict()},

           'plan_name': 'qxscan',
           'hints': {},
           }

    _md.update(md or {})
    energy_list = qxscan_params.energy_list
    return (yield from Escan_list(detectors, energy_list, md=_md))

# TODO: Add PRs
