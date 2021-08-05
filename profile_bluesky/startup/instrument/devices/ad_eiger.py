"""
Eiger area detector

From NSLS2:
https://github.com/NSLS-II-CHX/profile_collection/blob/master/startup/20-area-detectors.py

? Do we need to use a particular version of AD?

? Use more complex trigger?
https://github.com/bluesky/ophyd/blob/d0bc07ef85cf2d69319a059485a21a5cdbd0e677/ophyd/areadetector/trigger_mixins.py#L150
https://github.com/NSLS-II-CHX/profile_collection/blob/de6e03125a16f27f87cbce245bf355a2b783ebdc/startup/20-area-detectors.py#L24
"""

from time import time as ttime
from ophyd import EigerDetectorCam, ADComponent, DetectorBase, Staged
from ophyd.status import wait as status_wait, SubscriptionStatus
from ophyd.areadetector.plugins import (
        HDF5Plugin_V34, ImagePlugin_V34, ROIPlugin_V34, StatsPlugin_V34,
        NetCDFPlugin_V34, FilePlugin_V34
)
from ophyd.areadetector.trigger_mixins import TriggerBase, ADTriggerStatus
from ophyd.areadetector.filestore_mixins import (
    FileStoreIterativeWrite, FileStorePluginBase
)
# from ophyd.areadetector.filestore_mixins import (
#     FileStoreHDF5Single, FileStoreHDF5SingleIterativeWrite
# )
from apstools.devices import AD_EpicsHdf5FileName
# from os.path import 
from ..session_logs import logger
logger.info(__file__)

# TODO: Should one of these be used?
# class LocalHDF5Plugin(HDF5Plugin, FileStoreHDF5Single):
#     pass
#
# class LocalHDF5Plugin(HDF5Plugin, FileStoreHDF5SingleIterativeWrite):
#     pass
# class LocalHDF5Plugin(HDF5Plugin, AD_EpicsHdf5FileName):
#     pass
# see: https://github.com/BCDA-APS/apstools/blob/0d3a7a2ca2305bc6a5d32be1def333f14352f07e/apstools/devices.py#L2016
# Use other versions of AD?

EIGER_FILES_ROOT = "/local/home/dpuser/data2/4IDD/bluesky_test/"
BLUESKY_FILES_ROOT = "/home/beams/POLAR/bluesky_setup/images_test/"
TEST_IMAGE_DIR = "eiger/%Y/%m/%d/"

# EigerDetectorCam inherits FileBase, which contains a couple of PVs that were
# removed from AD after V22: file_number_sync, file_number_write,
# pool_max_buffers
class myEigerCam(EigerDetectorCam):
    file_number_sync = None
    file_number_write = None
    pool_max_buffers = None


class myHdf5EpicsIterativeWriter(
    AD_EpicsHdf5FileName,
    FileStoreIterativeWrite
):
    ...


class myHDF5FileNames(HDF5Plugin_V34, myHdf5EpicsIterativeWriter):
    ...

# TODO: Not sure this will work, may need to change the AD_EpicsHdf5FileName
class myNetCDFFileNames(NetCDFPlugin_V34, myHdf5EpicsIterativeWriter):
    ...


class myTrigger(TriggerBase):
    """
    This trigger mixin class takes one acquisition per trigger.
    Examples
    --------
    >>> class SimDetector(SingleTrigger):
    ...     pass
    >>> det = SimDetector('..pv..')
    # optionally, customize name of image
    >>> det = SimDetector('..pv..', image_name='fast_detector_image')
    """
    _status_type = ADTriggerStatus

    def __init__(self, *args, image_name=None, **kwargs):
        super().__init__(*args, **kwargs)
        if image_name is None:
            image_name = '_'.join([self.name, 'image'])
        self._image_name = image_name
        self._image_count = self.cam.array_counter
        self._acquisition_signal = self.cam.special_trigger_button
        
    def setup_manual_trigger(self):
        # Stage signals
        self.cam.stage_sigs["trigger_mode"] = "Internal Enable"
        self.cam.stage_sigs["manual_trigger"] = "Enable"
        self.cam.stage_sigs["num_images"] = 1
        self.cam.stage_sigs["num_exposures"] = 1
        self.cam.stage_sigs["num_triggers"] = 1e6


    def stage(self):
        # Make sure that detector is not armed.
        status_wait(self.cam.acquire.set(0))
        self._image_count.subscribe(self._acquire_changed)
        self.save_images_on()
        super().stage()
        # TODO: I don't like to use status_wait because it's not managed by
        # the RunEngine, but don't know how else to do this.
        status_wait(self.cam.acquire.set(1))
        
        def check_value(*, old_value, value, **kwargs):
            "Return True when detector is done"
            return value == "Waiting for manual triggers"
        status_wait(SubscriptionStatus(self.cam.status_message, check_value))

    def unstage(self):
        super().unstage()
        self._image_count.clear_sub(self._acquire_changed)
        status_wait(self.cam.acquire.set(0))
        
        def check_value(*, old_value, value, **kwargs):
            "Return True when detector is done"
            return (value == "Idle" or value == "Acquisition aborted")
        status_wait(SubscriptionStatus(self.cam.status_message, check_value))
        
        self.save_images_off()

    def trigger(self):
        "Trigger one acquisition."
        if self._staged != Staged.yes:
            raise RuntimeError("This detector is not ready to trigger."
                               "Call the stage() method before triggering.")

        self._status = self._status_type(self)
        self._acquisition_signal.put(1, wait=False)
        self.dispatch(self._image_name, ttime())
        return self._status

    def _acquire_changed(self, value=None, old_value=None, **kwargs):
        "This is called when the 'acquire' signal changes."
        if self._status is None:
            return
        if value > old_value: # There is a new image!
            self._status.set_finished()
            self._status = None
    
class LocalEigerDetector(myTrigger, DetectorBase):
    
    _html_docs = ['EigerDoc.html']
    cam = ADComponent(myEigerCam, 'cam1:')

    # Image -- Not sure this one is needed...
    image = ADComponent(ImagePlugin_V34, 'image1:')

    # TODO: use ROIStatNPlugin?

    # ROIs
    roi1 = ADComponent(ROIPlugin_V34, 'ROI1:')
    roi2 = ADComponent(ROIPlugin_V34, 'ROI2:')
    roi3 = ADComponent(ROIPlugin_V34, 'ROI3:')
    roi4 = ADComponent(ROIPlugin_V34, 'ROI4:')

    # ROIs stats
    stats1 = ADComponent(StatsPlugin_V34, "Stats1:")
    stats2 = ADComponent(StatsPlugin_V34, "Stats2:")
    stats3 = ADComponent(StatsPlugin_V34, "Stats3:")
    stats4 = ADComponent(StatsPlugin_V34, "Stats4:")

    def save_images_on(self):
        def check_value(*, old_value, value, **kwargs):
            "Return True when file writter is enabled"
            return value == "ready"
        
        self.cam.fw_enable.put("Enable")
        status_wait(SubscriptionStatus(self.cam.fw_state, check_value))

    def save_images_off(self):
        def check_value(*, old_value, value, **kwargs):
            "Return True when file writter is enabled"
            return value == "disabled"
        
        self.cam.fw_enable.put("Disable")
        status_wait(SubscriptionStatus(self.cam.fw_state, check_value))
