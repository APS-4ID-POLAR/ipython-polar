"""
Modifed bluesky scans
"""

__all__ = ['lup', 'ascan', 'mv', 'mvr', 'qxscan']

from bluesky.plans import rel_scan, scan, list_scan
from bluesky.plan_stubs import trigger_and_read, move_per_step
from bluesky.plan_stubs import mv as bps_mv, rd
from bluesky.preprocessors import relative_set_decorator
from ..devices import (scalerd, pr_setup, mag6t, counters, undulator,
                       pr1, pr2, pr3, energy, qxscan_params)
from .local_preprocessors import (configure_counts_decorator,
                                  stage_dichro_decorator,
                                  stage_ami_decorator,
                                  energy_scan_decorator)
from numpy import array

try:
    # cytools is a drop-in replacement for toolz, implemented in Cython
    from cytools import partition
except ImportError:
    from toolz import partition

from ..session_logs import logger
logger.info(__file__)


def _collect_extras():

    extras = []
    und_track = yield from rd(undulator.downstream.tracking)
    if und_track:
        extras.append(undulator.downstream.energy)
    for pr in [pr1, pr2, pr3]:
        pr_track = yield from rd(pr.tracking)
        if pr_track:
            extras.append(pr.th)

    return extras


def dichro_steps(detectors, motors, take_reading):

    pr_pos = yield from rd(pr_setup.positioner)
    offset = yield from rd(pr_setup.offset)

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


def lup(*args, time=None, detectors=None, lockin=False, dichro=False,
        **kwargs):
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
    time : float, optional
        If a number is passed, it will modify the counts over time. All
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

    if not detectors:
        detectors = counters.detectors

    # Scalerd is always selected.
    if scalerd not in detectors:
        scalerd.select_plot_channels([])
        detectors += [scalerd]

    extras = []
    if energy in args:
        extras = yield from _collect_extras()

    @energy_scan_decorator(energy in args, extras)
    @stage_ami_decorator(mag6t.field in args)
    @configure_counts_decorator(detectors, time)
    @stage_dichro_decorator(dichro, lockin)
    def _inner_lup():
        yield from rel_scan(
            detectors + extras,
            *args,
            per_step=one_dichro_step if dichro else None,
            **kwargs)

    return (yield from _inner_lup())


def ascan(*args, time=None, detectors=None, lockin=False,
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
    time : float, optional
        If a number is passed, it will modify the counts over time. All
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

    if not detectors:
        detectors = counters.detectors

    # Scalerd is always selected.
    if scalerd not in detectors:
        scalerd.select_plot_channels([])
        detectors += [scalerd]

    extras = []
    if energy in args:
        extras = yield from _collect_extras()

    @energy_scan_decorator(energy in args, extras)
    @stage_ami_decorator(mag6t.field in args)
    @configure_counts_decorator(detectors, time)
    @stage_dichro_decorator(dichro, lockin)
    def _inner_ascan():
        yield from scan(
            detectors + extras,
            *args,
            per_step=one_dichro_step if dichro else None,
            **kwargs
            )

    return (yield from _inner_ascan())


def qxscan(edge_energy, time=None, detectors=None, lockin=False,
           dichro=False, **kwargs):

    if not detectors:
        detectors = [scalerd]

    per_step = one_dichro_step if dichro else None

    # Get energy argument and extras
    energy_list = yield from rd(qxscan_params.energy_list)
    args = (energy, array(energy_list) + edge_energy)

    extras = []
    if energy in args:
        extras = yield from _collect_extras()

    # Setup count time
    factor_list = yield from rd(qxscan_params.factor_list)

    _ct = {}
    if time:
        if time < 0 and detectors != [scalerd]:
            raise TypeError('time < 0 can only be used with scaler.')
        else:
            for det in detectors:
                _ct[det] = abs(time)
                args += (det.preset_monitor, abs(time)*array(factor_list))
    else:
        for det in detectors:
            _ct[det] = yield from rd(det.preset_monitor)
            args += (det.preset_monitor, _ct[det]*array(factor_list))

    @energy_scan_decorator(True, extras)
    @configure_counts_decorator(detectors, time)
    @stage_dichro_decorator(dichro, lockin)
    def _inner_qxscan():
        yield from list_scan(detectors+extras, *args, per_step=per_step,
                             **kwargs)

        # put original times back.
        for det, preset in _ct.items():
            yield from mv(det.preset_monitor, preset)

    return (yield from _inner_qxscan())


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
    @stage_ami_decorator(mag6t.field in args)
    def _inner_mv():
        yield from bps_mv(*args, **kwargs)

    return (yield from _inner_mv())


def mvr(*args, **kwargs):
    """
    Move one or more devices to a relative setpoint. Wait for all to complete.
    If more than one device is specified, the movements are done in parallel.

    This is a local version of `bluesky.plan_stubs.mvr`.

    Parameters
    ----------
    args :
        device1, value1, device2, value2, ...
    kwargs :
        passed to bluesky.plan_stub.mvr
    Yields
    ------
    msg : Msg
    See Also
    --------
    :func:`bluesky.plan_stubs.rel_set`
    :func:`bluesky.plan_stubs.mv`
    """
    objs = []
    for obj, _ in partition(2, args):
        objs.append(obj)

    @relative_set_decorator(objs)
    def _inner_mvr():
        return (yield from mv(*args, **kwargs))

    return (yield from _inner_mvr())
