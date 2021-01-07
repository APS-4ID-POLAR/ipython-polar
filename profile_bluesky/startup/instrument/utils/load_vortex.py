from ..devices.xspress import Xspress3Vortex
from ..framework import sd
from ..session_logs import logger
logger.info(__file__)

__all__ = ['load_vortex']


class Xspress3Vortex1Ch(Xspress3Vortex):
    Ch2 = Ch3 = Ch4 = None


def load_vortex(electronic, num_channels):
    """
    Load the vortex detector.

    Parameters
    ----------
    electronic : str
        Type of electronics being used. Only accepts 'xspress3'
    num_channels : int
        Number of channels. Only accepts 1 or 4.

    Returns
    -------
    vortex : ophyd device
        Vortex device.
    """

    if electronic == 'xspress3':
        if num_channels == 1:
            vortex = Xspress3Vortex1Ch('XSP3_1Chan:', name='vortex')
        elif num_channels == 4:
            vortex = Xspress3Vortex('S4QX4:', name='vortex')
        else:
            raise ValueError('num_channels must be 1 or 4.')
    else:
        raise ValueError('electronic must be "xspress"')

    sd.baseline.append(vortex)
    return vortex
