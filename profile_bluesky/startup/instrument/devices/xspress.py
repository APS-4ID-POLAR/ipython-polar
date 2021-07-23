""" Vortex with Xspress"""

from ophyd.areadetector.detectors import Xspress3Detector
from ophyd.areadetector.trigger_mixins import SingleTrigger

from ophyd import (EpicsSignal, EpicsSignalRO, DerivedSignal, Signal, Device,
                   Component, FormattedComponent, Kind, DynamicDeviceComponent)
from ophyd.status import AndStatus, Status
from ophyd.signal import SignalRO
from collections import OrderedDict
from ..framework import sd

from ..session_logs import logger
logger.info(__file__)


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

    def get(self, **kwargs):
        bin_ = super().get(**kwargs)
        return bin_to_ev(bin_)

    def put(self, ev_value, **kwargs):
        bin_value = ev_to_bin(ev_value)
        return super().put(bin_value, **kwargs)

    def describe(self):
        desc = super().describe()
        desc[self.name]['units'] = 'eV'
        return desc


class TotalCorrectedSignal(SignalRO):
    """ Signal that returns the deadtime corrected total counts """

    def __init__(self, prefix, roi_index, **kwargs):
        if not roi_index:
            raise ValueError('chnum must be the channel number, but '
                             'f{roi_index} was passed.')
        self.roi_index = roi_index
        super().__init__(**kwargs)

    def get(self, **kwargs):
        value = 0
        for ch_num in range(1, self.root._num_channels+1):
            channel = getattr(self.root, f'Ch{ch_num}')
            roi = getattr(channel.rois, 'roi{:02d}'.format(self.roi_index))
            value += channel.dt_factor.get(**kwargs) * \
                roi.total_rbv.get(**kwargs)

        return value


class Xspress3ROI(Device):

    # Bin limits
    bin_low = Component(EpicsSignal, 'MinX', kind='config')
    bin_size = Component(EpicsSignal, 'SizeX', kind='config')

    # Energy limits
    ev_low = Component(EvSignal, parent_attr='bin_low', kind='config')
    ev_size = Component(EvSignal, parent_attr='bin_size', kind='config')

    # Raw total
    total_rbv = Component(EpicsSignalRO, 'Total_RBV', kind='normal')

    # Name
    roi_name = Component(EpicsSignal, 'Name', kind='config')

    # Enable
    enable_flag = Component(EpicsSignal, 'Use', kind='config',
                            put_complete=True, string=True)

    @enable_flag.sub_value
    def _change_kind(self, value=None, **kwargs):
        if value == 'Yes':
            self.kind = Kind.normal
        elif value == 'No':
            self.kind = Kind.omitted

    def enable(self):
        return self.enable_flag.set('Yes')

    def disable(self):
        return self.enable_flag.set('No')

    def clear(self):
        '''Clear and disable this ROI'''
        self.configure('', 0, 0, enable=False)

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


class ROIDevice(Device):
    # TODO: Using locals() feels like cheating...
    # Make 32 ROIs --> same number as in EPICS support.
    for i in range(1, 33):
        locals()['roi{:02d}'.format(i)] = Component(Xspress3ROI, f'{i}:')

    num_rois = Component(Signal, value=32, kind='config')


class Xspress3Channel(Device):

    rois = FormattedComponent(ROIDevice, '{prefix}MCA{_chnum}ROI:')

    # Timestamp --> it's used to tell when the ROI plugin is done.
    timestamp = FormattedComponent(EpicsSignalRO,
                                   '{prefix}MCA{_chnum}ROI:TimeStamp_RBV',
                                   kind='omitted', auto_monitor=True)

    # SCAs
    clock_ticks = FormattedComponent(EpicsSignalRO,
                                     '{prefix}C{_chnum}SCA0:Value_RBV')

    reset_ticks = FormattedComponent(EpicsSignalRO,
                                     '{prefix}C{_chnum}SCA1:Value_RBV')

    reset_counts = FormattedComponent(EpicsSignalRO,
                                      '{prefix}C{_chnum}SCA2:Value_RBV')

    all_events = FormattedComponent(EpicsSignalRO,
                                    '{prefix}C{_chnum}SCA3:Value_RBV')

    all_good = FormattedComponent(EpicsSignalRO,
                                  '{prefix}C{_chnum}SCA4:Value_RBV')

    pileup = FormattedComponent(EpicsSignalRO,
                                '{prefix}C{_chnum}SCA7:Value_RBV')

    dt_factor = FormattedComponent(EpicsSignalRO,
                                   '{prefix}C{_chnum}SCA8:Value_RBV')

    def __init__(self, *args, chnum, **kwargs):
        # TODO: I don't like how this is currently implemented, but it works.
        self._chnum = chnum
        super().__init__(*args, **kwargs)

    def _status_done(self):

        # Create status that checks when the timestamp updates.
        status = Status(self.timestamp, settle_time=0.01)

        def _set_finished(**kwargs):
            status.set_finished()
            self.timestamp.clear_sub(_set_finished)

        self.timestamp.subscribe(_set_finished, event_type='value', run=False)

        return status

    @property
    def all_rois(self):
        for roi in range(1, self.rois.num_rois.get() + 1):
            yield getattr(self.rois, 'roi{:02d}'.format(roi))

    def set_roi(self, index, ev_low, ev_size, name=None, enable=True):
        '''Set specified ROI to (ev_low, ev_size)
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

            if not name:
                name = roi.roi_name.get()

            roi.configure(name, ev_low, ev_size, enable=enable)


def _totals(attr_fix, id_range):
    defn = OrderedDict()
    for k in id_range:
        defn['{}{:02d}'.format(attr_fix, k)] = (TotalCorrectedSignal, '',
                                                {'roi_index': k,
                                                 'kind': Kind.normal})
    return defn


class Xspress3VortexBase(Xspress3Detector, SingleTrigger):

    # Total corrected counts of each ROI
    corrected_counts = DynamicDeviceComponent(_totals('roi', range(1, 33)))

    def __init__(self, prefix, *, configuration_attrs=None,
                 read_attrs=None, **kwargs):

        super().__init__(prefix, configuration_attrs=None, read_attrs=None,
                         **kwargs)

        self._enabled_rois = []

    def set_roi(self, index, ev_low, ev_size, name='', channels=None):
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

        if not channels:
            channels = range(1, self._num_channels+1)
            # TODO: There is some redundancy here, but for now this is needed
            # to activate the corrected_counts.roi{index}
            self._toggle_roi(index, channels=channels)

        for ch in channels:
            getattr(self, f'Ch{ch}').set_roi(index, ev_low, ev_size, name=name)

    def _toggle_roi(self, index, channels=None, enable=True):
        if not channels:
            channels = range(1, self._num_channels+1)

        if isinstance(index, (int, float)):
            index = (int(index), )

        action = 'enable' if enable else 'disable'

        for ch in channels:
            channel = getattr(self, f'Ch{ch}')

            for ind in index:
                try:
                    getattr(channel.rois, 'roi{:02d}.{}'.format(ind, action))()
                    roi_cnt = getattr(self.corrected_counts,
                                      'roi{:02d}'.format(ind))
                    if len(channels) == self._num_channels:
                        roi_cnt.kind = Kind.hinted if enable else Kind.omitted
                except AttributeError:
                    break

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
        for ind in index:
            roi = getattr(self.corrected_counts, 'roi{:02d}'.format(ind))
            roi.kind = Kind.normal

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
        for ind in index:
            roi = getattr(self.corrected_counts, 'roi{:02d}'.format(ind))
            roi.kind = Kind.omitted

    def unload(self):
        """
        Remove detector from baseline and run .destroy()
        """
        sd.baseline.remove(self)
        self.destroy()

    def select_plot_channels(self, value):
        """
        Selects channels to plot

        Parameters
        ----------
        value : int or iterable of ints
            ROI number.
        """
        if isinstance(value, int):
            value = [value]

        for roi_num in range(1, 33):
            roi = getattr(self.corrected_counts, 'roi{:02d}'.format(roi_num))
            roi.kind = Kind.hinted if roi_num in value else Kind.normal


class Xspress3Vortex4Ch(Xspress3VortexBase):

    # Channels
    Ch1 = Component(Xspress3Channel, '', chnum=1)
    Ch2 = Component(Xspress3Channel, '', chnum=2)
    Ch3 = Component(Xspress3Channel, '', chnum=3)
    Ch4 = Component(Xspress3Channel, '', chnum=4)

    _num_channels = 4


class Xspress3Vortex1Ch(Xspress3VortexBase):

    # Channels
    Ch1 = Component(Xspress3Channel, '', chnum=1)

    _num_channels = 1


# FROM NSLS2
# def trigger(self):
#      if self._staged != Staged.yes:
#          raise RuntimeError("not staged")

#      self._status = DeviceStatus(self)
#      self.settings.erase.put(1)
#      self._acquisition_signal.put(1, wait=False)
#      trigger_time = ttime.time()

#      for sn in self.read_attrs:
#          if sn.startswith('channel') and '.' not in sn:
#              ch = getattr(self, sn)
#              self.dispatch(ch.name, trigger_time)

#      self._abs_trigger_count += 1
#      return self._status

# class XspressTrigger(BlueskyInterface):
#     """Base class for trigger mixin classes
#     Subclasses must define a method with this signature:
#     `acquire_changed(self, value=None, old_value=None, **kwargs)`
#     """
#     # TODO **
#     # count_time = self.settings.acquire_period

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # settings
#         self._status = None
#         self._acquisition_signal = self.settings.acquire
#         self._abs_trigger_count = 0

#     def stage(self):
#         self._abs_trigger_count = 0
#         self._acquisition_signal.subscribe(self._acquire_changed)
#         return super().stage()

#     def unstage(self):
#         ret = super().unstage()
#         self._acquisition_signal.clear_sub(self._acquire_changed)
#         self._status = None
#         return ret

#     def _acquire_changed(self, value=None, old_value=None, **kwargs):
#         "This is called when the 'acquire' signal changes."
#         if self._status is None:
#             return
#         if (old_value == 1) and (value == 0):
#             # Negative-going edge means an acquisition just finished.
#             self._status._finished()

#     def trigger(self):
#         if self._staged != Staged.yes:
#             raise RuntimeError("not staged")

#         self._status = DeviceStatus(self)
#         self._acquisition_signal.put(1, wait=False)
#         trigger_time = ttime.time()

#         for sn in self.read_attrs:
#             if sn.startswith('channel') and '.' not in sn:
#                 ch = getattr(self, sn)
#                 self.dispatch(ch.name, trigger_time)

#         self._abs_trigger_count += 1
#         return self._status
