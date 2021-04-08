"""
Ruby spectrometer motors and controls.
"""

__all__ = ['ruby']

from ophyd import (Component, Device, EpicsMotor, EpicsSignal, PVPositioner,
                   EpicsSignalRO, FormattedComponent)
from ..framework import sd
from .util_components import DoneSignal
from ..session_logs import logger
logger.info(__file__)


class DAC(PVPositioner):
    """ Setup DAC as a PVPositioner """

    setpoint = Component(EpicsSignal, '.VAL', put_complete=True, kind='normal')
    readback = Component(EpicsSignalRO, '_rbv.VAL', auto_monitor=True,
                         kind='hinted')

    done = Component(DoneSignal, value=1)
    done_value = 1

    low_limit = Component(EpicsSignal, '.DRVL', kind='config')
    high_limit = Component(EpicsSignal, '.DRVH', kind='config')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._tolerance = 0.001

        self.readback.subscribe(self.done.get)
        self.setpoint.subscribe(self.done.get)

    @property
    def tolerance(self):
        return self._tolerance

    @tolerance.setter
    def tolerance(self, value):
        if value < 0:
            raise ValueError('Tolerance needs to be >= 0.')
        else:
            self._tolerance = value
            _ = self.done.get()

    @property
    def limits(self):
        return (self.low_limit.get(), self.high_limit.get())


class RubyDevice(Device):
    """ Ruby system """

    focus = Component(EpicsMotor, 'm37', labels=('motor', 'ruby'))
    y = Component(EpicsMotor, 'm38', labels=('motor', 'ruby'))
    z = Component(EpicsMotor, 'm39', labels=('motor', 'ruby'))
    zoom = Component(EpicsMotor, 'm40', labels=('motor', 'ruby'))

    led = FormattedComponent(DAC, '4idd:DAC1_1', labels=('ruby',))
    laser = FormattedComponent(DAC, '4idd:DAC1_2', labels=('ruby',))


ruby = RubyDevice('4iddx:', name='ruby')
sd.baseline.append(ruby)
