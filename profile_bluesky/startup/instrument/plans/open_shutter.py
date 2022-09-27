"""
Plan to open shutters
"""

from ..devices import ashutter, bshutter, dshutter
from .local_preprocessors import _difference_check, SetSignal
from .local_scans import mv
from bluesky.plan_stubs import abs_set, rd
from toolz import partition

__all__ = [
    'shopen',
    'shclose'
]
# 30 sec timeout.
signal = SetSignal(name='tmp', timeout=30)


def shopen(hutch="d"):

    if hutch.lower() == "a":
        args = (ashutter, 1)
    elif hutch.lower() == "b":
        args = (ashutter, 1, bshutter, 1)
    elif hutch.lower() == "d":
        args = (ashutter, 1, bshutter, 1, dshutter, 1)
    else:
        raise ValueError("Input must be 'a', 'b', or 'd'.")

    for shutter, _ in partition(2, args):
        # Checking if all permits are good.
        for permit in ["user_enable", "aps_enable", "bleps"]:

            good = (
                0 if (shutter == ashutter) and (permit == "bleps") else 1
            )
            status = yield from rd(getattr(shutter, permit))
            
            if status != good:
                raise ValueError(f"{getattr(shutter, permit).name} is not enabled!")

        # Wait for search to end. Timeout is defined above.
        function = _difference_check(1, tolerance=0.1)
        yield from abs_set(
            signal, getattr(shutter, "searched"), function, wait=True,
        )

    yield from mv(*args)


def shclose(hutch="d"):
    if hutch.lower() == "a":
        args = (ashutter, 0)
    elif hutch.lower() == "b":
        args = (bshutter, 0)
    elif hutch.lower() == "d":
        args = (dshutter, 0)
    elif hutch.lower() == "all":
        args = (ashutter, 0, bshutter, 0, dshutter, 0)
    else:
        raise ValueError("Input must be 'a', 'b', 'd', or 'all'.")

    yield from mv(*args)
