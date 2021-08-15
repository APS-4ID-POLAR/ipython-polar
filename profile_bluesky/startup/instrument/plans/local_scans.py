"""
Modifed bluesky scans
"""

__all__ = ['lup', 'ascan', 'mv', 'mvr', 'grid_scan', 'rel_grid_scan', 'qxscan',
           'dichro_steps']

from bluesky.plans import scan, list_scan, grid_scan as bp_grid_scan
from bluesky.plan_stubs import (
    trigger_and_read, move_per_step, mv as bps_mv, rd
)
from bluesky.preprocessors import (
    reset_positions_decorator, relative_set_decorator
)
from bluesky.plan_patterns import chunk_outer_product_args
from ..devices import (scalerd, pr_setup, mag6t, undulator, fourc,
                       pr1, pr2, pr3, energy, qxscan_params)
from .local_preprocessors import (configure_counts_decorator,
                                  stage_dichro_decorator,
                                  stage_ami_decorator,
                                  extra_devices_decorator)
from ..utils import counters
from ..devices.ad_eiger import LocalEigerDetector
from ..framework import RE
from numpy import array

try:
    # cytools is a drop-in replacement for toolz, implemented in Cython
    from cytools import partition
except ImportError:
    from toolz import partition

from ..session_logs import logger
logger.info(__file__)


class LocalFlag:
    dichro = False
    fixq = False
    hkl_pos = {}


flag = LocalFlag()


def _collect_extras(escan_flag, fourc_flag):

    extras = counters.extra_devices.copy()

    if escan_flag:
        und_track = yield from rd(undulator.downstream.tracking)
        if und_track:
            extras.append(undulator.downstream.energy)
        for pr in [pr1, pr2, pr3]:
            pr_track = yield from rd(pr.tracking)
            if pr_track:
                extras.append(pr.th)

    if fourc_flag:
        extras.append(fourc)

    return extras


def dichro_steps(devices_to_read, take_reading):

    pr_pos = yield from rd(pr_setup.positioner)
    offset = yield from rd(pr_setup.offset)
    devices_to_read += [pr_setup.positioner]
    for sign in pr_setup.dichro_steps:
        yield from mv(pr_setup.positioner, pr_pos + sign*offset)
        yield from take_reading(devices_to_read)

    yield from mv(pr_setup.positioner, pr_pos)


def one_local_step(detectors, step, pos_cache, take_reading=trigger_and_read):
    """
    Inner loop for fixQ and dichro scans.

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

    devices_to_read = list(step.keys()) + list(detectors)
    yield from move_per_step(step, pos_cache)

    if flag.fixq:
        devices_to_read += [fourc]
        args = (fourc.h, flag.hkl_pos[fourc.h],
                fourc.k, flag.hkl_pos[fourc.k],
                fourc.l, flag.hkl_pos[fourc.l])
        yield from bps_mv(*args)

    if flag.dichro:
        yield from dichro_steps(devices_to_read, take_reading)
    else:
        yield from take_reading(devices_to_read)


def ascan(*args, time=None, detectors=None, lockin=False, dichro=False,
          fixq=False, per_step=None, md=None):
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
    detectors : list, optional
        List of detectors to be used in the scan. If None, will use the
        detectors defined in `counters.detectors`.
    lockin : boolean, optional
        Flag to do a lock-in scan. Please run pr_setup.config() prior do a
        lock-in scan
    dichro : boolean, optional
        Flag to do a dichro scan. Please run pr_setup.config() prior do a
        dichro scan. Note that this will switch the x-ray polarization at every
        point using the +, -, -, + sequence, thus increasing the number of
        points by a factor of 4
    fixq : boolean, optional
        Flag for fixQ scans. If True, it will fix the diffractometer hkl
        position during the scan. This is particularly useful for energy scan.
        Note that hkl is moved ~after~ the other motors!
    per_step: callable, optional
        hook for customizing action of inner loop (messages per step).
        See docstring of :func:`bluesky.plan_stubs.one_nd_step` (the default)
        for details.
    md : dictionary, optional
        Metadata to be added to the run start.

    See Also
    --------
    :func:`bluesky.plans.scan`
    :func:`lup`
    """
    flag.dichro = dichro
    flag.fixq = fixq
    if per_step is None:
        per_step = one_local_step if fixq or dichro else None
    if fixq:
        flag.hkl_pos = {
            fourc.h: fourc.h.get().setpoint,
            fourc.k: fourc.k.get().setpoint,
            fourc.l: fourc.l.get().setpoint,
        }

    # This allows passing "time" without using the keyword.
    if len(args) % 3 == 2 and time is None:
        time = args[-1]
        args = args[:-1]

    if detectors is None:
        detectors = counters.detectors

    extras = yield from _collect_extras(energy in args, "fourc" in str(args))

    for det in detectors + extras:
        if isinstance(det, LocalEigerDetector):
            det.file.base_name = f"scan{RE.md['scan_id'] + 1}"

    # TODO: The md handling might go well in a decorator.
    # TODO: May need to add reference to stream.
    _md = {'hints': {'monitor': counters.monitor, 'detectors': []}}
    for item in detectors:
        _md['hints']['detectors'].extend(item.hints['fields'])

    if dichro:
        _md['hints']['scan_type'] = 'dichro'

    _md.update(md or {})

    @configure_counts_decorator(detectors, time)
    @stage_ami_decorator(mag6t.field in args)
    @stage_dichro_decorator(dichro, lockin)
    @extra_devices_decorator(extras)
    def _inner_ascan():
        yield from scan(
            detectors + extras,
            *args,
            per_step=per_step,
            md=_md
            )

    return (yield from _inner_ascan())


def lup(*args, time=None, detectors=None, lockin=False, dichro=False,
        fixq=False, per_step=None, md=None):
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
    detectors : list, optional
        List of detectors to be used in the scan. If None, will use the
        detectors defined in `counters.detectors`.
    lockin : boolean, optional
        Flag to do a lock-in scan. Please run pr_setup.config() prior do a
        lock-in scan.
    dichro : boolean, optional
        Flag to do a dichro scan. Please run pr_setup.config() prior do a
        dichro scan. Note that this will switch the x-ray polarization at every
        point using the +, -, -, + sequence, thus increasing the number of
        points by a factor of 4
    fixq : boolean, optional
        Flag for fixQ scans. If True, it will fix the diffractometer hkl
        position during the scan. This is particularly useful for energy scan.
        Note that hkl is moved ~after~ the other motors!
    per_step: callable, optional
        hook for customizing action of inner loop (messages per step).
        See docstring of :func:`bluesky.plan_stubs.one_nd_step` (the default)
        for details.
    md : dictionary, optional
        Metadata to be added to the run start.

    See Also
    --------
    :func:`bluesky.plans.rel_scan`
    :func:`ascan`
    """

    _md = {'plan_name': 'rel_scan'}
    md = md or {}
    _md.update(md)
    motors = [motor for motor, _, _ in partition(3, args)]

    @reset_positions_decorator(motors)
    @relative_set_decorator(motors)
    def inner_lup():
        return (yield from ascan(
            *args,
            time=time,
            detectors=detectors,
            lockin=lockin,
            dichro=dichro,
            fixq=fixq,
            per_step=per_step,
            md=_md
        ))

    return (yield from inner_lup())


def grid_scan(*args, time=None, detectors=None, snake_axes=None, lockin=False,
              dichro=False, fixq=False, per_step=None, md=None):
    """
    Scan over a mesh; each motor is on an independent trajectory.
    Parameters
    ----------
    ``*args``
        patterned like (``motor1, start1, stop1, num1,``
                        ``motor2, start2, stop2, num2,``
                        ``motor3, start3, stop3, num3,`` ...
                        ``motorN, startN, stopN, numN``)
        The first motor is the "slowest", the outer loop. For all motors
        except the first motor, there is a "snake" argument: a boolean
        indicating whether to following snake-like, winding trajectory or a
        simple left-to-right trajectory.
    time : float, optional
        If a number is passed, it will modify the counts over time. All
        detectors need to have a .preset_monitor signal.
    snake_axes: boolean or iterable, optional
        which axes should be snaked, either ``False`` (do not snake any axes),
        ``True`` (snake all axes) or a list of axes to snake. "Snaking" an axis
        is defined as following snake-like, winding trajectory instead of a
        simple left-to-right trajectory. The elements of the list are motors
        that are listed in `args`. The list must not contain the slowest
        (first) motor, since it can't be snaked.
    detectors : list, optional
        List of detectors to be used in the scan. If None, will use the
        detectors defined in `counters.detectors`.
    lockin : boolean, optional
        Flag to do a lock-in scan. Please run pr_setup.config() prior do a
        lock-in scan
    dichro : boolean, optional
        Flag to do a dichro scan. Please run pr_setup.config() prior do a
        dichro scan. Note that this will switch the x-ray polarization at every
        point using the +, -, -, + sequence, thus increasing the number of
        points by a factor of 4
    fixq : boolean, optional
        Flag for fixQ scans. If True, it will fix the diffractometer hkl
        position during the scan. This is particularly useful for energy scan.
        Note that hkl is moved ~after~ the other motors!
    per_step: callable, optional
        hook for customizing action of inner loop (messages per step).
        See docstring of :func:`bluesky.plan_stubs.one_nd_step` (the default)
        for details.
    md: dict, optional
        metadata

    See Also
    --------
    :func:`bluesky.plans.grid_scan`
    :func:`bluesky.plans.rel_grid_scan`
    :func:`bluesky.plans.inner_product_scan`
    :func:`bluesky.plans.scan_nd`
    """

    flag.dichro = dichro
    flag.fixq = fixq
    if per_step is None:
        per_step = one_local_step if fixq or dichro else None

    if fixq:
        flag.hkl_pos = {
            fourc.h: fourc.h.get().setpoint,
            fourc.k: fourc.k.get().setpoint,
            fourc.l: fourc.l.get().setpoint,
        }

    # This allows passing "time" without using the keyword.
    if len(args) % 4 == 1 and time is None:
        time = args[-1]
        args = args[:-1]

    if detectors is None:
        detectors = counters.detectors

    extras = yield from _collect_extras(energy in args, "fourc" in str(args))

    for det in detectors + extras:
        if isinstance(det, LocalEigerDetector):
            det.file.base_name = f"scan{RE.md['scan_id'] + 1}"

    # TODO: The md handling might go well in a decorator.
    # TODO: May need to add reference to stream.
    _md = {'hints': {'monitor': counters.monitor, 'detectors': []}}
    for item in detectors:
        _md['hints']['detectors'].extend(item.hints['fields'])

    if dichro:
        _md['hints']['scan_type'] = 'dichro'

    _md.update(md or {})

    @configure_counts_decorator(detectors, time)
    @stage_ami_decorator(mag6t.field in args)
    @stage_dichro_decorator(dichro, lockin)
    @extra_devices_decorator(extras)
    def _inner_grid_scan():
        yield from bp_grid_scan(
            detectors + extras,
            *args,
            snake_axes=snake_axes,
            per_step=per_step,
            md=_md
        )
    return (yield from _inner_grid_scan())


def rel_grid_scan(*args, time=None, detectors=None, snake_axes=None,
                  lockin=False, dichro=False, fixq=False, per_step=None,
                  md=None):
    """
    Scan over a mesh relative to current position.

    Each motor is on an independent trajectory.

    Parameters
    ----------
    ``*args``
        patterned like (``motor1, start1, stop1, num1,``
                        ``motor2, start2, stop2, num2,``
                        ``motor3, start3, stop3, num3,`` ...
                        ``motorN, startN, stopN, numN``)
        The first motor is the "slowest", the outer loop. For all motors
        except the first motor, there is a "snake" argument: a boolean
        indicating whether to following snake-like, winding trajectory or a
        simple left-to-right trajectory.
    time : float, optional
        If a number is passed, it will modify the counts over time. All
        detectors need to have a .preset_monitor signal.
    snake_axes: boolean or iterable, optional
        which axes should be snaked, either ``False`` (do not snake any axes),
        ``True`` (snake all axes) or a list of axes to snake. "Snaking" an axis
        is defined as following snake-like, winding trajectory instead of a
        simple left-to-right trajectory. The elements of the list are motors
        that are listed in `args`. The list must not contain the slowest
        (first) motor, since it can't be snaked.
    detectors : list, optional
        List of detectors to be used in the scan. If None, will use the
        detectors defined in `counters.detectors`.
    lockin : boolean, optional
        Flag to do a lock-in scan. Please run pr_setup.config() prior do a
        lock-in scan
    dichro : boolean, optional
        Flag to do a dichro scan. Please run pr_setup.config() prior do a
        dichro scan. Note that this will switch the x-ray polarization at every
        point using the +, -, -, + sequence, thus increasing the number of
        points by a factor of 4
    fixq : boolean, optional
        Flag for fixQ scans. If True, it will fix the diffractometer hkl
        position during the scan. This is particularly useful for energy scan.
        Note that hkl is moved ~after~ the other motors!
    per_step: callable, optional
        hook for customizing action of inner loop (messages per step).
        See docstring of :func:`bluesky.plan_stubs.one_nd_step` (the default)
        for details.
    md: dict, optional
        metadata

    See Also
    --------
    :func:`grid_scan`
    :func:`bluesky.plans.grid_scan`
    :func:`bluesky.plans.rel_grid_scan`
    :func:`bluesky.plans.inner_product_scan`
    :func:`bluesky.plans.scan_nd`
    """

    _md = {'plan_name': 'rel_grid_scan'}
    _md.update(md or {})
    motors = [m[0] for m in chunk_outer_product_args(args)]

    @reset_positions_decorator(motors)
    @relative_set_decorator(motors)
    def inner_rel_grid_scan():
        return (yield from grid_scan(
            *args,
            time=time,
            detectors=detectors,
            snake_axes=snake_axes,
            lockin=lockin,
            dichro=dichro,
            fixq=fixq,
            per_step=per_step,
            md=_md
        ))

    return (yield from inner_rel_grid_scan())


def qxscan(edge_energy, time=None, detectors=None, lockin=False, dichro=False,
           fixq=False, md=None):
    """
    Energy scan with fixed delta_K steps.

    WARNING: please run qxscan_params.setup() before using this plan! It will
    use the parameters set in qxscan_params to determine the energy points.

    Parameters
    ----------
    edge_energy : float
        Absorption edge energy. The parameters in qxscan_params offset by this
        energy.
    time : float, optional
        If a number is passed, it will modify the counts over time. All
        detectors need to have a .preset_monitor signal.
    detectors : list, optional
        List of detectors to be used in the scan. If None, will use the
        detectors defined in `counters.detectors`.
    lockin : boolean, optional
        Flag to do a lock-in scan. Please run pr_setup.config() prior do a
        lock-in scan
    dichro : boolean, optional
        Flag to do a dichro scan. Please run pr_setup.config() prior do a
        dichro scan. Note that this will switch the x-ray polarization at every
        point using the +, -, -, + sequence, thus increasing the number of
        points by a factor of 4
    fixq : boolean, optional
        Flag for fixQ scans. If True, it will fix the diffractometer hkl
        position during the scan. Note that hkl is moved ~after~ the other
        motors!
    md : dictionary, optional
        Metadata to be added to the run start.

    See Also
    --------
    :func:`bluesky.plans.scan`
    :func:`lup`
    """

    if detectors is None:
        detectors = counters.detectors

    flag.dichro = dichro
    flag.fixq = fixq
    per_step = one_local_step if fixq or dichro else None
    if fixq:
        flag.hkl_pos = {
            fourc.h: fourc.h.get().setpoint,
            fourc.k: fourc.k.get().setpoint,
            fourc.l: fourc.l.get().setpoint,
        }

    # Get energy argument and extras
    energy_list = yield from rd(qxscan_params.energy_list)
    args = (energy, array(energy_list) + edge_energy)

    extras = yield from _collect_extras(energy in args, "fourc" in str(args))

    # Setup count time
    factor_list = yield from rd(qxscan_params.factor_list)

    # TODO: The md handling might go well in a decorator.
    # TODO: May need to add reference to stream.
    _md = {'hints': {'monitor': counters.monitor, 'detectors': []}}
    for item in detectors:
        _md['hints']['detectors'].extend(item.hints['fields'])

    if dichro:
        _md['hints']['scan_type'] = 'dichro'

    _md.update(md or {})

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

    @configure_counts_decorator(detectors, time)
    @stage_dichro_decorator(dichro, lockin)
    @extra_devices_decorator(extras)
    def _inner_qxscan():
        yield from list_scan(
            detectors + extras, *args, per_step=per_step, md=_md
            )

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
