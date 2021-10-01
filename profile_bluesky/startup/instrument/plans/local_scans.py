"""
Modifed bluesky scans
"""

__all__ = ['lup', 'ascan', 'mv', 'mvr', 'qxscan', 'count']

from bluesky.plans import rel_scan, scan, list_scan, count as bp_count
from bluesky.plan_stubs import trigger_and_read, move_per_step
from bluesky.plan_stubs import mv as bps_mv, rd
from bluesky.preprocessors import relative_set_decorator
from ..devices import (scalerd, pr_setup, mag6t, undulator, fourc,
                       pr1, pr2, pr3, energy, qxscan_params)
from .local_preprocessors import (configure_counts_decorator,
                                  stage_dichro_decorator,
                                  stage_ami_decorator,
                                  extra_devices_decorator)
from ..utils import counters
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
    dichro_steps = None


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

    devices_to_read += [pr_setup.positioner]
    for pos in flag.dichro_steps:
        yield from mv(pr_setup.positioner, pos)
        yield from take_reading(devices_to_read)


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


def one_local_shot(detectors, take_reading=trigger_and_read):
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

    devices_to_read = list(detectors)
    if flag.dichro:
        yield from dichro_steps(devices_to_read, take_reading)
    else:
        yield from take_reading(devices_to_read)


def count(detectors=None, num=1, time=None, lockin=False, dichro=False,
          md=None):
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
    md : dictionary, optional
        Metadata to be added to the run start.

    See Also
    --------
    :func:`bluesky.plans.scan`
    :func:`lup`
    """
    fixq = False
    if detectors is None:
        detectors = counters.detectors

    flag.dichro = dichro
    if dichro:
        _offset = pr_setup.offset.get()
        _center = pr_setup.positioner.parent.center.get()
        _steps = pr_setup.dichro_steps
        flag.dichro_steps = [_center + step*_offset for step in _steps]

    flag.fixq = fixq
    per_shot = one_local_shot if fixq or dichro else None

    extras = yield from _collect_extras(False, False)

    # TODO: The md handling might go well in a decorator.
    # TODO: May need to add reference to stream.
    _md = {'hints': {'monitor': counters.monitor, 'detectors': []}}
    for item in detectors:
        _md['hints']['detectors'].extend(item.hints['fields'])

    if dichro:
        _md['hints']['scan_type'] = 'dichro'

    _md.update(md or {})

    _md.update(md or {})

    @configure_counts_decorator(detectors, time)
    @stage_ami_decorator(False)
    @stage_dichro_decorator(dichro, lockin)
    @extra_devices_decorator(extras)
    def _inner_ascan():
        yield from bp_count(
            detectors + extras,
            num = num,
            per_shot=per_shot,
            md=_md
            )

    return (yield from _inner_ascan())


def lup(*args, time=None, detectors=None, lockin=False, dichro=False,
        fixq=False, md=None):
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
    md : dictionary, optional
        Metadata to be added to the run start.

    See Also
    --------
    :func:`bluesky.plans.rel_scan`
    :func:`ascan`
    """
    if detectors is None:
        detectors = counters.detectors

    flag.dichro = dichro
    if dichro:
        _offset = pr_setup.offset.get()
        _center = pr_setup.positioner.parent.center.get()
        _steps = pr_setup.dichro_steps
        flag.dichro_steps = [_center + step*_offset for step in _steps]
        
    flag.fixq = fixq
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

    extras = yield from _collect_extras(energy in args, "fourc" in str(args))

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
    def _inner_lup():
        yield from rel_scan(
            detectors + extras,
            *args,
            per_step=per_step,
            md=_md,
            )

    return (yield from _inner_lup())


def ascan(*args, time=None, detectors=None, lockin=False, dichro=False,
          fixq=False, md=None):
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
    if dichro:
        _offset = pr_setup.offset.get()
        _center = pr_setup.positioner.parent.center.get()
        _steps = pr_setup.dichro_steps
        flag.dichro_steps = [_center + step*_offset for step in _steps]
        
    flag.fixq = fixq
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

    extras = yield from _collect_extras(energy in args, "fourc" in str(args))

    # TODO: The md handling might go well in a decorator.
    # TODO: May need to add reference to stream.
    _md = {'hints': {'monitor': counters.monitor, 'detectors': []}}
    for item in detectors:
        _md['hints']['detectors'].extend(item.hints['fields'])

    if dichro:
        _md['hints']['scan_type'] = 'dichro'

    _md.update(md or {})

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
    if dichro:
        _offset = pr_setup.offset.get()
        _center = pr_setup.positioner.parent.center.get()
        _steps = pr_setup.dichro_steps
        flag.dichro_steps = [_center + step*_offset for step in _steps]
        
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
