"""
Lakeshore temperature controllers
"""

__all__ = ['lakeshore_336','lakeshore_340lt','lakeshore_340ht']

from instrument.session_logs import logger
logger.info(__file__)

from .lakeshore336 import LS336Device
from .lakeshore340 import LS340Device

lakeshore_336 = LS336Device("4idd:LS336:TC3:", name="lakeshore 360", labels=["Lakeshore"])

lakeshore_340lt = LS340Device('4idd:LS340:TC1:',name="lakeshore 340 - low temperature",
                              labels=("Lakeshore"))

lakeshore_340ht = LS340Device('4idd:LS340:TC2:',name="lakeshore 340 - high temperature",
                              labels=("Lakeshore"))

# TODO: include limits, Fix offset AttributeError
# TODO: lakeshore 340 won't show a status bar, I don't know why.
