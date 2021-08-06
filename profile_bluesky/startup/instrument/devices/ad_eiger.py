"""
Eiger area detector
"""

from time import time as ttime
from ophyd import (Component, ADComponent, EigerDetectorCam, DetectorBase,
                   Staged, EpicsSignal, Signal, Kind)
from ophyd.status import wait as status_wait, SubscriptionStatus
from ophyd.areadetector.plugins import ROIPlugin_V34, StatsPlugin_V34
from ophyd.areadetector.trigger_mixins import TriggerBase, ADTriggerStatus

from ophyd.utils.epics_pvs import set_and_wait
from ..session_logs import logger
logger.info(__file__)

EIGER_FILES_ROOT = "/local/home/dpuser/data2/4IDD/bluesky_test/"
BLUESKY_FILES_ROOT = "/home/beams/POLAR/bluesky_setup/images_test/"
TEST_IMAGE_DIR = "eiger/%Y/%m/%d/"


# EigerDetectorCam inherits FileBase, which contains a couple of PVs that were
# removed from AD after V22: file_number_sync, file_number_write,
# pool_max_buffers.
class LocalEigerCam(EigerDetectorCam):
    file_number_sync = None
    file_number_write = None
    pool_max_buffers = None

    wait_for_plugins = ADComponent(EpicsSignal, 'WaitForPlugins', string=True,
                                   kind='config')

    file_path = ADComponent(
            EpicsSignal, 'FilePath', string=True, kind='config'
    )

    # _default_configuration_attrs = tuple(
    #     item for item in EigerDetectorCam.component_names if item not in
    #     _REMOVE_FROM_CONFIG
    # )

    # _default_read_attrs = ("num_images_counter", )


class LocalTrigger(TriggerBase):
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

    save_images_flag = ADComponent(Signal, False, kind="omitted")

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
        set_and_wait(self.cam.acquire, 0)
        super().stage()
        # The trigger button does not track that the detector is done, so
        # the image_count is used. Not clear it's the best choice.
        self._image_count.subscribe(self._acquire_changed)
        # Only save images if the save_images_flag is on...
        if self.save_images_flag.get() in (True, 1, "on", "enable"):
            self.save_images_on()
        set_and_wait(self.cam.acquire, 1)

    def unstage(self):
        super().unstage()
        self._image_count.clear_sub(self._acquire_changed)
        set_and_wait(self.cam.acquire, 0)

        def check_value(*, old_value, value, **kwargs):
            "Return True when detector is done"
            return (value == "Ready" or value == "Acquisition aborted")

        # When stopping the detector, it may take some time processing the
        # images. This will block until it's done.
        status_wait(
            SubscriptionStatus(
                self.cam.status_message, check_value, timeout=10
            )
        )

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
        if value > old_value:  # There is a new image!
            self._status.set_finished()
            self._status = None

    def save_images_on(self):
        def check_value(*, old_value, value, **kwargs):
            "Return True when file writter is enabled"
            return value == "ready"

        self.cam.fw_enable.put("Enable")
        status_wait(
            SubscriptionStatus(self.cam.fw_state, check_value, timeout=10)
        )

    def save_images_off(self):
        def check_value(*, old_value, value, **kwargs):
            "Return True when file writter is enabled"
            return value == "disabled"

        self.cam.fw_enable.put("Disable")
        status_wait(
            SubscriptionStatus(self.cam.fw_state, check_value, timeout=10)
        )


class LocalEigerDetector(LocalTrigger, DetectorBase):

    _html_docs = ['EigerDoc.html']
    cam = Component(LocalEigerCam, 'cam1:', kind="normal")

    # ROIs
    roi1 = Component(ROIPlugin_V34, 'ROI1:', kind="config")
    roi2 = Component(ROIPlugin_V34, 'ROI2:', kind="config")
    roi3 = Component(ROIPlugin_V34, 'ROI3:', kind="config")
    roi4 = Component(ROIPlugin_V34, 'ROI4:', kind="config")

    # ROIs stats
    stats1 = Component(StatsPlugin_V34, "Stats1:", kind="normal")
    stats2 = Component(StatsPlugin_V34, "Stats2:", kind="normal")
    stats3 = Component(StatsPlugin_V34, "Stats3:", kind="normal")
    stats4 = Component(StatsPlugin_V34, "Stats4:", kind="normal")

    def align_on(self, time=0.1):
        """Start detector in alignment mode"""
        self.save_images_off()
        set_and_wait(self.cam.manual_trigger, "Disable")
        set_and_wait(self.cam.num_triggers, 1e6)
        set_and_wait(self.cam.trigger_mode, "Internal Enable")
        set_and_wait(self.cam.trigger_exposure, time)
        set_and_wait(self.cam.acquire, 1)

    def align_off(self):
        """Stop detector"""
        set_and_wait(self.cam.acquire, 0)

    def default_kinds(self):

        # TODO: This is setting A LOT of stuff as "configuration_attrs", should
        # be revised at some point.

        # Some of the attributes return numpy arrays which Bluesky doesn't
        # accept: configuration_names, stream_hdr_appendix,
        # stream_img_appendix.
        _remove_from_cam_config = (
            "file_number_sync",  # Removed
            "file_number_write",  # Removed
            "pool_max_buffers",  # Removed
            "configuration_names",  # numpy.array
            "stream_hdr_appendix",  # numpy.array
            "stream_img_appendix",  # numpy.array
        )

        self.cam.configuration_attrs += [
            item for item in EigerDetectorCam.component_names if item not in
            _remove_from_cam_config
        ]

        self.read_attrs += ["num_images_counter"]

        for name in self.component_names:
            comp = getattr(self, name)
            if isinstance(comp, (ROIPlugin_V34, StatsPlugin_V34)):
                comp.configuration_attrs += [
                    item for item in comp.component_names
                ]
            if isinstance(comp, StatsPlugin_V34):
                comp.total.kind = Kind.hinted
                comp.read_attrs += ["max_value", "min_value"]

    def default_settings(self):
        self.cam.num_triggers.put(1)
        self.cam.manual_trigger.put("Disable")
        self.cam.trigger_mode.put("Internal Enable")
        self.cam.acquire.put(0)
        self.cam.wait_for_plugins.put("Yes")
        self.cam.fw_compression.put("Enable")
        self.cam.fw_num_images_per_file.put(1)
        self.setup_manual_trigger()
        self.save_images_off()
