"""
Lakeshore temperature controllers
"""

__all__ = ['lakeshore_336', 'lakeshore_340lt', 'lakeshore_340ht']

from instrument.session_logs import logger
logger.info(__file__)

from .lakeshore336 import LS336Device
from .lakeshore340 import LS340Device
from ..framework import sd


lakeshore_336 = LS336Device("4idd:LS336:TC3:", name="lakeshore 336",
                            labels=("lakeshore",))

lakeshore_340lt = LS340Device('4idd:LS340:TC1:', name="lakeshore340lt",
                              labels=("lakeshore",))

lakeshore_340ht = LS340Device('4idd:LS340:TC2:', name="lakeshore340ht",
                              labels=("lakeshore",))

sd.baseline.append(lakeshore_336)
sd.baseline.append(lakeshore_340ht)
sd.baseline.append(lakeshore_340lt)
