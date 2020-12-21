# TODO: We may want to split this into DXP and xpress3?
# For xpress3, this may get a bit complicated, see for instance:
# https://github.com/NSLS-II-HXN/ipython_ophyd/blob/master/profile_collection/startup/21-xspress3.py
# https://github.com/NSLS-II-HXN/hxntools/blob/master/hxntools/detectors/
# https://github.com/NSLS-II-CHX/profile_collection/blob/master/startup/98-xspress3.py

# 

from ophyd import Device, Component, EpicsSignal

class Xspress3Vortex(Device, num_ch = 4):
    #num_ch: number of channels
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
        # set default rois 


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

# two detectors using xspress3 ioc and hitachi vortex hardware
#vortex1 = Xspress3Vortex("XSP3_1Chan:", 1)     # single channel unit
#vortex4 = Xspress3Vortex("S4QX4:", 4)          # 4 channel unit


