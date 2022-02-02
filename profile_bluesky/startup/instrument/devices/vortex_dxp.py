""" Vortex with DXP"""

from ophyd.mca import SaturnDXP, SaturnMCA
from ophyd import Staged, Device, Kind, Component, EpicsSignal
from ophyd.status import DeviceStatus
from ..session_logs import logger
logger.info(__file__)


class MySaturnMCA(SaturnMCA):
    check_acquiring = Component(
        EpicsSignal, 'ACQG', kind='omitted', string=False
    )


class SingleTrigger(Device):
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

    _status_type = DeviceStatus

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._acquisition_signal = self.mca.start
        self._status_signal = self.mca.check_acquiring

    def stage(self):
        self._status_signal.subscribe(self._acquire_changed)
        super().stage()

    def unstage(self):
        super().unstage()
        self._status_signal.clear_sub(self._acquire_changed)

    def trigger(self):
        "Trigger one acquisition."
        if self._staged != Staged.yes:
            raise RuntimeError("This detector is not ready to trigger."
                               "Call the stage() method before triggering.")

        self._status = self._status_type(self)
        self._acquisition_signal.put(1, wait=False)
        return self._status

    def _acquire_changed(self, value=None, old_value=None, **kwargs):
        "This is called when the 'acquire' signal changes."
        if self._status is None:
            return
        if (old_value == 1) and (value == 0):
            # Negative-going edge means an acquisition just finished.
            self._status.set_finished()
            self._status = None


class MySaturn(SingleTrigger, MySaturnMCA, SaturnDXP):

    @property
    def preset_monitor(self):
        return self.mca.preset_real_time

    def default_kinds(self):

        # TODO: This is setting A LOT of stuff as "configuration_attrs", should
        # be revised at some point.

        self.mca.configuration_attrs += [
            item for item in self.mca.component_names
        ]

        self.dxp.configuration_attrs += [
            item for item in self.dxp.component_names
        ]

        self.mca.read_attrs = [
            "preset_real_time",
            "preset_live_time",
            "elapsed_real_time",
            "elapsed_live_time",
            "rois.R0",
            "rois.R1",
        ]

        self.mca.rois.R0.count.kind = Kind.hinted
        self.mca.rois.R1.count.kind = Kind.hinted

    def default_settings(self):
        self.stage_sigs['mca.stop_signal'] = 1
        self.stage_sigs['mca.erase'] = 1
        self.stage_sigs['mca.mode'] = "Real time"
