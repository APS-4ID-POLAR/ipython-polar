
"""
initialize the bluesky framework
"""

__all__ = [
    'RE', 'db', 'sd',
    'bec', 'peaks',
    'bp', 'bps', 'bpp',
    'summarize_plan',
    'np',
    'callback_db',
    ]

from ..session_logs import logger
logger.info(__file__)

from bluesky import RunEngine
from bluesky import SupplementalData
from bluesky.callbacks.best_effort import BestEffortCallback
from bluesky.callbacks.broker import verify_files_saved
from bluesky.magics import BlueskyMagics
from bluesky.simulators import summarize_plan
from bluesky.utils import PersistentDict
from bluesky.utils import ProgressBarManager
from bluesky.utils import ts_msg_hook
from IPython import get_ipython
from ophyd.signal import EpicsSignalBase
import databroker
import os


# convenience imports
import bluesky.plans as bp
import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp
import numpy as np


# Set up a RunEngine and use metadata-backed PersistentDict
RE = RunEngine({})
RE.md = PersistentDict(
    os.path.join(os.environ["HOME"], ".config", "Bluesky_RunEngine_md")
)

# keep track of callback subscriptions
callback_db = {}

# Set up a Broker.
db = databroker.Broker.named('mongodb_config')

# Subscribe metadatastore to documents.
# If this is removed, data is not saved to metadatastore.
callback_db['db'] = RE.subscribe(db.insert)

# Set up SupplementalData.
sd = SupplementalData()
RE.preprocessors.append(sd)

# Add a progress bar.
pbar_manager = ProgressBarManager()
RE.waiting_hook = pbar_manager

# Register bluesky IPython magics.
get_ipython().register_magics(BlueskyMagics)

# Set up the BestEffortCallback.
bec = BestEffortCallback()
callback_db['bec'] = RE.subscribe(bec)
peaks = bec.peaks  # just an alias, for less typing
bec.disable_baseline()

# At the end of every run, verify that files were saved and
# print a confirmation message.
# callback_db['post_run_verify'] = RE.subscribe(post_run(verify_files_saved), 'stop')

# Uncomment the following lines to turn on 
# verbose messages for debugging.
# ophyd.logger.setLevel(logging.DEBUG)

# diagnostics
#RE.msg_hook = ts_msg_hook

# set default timeout for all EpicsSignalBase connections & communications
EpicsSignalBase.set_default_timeout(timeout=10, connection_timeout=5)
