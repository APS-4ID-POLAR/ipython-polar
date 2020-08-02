"""
Slitscan
"""

__all__ = ['slitscan']

from bluesky.plans import list_scan
from numpy import linspace

def slitscan(dets,positioner,start,end,numPts):
    """
    Bluesky plan to perform a slit scan using vcen or hcen. This assumes that all
    motors/positioners are labeled the same way as SlitDevice.

    Parameters
    -----------
    dets: list
        Detectors to be read.

    positioner: EpicsSignal device
        Variable to scan. It will generally be [slit name].[vcen,hcen,vsize,hsize].

    start: float
        Initial position of scan.

    end: float
        Final position of scan.

    numPts: integer
        Number of points.
    """

    if ('vcen' in positioner.name) or ('vsize' in positioner.name):
        motor1 = positioner.parent.top
        motor2 = positioner.parent.bot
    elif ('hcen' in positioner.name) or ('hsize' in positioner.name):
        motor1 = positioner.parent.out
        motor2 = positioner.parent.inb
    else:
        raise NameError('The positioner entered is not setup.')

    if 'cen' in positioner.name:
        gap = motor1.position-motor2.position
        motor1_pos = linspace(start,end,numPts)+gap/2.
        motor2_pos = linspace(start,end,numPts)-gap/2.
    else:
        center = (motor1.position+motor2.position)/2
        motor1_pos = center + linspace(start,end,numPts)/2.
        motor2_pos = center - linspace(start,end,numPts)/2.

    dets = [positioner]+dets

    yield from list_scan(dets,motor1,motor1_pos,motor2,motor2_pos)


# TODO: Add metadata!
