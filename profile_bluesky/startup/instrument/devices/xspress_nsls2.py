from __future__ import print_function, division
import time as ttime

from collections import OrderedDict

from ophyd import (Signal, EpicsSignal, EpicsSignalRO, DerivedSignal, SignalRO,
                   Component, FormattedComponent, DynamicDeviceComponent, Kind)
from ophyd.areadetector.detectors import Xspress3Detector, ADBase
from ophyd.device import BlueskyInterface, Staged
from ophyd.status import DeviceStatus

from ..framework import sd
from ..session_logs import logger
logger.info(__file__)

MAX_NUM_ROIS = 40


def ev_to_bin(ev):
    '''Convert eV to bin number'''
    return int(ev / 10)


def bin_to_ev(bin_):
    '''Convert bin number to eV'''
    return int(bin_) * 10


class EvSignal(DerivedSignal):
    '''A signal that converts a bin number into electron volts'''
    def __init__(self, parent_attr, *, parent=None, **kwargs):
        bin_signal = getattr(parent, parent_attr)
        super().__init__(derived_from=bin_signal, parent=parent, **kwargs)

    def inverse(self, value):
        '''Compute original signal value -> derived signal value'''
        return bin_to_ev(value)

    def forward(self, value):
        '''Compute derived signal value -> original signal value'''
        return ev_to_bin(value)

    def describe(self):
        desc = super().describe()
        desc[self.name]['units'] = 'eV'
        return desc


class CorrectedSignal(DerivedSignal):
    """ Signal that returns the deadtime corrected counts """
    def inverse(self, value):
        return value*self.parent._channel.dt_factor.get()


class Xspress3ROI(ADBase):
    '''A configurable Xspress3 EPICS ROI'''

    # Bin limits
    bin_low = FormattedComponent(EpicsSignal, "{_prefix}MinX", kind="config")
    bin_size = FormattedComponent(EpicsSignal, "{_prefix}SizeX", kind="config")

    # Energy limits
    ev_low = Component(EvSignal, parent_attr='bin_low', kind='config')
    ev_size = Component(EvSignal, parent_attr='bin_size', kind='config')

    # Raw total
    total_rbv = FormattedComponent(EpicsSignalRO, '{_prefix}Total_RBV',
                                   kind='normal')

    # Corrected total
    total_corrected = Component(CorrectedSignal, parent_attr='total_rbv',
                                kind='normal')

    # Name
    roi_name = FormattedComponent(EpicsSignal, '{_prefix}Name', kind='config')

    # Enable
    use = Component(EpicsSignal, '{_prefix}Use', kind='config', string=True)

    @property
    def ad_root(self):
        root = self.parent
        while True:
            if not isinstance(root.parent, ADBase):
                return root
            root = root.parent

    def __init__(self, prefix, *, roi_num=0, read_attrs=None,
                 configuration_attrs=None, parent=None, **kwargs):

        if configuration_attrs is None:
            configuration_attrs = ['ev_low', 'ev_high', 'enable']

        rois = parent
        channel = rois.parent
        self._channel = channel
        self._roi_num = roi_num
        self._ad_plugin = getattr(rois, 'ad_attr{:02d}'.format(roi_num))

        self._prefix = f'MCA{channel.channel_num}ROI:{roi_num}:'

        super().__init__(prefix, parent=parent, read_attrs=read_attrs,
                         configuration_attrs=configuration_attrs, **kwargs)

    @property
    def settings(self):
        '''Full areaDetector settings'''
        return self._ad_plugin

    @property
    def channel(self):
        '''The Xspress3Channel instance associated with the ROI'''
        return self._channel

    @property
    def channel_num(self):
        '''The channel number associated with the ROI'''
        return self._channel.channel_num

    @property
    def roi_num(self):
        '''The ROI number'''
        return self._roi_num

    def clear(self):
        '''Clear and disable this ROI'''
        self.configure(0, 0)

    def enable(self):
        return self.use.set('Yes')

    def disable(self):
        return self.use.set('No')

    def configure(self, name, ev_low, ev_size, enable=True):
        '''Configure the ROI with low and high eV
        Parameters
        ----------
        name : string
            ROI label.
        ev_low : float or int
            Lower edge of ROI in electron volts.
        ev_size : float or int
            Size of ROI in electron volts.
        enable : boolean, optional
            Flag to determine if this ROI should be used.
        '''

        ev_low = int(ev_low)
        ev_size = int(ev_size)

        if ev_low < 0:
            raise ValueError(f'ev_low cannot be < 0, but {ev_low} was entered')
        if ev_size < 0:
            raise ValueError(f'ev_size cannot be < 0, but {ev_size} was '
                             'entered')

        self.roi_name.put(name)
        self.ev_size.put(ev_size)
        self.ev_low.put(ev_low)

        if enable is True:
            self.enable()
        else:
            self.disable()


def make_rois(rois):
    defn = OrderedDict()
    for roi in rois:
        attr = 'roi{:02d}'.format(roi)
        defn[attr] = (Xspress3ROI, "", dict(roi_num=roi))
        # e.g., device.rois.roi01 = Xspress3ROI('ROI1:', roi_num=1)

    defn['num_rois'] = (Signal, None, dict(value=len(rois)))
    # e.g., device.rois.num_rois.get() => 16
    return defn


class Xspress3Channel(ADBase):

    rois = DynamicDeviceComponent(make_rois(range(1, MAX_NUM_ROIS+1)))

    # TODO: Needed?
    # Timestamp --> it's used to tell when the ROI plugin is done.
    # timestamp = FormattedComponent(EpicsSignalRO,
    #                                '{prefix}MCA{_chnum}ROI:TimeStamp_RBV',
    #                                kind='omitted', auto_monitor=True)

    # SCAs
    clock_ticks = FormattedComponent(EpicsSignalRO,
                                     '{prefix}C{channel_num}SCA0:Value_RBV')

    reset_ticks = FormattedComponent(EpicsSignalRO,
                                     '{prefix}C{channel_num}SCA1:Value_RBV')

    reset_counts = FormattedComponent(EpicsSignalRO,
                                      '{prefix}C{channel_num}SCA2:Value_RBV')

    all_events = FormattedComponent(EpicsSignalRO,
                                    '{prefix}C{channel_num}SCA3:Value_RBV')

    all_good = FormattedComponent(EpicsSignalRO,
                                  '{prefix}C{channel_num}SCA4:Value_RBV')

    pileup = FormattedComponent(EpicsSignalRO,
                                '{prefix}C{channel_num}SCA7:Value_RBV')

    dt_factor = FormattedComponent(EpicsSignalRO,
                                   '{prefix}C{channel_num}SCA8:Value_RBV')

    def __init__(self, prefix, *, channel_num=None, **kwargs):
        self.channel_num = int(channel_num)
        super().__init__(prefix, **kwargs)

    @property
    def all_rois(self):
        for roi in range(1, self.rois.num_rois.get() + 1):
            yield getattr(self.rois, 'roi{:02d}'.format(roi))

    def set_roi(self, index, ev_low, ev_size, name=None, enable=True):
        '''Set specified ROI to (ev_low, ev_size)
        Parameters
        ----------
        index : int or iterable of int
            ROI index. It can be passed as an integer or an iterable with
            integers.
        ev_low : int
            low eV setting.
        ev_size : int
            size eV setting.
        name : str, optional
            ROI name, if nothing is passed it will keep the current name.
        enable : boolean
            Flag to enable the ROI.
        '''
        if isinstance(index, int):
            index = [index]

        rois = list(self.all_rois)

        for ind in index:
            if ind <= 0:
                raise ValueError('ROI index starts from 1')

            roi = rois[ind - 1]

            if name is None:
                name = roi.roi_name.get()

            roi.configure(name, ev_low, ev_size, enable=enable)

    def clear_all_rois(self):
        '''Clear all ROIs'''
        for roi in self.all_rois:
            roi.clear()


class Xspress3Trigger(BlueskyInterface):
    """Base class for trigger mixin classes
    Subclasses must define a method with this signature:
    `acquire_changed(self, value=None, old_value=None, **kwargs)`
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # settings
        self._status = None
        self._acquisition_signal = self.cam.acquire
        self._abs_trigger_count = 0

    def stage(self):
        self._abs_trigger_count = 0
        self._acquisition_signal.subscribe(self._acquire_changed)
        return super().stage()

    def unstage(self):
        ret = super().unstage()
        self._acquisition_signal.clear_sub(self._acquire_changed)
        self._status = None
        return ret

    def _acquire_changed(self, value=None, old_value=None, **kwargs):
        "This is called when the 'acquire' signal changes."
        if self._status is None:
            return
        if (old_value == 1) and (value == 0):
            # Negative-going edge means an acquisition just finished.
            self._status._finished()

    # TODO: I think this will not work...
    def trigger(self):
        if self._staged != Staged.yes:
            raise RuntimeError("not staged")

        self._status = DeviceStatus(self)
        self._acquisition_signal.put(1, wait=False)
        trigger_time = ttime.time()

        for _, ch in self.channels:
            self.dispatch(ch.name, trigger_time)

        self._abs_trigger_count += 1
        return self._status


class TotalSignal(SignalRO):
    """ Signal that sums a given ROI for all channels """
    # TODO: Needs prefix?
    def __init__(self, roi_index, **kwargs):
        self.roi_index = roi_index
        super().__init__(**kwargs)

    def get(self, **kwargs):
        values_list = []
        for _, ch in self.root.channels.items():
            values_list.append(
                getattr(ch.rois, 'roi{:02d}').format(
                    self.roi_index
                ).get(**kwargs)
            )

        return sum(values_list)


def _totals(id_range):
    defn = OrderedDict()
    for k in id_range:
        defn['roi{:02d}'.format(k)] = (TotalSignal,
                                       {'roi_index': k, 'kind': 'normal'})
    return defn


class Xspress3DetectorBase(Xspress3Detector, Xspress3Trigger):

    # Total corrected counts of each ROI
    total_counts = DynamicDeviceComponent(_totals(range(1, MAX_NUM_ROIS+1)))

    rewindable = Component(Signal, value=False,
                           doc='Xspress3 cannot safely be rewound in bluesky')

    # Add channels:
    # ch1 = Component(Xspress3Channel, '', channel_num=1)

    def __init__(self, prefix, *, read_attrs=None, configuration_attrs=None,
                 name=None, parent=None, **kwargs):

        super().__init__(prefix, read_attrs=read_attrs,
                         configuration_attrs=configuration_attrs,
                         name=name, parent=parent, **kwargs)

        # get all sub-device instances
        sub_devices = {attr: getattr(self, attr)
                       for attr in self._sub_devices}

        # filter those sub-devices, just giving channels
        channels = {
            dev.channel_num: dev for _, dev in sub_devices.items() if
            isinstance(dev, Xspress3Channel)
        }

        # make an ordered dictionary with the channels in order
        self._channels = OrderedDict(sorted(channels.items()))
        self._num_channels = len(self._channels.keys())

    @property
    def channels(self):
        return self._channels.copy()

    @property
    def enabled_rois(self):
        for roi in self.all_rois:
            if roi.enable.get():
                yield roi

    def _toggle_roi(self, index, channels=None, enable=True):
        if channels is None:
            channels = range(1, self._num_channels+1)

        if isinstance(index, (int, float)):
            index = (int(index), )

        action = 'enable' if enable else 'disable'

        for ind in index:
            if ind > MAX_NUM_ROIS:
                raise ValueError(f"Maximum ROI index is {MAX_NUM_ROIS}, but "
                                 f"{ind} was entered.")

            for ch in channels:
                channel = self.channels[ch]
                getattr(channel.rois, 'roi{:02d}.{}'.format(ind, action))()

            roi_cnt = getattr(self.total_counts, 'roi{:02d}'.format(ind))
            roi_cnt.kind = Kind.normal if enable else Kind.omitted

    def set_roi(self, index, ev_low, ev_size, name='', channels=None,
                enable=True):
        """
        Set up the same ROI configuration for selected channels

        Parameters
        ----------
        index : int or list of int
            ROI index. It can be passed as an integer or an iterable with
            integers.
        ev_low : int
            low eV setting.
        ev_size : int
            size eV setting.
        name : str, optional
            ROI name, if nothing is passed it will keep the current name.
        channels : iterable
            List with channel numbers to be changed.
        """

        # make a function Edge2Emission(AbsEdge) --> returns primary emission
        # energy
        # 1st argument for roi1, 2nd for roi2...
        # 'S4QX4:MCA1ROI:1:Total_RBV'  # roi1 of channel 1
        # 'S4QX4:MCA1ROI:2:Total_RBV'  # roi1 of channel 2

        if channels is None:
            channels = range(1, self._num_channels+1)

        self._toggle_roi(index, channels=channels, enable=enable)

        for ch in channels:
            self.channels[ch].set_roi(index, ev_low, ev_size, name=name)

    def enable_roi(self, index, channels=None):
        """
        Enable ROI(s).

        Parameters
        ----------
        index : int or list of int
            ROI index. It can be passed as an integer or an iterable with
            integers.
        channels : iterable, optional
            List with channel numbers to be changed. If None, all channels will
            be used.
        """
        self._toggle_roi(index, channels=channels, enable=True)

    def disable_roi(self, index, channels=None):
        """
        Disable ROI(s).

        Parameters
        ----------
        index : int or list of int
            ROI index. It can be passed as an integer or an iterable with
            integers.
        channels : iterable, optional
            List with channel numbers to be changed. If None, all channels will
            be used.
        """
        self._toggle_roi(index, channels=channels, enable=False)

    def unload(self):
        """
        Remove detector from baseline and run .destroy()
        """
        sd.baseline.remove(self)
        self.destroy()

    def select_plot_channels(self, rois):
        """
        Selects channels to plot

        Parameters
        ----------
        rois : int or iterable of ints
            ROI number.
        """
        if isinstance(rois, int):
            rois = (rois, )

        for roi_num in range(1, MAX_NUM_ROIS+1):
            roi = getattr(self.total_counts, 'roi{:02d}'.format(roi_num))
            if roi_num in rois:
                roi.kind = Kind.hinted
            elif roi.kind == Kind.hinted:
                roi.kind = Kind.normal


class Xspress3Vortex4Ch(Xspress3DetectorBase):

    # Channels
    ch1 = Component(Xspress3Channel, '', chnum=1)
    ch2 = Component(Xspress3Channel, '', chnum=2)
    ch3 = Component(Xspress3Channel, '', chnum=3)
    ch4 = Component(Xspress3Channel, '', chnum=4)

    _num_channels = 4


class Xspress3Vortex1Ch(Xspress3DetectorBase):

    # Channels
    ch1 = Component(Xspress3Channel, '', chnum=1)

    _num_channels = 1
