"""
Slitscan
"""

__all__ = ['slitscan','slitmv']

from bluesky.plans import list_scan
from bluesky.plan_stubs import mv
from numpy import linspace

def slitscan(dets,positioner,start,end,numPts,md=None):
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

    yield from list_scan(dets,motor1,motor1_pos,motor2,motor2_pos,md=md)


def slitmv(positioner,value):
    """
    Bluesky plan to move a slit positioner. This assumes that all
    motors/positioners are labeled the same way as SlitDevice.

    Parameters
    -----------
    positioner: EpicsSignal device
        Variable to scan. It will generally be [slit name].[top,bot,out,inb,vcen,hcen,vsize,hsize].

    value: float
        Target position
    """
    
    if ('vcen' in positioner.name) or ('vsize' in positioner.name):
        motor1 = positioner.parent.top
        motor2 = positioner.parent.bot
    elif ('hcen' in positioner.name) or ('hsize' in positioner.name):
        motor1 = positioner.parent.out
        motor2 = positioner.parent.inb

    if 'cen' in positioner.name:
        gap = motor1.position-motor2.position
        motor1_pos = value+gap/2.
        motor2_pos = value-gap/2.
        yield from mv(motor1,motor1_pos,motor2,motor2_pos)
    elif 'size' in positioner.name:
        center = (motor1.position+motor2.position)/2
        motor1_pos = center + value/2
        motor2_pos = center - value/2
        yield from mv(motor1,motor1_pos,motor2,motor2_pos)

    yield from mv(positioner,value)
        
    

# TODO: Add metadata!
# TODO: Change slitmv to handle moving multiple motors at the same time.
