from bee_py.modules.debug.tag import retrieve_extended_tag
from bee_py.modules.tag import create_tag


def test_retrieve_extended_tag(bee_ky_options, bee_debug_ky_options):
    tag1 = create_tag(
        bee_ky_options,
        "36b7efd913ca4cf880b8eeac5093fa27b0825906c600685b6abdd6566e6cfe8f",
    )
    tag2 = retrieve_extended_tag(bee_debug_ky_options, tag1.uid)

    assert isinstance(tag2.total, int)
    assert isinstance(tag2.split, int)
    assert isinstance(tag2.seen, int)
    assert isinstance(tag2.stored, int)
    assert isinstance(tag2.sent, int)
    assert isinstance(tag2.synced, int)
    assert isinstance(tag2.uid, int)
    assert isinstance(tag2.started_at, str)
    assert isinstance(tag2.address, str)
