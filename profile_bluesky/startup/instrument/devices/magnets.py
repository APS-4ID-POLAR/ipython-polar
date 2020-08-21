"""
Magnet motors
"""

__all__ = [
    'mag6t',
    ]

from ..session_logs import logger
logger.info(__file__)

from ophyd import Component, Device, EpicsMotor, PVPositioner
from ophyd import EpicsSignal, EpicsSignalRO
from ophyd import Kind

class AMIZones(Device):
    high_field = Component(EpicsSignal,"Field.VAL",write_pv="FieldSet")
    ramp_rate = Component(EpicsSignal,"Rate",write_pv="RateSet")

class AMIController(PVPositioner):

    # position
    readback = Component(EpicsSignalRO, "Field",auto_monitor=True,
                         kind=Kind.hinted)

    setpoint = Component(EpicsSignal, "PField",
                         write_pv="PField:Wrt.A",auto_monitor=True,
                         kind=Kind.hinted)

    current = Component(EpicsSignalRO, "Current",auto_monitor=True,
                        kind=Kind.omitted)

    voltage = Component(EpicsSignalRO, "Voltage",auto_monitor=True,
                        kind=Kind.omitted)

    supply_current = Component(EpicsSignalRO, "CurrentSP",
                               auto_monitor=True,kind=Kind.omitted)
    #status
    done = Component(EpicsSignalRO, "StateInt.A", auto_monitor=True,
                     kind=Kind.omitted)
    done_value = 1
    # TODO: Need to check what are the status available!!

    # configuration
    units = Component(EpicsSignalRO, "FieldUnits.SVAL", kind=Kind.config)

    field_limit = Component(EpicsSignalRO,"Field:Limit",kind=Kind.config)
    current_limit = Component(EpicsSignalRO, "Curr:Limit.VAL",kind=Kind.config)
    voltage_limit = Component(EpicsSignalRO, "Volt:Limit.VAL",kind=Kind.config)

    switch_heater = Component(EpicsSignal, "PSOnOff",kind=Kind.config)

    zone_1 = Component(AMIZones,"RampR1:",kind=Kind.config)
    zone_2 = Component(AMIZones,"RampR2:",kind=Kind.config)
    zone_3 = Component(AMIZones,"RampR3:",kind=Kind.config)
    ramp_units = Component(EpicsSignalRO,"RampR:Units.SVAL",kind=Kind.config)

    # Buttons
    ramp_button = Component(EpicsSignal,"Ramp.PROC",kind=Kind.omitted)
    pause_button = Component(EpicsSignal,"Pause.PROC",kind=Kind.omitted)
    zero_button = Component(EpicsSignal,"Zero.PROC",kind=Kind.omitted)

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self._settle_time = 0

    @property
    def settle_time(self):
        return self._settle_time

    @settle_time.setter
    def settle_time(self,value):
        if value < 0:
            raise ValueError('Settle value needs to be >= 0.')
        else:
            self._settle_time = value

    @property
    def egu(self):
        return self.units.get(as_string=True)

    def stop(self,*,success=False):
        if success is False:
            self.pause_button.put(1)
        super().stop(success=success)

    def pause(self):
        self.pause_button.put(1)

    @done.sub_value
    def _move_changed(self,**kwargs):
        super()._move_changed(**kwargs)

# Magnet and sample motors #
class Magnet6T(Device):

    # Motors #
    tabth = Component(EpicsMotor, 'm53', labels=('motor'))  # 4T Mag Th
    tabx = Component(EpicsMotor, 'm49', labels=('motor'))  # 4T MagTab X
    taby = Component(EpicsMotor, 'm50', labels=('motor'))    # 4T MagTab Y

    tabth2 = Component(EpicsMotor,'m56', labels=('motor'))  # AMIMagnetPhi
    tabz2 = Component(EpicsMotor,'m51', labels=('motor'))  # AMIMagnetZ
    tabx2 = Component(EpicsMotor,'m52', labels=('motor'))  # AMIMagenetX

    sampy = Component(EpicsMotor,'m63', labels=('motor'))  # CIATRA
    sampth = Component(EpicsMotor,'m58', labels=('motor'))  # CIA ROT

    # Temperatures
    # TODO: Do we want these here?
    Tvaporizer = None
    Tsample = None

    # Magnetic field controller
    field = Component(AMIController,'4idd:AMI430:',add_prefix='')


mag6t = Magnet6T('4iddx:',name='6T magnet')



# TODO: Is it ok to add the lakeshores here?
# TODO: should we add the magnet field controls here?
