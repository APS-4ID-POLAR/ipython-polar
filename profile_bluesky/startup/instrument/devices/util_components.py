
"""
Utilities
"""

from ophyd import Signal, EpicsSignal, FormattedComponent
from ..session_logs import logger
logger.info(__file__)


class DoneSignal(Signal):
    """ Signal that tracks if two values become the same. """
    def __init__(self, *args, readback_attr='readback',
                 setpoint_attr='setpoint', tolerance_attr='tolerance',
                 **kwargs):
        super().__init__(*args, **kwargs)
        self._readback_attr = readback_attr
        self._setpoint_attr = setpoint_attr
        self._tolerance_attr = tolerance_attr

    def get(self, **kwargs):
        readback = getattr(self.parent, self._readback_attr)
        setpoint = getattr(self.parent, self._setpoint_attr)
        tolerance = getattr(self.parent, self._tolerance_attr)
        if abs(readback.get()-setpoint.get()) <= tolerance:
            self.put(1)
        else:
            self.put(0)
        return self._readback


class TrackingSignal(Signal):
    """ Signal that forces value to be a boolean. """
    def check_value(self, value):
        """
        Check if the value is a boolean.

        Raises
        ------
        ValueError
        """
        if not isinstance(value, bool):
            raise ValueError('tracking is boolean, it can only be True or \
                False.')


class EpicsSignalwithStop(EpicsSignal):
    stop_signal = FormattedComponent("{_stop_pv}", kind="omitted")
    stop_value = 1

    def __init__(self, *args, stop_pv=None, stop_value=1, **kwargs):
        self._stop_pv = stop_pv
        super().__init__(*args, **kwargs)
        self.stop_value = stop_value

    def stop(self, *, success=False):
        self.stop_signal.put(self.stop_value, wait=False)
