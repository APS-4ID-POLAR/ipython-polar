"""
Kepko power supply
"""

__all__ = ['kepko']

from ophyd import Component, FormattedComponent, Device, PVPositioner, Kind
from ophyd import EpicsSignal, EpicsSignalRO
from ..framework import sd
from ..utils import DoneSignal

from ..session_logs import logger
logger.info(__file__)


class LocalPositioner(PVPositioner):

    readback = FormattedComponent(
        EpicsSignalRO, '{prefix}d{_type}', kind='normal',
        labels=('kepko', 'magnet')
        )

    setpoint = FormattedComponent(
        EpicsSignal, "{prefix}{_type}", write_pv="{prefix}set{_type}",
        kind='normal', labels=('kepko', 'magnet')
        )

    done = Component(DoneSignal, value=0, kind='omitted')
    done_value = 1

    def __init__(self, *args, progtype, **kwargs):
        self._type = progtype
        super().__init__(*args, **kwargs)
        # TODO: This seems good, but may need to be tested.
        self.tolerance = 0.02


class KepkoController(Device):

    voltage = Component(LocalPositioner, '', progtype='V')
    current = Component(LocalPositioner, '', progtype='C')

    output = Component(
        EpicsSignal, 'OnOff', write_pv='OUTP', kind='config', string=True,
        labels=('kepko', 'magnet')
        )

    mode = Component(
        EpicsSignal, 'setMode', kind='config', string=True,
        labels=('kepko', 'magnet')
        )

    remote = Component(
        EpicsSignal, 'setRemote', kind='config', string=True,
        labels=('kepko', 'magnet')
        )

    enable = Component(
        EpicsSignal, 'Enable.val', kind='config', string=True,
        labels=('kepko', 'magnet')
        )

    @mode.sub_value
    def mode_change(self, value=None, **kwargs):
        if value == 'Current':
            self.current.readback.kind = Kind.hinted
            self.voltage.readback.kind = Kind.normal

        if value == 'Voltage':
            self.current.readback.kind = Kind.normal
            self.voltage.readback.kind = Kind.hinted


kepko = KepkoController('4idd:Kepko1:', name='kepko')
sd.baseline.append(kepko)
