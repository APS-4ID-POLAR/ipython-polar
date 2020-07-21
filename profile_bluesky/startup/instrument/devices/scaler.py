
"""
our diffractometer
"""

__all__ = [
    'scaler1',
    ]

from ..session_logs import logger
logger.info(__file__)

from ophyd.scaler import ScalerCH

scaler1 = ScalerCH('4id:scaler1', name='scaler1', labels=('detectors',))
scaler1.select_channels(None)

# TODO: name the other channels, watch out for python keywords such as del!
# TODO: How should we handle the scalers? What is scaler3?
