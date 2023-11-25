from bee_py.types.debug import DebugStatus, Health, NodeInfo
from bee_py.types.type import BeeRequestOptions
from bee_py.utils.http import http
from bee_py.utils.logging import logger

"""
    Following lines bellow are automatically updated with GitHub Action when Bee version is updated
    so if you are changing anything about them change the `update_bee` action accordingly!
"""
SUPPORTED_BEE_VERSION_EXACT = "1.13.0-f1067884"
SUPPORTED_API_VERSION = "4.0.0"
SUPPORTED_DEBUG_API_VERSION = "4.0.0"
SUPPORTED_BEE_VERSION = SUPPORTED_BEE_VERSION_EXACT[: SUPPORTED_BEE_VERSION_EXACT.find("-")]

NODE_INFO_URL = "node"
STATUS_URL = "status"
HEALTH_URL = "health"
READINESS_URL = "readiness"
