""" Loads a new eiger device """

from ..devices.ad_eiger import (
        LocalEigerDetector, EIGER_FILES_ROOT, TEST_IMAGE_DIR
)
from os.path import join
from ..framework import sd
from ..session_logs import logger
logger.info(__file__)

__all__ = ['load_eiger']


def load_eiger(pv = "dp_eiger_xrd92:"):
    eiger = LocalEigerDetector("dp_eiger_xrd92:", name="eiger")
    sd.baseline.append(eiger)
    
    eiger.wait_for_connection(timeout=10)
    # This is needed otherwise .get may fail!!!
    for name in eiger.component_names:
        if "roi" in name:
            roi = getattr(eiger, name)
            roi.wait_for_connection(timeout=10)
            roi.nd_array_port.put("EIG")
        if "stats" in name:
            stat = getattr(eiger, name)
            stat.wait_for_connection(timeout=10)
            stat.nd_array_port.put(f"ROI{stat.port_name.get()[-1]}")
    
    # start with image saving off
    # eiger.save_images_off()
    
    # Default parameters
    eiger.cam.num_triggers.put(1)
    eiger.cam.manual_trigger.put("Disable")
    eiger.cam.trigger_mode.put("Internal Enable")
    eiger.cam.acquire.put(0)
    eiger.setup_manual_trigger()
#    eiger.netcdf.file_path(join(EIGER_FILES_ROOT, TEST_IMAGE_DIR))
#    eiger.netcdf.file_name.put("image")
#    eiger.netcdf.file_template.put("%s%s_%5.5.nc")
    eiger.cam.fw_compression.put("Enable")
    eiger.save_images_off()
    # eiger.cam.file_path.put(join(EIGER_FILES_ROOT, TEST_IMAGE_DIR))
    
    
    
    return eiger
