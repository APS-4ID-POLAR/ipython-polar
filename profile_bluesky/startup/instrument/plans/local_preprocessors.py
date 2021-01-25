"""Local decorators."""

from bluesky.utils import make_decorator, single_gen
from bluesky.preprocessors import pchain, plan_mutator, finalize_wrapper
from bluesky.plan_stubs import mv, sleep, abs_set
from ophyd import Signal
from ophyd.status import SubscriptionStatus
from ..devices import scalerd, pr_setup, mag6t
from ..utils import local_rd

from ..session_logs import logger
logger.info(__file__)


class SetSignal(Signal):

    """ Signal that only matters for the set function """

    def set(self, device, function):
        return SubscriptionStatus(device, function)


def _difference_check(target, tolerance):
    """
    Returns a callback function that checks the distance from target.

    Parameters
    ----------
    target : float
        Final position.
    tolerance : float
        Maximum accepted tolerance.

    Returns
    -------
    check_pos : function
        Function that can be used as a callback of SubscriptionStatus.
    """
    def check_pos(value=None, **kwargs):
        return abs(value-target) <= tolerance

    return check_pos


def _status_check(target):
    """
    Returns a callback function that checks the positioner status.

    Parameters
    ----------
    target : list
        List of acceptable status.

    Returns
    -------
    check_pos : function
        Function that can be used as a callback of SubscriptionStatus.
    """
    def check_pos(value=None, **kwargs):
        return value in target

    return check_pos


def stage_ami_wrapper(plan, magnet):
    """
    Stage the AMI magnet.

    Turns on/off the persistence switch heater before/after the magnetic field
    scan or move.

    Parameters
    ----------
    plan : iterable or iterator
        a generator, list, or similar containing `Msg` objects
    magnet : boolean
        Flag that triggers the stage/unstage.

    Yields
    ------
    msg : Msg
        messages from plan, with 'subscribe' and 'unsubscribe' messages
        inserted and appended
    """

    # This just needs to be set once here.
    signal = SetSignal(name='tmp')

    def _stage():

        _heater_status = yield from local_rd(mag6t.field.switch_heater)

        if _heater_status != 'On':
            # Click current ramp button
            yield from mv(mag6t.field.ramp_button, 1)

            # Wait for the supply current to match the magnet.
            target = yield from local_rd(mag6t.field.current)
            function = _difference_check(target, tolerance=0.01)
            yield abs_set(signal, mag6t.field.supply_current, function,
                          wait=True)

            # Turn on persistance switch heater.
            yield from mv(mag6t.field.switch_heater, 'On')
            yield from sleep(2)

            # Wait for the heater to be on.
            function = _status_check(target=[3])
            yield from abs_set(signal, mag6t.field.magnet_status, function,
                               wait=True)

            # Click current ramp button
            yield from mv(mag6t.field.ramp_button, 1)

    def _unstage():

        # Wait for the voltage to be zero.
        function = _difference_check(target=0.0, tolerance=0.01)
        yield abs_set(signal, mag6t.field.voltage, function,
                      wait=True)

        # Turn off persistance switch heater
        yield from mv(mag6t.field.switch_heater, 'Off')
        yield from sleep(2)

        # Wait for the heater to be off.
        function = _status_check(target=[2, 3])
        yield from abs_set(signal, mag6t.field.magnet_status, function,
                           wait=True)

    def _inner_plan():
        yield from _stage()
        return (yield from plan)

    if magnet:
        return (yield from finalize_wrapper(_inner_plan(), _unstage()))
    else:
        return (yield from plan)


def configure_monitor_wrapper(plan, monitor):
    """
    Set all devices with a `preset_monitor` to the same value.

    The original setting is stashed and restored at the end.

    Parameters
    ----------
    plan : iterable or iterator
        a generator, list, or similar containing `Msg` objects
    monitor : float or None
        If None, the plan passes through unchanged.

    Yields
    ------
    msg : Msg
        messages from plan, with 'set' messages inserted
    """
    devices_seen = set()
    original_times = {}

    def insert_set(msg):
        obj = msg.obj
        if obj is not None and obj not in devices_seen:
            devices_seen.add(obj)
            if hasattr(obj, 'preset_monitor'):
                original_times[obj] = obj.preset_monitor.get()
                return pchain(mv(obj.preset_monitor, monitor),
                              single_gen(msg)), None
        return None, None

    def reset():
        for obj, time in original_times.items():
            yield from mv(obj.preset_monitor, time)

    if monitor is None:
        return (yield from plan)
    else:
        return (yield from finalize_wrapper(plan_mutator(plan, insert_set),
                                            reset()))


def stage_dichro_wrapper(plan, dichro, lockin):
    """
    Stage dichoic scans.

    Parameters
    ----------
    plan : iterable or iterator
        a generator, list, or similar containing `Msg` objects
    dichro : boolean
        Flag that triggers the stage/unstage process of dichro scans.
    lockin : boolean
        Flag that triggers the stage/unstage process of lockin scans.

    Yields
    ------
    msg : Msg
        messages from plan, with 'subscribe' and 'unsubscribe' messages
        inserted and appended
    """
    _current_scaler_plot = []

    def _stage():

        if dichro and lockin:
            raise ValueError('Cannot have both dichro and lockin = True.')

        if lockin:
            for chan in scalerd.channels.component_names:
                scaler_channel = getattr(scalerd.channels, chan)
                if scaler_channel.kind.value >= 5:
                    _current_scaler_plot.append(scaler_channel.s.name)

            scalerd.select_plot_channels(['Lock DC', 'Lock AC'])

            if pr_setup.positioner is None:
                raise ValueError('Phase retarder was not selected.')

            if 'th' in pr_setup.positioner.name:
                raise TypeError('Theta motor cannot be used in lock in! \
                                Please run pr_setup.config() and choose \
                                pzt.')

            yield from mv(pr_setup.positioner.parent.selectAC, 1)

        if dichro:
            # move PZT to center.
            if 'pzt' in pr_setup.positioner.name:
                yield from mv(pr_setup.positioner,
                              pr_setup.positioner.parent.center.get())

    def _unstage():
        if lockin:
            scalerd.select_plot_channels(_current_scaler_plot)
            yield from mv(pr_setup.positioner.parent.selectDC, 1)

    def _inner_plan():
        yield from _stage()
        return (yield from plan)

    return (yield from finalize_wrapper(_inner_plan(), _unstage()))


configure_monitor_decorator = make_decorator(configure_monitor_wrapper)
stage_dichro_decorator = make_decorator(stage_dichro_wrapper)
stage_ami_decorator = make_decorator(stage_ami_wrapper)
