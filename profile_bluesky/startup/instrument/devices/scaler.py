
"""
our diffractometer
"""

__all__ = [
    'scaler1',
    'ic1',
    'ic2',
    'ic3',
    'ic4',
    'ic5',
    ]

from ..session_logs import logger
logger.info(__file__)

from ophyd.scaler import ScalerCH


scaler1 = ScalerCH('4id:scaler1', name='scaler1', labels=('detectors',))
# counter: sec = SpecCounter(mne='sec', config_line='0', name='Seconds', unit='0', chan='0', pvname=4id:scaler1.S1)
# counter: ic1 = SpecCounter(mne='ic1', config_line='1', name='IC1', unit='0', chan='1', pvname=4id:scaler1.S2)
# counter: ic2 = SpecCounter(mne='ic2', config_line='2', name='IC2', unit='0', chan='2', pvname=4id:scaler1.S3) # misc_par_2=0
# counter: ic3 = SpecCounter(mne='ic3', config_line='3', name='IC3', unit='0', chan='3', pvname=4id:scaler1.S4)
# counter: ic5 = SpecCounter(mne='ic5', config_line='5', name='IC5', unit='0', chan='5', pvname=4id:scaler1.S6)
# counter: cyber8c = SpecCounter(mne='cyber8c', config_line='6', name='Cyber8C', unit='0', chan='6', pvname=4id:scaler1.S7)
# counter: cyberm = SpecCounter(mne='cyberm', config_line='7', name='CyberMag', unit='0', chan='7', pvname=4id:scaler1.S8)
# counter: yapicr = SpecCounter(mne='yapicr', config_line='8', name='AP/ICR', unit='0', chan='8', pvname=4id:scaler1.S9)
# counter: apd = SpecCounter(mne='apd', config_line='9', name='APD', unit='0', chan='9', pvname=4id:scaler1.S10)
# counter: sca1 = SpecCounter(mne='sca1', config_line='10', name='Sca1', unit='0', chan='10', pvname=4id:scaler1.S11)
# counter: sca2 = SpecCounter(mne='sca2', config_line='11', name='SCA2', unit='0', chan='11', pvname=4id:scaler1.S12)
# counter: photo = SpecCounter(mne='photo', config_line='12', name='PhotoDiode', unit='0', chan='12', pvname=4id:scaler1.S13)
# counter: ldc = SpecCounter(mne='ldc', config_line='13', name='Lock DC', unit='0', chan='13', pvname=4id:scaler1.S14)
# counter: lac = SpecCounter(mne='lac', config_line='14', name='Lock AC', unit='0', chan='14', pvname=4id:scaler1.S15)
# counter: lacoff = SpecCounter(mne='lacoff', config_line='15', name='Lock ACoff', unit='0', chan='15', pvname=4id:scaler1.S16)

ic1 = scaler1.channels.chan02
ic2 = scaler1.channels.chan03
ic3 = scaler1.channels.chan04
ic4 = scaler1.channels.chan05
ic5 = scaler1.channels.chan06
# TODO: name the other channels, watch out for python keywords such as del!
