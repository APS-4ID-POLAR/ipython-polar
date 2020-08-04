"""
Slitscan
"""

__all__ = ['moveE']


from bluesky.plan_stubs import mv,stage
from ..devices import undulator,mono

def moveE(energy):

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

    stage(mono)
    for args in args_list:
        yield from mv(*args)


# TODO: Add metadata?
# TODO: Add energy scans. Add a check of the energy direction, and a force option
# TODO: Add PRs
