# TODO: We may want to split this into DXP and xpress3?
# For xpress3, this may get a bit complicated, see for instance:
# https://github.com/NSLS-II-HXN/ipython_ophyd/blob/master/profile_collection/startup/21-xspress3.py
# https://github.com/NSLS-II-HXN/hxntools/blob/master/hxntools/detectors/
# https://github.com/NSLS-II-CHX/profile_collection/blob/master/startup/98-xspress3.py

# two detectors using xspress3 ioc and hitachi vortex hardware
#vortex1 = Xspress3Vortex('XSP3_1Chan:', name='quad_vortex')     # single channel unit
#vortex4 = Xspress3Vortex('S4QX4:', name='single_vortex')          # 4 channel unit

from ophyd import Device, Component, EpicsSignal

class Xspress3Vortex(Device):
    # if name == 'S4QX4:': 
    #   numCh = 4
    # if name == 'XSP3_1Chan:': 
    #   numCh = 1
    Acquire_button = Component(EpicsSignal, 'det1:Acquire', trigger_value=1, kind='omitted')
    AcquireTime_button = Component(EpicsSignal, 'det1:AcquireTime', trigger_value=1, kind='omitted')                         
    Erase_button = Component(EpicsSignal, 'det1:Erase', trigger_value=1, kind='omitted')
    NumImage_button = Component(EpicsSignal, 'det1:NumImages', trigger_value=1, kind='omitted')                         
    TriggerMode_button = Component(EpicsSignal, 'det1:TriggerMode', trigger_value=1, kind='omitted')
    AbsEdge = 'IrL3'  # select roi energy range, make a dict for edge:emission line...
    #TriggerMode, 1:internal, 3: TTL veto only
    AcuireMode = 'step'  #step: trigger once and read roi pvs only, frame: 
    hdf5 = Component(EpicsSignal, 'HDF5:',
        # HDF5 saving useful when NumImage is large, 
        #S4QX4:HDF1:Capture # 0/1: done/capture, this needs to be 1 before acquiring to save hdf files
        #S4QX4:HDF1:FilePath  # /home/xspress3/data
        #S4QX4:HDF1:FileName  # file prefix, "data1"
        #S4QX4:HDF1:FileTemplate  # filename format, %s%s%d.hdf5
        )


    def __init__(self, prefix, *, configuration_attrs=None, read_attrs=None,**kwargs):
        pass
        # initialize hdf5 folers
        # set 4 or 1 xsp channels,  Xspress3Channel
        # xspCh1 = Xspress3Channel(channel_num=1)
        # xspCh2 = Xspress3Channel(channel_num=2)...
        # define number of roi 
        # roi1 = Xspress3ROI(1)
        # MCA1ROI:1:Total_RBV  # channel-1, roi-1
        # MCA1ROI:2:Total_RBV  # channel-1, roi-2

    def stage(self, *args, **kwargs): # need to separate, hdf5 saving or none.
        pass
        # if frame mode: hdf5: 
        #   S4QX4:HDF1:Capture # 0/1: done/capture, this needs to be 1 before acquiring to save hdf files
        #   put default det1:NumImages, det1:AcquireTime
        # else:
        #   det1:NumImages=1, det1:AcquireTime


    def unstage(self, *args, **kwargs):
        pass


    def set_roi(self, *arg):
        pass
        # make a function Edge2Emission(AbsEdge) --> returns primary emission energy
        # 1st argument for roi1, 2nd for roi2...
        # 'S4QX4:MCA1ROI:1:Total_RBV'  # roi1 of channel 1
        # 'S4QX4:MCA1ROI:2:Total_RBV'  # roi1 of channel 2

    def trigger(self):
        pass
        # after triggering, check and return det1:DetectorState_RBV         
        # after DetectorState_RBV, update pvs

    # need to add something like below when checking status.
    def check_value(*, old_value, value, **kwargs):
        """Return True when the acquisition is complete, False otherwise."""
        end_states= ("Aborted", "Idle")
        return value in end_states and old_value not in end_states


# adapted from nslsii/detectors/xspress3.py
class Xspress3Channel(Signal):
    roi_name_format = 'Det{self.channel_num}_{roi_name}'
    roi_sum_name_format = 'Det{self.channel_num}_{roi_name}_sum'

    def __init__(self, prefix, *, channel_num=None, **kwargs):
        self.channel_num = int(channel_num)
        super().__init__(prefix, **kwargs)

    @property
    def all_rois(self):
        for roi in range(1, self.rois.num_rois.get() + 1):
            yield getattr(self.rois, 'roi{:02d}'.format(roi))

    def set_roi(self, index, ev_low, ev_high, *, name=None):
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

        roi.configure(ev_low, ev_high)
        if name is not None:
            roi_name = self.roi_name_format.format(self=self, roi_name=name)
            roi.name = roi_name
            roi.value.name = roi_name
            roi.value_sum.name = self.roi_sum_name_format.format(self=self,
                                                                 roi_name=name)

    def clear_all_rois(self):
        '''Clear all ROIs'''
        for roi in self.all_rois:
            roi.clear()

class Xspress3ROI(Signal):
    '''A configurable Xspress3 EPICS ROI'''

    # prefix: C{channel}_   MCA_ROI{self.roi_num}
    bin_low = FC(SignalWithRBV, '{self.channel.prefix}{self.bin_suffix}_LLM')
    bin_high = FC(SignalWithRBV, '{self.channel.prefix}{self.bin_suffix}_HLM')

    # derived from the bin signals, low and high electron volt settings:
    ev_low = Cpt(EvSignal, parent_attr='bin_low')
    ev_high = Cpt(EvSignal, parent_attr='bin_high')

    # C{channel}_  ROI{self.roi_num}
    value = Cpt(EpicsSignalRO, 'Value_RBV')
    value_sum = Cpt(EpicsSignalRO, 'ValueSum_RBV')

    enable = Cpt(SignalWithRBV, 'EnableCallbacks')
    # ad_plugin = Cpt(Xspress3ROISettings, '')

    @property
    def ad_root(self):
        root = self.parent
        while True:
            if not isinstance(root.parent, ADBase):
                return root
            root = root.parent

    def __init__(self, prefix, *, roi_num=0, use_sum=False,
                 read_attrs=None, configuration_attrs=None, parent=None,
                 bin_suffix=None, **kwargs):

        if read_attrs is None:
            if use_sum:
                read_attrs = ['value_sum']
            else:
                read_attrs = ['value', 'value_sum']

        if configuration_attrs is None:
            configuration_attrs = ['ev_low', 'ev_high', 'enable']

        rois = parent
        channel = rois.parent
        self._channel = channel
        self._roi_num = roi_num
        self._use_sum = use_sum
        self._ad_plugin = getattr(rois, 'ad_attr{:02d}'.format(roi_num))

        if bin_suffix is None:
            bin_suffix = 'MCA_ROI{}'.format(roi_num)

        self.bin_suffix = bin_suffix

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

    def configure(self, ev_low, ev_high):
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

        enable = 1 if ev_high > ev_low else 0
        changed = any([self.ev_high.get() != ev_high,
                       self.ev_low.get() != ev_low,
                       self.enable.get() != enable])

        if not changed:
            return

        logger.debug('Setting up EPICS ROI: name=%s ev=(%s, %s) '
                     'enable=%s prefix=%s channel=%s',
                     self.name, ev_low, ev_high, enable, self.prefix,
                     self._channel)
        if ev_high <= self.ev_low.get():
            self.ev_low.put(0)

        self.ev_high.put(ev_high)
        self.ev_low.put(ev_low)
        self.enable.put(enable)


def make_rois(rois):
    pass

