
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
from ophyd.signal import Signal
from ..framework import sd
from ophyd import Kind, Component
import time
from bluesky.plan_stubs import mv


def PresetMonitorSignal(Signal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._readback = 0

    def put(self, value, *, timestamp=None, force=False, metadata=None):
        """Put updates the internal readback value.

        The value is optionally checked first, depending on the value of force.
        In addition, VALUE subscriptions are run.
        Extra kwargs are ignored (for API compatibility with EpicsSignal kwargs
        pass through).
        Parameters
        ----------
        value : any
            Value to set
        timestamp : float, optional
            The timestamp associated with the value, defaults to time.time()
        metadata : dict, optional
            Further associated metadata with the value (such as alarm status,
            severity, etc.)
        force : bool, optional
            Check the value prior to setting it, defaults to False
        """
        self.log.debug(
            'put(value=%s, timestamp=%s, force=%s, metadata=%s)',
            value, timestamp, force, metadata
        )

        if float(value) <= 0:
            raise ValueError('preset_value has to be > 0.')

        if self.parent._monitor.s.name == 'Time':
            value *= 1e7  # convert to seconds

        old_value = self._readback
        self.parent._monitor.preset.put(value)
        self._readback = value

        if metadata is None:
            metadata = {}

        if timestamp is None:
            timestamp = metadata.get('timestamp', time.time())

        metadata = metadata.copy()
        metadata['timestamp'] = timestamp
        self._metadata.update(**metadata)

        md_for_callback = {key: metadata[key]
                           for key in self._metadata_keys
                           if key in metadata}

        if 'timestamp' not in self._metadata_keys:
            md_for_callback['timestamp'] = timestamp

        self._run_subs(sub_type=self.SUB_VALUE, old_value=old_value,
                       value=value, **md_for_callback)


class LocalScalerCH(ScalerCH):

    preset_time = None
    preset_monitor = Component(PresetMonitorSignal, kind=Kind.config)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._monitor = self.channels.chan01  # Time is the default monitor

    @property
    def hints(self):
        fields = []
        for component in scalerd.channels.component_names:
            channel = getattr(scalerd.channels, component)
            if channel.kind.value in [5, 7]:
                if len(channel.s.name) > 0:
                    fields.append(channel.s.name)
        return {'fields': fields}

    def select_plot_channels(self, chan_names):

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
                    getattr(self.channels, name_map[ch]).kind = Kind.hinted
                else:
                    if getattr(self.channels, name_map[ch]).kind.value != 0:
                        getattr(self.channels, name_map[ch]).kind = Kind.normal
                    else:
                        getattr(self.channels, name_map[ch]).kind = Kind.omitted
            except KeyError:
                raise RuntimeError("The channel {} is not configured "
                                   "on the scaler.  The named channels are "
                                   "{}".format(ch, tuple(name_map)))

    def select_channels(self, chan_names):
        """Select channels based on the EPICS name PV.

        Parameters
        ----------
        chan_names : Iterable[str] or None

            The names (as reported by the channel.chname signal)
            of the channels to select.
            If *None*, select all channels named in the EPICS scaler.
        """
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

    @property
    def monitor(self):
        return self._monitor

    @monitor.setter
    def monitor(self, value):
        # This takes a name such as 'chan01', intended for internal use.
        if value in self.channels.component_names:
            self._monitor = getattr(self.channels, value)

    def select_monitor(self, value):

        self.match_names()
        name_map = {}
        for s in self.channels.component_names:
            scaler_channel = getattr(self.channels, s)
            nm = scaler_channel.s.name  # as defined in self.match_names()
            if len(nm) > 0:
                name_map[nm] = s

        current = []
        for item in self.channels.read_attrs:
            if item in self.channels.component_names:
                current.append(getattr(self.channels, item).s.name)

        if value not in current:
            self.select_channels(current+[value])

        self.monitor = name_map[value]

        # Adjust gates
        for channel_name in self.channels.component_names:
            channel = getattr(self.channels, channel_name)
            if channel == self.monitor:
                channel.gate.put(1)
            else:
                channel.gate.put(0)

    def SetCountTimePlan(self, value, **kwargs):
        yield from mv(self.preset_monitor.put(value), **kwargs)


scalerd = LocalScalerCH('4id:scaler1', name='scalerd',
                        labels=('detectors', 'counters'))
scalerd.select_channels(None)
scalerd.select_plot_channels(None)
sd.baseline.append(scalerd)

scalerb = LocalScalerCH('4idb:scaler1', name='scalerb',
                        labels=('detectors', 'counters'))
scalerb.channels.chan01.chname.set('Time_b')
scalerb.select_channels(None)
scalerb.select_plot_channels(None)
sd.baseline.append(scalerb)

# TODO: name the other channels, watch out for python keywords such as del!
# TODO: How should we handle the scalers? What is scaler3?
