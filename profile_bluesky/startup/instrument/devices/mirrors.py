
"""
Magnet motor
"""

__all__ = [
    'toroidal_mirror','flat_mirror'
    ]

from ..session_logs import logger
logger.info(__file__)

from ophyd import Component, Device, EpicsMotor, EpicsSignal

## Toroidal Mirror ##
class ToroidalMirror(Device):

    y_upstream   = Component(EpicsMotor,'m35',labels=('motor','mirrors'))
    y_downstream = Component(EpicsMotor,'m36',labels=('motor','mirrors'))
    y = Component(EpicsSignal,'M1t2.D',write_pv=':M1avg',
                          labels=('motor','mirrors'))
    angle = Component(EpicsSignal,'M1t2.C',write_pv=':M1angl',
                        labels=('motor','mirrors'))


    x_upstream   = Component(EpicsMotor,'m33',labels=('motor','mirrors'))
    x_downstream = Component(EpicsMotor,'m34',labels=('motor','mirrors'))
    x = Component(EpicsSignal,'M1xt2.D',write_pv=':M1xavg',
                          labels=('mirrors'))
    x_angle = Component(EpicsSignal,'M1xt2.C',write_pv=':M1xangl',
                        labels=('mirrors'))

    bender = Component(EpicsMotor,'m32',labels=('motor','mirrors'))

toroidal_mirror = ToroidalMirror('4idb:',name='toroidal mirror')

class FlatMirror(Device):

    y_upstream   = Component(EpicsMotor,'m39',labels=('motor','mirrors'))
    y_downstream = Component(EpicsMotor,'m40',labels=('motor','mirrors'))
    y = Component(EpicsSignal,'M2t2.D',write_pv=':M2avg',
                          labels=('mirrors'))
    angle = Component(EpicsSignal,'M2t2.C',write_pv=':M2angl',
                        labels=('mirrors'))

    x_upstream   = Component(EpicsMotor,'m37',labels=('motor','mirrors'))
    x_downstream = Component(EpicsMotor,'m38',labels=('motor','mirrors'))
    x = Component(EpicsSignal,'M2xt2.D',write_pv=':M1xavg',
                          labels=('mirrors'))
    x_angle = Component(EpicsSignal,'M1xt2.C',write_pv=':M1xangl',
                        labels=('mirrors'))

flat_mirror = FlatMirror('4idb:',name='flat mirror')

# TODO: How to add the different default positions in the mirrors?
# TODO: Check that the limits option of EpicsSignal will work!
# TODO: KB mirrors.
