"""
Slitscan
"""

__all__ = ['moveE']


from bluesky.plan_stubs import mv
from ..devices import undulator,mono

def moveE(energy):

    args_list = []
    
    args_list.append((mono.energy,energy))

    if undulator.tracking is True:
        
        target_energy = undulator.offset + energy
        current_energy = undulator.downstream.energy.get()+undulator.deadband
        
        if current_energy < target_energy:
            args_list[0] += (undulator.downstream.energy,target_energy+undulator.backlash)
            args_list[0] += (undulator.downstream.start_button,1)

            args_list.append((undulator.downstream.energy,target_energy))
            args_list[-1] += (undulator.downstream.start_button,1)
            
        else:
            args_list[0] += (undulator.downstream.energy,target_energy)
            args_list[0] += (undulator.downstream.start_button,1)

    for args in args_list:
        yield from mv(*args)


# TODO: Add metadata?
# TODO: Add energy scans
# TODO: Add PRs
    
