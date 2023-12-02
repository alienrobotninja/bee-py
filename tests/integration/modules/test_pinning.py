import pytest
import requests

import bee_py
from bee_py.modules import bytes
from bee_py.modules.bzz import upload_collection, upload_file
from bee_py.modules.chunk import upload
from bee_py.modules.pinning import get_pin, pin, unpin

ERR_TIMEOUT = 40_000


test_chunk_payload = bytearray([1, 2, 3])
test_chunk_span = bytearray([len(test_chunk_payload), 0, 0, 0, 0, 0, 0, 0])
test_chunk_data = bytearray([*test_chunk_span, *test_chunk_payload])
test_chunk_hash = "ca6357a08e317d15ec560fef34e4c45f8f19f01c372aa70f1da72bfa7f1a4338"

# TODO: there is an issue with the upload function of chunk. tests are sutck


def test_pin_existing_file(bee_ky_options, random_byte_array, get_debug_postage):
    random_data = random_byte_array

    result = upload_file(bee_ky_options, random_data, get_debug_postage)
    pin(bee_ky_options, result.reference)


def test_unpin_existing_file(bee_ky_options, random_byte_array, get_debug_postage):
    random_data = random_byte_array

    result = upload_file(bee_ky_options, random_data, get_debug_postage)
    unpin(bee_ky_options, result.reference)


@pytest.mark.timeout(ERR_TIMEOUT)
def test_fail_pin_non_existing_file(bee_ky_options, invalid_reference):
    with pytest.raises(requests.exceptions.HTTPError, match="500"):
        pin(bee_ky_options, invalid_reference)


@pytest.mark.timeout(ERR_TIMEOUT)
def test_fail_unpin_non_existing_file(bee_ky_options, invalid_reference):
    with pytest.raises(requests.exceptions.HTTPError, match="404"):
        unpin(bee_ky_options, invalid_reference)


def test_pin_existing_collection(bee_ky_options, test_collection, get_debug_postage):
    result = upload_collection(bee_ky_options, test_collection, get_debug_postage)
    # * Nothing is asserted as nothing is returned, will throw error if something is wrong
    pin(bee_ky_options, result.reference)


def test_unpin_existing_collection(bee_ky_options, test_collection, get_debug_postage):
    result = upload_collection(bee_ky_options, test_collection, get_debug_postage)
    # * Nothing is asserted as nothing is returned, will throw error if something is wrong
    unpin(bee_ky_options, result.reference)


def test_pin_existing_data(bee_ky_options, random_byte_array, get_debug_postage):
    random_data = random_byte_array

    result = bytes.upload(bee_ky_options, random_data, get_debug_postage)
    pin(bee_ky_options, result.reference)


def test_unpin_existing_data(bee_ky_options, random_byte_array, get_debug_postage):
    random_data = random_byte_array

    result = bytes.upload(bee_ky_options, random_data, get_debug_postage)
    pin(bee_ky_options, result.reference)
    unpin(bee_ky_options, result.reference)


@pytest.mark.timeout(ERR_TIMEOUT)
def test_pin_non_existing_data(bee_ky_options, invalid_reference):
    with pytest.raises(requests.exceptions.HTTPError, match="500"):
        pin(bee_ky_options, invalid_reference)


@pytest.mark.timeout(ERR_TIMEOUT)
def test_unpin_non_existing_data(bee_ky_options, invalid_reference):
    with pytest.raises(requests.exceptions.HTTPError, match="404"):
        unpin(bee_ky_options, invalid_reference)


def test_pin_existing_chunk(bee_ky_options, get_debug_postage):
    chunk_reference = upload(bee_ky_options, test_chunk_data, get_debug_postage)
    assert str(chunk_reference) == test_chunk_hash

    pin(bee_ky_options, test_chunk_hash)


def test_unpin_existing_chunk(bee_ky_options, get_debug_postage):
    chunk_reference = upload(bee_ky_options, test_chunk_data, get_debug_postage)
    assert str(chunk_reference) == test_chunk_hash

    pin(bee_ky_options, test_chunk_hash)
    unpin(bee_ky_options, test_chunk_hash)


@pytest.mark.timeout(ERR_TIMEOUT)
def test_pin_non_existing_chunk(bee_ky_options, invalid_reference):
    with pytest.raises(requests.exceptions.HTTPError, match="500"):
        pin(bee_ky_options, invalid_reference)


@pytest.mark.timeout(ERR_TIMEOUT)
def test_unpin_non_existing_chunk(bee_ky_options, invalid_reference):
    with pytest.raises(requests.exceptions.HTTPError, match="404"):
        unpin(bee_ky_options, invalid_reference)


def test_return_pinning_status_of_existing_chunk(bee_ky_options, get_debug_postage):
    chunk_reference = upload(bee_ky_options, test_chunk_data, get_debug_postage)
    assert str(chunk_reference) == test_chunk_hash

    pin(bee_ky_options, test_chunk_hash)
    pinning_status = get_pin(bee_ky_options, test_chunk_hash)
    assert pinning_status.reference == test_chunk_hash


@pytest.mark.timeout(ERR_TIMEOUT)
def test_not_return_pinning_status_of_non_existing_chunk(bee_ky_options, invalid_reference):
    with pytest.raises(bee_py.Exceptions.PinNotFoundError):
        get_pin(bee_ky_options, invalid_reference)


def test_return_list_of_pinned_chunks(bee_ky_options, get_debug_postage):
    chunk_reference = upload(bee_ky_options, test_chunk_data, get_debug_postage)
    assert str(chunk_reference) == test_chunk_hash

    pin(bee_ky_options, test_chunk_hash)
