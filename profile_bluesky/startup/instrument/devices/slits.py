"""
Slits
"""
__all__ = ['wbslt', 'enslt', 'inslt', 'grdslt', 'detslt', 'magslt']

from ophyd import (Device, EpicsMotor, EpicsSignal, EpicsSignalRO, Signal,
                   FormattedComponent, PVPositioner, Component)
from ..framework import sd
from ..session_logs import logger
logger.info(__file__)


class PVPositionerSoftDone(PVPositioner):

    # positioner
    readback = FormattedComponent(EpicsSignalRO, "{prefix}{_readback_pv}",
                                  kind="hinted", auto_monitor=True)
    setpoint = FormattedComponent(EpicsSignal, "{prefix}{_setpoint_pv}",
                                  kind="normal")
    done = Component(Signal, value=True)
    done_value = True

    tolerance = Component(Signal, value=0.001)
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
                 parent=None, egu="", **kwargs):

        self._setpoint_pv = setpoint_pv
        self._readback_pv = readback_pv

        super().__init__(prefix=prefix, limits=limits, name=name,
                         read_attrs=read_attrs,
                         configuration_attrs=configuration_attrs,
                         parent=parent, egu=egu, **kwargs)

        self.readback.subscribe(self.cb_readback)
        self.setpoint.subscribe(self.cb_setpoint)


class SlitDevice(Device):

    # Setting motors
    top = FormattedComponent(EpicsMotor, '{prefix}{_motorsDict[top]}',
                             labels=('motors', 'slits'))

    bot = FormattedComponent(EpicsMotor, '{prefix}{_motorsDict[bot]}',
                             labels=('motors', 'slits'))

    out = FormattedComponent(EpicsMotor, '{prefix}{_motorsDict[out]}',
                             labels=('motors', 'slits'))

    inb = FormattedComponent(EpicsMotor, '{prefix}{_motorsDict[inb]}',
                             labels=('motors', 'slits'))

    # Setting pseudo positioners
    vcen = FormattedComponent(PVPositionerSoftDone, '{prefix}{_slit_prefix}',
                              readback_pv='Vt2.D', setpoint_pv='Vcenter.VAL',
                              labels=('slits',))

    vsize = FormattedComponent(PVPositionerSoftDone, '{prefix}{_slit_prefix}',
                               readback_pv='Vt2.C', setpoint_pv='Vsize.VAL',
                               labels=('slits',))

    hcen = FormattedComponent(PVPositionerSoftDone, '{prefix}{_slit_prefix}',
                              readback_pv='Ht2.D', setpoint_pv='Hcenter.VAL',
                              labels=('slits',))

    hsize = FormattedComponent(PVPositionerSoftDone, '{prefix}{_slit_prefix}',
                               readback_pv='Ht2.C', setpoint_pv='Hsize.VAL',
                               labels=('slits',))

    def __init__(self, PV, name, motorsDict, slitnum, **kwargs):

        self._motorsDict = motorsDict
        self._slit_prefix = f'Slit{slitnum}'

        super().__init__(prefix=PV, name=name, **kwargs)


# White beam slit
wbslt = SlitDevice('4idb:', 'wbslt',
                   {'top': 'm25', 'bot': 'm26', 'out': 'm27', 'inb': 'm28'},
                   1)
sd.baseline.append(wbslt)

# Entrance slit
enslt = SlitDevice('4iddx:', 'enslt',
                   {'top': 'm1', 'bot': 'm2', 'out': 'm3', 'inb': 'm4'},
                   1)
sd.baseline.append(enslt)

# 8C incident slit
inslt = SlitDevice('4iddx:', 'inslt',
                   {'top': 'm5', 'bot': 'm6', 'out': 'm7', 'inb': 'm11'},
                   2)
sd.baseline.append(inslt)

# 2th guard slit
grdslt = SlitDevice('4iddx:', 'grdslt',
                    {'top': 'm21', 'bot': 'm22', 'out': 'm23', 'inb': 'm24'},
                    3)
sd.baseline.append(grdslt)

# 2th detector slit
detslt = SlitDevice('4iddx:', 'detslt',
                    {'top': 'm25', 'bot': 'm26', 'out': 'm27', 'inb': 'm28'},
                    4)
sd.baseline.append(detslt)

# Magnet incident slit
magslt = SlitDevice('4iddx:', 'magslt',
                    {'top': 'm29', 'bot': 'm30', 'out': 'm31', 'inb': 'm32'},
                    5)
sd.baseline.append(magslt)
