""" Loads a new eiger device """

from ..devices.ad_eiger import (
    EigerDetectorTimeTrigger, EigerDetectorImageTrigger
)
from ..framework import sd
from ..session_logs import logger
logger.info(__file__)

__all__ = ['load_eiger']


def load_eiger(
    pv="dp_eiger_xrd92:",
    trigger_type="time",
    write_image_path="/local/home/dpuser/test_gilberto/",
    read_image_path="/home/beams17/POLAR/data/gilberto/test_gilberto/"
):

    if not isinstance(trigger_type, str):
        raise TypeError("trigger_type must be either 'time' or 'image'")

    if trigger_type.lower() == "time":
        detector = EigerDetectorTimeTrigger
    elif trigger_type.lower() == "image":
        detector = EigerDetectorImageTrigger
    else:
        raise TypeError("trigger_type must be either 'time' or 'image'")

    print("-- Loading Eiger detector --")
    eiger = detector(
        pv,
        write_image_path=write_image_path,
        read_image_path=read_image_path,
        name="eiger"
    )
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
