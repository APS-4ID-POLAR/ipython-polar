__all__ = ['setup_magnet_lakeshore','setup_diffractometer_lowT']

from ..devices import lakeshore_336,lakeshore_340lt

def setup_magnet_lakeshore():
    Tvaporizer = lakeshore_336.loop1
    Tsample = lakeshore_336.loop2

def setup_diffractometer_lowT(lakeshore = 340):
    if lakeshore == '340':
        Tcontrol = lakeshore_340lt.control
        Tsample = lakeshore_340lt.sample
    elif lakeshore == '336':
        Tcontrol = lakeshore_336.loop1
        Tsample = lakeshore_336.loop2
    else:
        raise ValueError('Lakeshore model {} is not setup.'.format(lakeshore))
