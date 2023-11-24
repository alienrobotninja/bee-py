from bee_py.modules.debug.settlements import get_all_settlements, get_settlements


def test_all_settlements(bee_debug_ky_options):
    response = get_all_settlements(bee_debug_ky_options)

    assert isinstance(response.total_received, str)
    assert isinstance(response.total_sent, str)
    assert isinstance(response.settlements, list)

    if len(response.settlements) > 0:
        peer_settlement = response.settlements[0]

        peer_settlement_response = get_settlements(bee_debug_ky_options, peer_settlement.peer)

        assert peer_settlement_response.peer == peer_settlement.peer
        assert isinstance(peer_settlement_response.received, str)
        assert isinstance(peer_settlement_response.sent, str)
