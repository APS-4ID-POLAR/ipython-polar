
"""
Shutters
"""
__all__ = ["ashutter", "bshutter", "dshutter"]

from ..framework import sd
from apstools.devices import ApsPssShutterWithStatus
from ..session_logs import logger
from ophyd import Component, EpicsSignal, FormattedComponent, EpicsSignalRO
logger.info(__file__)


class PolarShutter(ApsPssShutterWithStatus):

    open_signal = Component(EpicsSignal, "OPEN_REQUEST")
    close_signal = Component(EpicsSignal, "CLOSE_REQUEST")

    # Extra info
    user_enable = FormattedComponent(
        EpicsSignalRO, "PA:04ID:{self._hutch}_USER_KEY", kind="config"
    )
    aps_enable = FormattedComponent(
        EpicsSignalRO, "PA:04ID:{self._hutch}_APS_KEY", kind="config"
    )
    searched = FormattedComponent(
        EpicsSignalRO, "PA:04ID:{self._hutch}_SEARCHED", kind="config"
    )
    bleps = FormattedComponent(
        EpicsSignalRO, "{self._bleps_pv}", kind="config"
    )

    def __init__(self, prefix, state_pv, hutch, *args, **kwargs):

        # this is very specific to 4ID
        self._hutch = hutch
        if hutch == "A":
            self._bleps_pv = "4ideps:A_TRIP_EXISTS"
        elif hutch in ["B", "D"]:
            self._bleps_pv = f"PC:04ID:S{hutch}S_BLEPS_PERMIT"
        else:
            raise ValueError(
                f"Invalid hutch {hutch}. It must to be 'A', 'B' or 'D'"
            )
        super().__init__(prefix, state_pv, *args, **kwargs)


ashutter = PolarShutter(
    "PC:04ID:FES_", "PA:04ID:FES_PERMIT", hutch="A", name="ashutter"
)
bshutter = PolarShutter(
    "PC:04ID:SBS_", "PA:04ID:SBS_PERMIT", hutch="B", name="bshutter"
)
dshutter = PolarShutter(
    "PC:04ID:SDS_", "PA:04ID:SDS_PERMIT", hutch="D", name="dshutter"
)

sd.baseline.extend((ashutter, bshutter, dshutter))
