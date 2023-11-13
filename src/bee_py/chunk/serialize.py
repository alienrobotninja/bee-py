import pickle


def serialize_bytes(*arrays: bytes) -> list:
    """
    Serializes a byte array using pickle.

    Args:
    array: The byte array to serialize.

    Returns:
    A byte array containing the serialized data.
    """
    serialized_data = pickle.dumps(arrays)
    return serialized_data
