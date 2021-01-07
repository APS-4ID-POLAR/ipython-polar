""" Vortex with Xspress"""

from ophyd import (EpicsSignal, EpicsSignalRO, DerivedSignal, Signal, Device,
                   Component, DynamicDeviceComponent)
from ophyd.status import SubscriptionStatus, AndStatus
from collections import OrderedDict
from ..session_logs import logger
logger.info(__file__)


# TODO: Are these correct?
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


class Xspress3ROI(Device):

    # Bin limits
    # TODO: PVS!!!!
    bin_low = Component(EpicsSignal, 'ENTER PV!!!', kind='config')
    bin_high = Component(EpicsSignal, 'ENTER PV!!!', kind='config')

    # Energy limits
    ev_low = Component(EvSignal, parent_attr='bin_low', kind='config')
    ev_high = Component(EvSignal, parent_attr='bin_high', kind='config')

    # Value
    total_rbv = Component(EpicsSignalRO, 'Total_RBV', kind='hinted')

    # Name
    name = Component(EpicsSignal, 'ENTER PV!!!', kind='config')

    # Enable
    enable_button = Component(EpicsSignal, 'ENTER PV!!!', kind='config',
                              put_complete=True)

    def enable(self):
        return self.enable_button.set(1)

    def disable(self):
        return self.enable_button.set(0)

    def clear(self):
        '''Clear and disable this ROI'''
        self.configure(0, 0, )

    def configure(self, ev_low, ev_high, enable=True):
        '''Configure the ROI with low and high eV
        Parameters
        ----------
        ev_low : int
            low electron volts for ROI
        ev_high : int
            high electron volts for ROI
        '''
        ev_low = int(ev_low)
        ev_high = int(ev_high)

        if ev_low > ev_high:
            raise ValueError('ev_low is larger than ev_high.')

        if enable is True:
            self.enable()
        else:
            self.disable()

        self.ev_high.put(ev_high)
        self.ev_low.put(ev_low)


def make_rois(rois_rng):
    defn = OrderedDict()
    for roi in rois_rng:
        attr = 'roi{:02d}'.format(roi)
        defn[attr] = (Xspress3ROI, '{}:'.format(roi))

    defn['num_rois'] = (Signal, None, dict(value=len(rois_rng)))
    # e.g., device.rois.num_rois.get() => 16
    return defn


# adapted from nslsii/detectors/xspress3.py
class Xspress3Channel(Device):

    # Make 5 ROIs
    rois = DynamicDeviceComponent(make_rois(range(1, 6)))

    @property
    def all_rois(self):
        for roi in range(1, self.rois.num_rois.get() + 1):
            yield getattr(self.rois, 'roi{:02d}'.format(roi))

    def set_roi(self, index, ev_low, ev_high, enable=True):
        '''Set specified ROI to (ev_low, ev_high)
        Parameters
        ----------
        index : int or Xspress3ROI
            The roi index or instance to set
        ev_low : int
            low eV setting
        ev_high : int
            high eV setting
        name : str, optional
            The unformatted ROI name to set. Each channel specifies its own
            `roi_name_format` and `roi_sum_name_format` in which the name
            parameter will get expanded.
        '''
        if isinstance(index, Xspress3ROI):
            roi = index
        else:
            if index <= 0:
                raise ValueError('ROI index starts from 1')
            roi = list(self.all_rois)[index - 1]

        roi.configure(ev_low, ev_high, enable=enable)


class Xspress3Vortex(Device):
    # if name == 'S4QX4:':
    #   numCh = 4
    # if name == 'XSP3_1Chan:':
    #   numCh = 1

    # Channels
    Ch1 = Component(Xspress3Channel, 'MCA1ROI:')
    Ch2 = Component(Xspress3Channel, 'MCA2ROI:')
    Ch3 = Component(Xspress3Channel, 'MCA3ROI:')
    Ch4 = Component(Xspress3Channel, 'MCA4ROI:')

    # Buttons
    Acquire_button = Component(EpicsSignal, 'det1:Acquire', trigger_value=1,
                               kind='omitted')

    Erase_button = Component(EpicsSignal, 'det1:Erase', kind='omitted')

    # State
    State = Component(EpicsSignal, 'det1:DetectorState_RBV', kind='config')

    # Config
    AcquireTime = Component(EpicsSignal, 'det1:AcquireTime', kind='config')
    NumImages = Component(EpicsSignal, 'det1:NumImages', kind='config')
    TriggerMode = Component(EpicsSignal, 'det1:TriggerMode', kind='config')

    # TriggerMode, 1:internal, 3: TTL veto only
    # AcquireMode = 'step'  #step: trigger once and read roi pvs only, frame:

    def __init__(self, prefix, *, configuration_attrs=None,
                 read_attrs=None, **kwargs):

        super().__init__(prefix, configuration_attrs=None, read_attrs=None,
                         **kwargs)

        # initialize hdf5 folers
        # set 4 or 1 xsp channels,  Xspress3Channel
        # xspCh1 = Xspress3Channel(channel_num=1)
        # xspCh2 = Xspress3Channel(channel_num=2)...
        # define number of roi
        # roi1 = Xspress3ROI(1)
        # MCA1ROI:1:Total_RBV  # channel-1, roi-1
        # MCA1ROI:2:Total_RBV  # channel-1, roi-2

    def stage(self, *args, **kwargs):  # need to separate, hdf5 saving or none.
        pass
        # if frame mode: hdf5:
        #   S4QX4:HDF1:Capture # 0/1: done/capture, this needs to be 1 before
        # acquiring to save hdf files
        #   put default det1:NumImages, det1:AcquireTime
        # else:
        #   det1:NumImages=1, det1:AcquireTime

    def unstage(self, *args, **kwargs):
        pass

    def set_roi(self, *arg):
        pass
        # make a function Edge2Emission(AbsEdge) --> returns primary emission
        # energy
        # 1st argument for roi1, 2nd for roi2...
        # 'S4QX4:MCA1ROI:1:Total_RBV'  # roi1 of channel 1
        # 'S4QX4:MCA1ROI:2:Total_RBV'  # roi1 of channel 2

    def trigger(self):

        def _check_value(*, old_value, value, **kwargs):
            """
            Check status of acquisition.

            Return True when the acquisition is complete, False otherwise.
            """
            end_states = ("Aborted", "Idle")
            return value in end_states and old_value not in end_states

        # Create status that checks the xspress state.
        state_status = SubscriptionStatus(self.Status, _check_value)

        # Click the Acquire_button
        button_status = super.trigger()

        return AndStatus(state_status, button_status)
