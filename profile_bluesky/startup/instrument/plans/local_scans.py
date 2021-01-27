"""
Modifed bluesky scans
"""

__all__ = ['lup', 'ascan', 'mv']

from bluesky.plans import rel_scan, scan
from bluesky.plan_stubs import trigger_and_read, move_per_step
from bluesky.plan_stubs import mv as bps_mv
from ..devices import pr_setup, mag6t
from .local_preprocessors import (configure_monitor_decorator,
                                  stage_dichro_decorator,
                                  stage_ami_decorator)
from ..utils import local_rd

from ..session_logs import logger
logger.info(__file__)

# TODO: I would like to have something like this, but it cannot just be a list.
# Something like an imutable list might work.
# DEFAULT_DETECTORS = [scalerd]


def dichro_steps(detectors, motors, take_reading):

    pr_pos = yield from local_rd(pr_setup.positioner)
    offset = yield from local_rd(pr_setup.offset)

    for sign in pr_setup.dichro_steps:
        yield from mv(pr_setup.positioner, pr_pos + sign*offset)
        yield from take_reading(list(detectors) + list(motors) +
                                [pr_setup.positioner])

    # TODO: This step is unnecessary if the pr motor is used.
    yield from mv(pr_setup.positioner, pr_pos)


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
    yield from dichro_steps(detectors, motors, take_reading)


def lup(*args, monitor=None, detectors=None, lockin=False,
        dichro=False, **kwargs):
    """
    Scan over one multi-motor trajectory relative to current position.

    This is a local version of `bluesky.plans.rel_scan`. Note that the
    `per_step` cannot be set here, as it is used for dichro scans.

    Parameters
    ----------
    *args :
        For one dimension, ``motor, start, stop, number of points``.
        In general:
        .. code-block:: python
            motor1, start1, stop1,
            motor2, start2, start2,
            ...,
            motorN, startN, stopN,
            number of points
        Motors can be any 'settable' object (motor, temp controller, etc.)
    monitor : float, optional
        If a number is passed, it will modify the counts over monitor. All
        detectors need to have a .preset_monitor signal.
    lockin : boolean, optional
        Flag to do a lock-in scan. Please run pr_setup.config() prior do a
        lock-in scan.
    dichro : boolean, optional
        Flag to do a dichro scan. Please run pr_setup.config() prior do a
        dichro scan. Note that this will switch the x-ray polarization at every
        point using the +, -, -, + sequence, thus increasing the number of
        points by a factor of 4
    kwargs :
        Passed to `bluesky.plans.rel_scan`.

    See Also
    --------
    :func:`bluesky.plans.rel_scan`
    :func:`ascan`
    """

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
        yield from rel_scan(detectors, *args, per_step=per_step, **kwargs)

    return (yield from _inner_lup())


def ascan(*args, monitor=None, detectors=None, lockin=False,
          dichro=False, **kwargs):
    """
    Scan over one multi-motor trajectory.

    This is a local version of `bluesky.plans.scan`. Note that the `per_step`
    cannot be set here, as it is used for dichro scans.

    Parameters
    ----------
    *args :
        For one dimension, ``motor, start, stop, number of points``.
        In general:
        .. code-block:: python
            motor1, start1, stop1,
            motor2, start2, start2,
            ...,
            motorN, startN, stopN,
            number of points
        Motors can be any 'settable' object (motor, temp controller, etc.)
    monitor : float, optional
        If a number is passed, it will modify the counts over monitor. All
        detectors need to have a .preset_monitor signal.
    lockin : boolean, optional
        Flag to do a lock-in scan. Please run pr_setup.config() prior do a
        lock-in scan
    dichro : boolean, optional
        Flag to do a dichro scan. Please run pr_setup.config() prior do a
        dichro scan. Note that this will switch the x-ray polarization at every
        point using the +, -, -, + sequence, thus increasing the number of
        points by a factor of 4
    kwargs :
        Passed to `bluesky.plans.scan`.
    See Also
    --------
    :func:`bluesky.plans.scan`
    :func:`lup`
    """

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
        yield from scan(detectors, *args, per_step=per_step, **kwargs)

    return (yield from _inner_ascan())


def mv(*args, **kwargs):
    """
    Move one or more devices to a setpoint, and wait for all to complete.

    This is a local version of `bluesky.plan_stubs.mv`. If more than one device
    is specifed, the movements are done in parallel.


    Parameters
    ----------
    args :
        device1, value1, device2, value2, ...
    kwargs :
        passed to bluesky.plan_stubs.mv

    Yields
    ------
    msg : Msg

    See Also
    --------
    :func:`bluesky.plan_stubs.mv`
    """
    if mag6t.field in args:
        magnet = True
    else:
        magnet = False

    @stage_ami_decorator(magnet)
    def _inner_mv():
        yield from bps_mv(*args, **kwargs)

    return (yield from _inner_mv())
