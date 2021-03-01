"""
Tracking signal for phase retarders and undulator
"""

from ..session_logs import logger
logger.info(__file__)

__all__ = ['TrackingSignal']

from ophyd import Signal


class TrackingSignal(Signal):

    def check_value(self, value):
        """
        Check if the value is a boolean.

        Raises
        ------
        ValueError
        """
        if type(value) != bool:
            raise ValueError('tracking is boolean, it can only be True or \
                False.')
