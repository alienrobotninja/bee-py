from bee_py.modules.chunk import downalod, upload


def test_store_retreive_data(bee_ky_options, get_postage_batch):
    payload = bytes[(1, 2, 3)]
    span = bytes[(len(payload), 0, 0, 0, 0, 0, 0, 0)]
    data = bytes[(span, payload)]

    reference = "ca6357a08e317d15ec560fef34e4c45f8f19f01c372aa70f1da72bfa7f1a4338"
    # the hash is hardcoded because we would need the bmt hasher otherwise
    response = upload(bee_ky_options, data, get_postage_batch)

    assert response == reference

    downaloded_data = downalod(bee_ky_options, response)

    assert downaloded_data == data
