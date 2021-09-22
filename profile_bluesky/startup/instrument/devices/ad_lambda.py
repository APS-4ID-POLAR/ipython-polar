"""
Lambda area detector
"""

from ophyd import ADComponent, EpicsSignalRO, Kind
from ophyd.areadetector import (
    CamBase, SignalWithRBV, SingleTrigger, DetectorBase
)
from ophyd.areadetector.common_plugins import HDF5Plugin_V34
from ophyd.areadetector.filestore_mixins import FileStoreHDF5IterativeWrite
from ophyd.areadetector.plugins import ROIPlugin_V34, StatsPlugin_V34
from os.path import join

LAMBDA_FILES_ROOT = "/extdisk/4idd/bluesky_images/"
BLUESKY_FILES_ROOT = "/home/beams/POLAR/data/"
TEST_IMAGE_DIR = "%Y/%m/%d/"


class Lambda250kCam(CamBase):
    """
    support for X-Spectrum Lambda 750K detector
    https://x-spectrum.de/products/lambda-350k750k/
    """
    _html_docs = ['Lambda250kCam.html']

    serial_number = ADComponent(EpicsSignalRO, 'SerialNumber_RBV')
    firmware_version = ADComponent(EpicsSignalRO, 'FirmwareVersion_RBV')

    operating_mode = ADComponent(SignalWithRBV, 'OperatingMode')
    energy_threshold = ADComponent(SignalWithRBV, 'EnergyThreshold')
    dual_threshold = ADComponent(SignalWithRBV, 'DualThreshold')


class MyHDF5Plugin(FileStoreHDF5IterativeWrite, HDF5Plugin_V34):
    pass


class Lambda250kDetector(SingleTrigger, DetectorBase):

    cam = ADComponent(Lambda250kCam, 'cam1:')
    hdf1 = ADComponent(
        MyHDF5Plugin,
        "HDF1:",
        write_path_template=join(LAMBDA_FILES_ROOT, TEST_IMAGE_DIR),
        read_path_template=join(BLUESKY_FILES_ROOT, TEST_IMAGE_DIR),
    )
    roi = ADComponent(ROIPlugin_V34, 'ROI1:')
    stats = ADComponent(StatsPlugin_V34, 'STATS1:')

    def default_kinds(self):

        # TODO: This is setting A LOT of stuff as "configuration_attrs", should
        # be revised at some point.

        # Some of the attributes return numpy arrays which Bluesky doesn't
        # accept: configuration_names, stream_hdr_appendix,
        # stream_img_appendix.
        _remove_from_config = (
            "file_number_sync",  # Removed from EPICS
            "file_number_write",  # Removed from EPICS
            "pool_max_buffers",  # Removed from EPICS
            # all below are numpy.ndarray
            "configuration_names",
            "stream_hdr_appendix",
            "stream_img_appendix",
            "dim0_sa",
            "dim1_sa",
            "dim2_sa",
            "nd_attributes_macros",
            "dimensions",
            'asyn_pipeline_config',
            'dim0_sa',
            'dim1_sa',
            'dim2_sa',
            'dimensions',
            'histogram',
            'ts_max_value',
            'ts_mean_value',
            'ts_min_value',
            'ts_net',
            'ts_sigma',
            'ts_sigma_xy',
            'ts_sigma_y',
            'ts_total',
            'ts_timestamp',
            'ts_centroid_total',
            'ts_eccentricity',
            'ts_orientation',
            'histogram_x',
        )

        self.cam.configuration_attrs += [
            item for item in Lambda250kCam.component_names if item not in
            _remove_from_config
        ]

        self.cam.read_attrs += ["num_images_counter"]

        for name in self.component_names:
            comp = getattr(self, name)
            if isinstance(comp, (ROIPlugin_V34, StatsPlugin_V34)):
                comp.configuration_attrs += [
                    item for item in comp.component_names if item not in
                    _remove_from_config
                ]
            if isinstance(comp, StatsPlugin_V34):
                comp.total.kind = Kind.hinted
                comp.read_attrs += ["max_value", "min_value"]
