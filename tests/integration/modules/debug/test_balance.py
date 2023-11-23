from bee_py.modules.debug.balance import (
    get_all_balances,
    get_past_due_consumption_balances,
    get_past_due_consumption_peer_balance,
    get_peer_balance,
)


def test_get_all_balances(peer_overlay, bee_debug_ky_options):
    """
    Get the balances with all known peers including prepaid services
    """
    response = get_all_balances(bee_debug_ky_options)

    assert isinstance(response.balances, list)

    for peer_balance in response.balances:
        assert isinstance(peer_balance.peer, str)
        assert isinstance(peer_balance.balance, str)

    peer_balances = [peer_balance.peer for peer_balance in response.balances]
    assert peer_overlay in peer_balances


def test_get_peer_balance(peer_overlay, bee_debug_ky_options):
    peer_balance = get_peer_balance(bee_debug_ky_options, peer_overlay)

    assert peer_balance.peer == peer_overlay
    assert isinstance(peer_balance.balance, str)


def test_get_past_due_consumption_balances(peer_overlay, bee_debug_ky_options):
    response = get_past_due_consumption_balances(bee_debug_ky_options)

    assert isinstance(response.balances, list)
    for peer_balance in response.balances:
        assert isinstance(peer_balance.peer, str)
        assert isinstance(peer_balance.balance, str)

    peer_balances = [peer_balance.peer for peer_balance in response.balances]
    assert peer_overlay in peer_balances


def test_get_past_due_consumption_peer_balance(peer_overlay, bee_debug_ky_options):
    peer_balance = get_past_due_consumption_peer_balance(bee_debug_ky_options, peer_overlay)

    assert peer_balance.peer == peer_overlay
    assert isinstance(peer_balance.balance, str)
