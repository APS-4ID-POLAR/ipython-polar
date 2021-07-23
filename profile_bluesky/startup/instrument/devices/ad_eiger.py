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

from ophyd import EigerDetector, ImagePlugin, ROIPlugin, StatsPlugin, Component
from ophyd.areadetector.plugins import HDF5Plugin
from ophyd.areadetector.trigger_mixins import SingleTrigger
# from ophyd.areadetector.filestore_mixins import (
#     FileStoreHDF5Single, FileStoreHDF5SingleIterativeWrite
# )

from ..framework import sd
from ..session_logs import logger
logger.info(__file__)

image_folder = "/tmp"  # in production, use a directory on your system


# TODO: Should one of these be used?
# class LocalHDF5Plugin(HDF5Plugin, FileStoreHDF5Single):
#     pass
#
# class LocalHDF5Plugin(HDF5Plugin, FileStoreHDF5SingleIterativeWrite):
#     pass

class LocalEigerDetector(EigerDetector, SingleTrigger):

    # Image -- Not sure this one is needed...
    image = Component(ImagePlugin, 'image1:')

    # TODO: use ROIStatNPlugin?

    # ROIs
    roi1 = Component(ROIPlugin, 'ROI1:')
    roi2 = Component(ROIPlugin, 'ROI2:')
    roi3 = Component(ROIPlugin, 'ROI3:')
    roi4 = Component(ROIPlugin, 'ROI4:')

    # ROIs stats
    stats1 = Component(StatsPlugin, "Stats1:")
    stats2 = Component(StatsPlugin, "Stats2:")
    stats3 = Component(StatsPlugin, "Stats3:")
    stats4 = Component(StatsPlugin, "Stats4:")

    # Save HDF5 images
    # file_plugin = LocalHDF5Plugin(
    #     suffix='HDF1:', write_path_template=image_folder
    # )
    file_plugin = HDF5Plugin(suffix='HDF1:')

    def save_images_on(self):
        self.file_plugin.enable_on_stage()

    def save_images_off(self):
        self.file_plugin.disable_on_stage()


eiger = LocalEigerDetector("ENTER_PV!!", name="eiger")
sd.baseline.append(eiger)

# start with image saving off
eiger.save_images_off()
