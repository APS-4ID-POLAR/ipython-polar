from ..devices.xspress import Xspress3Vortex1Ch, Xspress3Vortex4Ch
from ..framework import sd
from ..session_logs import logger
logger.info(__file__)

__all__ = ['load_vortex']


def load_vortex(electronic, num_channels, num_rois=2):
    """
    Load the vortex detector.

    Parameters
    ----------
    electronic : str
        Type of electronics being used. Only accepts 'xspress3'
    num_channels : int
        Number of channels. Only accepts 1 or 4.
    num_rois : int
        Number of ROIs to be enabled during startup.

    Returns
    -------
    vortex : ophyd device
        Vortex device.
    """

    if electronic == 'xspress3':
        if num_channels == 1:
            vortex = Xspress3Vortex1Ch('XSP3_1Chan:', name='vortex')
        elif num_channels == 4:
            vortex = Xspress3Vortex4Ch('S4QX4:', name='vortex')
        else:
            raise ValueError('num_channels must be 1 or 4.')
        # Disable all but ROI 1 and 2
        for i in range(num_channels):
            ch = getattr(vortex, f'Ch{i+1}')
            
            for j in range(ch.rois.num_rois.get()):
                roi = getattr(ch.rois, 'roi{:02d}'.format(j+1))
                if j < num_rois:
                    roi.enable()
                else:
                    roi.disable()
    else:
        raise ValueError('electronic must be "xspress"')
        

    sd.baseline.append(vortex)
    return vortex
