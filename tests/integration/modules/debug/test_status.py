from semver import Version

from bee_py.modules.debug.status import (
    SUPPORTED_API_VERSION,
    SUPPORTED_BEE_VERSION_EXACT,
    SUPPORTED_DEBUG_API_VERSION,
    get_health,
    get_node_info,
    get_readiness,
    get_versions,
    is_supported_api_version,
    is_supported_debug_api_version,
    is_supported_exact_version,
    is_supported_main_api_version,
)
from bee_py.types.debug import NodeInfo


def test_get_health(bee_debug_ky_options):
    health = get_health(bee_debug_ky_options)

    assert health.status == "ok"

    # Matches both versions like 0.5.3-c423a39c, 0.5.3-c423a39c-dirty and 0.5.3
    assert Version.parse(health.version)


def test_get_readiness(bee_debug_ky_options):
    is_ready = get_readiness(bee_debug_ky_options)

    assert is_ready


def test_is_supported_exact_version(bee_debug_ky_options):
    is_supported = is_supported_exact_version(bee_debug_ky_options)

    assert is_supported


def test_is_supported_main_api_version(bee_debug_ky_options):
    is_supported = is_supported_main_api_version(bee_debug_ky_options)
    assert is_supported


def test_is_supported_debug_api_version(bee_debug_ky_options):
    is_supported = is_supported_debug_api_version(bee_debug_ky_options)
    assert is_supported


def test_is_supported_api_version(bee_debug_ky_options):
    is_supported = is_supported_api_version(bee_debug_ky_options)
    assert is_supported


def test_get_node_info(bee_debug_ky_options):
    status = get_node_info(bee_debug_ky_options)

    assert isinstance(status, NodeInfo)


# def test_get_debug_status(bee_debug_ky_options):
#     debug_status = get_debug_status(bee_debug_ky_options)

#     assert isinstance(debug_status, DebugStatus)


def test_get_versions(bee_debug_ky_options):
    versions = get_versions(bee_debug_ky_options)

    assert isinstance(versions.supported_bee_version, str)
    assert isinstance(versions.supported_bee_api_version, str)
    assert isinstance(versions.supported_bee_debug_api_version, str)
    assert isinstance(versions.bee_version, str)
    assert isinstance(versions.bee_api_version, str)
    assert isinstance(versions.bee_debug_api_version, str)

    assert Version.parse(versions.bee_version)
    assert Version.parse(versions.bee_api_version)
    assert Version.parse(versions.bee_debug_api_version)
    assert Version.parse(versions.supported_bee_api_version) == SUPPORTED_API_VERSION
    assert Version.parse(versions.supported_bee_version) == SUPPORTED_BEE_VERSION_EXACT
    assert Version.parse(versions.supported_bee_debug_api_version) == SUPPORTED_DEBUG_API_VERSION
