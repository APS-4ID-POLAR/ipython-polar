from ..framework import peaks
from ..plans import mv
from ..session_logs import logger
logger.info(__file__)

__all__ = ['maxi', 'cen']


# TODO: read the positioner from hints? Would need a way to convert the name
# into the actual python object.
def cen(positioner, detector=None):

    if detector is None:
        if len(peaks['cen'].keys()) > 1:
            raise TypeError("You need to provide a detector name if more than "
                            "1 detector was plotted")
        else:
            pos = peaks['cen'][list(peaks['cen'].keys())[0]]
    else:
        pos = peaks['cen'][detector]

    if hasattr(positioner, 'position'):
        current_pos = positioner.position
    elif hasattr(positioner, 'readback'):
        current_pos = positioner.readback.get()
    else:
        current_pos = positioner.get()
    print('Moving {} from {} to {}'.format(
        positioner.name, current_pos, pos
        ))

    yield from mv(positioner, pos)


def maxi(positioner, detector=None):

    if detector is None:
        if len(peaks['cen'].keys()) > 1:
            raise TypeError("You need to provide a detector name if more than "
                            "1 detector was plotted")
        else:
            pos = peaks['max'][list(peaks['cen'].keys())[0]][0]
    else:
        pos = peaks['max'][detector][0]

    if hasattr(positioner, 'position'):
        current_pos = positioner.position
    elif hasattr(positioner, 'readback'):
        current_pos = positioner.readback.get()
    else:
        current_pos = positioner.get()
    print('Moving {} from {} to {}'.format(
        positioner.name, current_pos, pos
        ))

    yield from mv(positioner, pos)
