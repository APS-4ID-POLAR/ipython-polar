
"""
our diffractometer
"""

__all__ = [
    'scalerd',
    'scalerb',
    ]

from ..session_logs import logger
logger.info(__file__)

from ophyd.scaler import ScalerCH

scalerd = ScalerCH('4id:scaler1', name='scalerd', labels=('detectors','counters'))
scalerd.select_channels(None)

scalerb = ScalerCH('4idb:scaler1', name='scalerb', labels=('detectors','counters'))
scalerb.select_channels(None)

# TODO: name the other channels, watch out for python keywords such as del!
# TODO: How should we handle the scalers? What is scaler3?
