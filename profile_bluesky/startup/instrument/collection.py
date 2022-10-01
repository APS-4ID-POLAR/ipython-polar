
"""
configure for data collection in a console session
"""

from .session_logs import logger
logger.info(__file__)

# from . import mpl

logger.info("bluesky framework")

from .framework import *
from .devices import *
from .callbacks import *
from .plans import *
from .utils import *
from .mpl import *

from apstools.utils import *

from hkl.user import (
    cahkl,
    cahkl_table,
    calc_UB,
    list_samples,
    new_sample,
    or_swap,
    select_diffractometer,
    set_energy,
    setor,
    show_sample,
    show_selected_diffractometer,
    update_sample,
    wh,
    pa,
)

from hkl.util import (
    list_orientation_runs,
    restore_constraints,
    restore_energy,
    restore_orientation as hkl_restore_orientation,
    restore_reflections,
    restore_sample,
    restore_UB,
    run_orientation_info,
)

from polartools.absorption import (
    load_absorption,
    load_dichro,
    load_lockin,
    load_multi_dichro,
    load_multi_lockin,
    load_multi_xas,
    process_xmcd,
    plot_xmcd
)

from polartools.diffraction import (
    fit_peak,
    load_info,
    fit_series,
    load_series,
    get_type,
    load_mesh,
    plot_2d,
    plot_fit,
    load_axes,
    plot_data,
    dbplot,
)

from polartools.load_data import (
    db_query,
    show_meta,
    collect_meta,
    lookup_position,
)

from polartools.pressure_calibration import (
    xrd_calibrate_pressure
)

from polartools.process_images import (
   load_images,
   get_curvature,
   get_spectrum,
   get_spectra,
)

from IPython import get_ipython
from .utils.local_magics import LocalMagics
get_ipython().register_magics(LocalMagics)

qxscan_params.load_from_scan(-1)

# This is a workaround to ensure that we preserve the beamline energy and
# the previously defined UB matrix.
def restore_orientation(orientation, diffractometer):
    hkl_restore_orientation(orientation, diffractometer)
    # There is a bug in restore_UB, this is a workaround.
    # restore_UB(orientation, diffractometer)
    diffractometer.UB.put(orientation["UB"])
    diffractometer.engine.mode = orientation["_mode"]
    diffractometer.energy.put(energy.get())
