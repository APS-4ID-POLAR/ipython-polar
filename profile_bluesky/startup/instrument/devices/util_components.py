
"""
Utilities
"""

from ophyd import (
    Component, FormattedComponent, Signal, EpicsSignal, EpicsSignalRO,
    PVPositioner
)
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
            raise ValueError('tracking is boolean, it can only be True or '
                             'False.')


# TODO: Can we have readback_pv, setpoint_pv as *args? It looks
# like it doesn't work because it breaks the "name" while creating a
# component?
class PVPositionerSoftDone(PVPositioner):

    # positioner
    readback = FormattedComponent(EpicsSignalRO, "{prefix}{_readback_pv}",
                                  kind="hinted", auto_monitor=True)
    setpoint = FormattedComponent(EpicsSignal, "{prefix}{_setpoint_pv}",
                                  kind="normal", put_complete=True)
    done = Component(Signal, value=True)
    done_value = True

    tolerance = Component(Signal, value=1)  # Value always updated during init.
    report_dmov_changes = Component(Signal, value=False, kind="omitted")

    def cb_readback(self, *args, **kwargs):
        """
        Called when readback changes (EPICS CA monitor event).
        """
        diff = self.readback.get() - self.setpoint.get()
        dmov = abs(diff) <= self.tolerance.get()
        if self.report_dmov_changes.get() and dmov != self.done.get():
            logger.debug(f"{self.name} reached: {dmov}")
        self.done.put(dmov)

    def cb_setpoint(self, *args, **kwargs):
        """
        Called when setpoint changes (EPICS CA monitor event).
        When the setpoint is changed, force done=False.  For any move,
        done must go != done_value, then back to done_value (True).
        Without this response, a small move (within tolerance) will not return.
        Next update of readback will compute self.done.
        """
        self.done.put(not self.done_value)

    def __init__(self, prefix, *, limits=None, readback_pv="", setpoint_pv="",
                 name=None, read_attrs=None, configuration_attrs=None,
                 parent=None, egu="", tolerance=None, **kwargs):

        self._setpoint_pv = setpoint_pv
        self._readback_pv = readback_pv

        super().__init__(prefix=prefix, limits=limits, name=name,
                         read_attrs=read_attrs,
                         configuration_attrs=configuration_attrs,
                         parent=parent, egu=egu, **kwargs)

        self.readback.subscribe(self.cb_readback)
        self.setpoint.subscribe(self.cb_setpoint)

        if tolerance is None:
            self.readback.wait_for_connection()
            self.setpoint.wait_for_connection()

            rb = self.readback.precision
            sp = self.setpoint.precision

            tolerance = rb if rb >= sp else sp

        self.tolerance.put(tolerance)

    def _setup_move(self, position):
        '''Move and do not wait until motion is complete (asynchronous)'''
        self.log.debug('%s.setpoint = %s', self.name, position)
        self.setpoint.put(position, wait=False)
        if self.actuate is not None:
            self.log.debug('%s.actuate = %s', self.name, self.actuate_value)
            self.actuate.put(self.actuate_value, wait=False)
