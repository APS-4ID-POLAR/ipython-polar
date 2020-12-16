# TODO: We may want to split this into DXP and xpress3?
# For xpress3, this may get a bit complicated, see for instance:
# https://github.com/NSLS-II-HXN/ipython_ophyd/blob/master/profile_collection/startup/21-xspress3.py
# https://github.com/NSLS-II-HXN/hxntools/blob/master/hxntools/detectors/
# https://github.com/NSLS-II-CHX/profile_collection/blob/master/startup/98-xspress3.py


# ...test saving
# CHX using different electronics (zebra)

from ophyd import Device, Component, EpicsSignal

class Xspress3Vortex(Device, num_ch = 4):
    #num_ch: number of channels
    Acquire_button = Component(EpicsSignal, 'det1:Acquire', trigger_value=1, kind='omitted')
    AcquireTime_button = Component(EpicsSignal, 'det1:AcquireTime', trigger_value=1, kind='omitted')                         
    Erase_button = Component(EpicsSignal, 'det1:Erase', trigger_value=1, kind='omitted')
    NumImage_button = Component(EpicsSignal, 'det1:NumImages', trigger_value=1, kind='omitted')                         
    TriggerMode_button = = Component(EpicsSignal, 'det1:TriggerMode', trigger_value=1, kind='omitted')
    #TriggerMode, 1:internal, 3: TTL veto only

    # HDF5 saving useful when NumImage is large, 
    #S4QX4:HDF1:Capture # 0/1: done/capture, this needs to be 1 before acquiring to save hdf files
    #S4QX4:HDF1:FilePath  # /home/xspress3/data
    #S4QX4:HDF1:FileName  # file prefix, "data1"
    #S4QX4:HDF1:FileTemplate  # filename format, %s%s%d.hdf5

#str1 = '%sMCA%dROI:1:Total_RBV' % (self.prefix, 1) # roi 


vortex1 = Xspress3Vortex("XSP3_1Chan:", 1)     # single channel unit
vortex4 = Xspress3Vortex("S4QX4:", 4)          # 4 channel unit
