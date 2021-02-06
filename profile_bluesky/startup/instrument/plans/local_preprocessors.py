"""Local decorators."""

from bluesky.utils import make_decorator
from bluesky.preprocessors import finalize_wrapper
from bluesky.plan_stubs import mv, sleep, rd
from ..devices import scalerd, pr_setup, mag6t
from ..utils import local_rd

from ..session_logs import logger
logger.info(__file__)


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
    def _stage():

        _heater_status = yield from local_rd(mag6t.field.switch_heater)
        if _heater_status != 'On':

            yield from mv(mag6t.field.ramp_button, 1)

            while True:
                supply = yield from local_rd(mag6t.field.supply_current)
                target = yield from local_rd(mag6t.field.current)
                if abs(supply-target) > 0.01:
                    yield from sleep(1)
                else:
                    break

            yield from mv(mag6t.field.switch_heater, 'On')
            yield from sleep(2)

            while True:
                _status = yield from local_rd(mag6t.field.magnet_status)

                if _status != 3:
                    yield from sleep(1)
                else:
                    break

            yield from mv(mag6t.field.ramp_button, 1)

    def _unstage():

        while True:
            voltage = yield from local_rd(mag6t.field.voltage)
            if abs(voltage) > 0.01:
                yield from sleep(1)
            else:
                break

        yield from mv(mag6t.field.switch_heater, 'Off')
        yield from sleep(2)

        while True:
            _status = yield from local_rd(mag6t.field.magnet_status)

            if _status not in [2, 3]:
                yield from sleep(1)
            else:
                break

        yield from mv(mag6t.field.zero_button, 1)

    def _inner_plan():
        yield from _stage()
        return (yield from plan)

    if magnet:
        return (yield from finalize_wrapper(_inner_plan(), _unstage()))
    else:
        return (yield from plan)


def configure_counts_wrapper(plan, detectors, count_time):
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
    original_times = {}
    original_monitor = []

    def setup():
        if count_time < 0:
            if detectors != [scalerd]:
                raise ValueError('count_time can be < 0 only if the scalerd '
                                 'is only detector used.')
            else:
                original_times[scalerd] = yield from scalerd.GetCountTimePlan()
                yield from mv(scalerd.preset_monitor, abs(count_time))

        elif count_time > 0:
            for det in detectors:
                original_times[det] = yield from rd(det.preset_monitor)

                if det == scalerd:
                    original_monitor.append(scalerd.monitor)
                    det.monitor = 'Time'

                yield from mv(det.preset_monitor, count_time)
        else:
            raise ValueError('count_time cannot be zero.')

    def reset():
        for det, time in original_times.items():
            if det == scalerd and len(original_monitor) == 1:
                det.monitor = original_monitor[0]

            yield from mv(det.preset_monitor, time)

    def _inner_plan():
        yield from setup()
        return (yield from plan)

    if count_time is None:
        return (yield from plan)
    else:
        return (yield from finalize_wrapper(_inner_plan(), reset()))


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


configure_counts_decorator = make_decorator(configure_counts_wrapper)
stage_dichro_decorator = make_decorator(stage_dichro_wrapper)
stage_ami_decorator = make_decorator(stage_ami_wrapper)
