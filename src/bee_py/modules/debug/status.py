from semver import Version

from bee_py.types.debug import BeeVersions, DebugStatus, Health, NodeInfo
from bee_py.types.type import BeeRequestOptions
from bee_py.utils.http import http
from bee_py.utils.logging import logger

"""
    Following lines bellow are automatically updated with GitHub Action when Bee version is updated
    so if you are changing anything about them change the `update_bee` action accordingly!
"""
SUPPORTED_BEE_VERSION_EXACT = "1.15.0-rc2-3db3dab2"
SUPPORTED_API_VERSION = "4.1.0"
SUPPORTED_DEBUG_API_VERSION = "4.1.0"
SUPPORTED_BEE_VERSION = SUPPORTED_BEE_VERSION_EXACT[: SUPPORTED_BEE_VERSION_EXACT.find("-")]

NODE_INFO_URL = "node"
STATUS_URL = "status"
HEALTH_URL = "health"
READINESS_URL = "readiness"


def get_debug_status(request_options: BeeRequestOptions) -> DebugStatus:
    """
    Retrieves debug status information from the Bee node.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.

    Returns:
        DebugStatus: The debug status information.
    """

    config = {"url": STATUS_URL, "method": "GET"}
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():  # type: ignore
            logger.error(response.raise_for_status())  # type: ignore
            return None  # type: ignore

    debug_status_response = response.json()
    return DebugStatus.model_validate(debug_status_response)


def get_health(request_options: BeeRequestOptions) -> Health:
    """
    Retrieves health information about the Bee node.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.

    Returns:
        Health: The health information of the Bee node.
    """

    config = {"url": HEALTH_URL, "method": "GET"}
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():  # type: ignore
            logger.error(response.raise_for_status())  # type: ignore
            return None  # type: ignore

    health_response = response.json()
    return Health.model_validate(health_response)


def get_readiness(request_options: BeeRequestOptions) -> bool:
    """
    Checks the readiness status of the Bee node.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.

    Returns:
        bool: True if the node is ready, False otherwise.
    """

    try:
        config = {"url": READINESS_URL, "method": "GET"}
        response = http(request_options, config)

        return response.status_code == 200  # noqa: PLR2004
    except:  # noqa: E722
        return False


def get_node_info(request_options: BeeRequestOptions) -> NodeInfo:
    """
    Retrieves information about the Bee node.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.

    Returns:
        NodeInfo: The node information.
    """

    config = {"url": NODE_INFO_URL, "method": "GET"}
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        if response.raise_for_status():  # type: ignore
            logger.error(response.raise_for_status())  # type: ignore
            return None  # type: ignore

    node_info_response = response.json()
    return NodeInfo.model_validate(node_info_response)


def is_supported_exact_version(request_options: BeeRequestOptions) -> bool:
    """
    Checks if the connected Bee node is running the exact supported version.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.

    Returns:
        bool: True if the Bee node version matches the exact supported version, False otherwise.
    """

    health_info = get_health(request_options)
    node_version = health_info.version

    return node_version == SUPPORTED_BEE_VERSION_EXACT


# TODO: Remove on break
# def is_supported_version(request_options: BeeRequestOptions) -> bool:
#     """
#     Checks if the connected Bee node is running a supported version.

#     Args:
#         request_options (BeeRequestOptions): Ky Options for making requests.

#     Returns:
#         bool: True if the Bee node version is supported, False otherwise.
#     """

#     return is_supported_exact_version(request_options)


def get_major_semver(api_version: str) -> str:
    """
    Returns the major version of the semver string.

    Args:
        api_version (str): The semver string.

    Returns:
        str: The major version.
    """
    return str(Version.parse(api_version).major)


def is_supported_main_api_version(request_options: BeeRequestOptions) -> bool:
    """
    Checks if the connected Bee node's main API version is supported.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.

    Returns:
        bool: True if the main API version is supported, False otherwise.
    """

    health_info = get_health(request_options)
    main_api_version = health_info.api_version

    # Extract major version from the API version
    main_api_version_major = get_major_semver(main_api_version)
    supported_api_version_major = get_major_semver(SUPPORTED_API_VERSION)

    return main_api_version_major == supported_api_version_major


def is_supported_debug_api_version(request_options: BeeRequestOptions) -> bool:
    """
    Checks if the connected Bee node's Debug API version is supported.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.

    Returns:
        bool: True if the Debug API version is supported, False otherwise.
    """

    health_info = get_health(request_options)
    debug_api_version = health_info.debug_api_version

    # Extract major version from the API version
    debug_api_version_major = get_major_semver(debug_api_version)
    supported_debug_api_version_major = get_major_semver(SUPPORTED_DEBUG_API_VERSION)

    return debug_api_version_major == supported_debug_api_version_major


def is_supported_api_version(request_options: BeeRequestOptions) -> bool:
    """
    Checks if the connected Bee node's Main and Debug API versions are supported.

    This is the recommended check for ensuring compatibility between your application and the Bee node.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.

    Returns:
        bool: True if both Main and Debug API versions are supported, False otherwise.
    """

    health_info = get_health(request_options)
    main_api_version = health_info.api_version
    debug_api_version = health_info.debug_api_version

    # Extract major versions from the API versions
    main_api_version_major = get_major_semver(main_api_version)
    debug_api_version_major = get_major_semver(debug_api_version)

    return main_api_version_major == get_major_semver(
        SUPPORTED_API_VERSION
    ) and debug_api_version_major == get_major_semver(SUPPORTED_DEBUG_API_VERSION)


def get_versions(request_options: BeeRequestOptions) -> BeeVersions:
    """
    Retrieves comprehensive version information for the connected Bee node.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.

    Returns:
        BeeVersions: Object containing both the Bee node's reported versions and the supported versions by bee-js.
    """

    health_info = get_health(request_options)

    node_version = health_info.version
    main_api_version = health_info.api_version
    debug_api_version = health_info.debug_api_version

    return BeeVersions(
        supported_bee_version=SUPPORTED_BEE_VERSION_EXACT,
        supported_bee_api_version=SUPPORTED_API_VERSION,
        supported_bee_debug_api_version=SUPPORTED_DEBUG_API_VERSION,
        bee_version=node_version,
        bee_api_version=main_api_version,
        bee_debug_api_version=debug_api_version,
    )
