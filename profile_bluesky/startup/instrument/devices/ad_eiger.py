"""
Eiger area detector

From NSLS2:
https://github.com/NSLS-II-CHX/profile_collection/blob/master/startup/20-area-detectors.py

? Do we need to use a particular version of AD?

? Use more complex trigger?
https://github.com/bluesky/ophyd/blob/d0bc07ef85cf2d69319a059485a21a5cdbd0e677/ophyd/areadetector/trigger_mixins.py#L150
https://github.com/NSLS-II-CHX/profile_collection/blob/de6e03125a16f27f87cbce245bf355a2b783ebdc/startup/20-area-detectors.py#L24
"""


__all__ = ['eiger']

from time import time as ttime
from ophyd import EigerDetectorCam, ADComponent, DetectorBase, Staged
from ophyd.status import wait as status_wait
from ophyd.areadetector.plugins import (HDF5Plugin_V34, ImagePlugin_V34,
                                        ROIPlugin_V34, StatsPlugin_V34)
from ophyd.areadetector.trigger_mixins import TriggerBase, ADTriggerStatus
from ophyd.areadetector.filestore_mixins import (
    FileStoreIterativeWrite
)
# from ophyd.areadetector.filestore_mixins import (
#     FileStoreHDF5Single, FileStoreHDF5SingleIterativeWrite
# )
from apstools.devices import AD_EpicsHdf5FileName
from os.path import join
from ..framework import sd
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

    def stage(self):
        self._image_count.subscribe(self._acquire_changed)
        super().stage()
        # TODO: I don't like to use status_wait because it's not managed by
        # the RunEngine, but don't know how else to do this.
        status_wait(self.cam.acquire.set(1))

    def unstage(self):
        super().unstage()
        self._image_count.clear_sub(self._acquire_changed)
        status_wait(self.cam.acquire.set(0))

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
        if value > old_value:
            # There is a new image!
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

    # Save HDF5 images
    # file_plugin = LocalHDF5Plugin(
    #     suffix='HDF1:', write_path_template=image_folder
    # )
    # hdf5_plugin = HDF5Plugin(suffix='HDF1:')

    hdf5 = ADComponent(
        myHDF5FileNames,
        "HDF1:",
        write_path_template=join(EIGER_FILES_ROOT, TEST_IMAGE_DIR),
        read_path_template=join(BLUESKY_FILES_ROOT, TEST_IMAGE_DIR),
    )

    def save_images_on(self):
        self.hdf5.enable_on_stage()

    def save_images_off(self):
        self.hdf5.disable_on_stage()


eiger = LocalEigerDetector("dp_eiger_xrd92:", name="eiger")
sd.baseline.append(eiger)

# start with image saving off
eiger.save_images_off()

# Ensure standard file name
eiger.hdf5.stage_sigs["file_template"] = "%s%s_%5.5d.h5"

# This is needed otherwise .get may fail!!!
#for name in eiger.component_names:
#    if "roi" in name:
#        roi = getattr(eiger, name)
#        roi.nd_array_port.put("EIG")

eiger.cam.stage_sigs["trigger_mode"] = "Internal Enable"
eiger.cam.stage_sigs["manual_trigger"] = "Enable"
eiger.cam.stage_sigs["num_images"] = 1
# det.cam.stage_sigs["acquire_time"] = 0.1
# det.cam.stage_sigs["acquire_period"] = 0.2
 
 
# det.hdf1.stage_sigs["lazy_open"] = 1
# det.hdf1.stage_sigs["compression"] = "LZ4"
# det.hdf1.create_directory.put(-5)
# det.hdf1.stage_sigs["capture"] = 1

