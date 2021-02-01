"""
Lakeshore temperature controllers
"""

__all__ = ['lakeshore_336', 'lakeshore_340lt', 'lakeshore_340ht']

from .lakeshore336 import LS336Device
from .lakeshore340 import LS340Device
from ..framework import sd

from instrument.session_logs import logger
logger.info(__file__)

# Lakeshore 336
lakeshore_336 = LS336Device("4idd:LS336:TC3:", name="lakeshore336",
                            labels=("lakeshore",))
lakeshore_336.loop1.readback.kind = "normal"
lakeshore_336.loop1._auto_ranges = {'LOW': (0, 6), 'MEDIUM': (6, 20),
                                    'HIGH': (20, 305)}
lakeshore_336.loop2._auto_ranges = {'LOW': (0, 6), 'MEDIUM': (6, 20),
                                    'HIGH': (20, 305)}

# Lakeshore 340 - Low temperature
lakeshore_340lt = LS340Device('4idd:LS340:TC1:', name="lakeshore340lt",
                              labels=("lakeshore",))
lakeshore_340lt.control.readback.kind = "normal"
lakeshore_340lt._auto_ranges = {'10 mA': None, '33 mA': None,
                                '100 mA': (0, 8), '333 mA': (8, 20),
                                '1 A': (20, 305)}

# Lakeshore 340 - High temperature
lakeshore_340ht = LS340Device('4idd:LS340:TC2:', name="lakeshore340ht",
                              labels=("lakeshore",))
lakeshore_340ht.control.readback.kind = "normal"

sd.baseline.append(lakeshore_336)
sd.baseline.append(lakeshore_340ht)
sd.baseline.append(lakeshore_340lt)
