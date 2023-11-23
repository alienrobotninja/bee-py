import re

from dateutil import parser
from eth_utils import is_hex

from bee_py.modules.debug.connectivity import (
    get_blocklist,
    get_node_addresses,
    get_peers,
    get_topology,
    ping_peer,
    remove_peer,
)
from bee_py.types.type import NodeAddresses, Peers


def test_get_peers(bee_debug_ky_options):
    peers = get_peers(bee_debug_ky_options)

    assert isinstance(peers, Peers)
    assert len(peers) > 0

    # don't want index 0
    for i in range(1, len(peers)):
        assert peers[i].address, "Peer should have an address"
        assert is_hex(peers[i].address), "Peer address should be hex"


def test_get_blocklist(bee_debug_ky_options):
    peers = get_blocklist(bee_debug_ky_options)
    assert isinstance(peers, Peers)

    # don't want index 0
    for i in range(1, len(peers)):
        assert peers[i].address, "Peer should have an address"
        assert is_hex(peers[i].address), "Peer address should be hex"


def test_get_topology(bee_debug_ky_options):
    topology = get_topology(bee_debug_ky_options)

    # Check if baseAddr is a valid hexadecimal string
    assert is_hex(topology.base_address), "baseAddr should be a 64 character hexadecimal string"

    # Check if population, connected, nnLowWatermark, and depth are at least 0
    assert topology.population >= 0, "population should be at least 0"
    assert topology.connected >= 0, "connected should be at least 0"
    assert topology.nn_low_watermark >= 0, "nnLowWatermark should be at least 0"
    assert topology.depth >= 0, "depth should be at least 0"

    # Check if timestamp is a valid date
    assert not isinstance(parser.parse(topology.timestamp), ValueError), "timestamp should be a valid date"

    # Check if bins are valid
    for i in range(16):
        _bin = topology.bins[f"bin_{i}"]
        assert _bin.population >= 0, "population should be at least 0"
        assert _bin.connected >= 0, "connected should be at least 0"
        assert (
            isinstance(_bin.disconnected_peers, list) or _bin.disconnected_peers is None
        ), "disconnected_peers should be a list or None"
        assert (
            isinstance(_bin.connected_peers, list) or _bin.connected_peers is None
        ), "connected_peers should be a list or None"


def test_get_node_address(bee_debug_ky_options):
    addresses = get_node_addresses(bee_debug_ky_options)
    assert (
        is_hex(addresses.overlay) and len(addresses.overlay) == 64
    ), "overlay should be a 64 character hexadecimal string"

    assert isinstance(addresses, NodeAddresses)
    assert (
        # 42 with 0x prefix
        is_hex(addresses.ethereum)
        and len(addresses.ethereum[2:]) == 40
    ), "ethereum should a 40 character hexadecimal string"
    assert (
        is_hex(addresses.public_key) and len(addresses.public_key) == 66
    ), "ethereum should a 66 character hexadecimal string"
    assert (
        is_hex(addresses.pss_public_key) and len(addresses.pss_public_key) == 66
    ), "ethereum should a 66 character hexadecimal string"


def test_ping_peer(bee_debug_ky_options):
    peers = get_peers(bee_debug_ky_options)
    res = ping_peer(bee_debug_ky_options, peers[0].address)

    assert re.match(r"^\d+(\.\d+)?[mnpµ]?s$", res.rtt)


def test_remove_peer(bee_debug_ky_options):
    peers = get_peers(bee_debug_ky_options)
    response = remove_peer(bee_debug_ky_options, peers[0].address)

    assert response.message
