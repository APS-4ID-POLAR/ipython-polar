"""
Modifed bluesky scans
"""

__all__ = ['lup', 'ascan']

from bluesky.plans import rel_scan, scan
from bluesky.plan_stubs import mv, trigger_and_read, move_per_step
from ..devices import scalerd, pr_setup
from .local_preprocessors import (configure_monitor_decorator,
                                  stage_dichro_decorator)

# TODO: should I have some default like this?
# DETECTORS = [scalerd]


def one_dichro_step(detectors, step, pos_cache, take_reading=trigger_and_read):
    """
    Inner loop for dichro scans.

    Parameters
    ----------
    detectors : iterable
        devices to read
    step : dict
        mapping motors to positions in this step
    pos_cache : dict
        mapping motors to their last-set positions
    take_reading : plan, optional
        function to do the actual acquisition ::
           def take_reading(dets, name='primary'):
                yield from ...
        Callable[List[OphydObj], Optional[str]] -> Generator[Msg], optional
        Defaults to `trigger_and_read`
    """

    motors = step.keys()
    yield from move_per_step(step, pos_cache)

    offset = pr_setup.positioner.parent.offset.get()
    pr_pos = pr_setup.positioner.get()

    for sign in [1, -1, -1, 1]:
        yield from mv(pr_setup.positioner, pr_pos + sign*offset)
        yield from take_reading(list(detectors) + list(motors) +
                                [pr_setup.positioner])

    # TODO: This step is unnecessary if the pr motor is used.
    yield from mv(pr_setup.positioner, pr_pos)

def lup(*args, monitor=None, detectors=[scalerd], lockin=False, dichro=False,
        md=None):

    if dichro:
        per_step = one_dichro_step
    else:
        per_step = None

    @configure_monitor_decorator(monitor)
    @stage_dichro_decorator(dichro, lockin)
    def _inner_lup():
        yield from rel_scan(detectors, *args, md=md, per_step=per_step)

    return (yield from _inner_lup())


def ascan(*args, monitor=None, detectors=[scalerd], lockin=False,
          dichro=False, md=None):

    if dichro:
        per_step = one_dichro_step
    else:
        per_step = None

    @configure_monitor_decorator(monitor)
    @stage_dichro_decorator(dichro, lockin)
    def _inner_lup():
        yield from scan(detectors, *args, md=md, per_step=per_step)

    return (yield from _inner_lup())
