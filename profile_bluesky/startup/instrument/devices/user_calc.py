"""
User Calculator
"""

__all__ = ['absorption_calc','normalize_calc']

from instrument.session_logs import logger
logger.info(__file__)

from ophyd import Device, EpicsSignal, Kind
from ophyd import  Component,FormattedComponent, DynamicDeviceComponent
from string import ascii_uppercase
from collections import OrderedDict
from ..framework import sd

# Based on ophyd.ScalerCH

class UserCalcChannel(Device):

    trigger_option = FormattedComponent(EpicsSignal,
                                        '{self.prefix}.IN{self._ch}P',
                                        kind=Kind.config)

    PVname = FormattedComponent(EpicsSignal,
                                '{self.prefix}.IN{self._ch}N',
                                kind=Kind.config)

    value = FormattedComponent(EpicsSignal,
                               '{self.prefix}.{self._ch}',
                               kind=Kind.config)

    def __init__(self, prefix, ch, **kwargs):
        self._ch = ch
        super().__init__(prefix, **kwargs)


def _sc_chans(attr_fix, id_range):
    defn = OrderedDict()
    for k in id_range:
        defn['{}{}'.format(attr_fix, k)] = (UserCalcChannel,
                                                '', {'ch': k,
                                                     'kind': Kind.config})
    return defn  

class UserCalc(Device):

    channels =  DynamicDeviceComponent(_sc_chans('chan',
                                                 list(ascii_uppercase)[:12]),
                                        kind=Kind.config)

    scan = Component(EpicsSignal,'.SCAN',kind=Kind.omitted)
    expression = Component(EpicsSignal,'.CALC$',string=True,kind=Kind.config)
    calc_value = Component(EpicsSignal,'.VAL',kind=Kind.hinted)
    enable = Component(EpicsSignal,'.DESC',string=True,kind=Kind.config)
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self._read_attrs = ['calc_value']
    
    @property
    def read_attrs(self):
        return self._read_attrs
    
    @read_attrs.setter
    def read_attrs(self,value):
        if type(value) is not list:
            raise TypeError('read_attrs has to be a list!')
        else:
            self._read_attrs = value

absorption_calc = UserCalc('4id:userCalc9',name='absorption_calc')
absorption_calc.scan.put(2)

normalize_calc = UserCalc('4id:userCalc10',name='normalize_calc')
normalize_calc.scan.put(2)

sd.baseline.append(absorption_calc)
