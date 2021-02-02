
__all__ = ['DoneSignal']

from ophyd import Signal
from ..session_logs import logger
logger.info(__file__)


class DoneSignal(Signal):
    def __init__(self, *args, readback=None, setpoint=None, tolerance=None,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self._readback_signal = readback if readback else self.parent.readback
        self._setpoint_signal = setpoint if setpoint else self.parent.setpoint
        self._tolerance = tolerance if tolerance else self.parent.tolerance

    def get(self, **kwargs):
        if abs(self._readback_signal.get()-self._setpoint_signal.get()) <= \
                self._tolerance:
            self.put(1)
        else:
            self.put(0)
        return self._readback
