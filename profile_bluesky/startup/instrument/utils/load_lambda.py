""" Loads a new lambda device """

from ..devices.ad_lambda import Lambda250kDetector
from ..session_logs import logger
logger.info(__file__)

__all__ = ['load_lambda']


def load_lambda(pv="DP_LAMBDA250K_1:"):

    print("-- Loading Lambda 250k detector --")
    lambda250k = Lambda250kDetector(pv, name="lambda250k")

    lambda250k.wait_for_connection(timeout=10)

    print("Setting up ROI and STATS defaults ...", end=" ")
    for name in lambda250k.component_names:
        if "roi" in name:
            roi = getattr(lambda250k, name)
            roi.wait_for_connection(timeout=10)
            roi.nd_array_port.put("PROC1")
        if "stats" in name:
            stat = getattr(lambda250k, name)
            stat.wait_for_connection(timeout=10)
            stat.nd_array_port.put(f"ROI{stat.port_name.get()[-1]}")
    print("Done!")

    print("Setting up defaults kinds ...", end=" ")
    lambda250k.default_kinds()
    print("Done!")
    print("Setting up default settings ...", end=" ")
    lambda250k.default_settings()
    print("Done!")
    print("All done!")
    return lambda250k
