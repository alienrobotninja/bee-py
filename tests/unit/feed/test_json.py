from unittest.mock import MagicMock

import pytest

from bee_py.bee import Bee
from bee_py.feed.json import get_json_data, set_json_data
from bee_py.modules.feed import fetch_latest_feed_update
from bee_py.types.type import FeedWriter, Reference
from bee_py.utils.bytes import wrap_bytes_with_helpers

test_data = [
    ("", bytes([34, 34])),
    ("hello world", bytes([34, 104, 101, 108, 108, 111, 32, 119, 111, 114, 108, 100, 34])),
    (None, bytes([110, 117, 108, 108])),
    (True, bytes([116, 114, 117, 101])),
    (10, bytes([49, 48])),
    ([], bytes([91, 93])),
    ([1, "hello", None], bytes([91, 49, 44, 34, 104, 101, 108, 108, 111, 34, 44, 110, 117, 108, 108, 93]))(
        {"hello": "world", "from": None},
        bytes(
            [
                123,
                34,
                104,
                101,
                108,
                108,
                111,
                34,
                58,
                34,
                119,
                111,
                114,
                108,
                100,
                34,
                44,
                34,
                102,
                114,
                111,
                109,
                34,
                58,
                110,
                117,
                108,
                108,
                125,
            ]
        ),
    ),
]


@pytest.mark.parametrize("data, expected_bytes", test_data)
def test_set_feed(data, expected_bytes, test_chunk_hash, feed_reference_hash, test_address):
    bee = MagicMock(spec=Bee)
    bee.upload_data.return_value = {"reference": test_chunk_hash, "tagUid": 0}

    writer = MagicMock(spec=FeedWriter)
    writer.upload.return_value = feed_reference_hash

    assert set_json_data(bee, writer, test_address, data) == feed_reference_hash
    bee.upload_data.assert_called_with(test_address, expected_bytes)


@pytest.mark.parametrize("data, expected_bytes", test_data)
def test_get_feed(data, expected_bytes):
    # Test body
    ...
