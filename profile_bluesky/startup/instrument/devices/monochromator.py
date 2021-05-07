"""
Monochromator motors
"""

__all__ = ['mono']

from apstools.devices import KohzuSeqCtl_Monochromator
from ophyd import (
    Component, Device, FormattedComponent, EpicsMotor, EpicsSignal,
    EpicsSignalRO
)
from .util_components import PVPositionerSoftDone
from ..framework import sd
from ..session_logs import logger
logger.info(__file__)


class MonoFeedback(Device):
    """ Mono feedback reading """

    readback = Component(EpicsSignalRO, 'mono_pid2.CVAL', kind='config',
                         labels=('mono',))
    setpoint = Component(EpicsSignal, 'mono_pid2.VAL', kind='config',
                         put_complete=True, labels=('mono',))
    onoff = Component(EpicsSignal, 'mono_pid2.FBON', kind='config',
                      labels=('mono',), put_complete=True)


class KohzuPositioner(PVPositionerSoftDone):
    stop_signal = FormattedComponent(EpicsSignal, "{_theta_pv}.STOP",
                                     kind="omitted")
    stop_value = 1

    def __init__(self, prefix, *, limits=None, readback_pv="", setpoint_pv="",
                 name=None, read_attrs=None, configuration_attrs=None,
                 parent=None, egu="", **kwargs):

        # TODO: Ugly... but works.
        _theta_pv_signal = EpicsSignalRO(f"{prefix}KohzuThetaPvSI", name="tmp")
        _theta_pv_signal.wait_for_connection()
        self._theta_pv = _theta_pv_signal.get(as_string=True)
        _theta_pv_signal.destroy()
        _theta_pv_signal = None

        super().__init__(
            prefix, limits=limits, readback_pv=readback_pv,
            setpoint_pv=setpoint_pv, name=name, read_attrs=read_attrs,
            configuration_attrs=configuration_attrs, parent=parent, egu=egu,
            **kwargs
        )


class Monochromator(KohzuSeqCtl_Monochromator):
    """ Tweaks from apstools mono """

    wavelength = Component(
        KohzuPositioner, "", readback_pv="BraggLambdaRdbkAO",
        setpoint_pv="BraggLambdaAO"
    )

    energy = Component(
        KohzuPositioner, "", readback_pv="BraggERdbkAO", setpoint_pv="BraggEAO"
    )

    theta = Component(
        KohzuPositioner, "", readback_pv="BraggThetaRdbkAO",
        setpoint_pv="BraggThetaAO"
    )

    # No y1 at 4-ID-D
    y1 = None

    x2 = Component(EpicsMotor, 'm6', labels=('motors', 'mono'))
    y2 = Component(EpicsSignalRO, 'KohzuYRdbkAI',
                   labels=('motors', 'mono'))
    z2 = Component(EpicsSignalRO, 'KohzuZRdbkAI',
                   labels=('motors', 'mono'))

    thf2 = Component(EpicsMotor, 'm4', labels=('motors', 'mono'))
    chi2 = Component(EpicsMotor, 'm5', labels=('motors', 'mono'))

    table_x = Component(EpicsMotor, 'm7', labels=('motors', 'mono'))
    table_y = Component(EpicsMotor, 'm8', labels=('motors', 'mono'))

    feedback = FormattedComponent(MonoFeedback, '4id:')

    def calibrate_energy(self, value):
        """Calibrate the mono energy.

        Parameters
        ----------
        value: float
            New energy for the current monochromator position.
        """
        self.use_set.put('Set', use_complete=True)
        self.energy.put(value)
        self.use_set.put('Use', use_complete=True)


mono = Monochromator('4idb:', name='mono')
mono.stage_sigs['mode'] = 1  # Ensure that mono is in auto before moving.
mono.energy.put_complete = True
mono.wavelength.put_complete = True
sd.baseline.append(mono)
