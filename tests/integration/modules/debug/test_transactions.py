from bee_py.modules.debug.transactions import get_all_transactions


def test_get_all_transactions(bee_debug_ky_options):
    transations = get_all_transactions(bee_debug_ky_options)
    print(transations)
