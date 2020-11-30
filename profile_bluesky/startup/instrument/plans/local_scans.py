"""
Modifed bluesky scans
"""

__all__ = ['lup', 'ascan', 'mv']

from bluesky.plans import rel_scan, scan
from bluesky.plan_stubs import trigger_and_read, move_per_step
from bluesky.plan_stubs import mv as bps_mv
from ..devices import scalerd, pr_setup, mag6t
from .local_preprocessors import (configure_monitor_decorator,
                                  stage_dichro_decorator,
                                  stage_ami_decorator)

# TODO: should I have some default like this?
# DETECTORS = [scalerd]

#def amifield(target):
#    """ DEPRECATED - use RE(mv(mag6t.field,target)) """
#
#    @stage_ami_decorator(True)
#    def _inner_amifield():
#        yield from mv(mag6t.field, target)
#
#    return (yield from _inner_amifield())
    
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

    if mag6t.field in args:
        magnet = True
    else:
        magnet = False

    @stage_ami_decorator(magnet)
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

    if mag6t.field in args:
        magnet = True
    else:
        magnet = False

    @stage_ami_decorator(magnet)
    @configure_monitor_decorator(monitor)
    @stage_dichro_decorator(dichro, lockin)
    def _inner_ascan():
        yield from scan(detectors, *args, md=md, per_step=per_step)

    return (yield from _inner_ascan())

def mv(*args, **kwargs):
    
    if mag6t.field in args:
        magnet = True
    else:
        magnet = False
        
    @stage_ami_decorator(magnet)
    def _inner_mv():
        yield from bps_mv(*args, **kwargs)
        
    return (yield from _inner_mv())