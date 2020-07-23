"""
Slitscan
"""

__all__ = ['slitscan']

from bluesky.plans import list_scan

def slitscan(dets,positioner,start,end,numPts):

    # This assumes that all motors/positioners are labeled the same way as
    # SlitDevice.

    if ('Vcenter' in positioner.name) or ('Vsize' in positioner.name):
        motor1 = positioner.parent.top
        motor2 = positioner.parent.bot
    elif ('Hcenter' in positioner.name) or ('Hsize' in positioner.name):
        motor1 = positioner.parent.out
        motor2 = positioner.parent.inb
        # TODO: check this order, the gap should be motor1-motor2
    else:
        raise NameError('The positioner entered is not setup.')

    if 'center' in positioner.name:
        gap = motor1.position-motor2.position
        motor1_pos = np.linspace(start,end,numPts)+gap/2.
        motor2_pos = np.linspace(start,end,numPts)-gap/2.
    else:
        center = (motor1.position+motor2.position)/2
        motor1_pos = center + np.linspace(start,end,numPts)/2.
        motor2_pos = center - np.linspace(start,end,numPts)/2.

    dets = [positioner]+[dets]
    yield from list_scan(dets,motor1,motor1_pos,motor2,motor2_pos)
