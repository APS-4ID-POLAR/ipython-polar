"""
SRS preamplifiers
"""


__all__ = ['preamps']


from ..session_logs import logger
logger.info(__file__)

from ophyd import Component, Device, EpicsSignal, FormattedComponent
from ..framework import sd


class PreAmpDevice(Device):

    # Current sensitivity
    sensitivity_value = FormattedComponent(EpicsSignal,
                                           '{prefix}A{_num}sens_num.VAL',
                                           kind='config', string=True,
                                           labels=('preamps'))

    sensitivity_unit = FormattedComponent(EpicsSignal,
                                          '{prefix}A{_num}sens_unit.VAL',
                                          kind='config', string=True,
                                          labels=('preamps'))

    # Offset current
    offset_on = FormattedComponent(EpicsSignal, '{prefix}A{_num}offset_on.VAL',
                                   kind='config', string=True,
                                   labels=('preamps'))

    offset_sign = FormattedComponent(EpicsSignal,
                                     '{prefix}A{_num}offset_sign.VAL',
                                     kind='config', string=True,
                                     labels=('preamps'))

    offset_value = FormattedComponent(EpicsSignal,
                                      '{prefix}A{_num}offset_num.VAL',
                                      kind='config', string=True,
                                      labels=('preamps'))

    offset_unit = FormattedComponent(EpicsSignal,
                                     '{prefix}A{_num}offset_unit.VAL',
                                     kind='config', string=True,
                                     labels=('preamps'))

    offset_fine = FormattedComponent(EpicsSignal,
                                     '{prefix}A{_num}off_u_put.VAL',
                                     kind='config', string=True,
                                     labels=('preamps'))

    offset_cal = FormattedComponent(EpicsSignal,
                                    '{prefix}A{_num}offset_cal.VAL',
                                    kind='config', string=True,
                                    labels=('preamps'))

    # Set all button
    set_all = FormattedComponent(EpicsSignal, '{prefix}A{_num}init.PROC',
                                 kind='config', labels=('preamps'))

    # Bias voltage
    bias_value = FormattedComponent(EpicsSignal, '{prefix}A{_num}bias_put.VAL',
                                    kind='config', string=True,
                                    labels=('preamps'))

    bias_on = FormattedComponent(EpicsSignal, '{prefix}A{_num}bias_on.VAL',
                                 kind='config', string=True,
                                 labels=('preamps'))

    # Filter
    filter_type = FormattedComponent(EpicsSignal,
                                     '{prefix}A{_num}filter_type.VAL',
                                     kind='config', string=True,
                                     labels=('preamps'))

    filter_lowpass = FormattedComponent(EpicsSignal,
                                        '{prefix}A{_num}low_freq.VAL',
                                        kind='config', string=True,
                                        labels=('preamps'))

    filter_highpass = FormattedComponent(EpicsSignal,
                                         '{prefix}A{_num}high_freq.VAL',
                                         kind='config', string=True,
                                         labels=('preamps'))

    # Gain mode
    gain_mode = FormattedComponent(EpicsSignal, '{prefix}A{_num}gain_mode.VAL',
                                   kind='config', string=True,
                                   labels=('preamps'))

    # Invert
    invert = FormattedComponent(EpicsSignal, '{prefix}A{_num}invert_on.VAL',
                                kind='config', string=True, labels=('preamps'))

    # Blank
    blank = FormattedComponent(EpicsSignal, '{prefix}A{_num}blank_on.VAL',
                               kind='config', string=True, labels=('preamps'))

    def __init__(self, *args, num=0, **kwargs):
        self._num = num
        super().__init__(*args, **kwargs)


class PreAmpStack(Device):

    ch1 = Component(PreAmpDevice, '', num=1, labels=('preamps'))
    ch2 = Component(PreAmpDevice, '', num=2, labels=('preamps'))
    ch3 = Component(PreAmpDevice, '', num=3, labels=('preamps'))
    ch4 = Component(PreAmpDevice, '', num=4, labels=('preamps'))
    ch5 = Component(PreAmpDevice, '', num=5, labels=('preamps'))
    ch6 = Component(PreAmpDevice, '', num=6, labels=('preamps'))
    ch7 = Component(PreAmpDevice, '', num=7, labels=('preamps'))
    ch8 = Component(PreAmpDevice, '', num=8, labels=('preamps'))


preamps = PreAmpStack('4idd:', name='preamps')
sd.baseline.append(preamps)
