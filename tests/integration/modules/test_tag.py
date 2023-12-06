from bee_py.modules.tag import create_tag, get_all_tags, retrieve_tag
from bee_py.types.type import Tag


def test_list_all_tags(bee_ky_options):
    # * create a tag
    create_tag(bee_ky_options)

    tags = get_all_tags(bee_ky_options)

    for tag in tags:
        assert isinstance(tag, Tag)
        assert isinstance(tag.total, int)
        assert isinstance(tag.processed, int)
        assert isinstance(tag.synced, int)
        assert isinstance(tag.uid, int)
        assert isinstance(tag.started_at, str)


def test_create_empty_tag(bee_ky_options):
    tag1 = create_tag(bee_ky_options)

    assert tag1.split == 0
    assert tag1.sent == 0
    assert tag1.synced == 0
    assert isinstance(tag1.started_at, str)
    assert isinstance(tag1.uid, int)


def test_retrieve_previously_created_empty_tag(bee_ky_options):
    # Create a tag
    created_tag = create_tag(bee_ky_options)

    # Retrieve the created tag
    retrieved_tag = retrieve_tag(bee_ky_options, created_tag.uid)

    # Check if the retrieved tag is the same as the created tag
    assert created_tag == retrieved_tag

    # Verify the tag structure
    assert isinstance(created_tag, Tag)
    assert isinstance(created_tag.total, int)
    assert isinstance(created_tag.processed, int)
    assert isinstance(created_tag.synced, int)
    assert isinstance(created_tag.uid, int)
    assert isinstance(created_tag.started_at, str)
