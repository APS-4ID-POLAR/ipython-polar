"""
Beamline energy
"""
__all__ = ['energy']

from ophyd import Signal
from ophyd.status import AndStatus, wait as status_wait
from ..framework import sd
from .monochromator import mono
from .aps_source import undulator
from .phaseplates import pr1, pr2, pr3

from ..session_logs import logger
logger.info(__file__)


class EnergySignal(Signal):

    """
    Beamline energy.

    Here it is setup so that the monochromator is the beamline energy, but note
    that this can be changed.
    """
    # Uses the mono as the standard beamline energy.
    def get(self, **kwargs):
        return mono.energy.get(**kwargs)

    def set(self, position, *, wait=True, timeout=None, settle_time=None,
            move_cb=None):

        # Mono
        status = mono.energy.set(position, timeout=timeout,
                                 settle_time=settle_time)

        # Undulator
        if undulator.downstream.tracking.get():
            und_status = undulator.downstream.energy.move(
                position, wait=wait, timeout=timeout, move_cb=move_cb
                )
            status = AndStatus(status, und_status)

        # Phase retarders
        for pr in [pr1, pr2, pr3]:
            if pr.tracking.get():
                pr_status = pr.energy.move(
                    position, wait=wait, timeout=timeout, move_cb=move_cb
                    )
                status = AndStatus(status, pr_status)

        if wait:
            status_wait(status)

        return status


energy = EnergySignal(name='energy', value=10, kind='hinted')
sd.baseline.append(energy)
