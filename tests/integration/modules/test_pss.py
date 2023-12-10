import pytest

from bee_py.modules.debug.connectivity import get_node_addresses, get_peers
from bee_py.modules.pss import send, subscribe

PSS_TIMEOUT = 120_000


def make_test_target(target: str) -> str:
    return target[0:2]


# ! these tests only work when there is at least one peer connected


@pytest.mark.timeout(PSS_TIMEOUT)
def test_send_pss_message(bee_ky_options, bee_debug_ky_options, get_debug_postage):
    topic = "send-pss-message"
    message = "hello"

    peers = get_peers(bee_debug_ky_options)
    assert len(peers) > 0

    target = peers[0].address
    # * Nothing is asserted as nothing is returned, will throw error if something is wrong
    send(bee_ky_options, topic, make_test_target(target), message, get_debug_postage)


# @pytest.mark.timeout(PSS_TIMEOUT)
# @pytest.mark.asyncio
# async def test_send_receive_pss_message(bee_url, bee_debug_ky_options, bee_peer_ky_options, get_peer_debug_postage):
#     topic = "send-receive-pss-message"
#     message = "hello"

#     ws = await subscribe(bee_url, topic)

#     addresses = get_node_addresses(bee_debug_ky_options)
#     target = addresses.overlay
#     send(bee_peer_ky_options, topic, make_test_target(target), message, get_peer_debug_postage)

#     received_message = await ws.recv()
#     assert received_message == message
#     ws.close()
