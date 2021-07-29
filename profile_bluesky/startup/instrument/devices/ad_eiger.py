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

from ophyd import (EigerDetector, ImagePlugin, ROIPlugin, StatsPlugin,
                   ADComponent)
from ophyd.areadetector.plugins import HDF5Plugin
from ophyd.areadetector.trigger_mixins import SingleTrigger
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

EIGER_FILES_ROOT = "CHANGE THIS"
BLUESKY_FILES_ROOT = "CHANGE THIS"
TEST_IMAGE_DIR = "test/eiger/%Y/%m/%d/"


class myHdf5EpicsIterativeWriter(
    AD_EpicsHdf5FileName,
    FileStoreIterativeWrite
):
    ...


class myHDF5FileNames(HDF5Plugin, myHdf5EpicsIterativeWriter):
    ...


class LocalEigerDetector(EigerDetector, SingleTrigger):

    # Image -- Not sure this one is needed...
    image = ADComponent(ImagePlugin, 'image1:')

    # TODO: use ROIStatNPlugin?

    # ROIs
    roi1 = ADComponent(ROIPlugin, 'ROI1:')
    roi2 = ADComponent(ROIPlugin, 'ROI2:')
    roi3 = ADComponent(ROIPlugin, 'ROI3:')
    roi4 = ADComponent(ROIPlugin, 'ROI4:')

    # ROIs stats
    stats1 = ADComponent(StatsPlugin, "Stats1:")
    stats2 = ADComponent(StatsPlugin, "Stats2:")
    stats3 = ADComponent(StatsPlugin, "Stats3:")
    stats4 = ADComponent(StatsPlugin, "Stats4:")

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
        self.file_plugin.enable_on_stage()

    def save_images_off(self):
        self.file_plugin.disable_on_stage()


eiger = LocalEigerDetector("ENTER_PV!!", name="eiger")
sd.baseline.append(eiger)

# start with image saving off
eiger.save_images_off()

# Ensure standard file name
eiger.hdf5.stage_sigs["file_template"] = "%s%s_%5.5d.h5"

# det.hdf1.create_directory.put(-5)
# det.cam.stage_sigs["image_mode"] = "Single"
# det.cam.stage_sigs["num_images"] = 1
# det.cam.stage_sigs["acquire_time"] = 0.1
# det.cam.stage_sigs["acquire_period"] = 0.105
# det.hdf1.stage_sigs["lazy_open"] = 1
# det.hdf1.stage_sigs["compression"] = "LZ4"
# del det.hdf1.stage_sigs["capture"]
# det.hdf1.stage_sigs["capture"] = 1
