from eth_pydantic_types import HexBytes

from bee_py.chunk.bmt import bmt_hash, bmt_root_hash


def test_bmt_root_hash_empty_payload():
    payload = b""
    root_hash = bmt_root_hash(payload)
    assert root_hash.hex() == "0xffd70157e48063fc33c97a050f7f640233bf646cc98d9524c6b92bcf3ab56f83"


def test_bmt_root_hash_small_payload():
    payload = b"hello"
    root_hash = bmt_root_hash(payload)
    assert root_hash == HexBytes("0x226895c3da2556adaa58b1791c8afc4ee8812e3f14f0c196b5a1ba522e54c63e")


def test_bmt_root_hash_large_payload():
    payload = b"\x00" * 1024
    root_hash = bmt_root_hash(payload)
    assert root_hash == HexBytes("0xffd70157e48063fc33c97a050f7f640233bf646cc98d9524c6b92bcf3ab56f83")


def test_bmt_hash_chunked():
    payload = b"hello"
    span = bytes([3, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3])
    chunk_content = bytearray(span + payload)
    _bmt_hash = bmt_hash(chunk_content)
    expected_hash = "0xe5f4c5f45d2f1a848a31a5f33b5b5ec9c9c3f5208166fc994968befaae1ca863"
    assert _bmt_hash == HexBytes(expected_hash)


def test_bmt_hash():
    payload = bytes([1, 2, 3])
    span = bytes([3, 0, 0, 0, 0, 0, 0, 0])
    chunk_content = bytearray(span + payload)
    _bmt_hash = bmt_hash(chunk_content)
    expected_hash = "ca6357a08e317d15ec560fef34e4c45f8f19f01c372aa70f1da72bfa7f1a4338"
    assert _bmt_hash == HexBytes(expected_hash)
