
__all__ = [
    'simScalerCH',
    ]

from ophyd.sim import SynGauss,FakeEpicsSignal,FakeEpicsSignalRO,motor,make_fake_device
from ophyd import (Component as Cpt, Kind,
                   DynamicDeviceComponent as DDCpt, Device)
from ophyd.device import FormattedComponent as FCpt
from ophyd.scaler import ScalerChannel
from collections import OrderedDict

class FakeScalerChannel(Device):

    # TODO set up monitor on this to automatically change the name
    chname = FCpt(FakeEpicsSignal, '',kind=Kind.config)
    s = FCpt(FakeEpicsSignalRO, '',kind=Kind.hinted)
    preset = FCpt(FakeEpicsSignal, '',kind=Kind.config)
    gate = FCpt(FakeEpicsSignal, '', string=True,kind=Kind.config)

    def __init__(self, prefix, ch_num,
                 **kwargs):
        self._ch_num = ch_num

        super().__init__(prefix, **kwargs)
        self.match_name()

    def match_name(self):
        #self.s.name = self.chname.get()
        self.s.name = '{}{:02d}'.format('chan',self._ch_num)
        self.chname.put('{}{:02d}'.format('chan',self._ch_num))

def _sc_chans(attr_fix, id_range):

    #SynGauss('det', motor, 'motor', center=0, Imax=1, sigma=1)

    defn = OrderedDict()
    for k in id_range:
        defn['{}{:02d}'.format(attr_fix, k)] = (FakeScalerChannel,
                                                '', {'ch_num': k,
                                                     'kind': Kind.normal})
    return defn

class simScalerCH(Device):

    # The data
    channels = DDCpt(_sc_chans('chan', range(1, 33)))

    # tigger + trigger mode
    count = Cpt(FakeEpicsSignal, '.CNT', trigger_value=1, kind=Kind.omitted)
    count_mode = Cpt(FakeEpicsSignal, '.CONT', string=True, kind=Kind.config)

    # delay from triggering to starting counting
    delay = Cpt(FakeEpicsSignal, '.DLY', kind=Kind.config)
    auto_count_delay = Cpt(FakeEpicsSignal, '.DLY1', kind=Kind.config)

    time = Cpt(FakeEpicsSignal, '.T')
    freq = Cpt(FakeEpicsSignal, '.FREQ', kind=Kind.config)

    preset_time = Cpt(FakeEpicsSignal, '.TP', kind=Kind.config)
    auto_count_time = Cpt(FakeEpicsSignal, '.TP1', kind=Kind.config)

    update_rate = Cpt(FakeEpicsSignal, '.RATE', kind=Kind.omitted)
    auto_count_update_rate = Cpt(FakeEpicsSignal, '.RAT1', kind=Kind.omitted)

    egu = Cpt(FakeEpicsSignal, '.EGU', kind=Kind.config)

    def match_names(self):
        for s in self.channels.component_names:
            getattr(self.channels, s).match_name()

    def select_channels(self, chan_names):
        '''Select channels based on the EPICS name PV

        Parameters
        ----------
        chan_names : Iterable[str] or None

            The names (as reported by the channel.chname signal)
            of the channels to select.
            If *None*, select all channels named in the EPICS scaler.
        '''
        self.match_names()
        name_map = {}
        for s in self.channels.component_names:
            scaler_channel = getattr(self.channels, s)
            nm = scaler_channel.s.name  # as defined in self.match_names()
            if len(nm) > 0:
                name_map[nm] = s

        if chan_names is None:
            chan_names = name_map.keys()

        read_attrs = ['chan01']  # always include time
        for ch in chan_names:
            try:
                read_attrs.append(name_map[ch])
            except KeyError:
                raise RuntimeError("The channel {} is not configured "
                                   "on the scaler.  The named channels are "
                                   "{}".format(ch, tuple(name_map)))
        self.channels.kind = Kind.normal
        self.channels.read_attrs = list(read_attrs)
        self.channels.configuration_attrs = list(read_attrs)
        for ch in read_attrs[1:]:
            getattr(self.channels, ch).s.kind = Kind.hinted

# TODO: This almost works. But the counting is not quite right.
