""" Loads a new eiger device """

from ..devices.ad_eiger import LocalEigerDetector
from ..framework import sd
from ..session_logs import logger
logger.info(__file__)

__all__ = ['load_eiger']


def load_eiger(pv="dp_eiger_xrd92:"):

    print("-- Loading Eiger detector --")
    eiger = LocalEigerDetector(pv, name="eiger")
    sd.baseline.append(eiger)

    eiger.wait_for_connection(timeout=10)
    # This is needed otherwise .get may fail!!!

    print("Setting up ROI and STATS defaults ...", end=" ")
    for name in eiger.component_names:
        if "roi" in name:
            roi = getattr(eiger, name)
            roi.wait_for_connection(timeout=10)
            roi.nd_array_port.put("EIG")
        if "stats" in name:
            stat = getattr(eiger, name)
            stat.wait_for_connection(timeout=10)
            stat.nd_array_port.put(f"ROI{stat.port_name.get()[-1]}")
    print("Done!")

    print("Setting up defaults kinds ...", end=" ")
    eiger.default_kinds()
    print("Done!")
    print("Setting up default settings ...", end=" ")
    eiger.default_settings()
    print("Done!")
    print("All done!")
    return eiger
