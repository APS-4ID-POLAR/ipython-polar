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
        EpicsSignalRO, '{prefix}prog{_type}', kind='normal',
        labels=('kepko', 'magnet')
        )

    setpoint = FormattedComponent(
        EpicsSignal, "{prefix}prog{_type}SP.A", kind='normal',
        labels=('kepko', 'magnet')
        )

    done = Component(DoneSignal, value=0, kind='omitted')
    done_value = 1

    def __init__(self, *args, progtype, **kwargs):
        self._type = progtype
        super().__init__(*args, **kwargs)
        self.tolerance = 0.01


class KepkoController(Device):

    voltage = Component(LocalPositioner, '', progtype='Volt')
    current = Component(LocalPositioner, '', progtype='Curr')

    voltage_rbk = Component(
        EpicsSignalRO, 'Volt', kind='normal', labels=('kepko', 'magnet')
        )

    current_rbk = Component(
        EpicsSignalRO, 'Curr', kind='normal', labels=('kepko', 'magnet')
        )

    output = Component(
        EpicsSignal, 'OnOff', write_pv='OUTP', kind='config', string=True,
        labels=('kepko', 'magnet')
        )

    mode = Component(
        EpicsSignal, 'VCMode', kind='config', string=True,
        labels=('kepko', 'magnet')
        )

    @mode.sub_value
    def mode_change(self, value=None, **kwargs):
        if value == 'Current Mode':
            self.current_rbk.kind = Kind.hinted
            self.voltage_rbk.kind = Kind.normal

        if value == 'Voltage Mode':
            self.current_rbk.kind = Kind.normal
            self.voltage_rbk.kind = Kind.hinted


kepko = KepkoController('4idd:Kepko1:', name='kepko')
sd.baseline.append(kepko)
