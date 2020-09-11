"""
Slitscan
"""

__all__ = ['moveE','Escan','Escan_list','qxscan','qxscan_setup']

from bluesky.plan_stubs import mv,trigger_and_read
from bluesky.preprocessors import stage_decorator,run_decorator,subs_decorator
from bluesky.utils import Msg, short_uid
from ..devices import undulator,mono
from numpy import linspace,arange,sqrt,array
#from ..framework import bec
#from ..callbacks import AbsorptionPlot

hbar = 6.582119569E-16 #eV.s
speed_of_light = 299792458e10 # A/s
electron_mass = 0.510998950E6/speed_of_light**2 # eV.s**2/A**2

global constant
constant = 2*electron_mass/hbar**2 # A^2/eV

def moveE(energy,group=None):

    args_list = []

    args_list.append((mono.energy,energy))

    if undulator.downstream.tracking is True:

        target_energy = undulator.downstream.offset + energy
        current_energy = undulator.downstream.energy.get()+undulator.downstream.deadband

        if current_energy < target_energy:
            args_list[0] += (undulator.downstream.energy,target_energy+undulator.downstream.backlash)
            args_list[0] += (undulator.downstream.start_button,1)

            args_list.append((undulator.downstream.energy,target_energy))
            args_list[-1] += (undulator.downstream.start_button,1)

        else:
            args_list[0] += (undulator.downstream.energy,target_energy)
            args_list[0] += (undulator.downstream.start_button,1)

    @stage_decorator([mono,undulator.downstream])
    def _inner_moveE():
        for args in args_list:
            yield from mv(*args,group=group)

    return (yield from _inner_moveE())
    
def Escan_list(detectors, energy_list, md = None):

    _positioners= [mono.energy]
    if undulator.downstream.tracking:
        _positioners.append(undulator.downstream.energy)

    _md = {'detectors': [det.name for det in detectors],
           'positioners': [pos.name for pos in _positioners],
           'num_points': len(energy_list),
           'num_intervals': len(energy_list)- 1,
           'plan_args': {'detectors': list(map(repr, detectors)),
                         'energy_list': list(map(repr, energy_list))},
           'plan_name': 'Escan_list',
           'hints': {},
           }

    _md.update(md or {})

    _md['hints'] = {'dimensions': [(['monochromator_energy'],'primary')]}
    _md['hints'].update(md.get('hints', {}) or {})

    #abs_plot = AbsorptionCallback()
    #@subs_decorator(Absorption)
    @run_decorator(md=_md)
    def _inner_Escan_list():
        for energy in energy_list:
            grp = short_uid('set')
            yield Msg('checkpoint')
            yield from moveE(energy,group=grp)
            yield from trigger_and_read(list(detectors)+_positioners)

    return (yield from _inner_Escan_list())

def Escan(detectors,energy_0, energy_f, steps, md = None):

    _md = {'plan_args': {'detectors': list(map(repr, detectors)),
                         'initial_energy': repr(energy_0),
                         'final_energy': repr(energy_f),
                         'steps': repr(steps)},
           'plan_name': 'Escan',
           'hints': {'x':['mono_energy']},
           }

    _md.update(md or {})
    energy_list = linspace(energy_0,energy_f,steps)
    return (yield from Escan_list(detectors,energy_list,md=_md))

#TODO: not sure where to put this. Maybe it is best fit for the mono?
#TODO: How to implement distinct collection times?
def qxscan_setup():

    qxdict = {}
    print('Defining the energy range and steps for qxscan')
    print('All energies are relative to the absorption edge!')

    while True:
        qxdict['num_preedge'] = int(input('\n Number of pre-edge regions: '))
        if qxdict['num_preedge'] >= 1:
            break
        else:
            print('WARNING: number of pre-edge regions need to be >= 1!')

    qxdict['preedge_params'] = []
    for i in range(qxdict['num_preedge']):
        print('\n Defining pre-edge #{}'.format(i+1))
        relative_energy = float(input('Start energy (in eV): '))
        energy_increment = float(input('Energy increment (in eV): '))
        #collection_time
        qxdict['preedge_params'].append({'relative_energy_start': relative_energy,
                                         'energy_increment': energy_increment})

    print('\n Defining edge region')
    relative_energy_start = float(input('Start energy (in eV): '))
    relative_energy_end = float(input('Final energy (in eV): '))
    energy_increment = float(input('Energy increment (in eV): '))
    #collection_time
    qxdict['edge_params'] = {'relative_energy_start': relative_energy_start,
                             'relative_energy_end': relative_energy_end,
                             'energy_increment': energy_increment}

    kend = sqrt(constant*qxdict['edge_params']['relative_energy_end'])
    print('Your edge region end at k = {:0.3f} angstroms^-1'.format(kend))

    while True:
        qxdict['num_postedge'] = int(input('\n Number of post-edge regions: '))
        if qxdict['num_postedge'] >= 1:
            break
        else:
            print('WARNING: number of post-edge regions need to be >= 1!')

    qxdict['postedge_params'] = []
    for i in range(qxdict['num_postedge']):
        print('\n Defining post-edge #{}'.format(i+1))
        relative_k = float(input('k end (in angstroms^-1): '))
        k_increment = float(input('k increment (in angstroms^-1): '))
        #collection_time
        qxdict['postedge_params'].append({'relative_k_end': relative_k,
                                         'k_increment': k_increment})


    qxdict['relative_energy'] = []

    # Pre-edge region
    for i,params in enumerate(qxdict['preedge_params']):

        start = params['relative_energy_start']
        step = params['energy_increment']

        if i != qxdict['num_preedge']-1:
            end = qxdict['preedge_params'][i+1]['relative_energy_start']
        else:
            end = qxdict['edge_params']['relative_energy_start']

        qxdict['relative_energy'] += list(arange(start,end,step))

    # Edge region
    params = qxdict['edge_params']
    start = params['relative_energy_start']
    end = params['relative_energy_end']
    step = params['energy_increment']

    qxdict['relative_energy'] += list(arange(start,end,step))

    # Post-edge region

    for i,params in enumerate(qxdict['postedge_params']):

        end = params['relative_k_end']
        step = params['k_increment']

        if i == 0:
            start = sqrt(ßconstant*qxdict['edge_params']['relative_energy_end'])
        else:
            start = qxdict['postedge_params'][i-1]['relative_k_end']

        qxdict['relative_energy'] += list(arange(start,end,step)**2/constant)
        qxdict['relative_energy'] += [end**2/constant]

    qxdict['relative_energy'] = array(qxdict['relative_energy'])[::-1]/1000.
    
    print('\nNumber of points: {}'.format(qxdict['relative_energy'].size))
    print('Final relative energy: {:0.3f} eV'.format(qxdict['relative_energy'].max()))

    return qxdict

def qxscan(detectors, edge_energy, qxdict, md = None):

    _md = {'plan_args': {'detectors': list(map(repr, detectors)),
                         'edge_energy': repr(edge_energy),
                         'qx_setup': qxdict},

           'plan_name': 'qxscan',
           'hints': {},
           }

    _md.update(md or {})
    energy_list = qxdict['relative_energy']+edge_energy
    return (yield from Escan_list(detectors,energy_list,md=_md))

# TODO: Add PRs
