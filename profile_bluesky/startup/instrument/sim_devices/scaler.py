
"""
our diffractometer
"""

__all__ = [
    'scaler1',
    ]

from ..session_logs import logger
logger.info(__file__)

from ophyd.sim import det1


scaler1 = det1

# TODO: created simulated counters
