"""
Slitscan
"""

__all__ = ['moveE']


from bluesky.plan_stubs import mv
from ..devices import undulator,mono

def moveE(energy):

    args = (mono.energy,energy)

    if undulator.tracking is True:
        args += (undulator.downstream.energy,energy)

    yield from mv(*args)


# TODO: Add metadata?
# TODO: Add energy scans
