"""
Slitscan
"""

__all__ = ['moveE']


from bluesky.plan_stubs import mv,stage
from ..devices import undulator,mono,pr1,pr2,pr3

from scipy.constants import speed_of_light, Planck
from numpy import arcsin,pi

def moveE(energy):
    #energy in keV

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

    for pr in [pr1,pr2,pr3]:
        if pr.tracking is True:
            lamb = speed_of_light*Planck*6.241509e15*1e10/energy
            theta = arcsin(lamb/2/pr.d_spacing.get())*180./pi
            args_list.append((pr.th,theta))

    stage(mono)
    for args in args_list:
        yield from mv(*args)


# TODO: Add metadata?
# TODO: Add energy scans. Add a check of the energy direction, and a force option
