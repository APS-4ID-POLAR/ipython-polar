
"""
our diffractometer
"""

__all__ = [
    'scalerd',
    'scalerb',
    ]

from ..session_logs import logger
logger.info(__file__)

from ophyd.scaler import ScalerCH
from ..framework import sd
from ophyd import Kind


class LocalScalerCH(ScalerCH):
    
    @property
    def hints(self):
        fields = []
        for component in scalerd.channels.component_names: 
            channel = getattr(scalerd.channels,component) 
            if channel.kind.value in [5,7]:
                if len(channel.s.name) > 0:
                    fields.append(channel.s.name)
        return {'fields':fields}
    
    def select_plot_channels(self,chan_names):
        
        self.match_names()
        name_map = {}
        for s in self.channels.component_names:
            scaler_channel = getattr(self.channels, s)
            nm = scaler_channel.s.name  # as defined in self.match_names()
            if len(nm) > 0:
                name_map[nm] = s

        if chan_names is None:
            chan_names = name_map.keys()

        for ch in name_map.keys():
            try:
                if ch in chan_names: 
                    getattr(self.channels,name_map[ch]).kind = Kind.hinted
                else:
                    if getattr(self.channels,name_map[ch]).kind.value != 0:
                        getattr(self.channels,name_map[ch]).kind = Kind.normal
                    else:
                        getattr(self.channels,name_map[ch]).kind = Kind.omitted
            except KeyError:
                raise RuntimeError("The channel {} is not configured "
                                   "on the scaler.  The named channels are "
                                   "{}".format(ch, tuple(name_map)))
                
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
            
        if len(self.hints['fields']) == 0:
            self.select_plot_channels(chan_names)

scalerd = LocalScalerCH('4id:scaler1', name='scalerd', labels=('detectors','counters'))
scalerd.select_channels(None)
scalerd.select_plot_channels(None)
sd.baseline.append(scalerd)

scalerb = LocalScalerCH('4idb:scaler1', name='scalerb', labels=('detectors','counters'))
scalerb.channels.chan01.chname.set('Time_b')
scalerb.select_channels(None)
scalerb.select_plot_channels(None)
sd.baseline.append(scalerb)

# TODO: name the other channels, watch out for python keywords such as del!
# TODO: How should we handle the scalers? What is scaler3?
