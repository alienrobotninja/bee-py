from bee_py.types.type import BeeRequestOptions, NodeAddresses, Peers, PingResponse, RemovePeerResponse, Topology
from bee_py.utils.http import http
from bee_py.utils.logging import logger

ADDRESSES_ENDPOINT = "addresses"
PEERS_ENDPOINT = "peers"
BLOCKLIST_ENDPOINT = "blocklist"
TOPOLOGY_ENDPOINT = "topology"
PING_PONG_ENDPOINT = "pingpong"


def get_node_addresses(request_options: BeeRequestOptions) -> NodeAddresses:
    """Retrieves node addresses.

    Args:
        request_options: BeeRequestOptions object containing Bee API request options.

    Returns:
        NodeAddresses object containing the node's addresses.
    """
    config = {
        "url": ADDRESSES_ENDPOINT,
        "method": "get",
    }
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        print(response.json())  # noqa: T201
        logger.error(response.raise_for_status())

    addresses_response = response.json()
    return NodeAddresses.parse_obj(addresses_response)


def get_peers(request_options: NodeAddresses) -> Peers:
    """Retrieves peers.

    Args:
        request_options: BeeRequestOptions object containing Bee API request options.

    Returns:
        List of Peer objects i.e. Peers object
    """
    config = {
        "url": PEERS_ENDPOINT,
        "method": "get",
    }
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        print(response.json())  # noqa: T201
        logger.error(response.raise_for_status())

    peers_response = response.json()
    return Peers.parse_obj(peers_response)


def get_blocklist(request_options: BeeRequestOptions) -> Peers:
    """Retrieves blocklisted peers.

    Args:
       request_options: BeeRequestOptions object containing Bee API request options.

    Returns:
       List of Peer objects.
    """
    config = {
        "url": BLOCKLIST_ENDPOINT,
        "method": "get",
    }
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        print(response.json())  # noqa: T201
        logger.error(response.raise_for_status())

    blocklist_response = response.json()
    # * Extract the 'address' field from each peer in the 'peers' list
    # peers = [Peer.parse_obj({"address": peer["address"]["address"]}) for peer in blocklist_response["peers"]]
    return Peers.parse_obj(blocklist_response)


def remove_peer(request_options: BeeRequestOptions, peer: str) -> RemovePeerResponse:
    """Removes a peer.

    Args:
    request_options: BeeRequestOptions object containing Bee API request options.
    peer: String representing the peer to be removed.

    Returns:
    RemovePeerResponse object containing the response data.
    """
    config = {"url": f"{PEERS_ENDPOINT}/{peer}", "method": "DELETE"}
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        print(response.json())  # noqa: T201
        logger.error(response.raise_for_status())

    return RemovePeerResponse.parse_obj(response.json())


def get_topology(request_options: BeeRequestOptions) -> Topology:
    """Retrieves topology.

    Args:
    request_options: BeeRequestOptions object containing Bee API request options.

    Returns:
    Topology object containing the response data.
    """
    config = {
        "url": TOPOLOGY_ENDPOINT,
        "method": "get",
    }
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        print(response.json())  # noqa: T201
    logger.error(response.raise_for_status())

    return Topology.parse_obj(response.json())


def ping_peer(request_options: BeeRequestOptions, peer: str) -> PingResponse:
    """Pings a peer and returns the response.

    Args:
    request_options: BeeRequestOptions object containing Bee API request options.
    peer: String representing the peer to ping.

    Returns:
    PingResponse object containing the response data.
    """
    config = {"url": f"{PING_PONG_ENDPOINT}/{peer}", "method": "POST"}
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        print(response.json())  # noqa: T201
        logger.error(response.raise_for_status())

    return PingResponse.parse_obj(response.json())