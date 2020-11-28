"""
Magnets
"""

__all__ = [
    'mag6t',
    ]

from ..session_logs import logger
logger.info(__file__)

from ophyd import Component, Device, EpicsMotor, PVPositioner
from ophyd import EpicsSignal, EpicsSignalRO
from ophyd import Kind
from bluesky.plan_stubs import mv, sleep
from ..utils import local_rd

class AMIZones(Device):
    high_field = Component(EpicsSignal, "Field.VAL", write_pv="FieldSet")
    ramp_rate = Component(EpicsSignal, "Rate", write_pv="RateSet")

class AMIController(PVPositioner):

    # position
    readback = Component(EpicsSignalRO, "Field", auto_monitor=True,
                         kind=Kind.hinted, labels=('ami_controller', 'magnet'))

    setpoint = Component(EpicsSignal, "PField", write_pv="PField:Wrt.A",
                         auto_monitor=True, kind=Kind.hinted,
                         labels=('ami_controller', 'magnet'))

    current = Component(EpicsSignalRO, "Current", auto_monitor=True,
                        kind=Kind.normal, labels=('ami_controller', 'magnet'))

    voltage = Component(EpicsSignalRO, "Voltage", auto_monitor=True,
                        kind=Kind.normal, labels=('ami_controller', 'magnet'))

    supply_current = Component(EpicsSignalRO, "CurrentSP", auto_monitor=True,
                               kind=Kind.normal,
                               labels=('ami_controller', 'magnet'))
    # status
    magnet_status = Component(EpicsSignalRO, "StateInt.A", auto_monitor=True,
                              kind=Kind.config,
                              labels=('ami_controller', 'magnet'))

    done = magnet_status
    done_value = 2

    # configuration
    units = Component(EpicsSignalRO, "FieldUnits.SVAL", kind=Kind.config,
                      labels=('ami_controller', 'magnet'))

    field_limit = Component(EpicsSignalRO, "Field:Limit", kind=Kind.config,
                            labels=('ami_controller', 'magnet'))
    current_limit = Component(EpicsSignalRO, "Curr:Limit.VAL",
                              kind=Kind.config,
                              labels=('ami_controller', 'magnet'))
    voltage_limit = Component(EpicsSignalRO, "Volt:Limit.VAL",
                              kind=Kind.config,
                              labels=('ami_controller', 'magnet'))

    switch_heater = Component(EpicsSignal, "PSOnOff", string=True,
                              kind=Kind.config,
                              labels=('ami_controller', 'magnet'))

    zone_1 = Component(AMIZones, "RampR1:", kind=Kind.config,
                       labels=('ami_controller', 'magnet'))
    zone_2 = Component(AMIZones, "RampR2:", kind=Kind.config,
                       labels=('ami_controller', 'magnet'))
    zone_3 = Component(AMIZones, "RampR3:", kind=Kind.config,
                       labels=('ami_controller', 'magnet'))
    ramp_units = Component(EpicsSignalRO, "RampR:Units.SVAL", kind=Kind.config,
                           labels=('ami_controller', 'magnet'))

    # Buttons
    ramp_button = Component(EpicsSignal, "Ramp.PROC", kind=Kind.omitted,
                            put_complete=True)
    pause_button = Component(EpicsSignal, "Pause.PROC", kind=Kind.omitted,
                             put_complete=True)
    zero_button = Component(EpicsSignal, "Zero.PROC", kind=Kind.omitted,
                            put_complete=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._settle_time = 0

    @property
    def settle_time(self):
        return self._settle_time

    @settle_time.setter
    def settle_time(self, value):
        if value < 0:
            raise ValueError('Settle value needs to be >= 0.')
        else:
            self._settle_time = value

    @property
    def egu(self):
        return self.units.get(as_string=True)

    def stop(self, *, success=False):
        if success is False:
            self.pause_button.put(1)
        super().stop(success=success)

    def pause(self):
        self.pause_button.put(1)

    @done.sub_value
    def _move_changed(self, **kwargs):
        super()._move_changed(**kwargs)



# Magnet and sample motors
class Magnet6T(Device):

    # Motors #
    tabth = Component(EpicsMotor, 'm53', labels=('motor', 'magnet'))
    tabx = Component(EpicsMotor, 'm49', labels=('motor', 'magnet'))
    taby = Component(EpicsMotor, 'm50', labels=('motor', 'magnet'))

    tabth2 = Component(EpicsMotor, 'm56', labels=('motor', 'magnet'))
    tabz2 = Component(EpicsMotor, 'm51', labels=('motor', 'magnet'))
    tabx2 = Component(EpicsMotor, 'm52', labels=('motor', 'magnet'))

    sampy = Component(EpicsMotor, 'm63', labels=('motor', 'magnet'))
    sampth = Component(EpicsMotor, 'm58', labels=('motor', 'magnet'))

    # Magnetic field controller
    field = Component(AMIController, '4idd:AMI430:', add_prefix='')

    def _stage_magnet(self):

        if self.field.switch_heater.get() != 'On':

            yield from mv(self.field.ramp_button, 1)

            while True:
                supply = yield from local_rd(self.field.supply_current)
                target = yield from local_rd(self.field.current)
                if abs(supply-target) > 0.01:
                    yield from sleep(1)
                else:
                    break

            yield from mv(self.field.switch_heater, 'On')

            while True:
                _status = yield from local_rd(self.field.magnet_status)

                if _status != 3:
                    yield from sleep(1)
                else:
                    break

            yield from mv(self.field.ramp_button, 1)

    def _unstage_magnet(self):

        while True:
            voltage = yield from local_rd(self.field.voltage)
            if abs(voltage) > 0.01:
                yield from sleep(1)
            else:
                break

        yield from mv(self.field.switch_heater, 'Off')

        while True:
            _status = yield from local_rd(self.field.magnet_status)

            if _status not in [2, 3]:
                yield from sleep(1)
            else:
                break

        yield from mv(self.field.zero_button, 1)

    def move_field(self, target):

        yield from self._stage_magnet()
        yield from mv(self.field, target)
        yield from self._unstage_magnet()


mag6t = Magnet6T('4iddx:', name='magnet_6T')
