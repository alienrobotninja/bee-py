from typing import Union

from ens.utils import is_valid_ens_name
from swarm_cid import ReferenceType, decodeCid, encodeReference

from bee_py.types.type import (
    ADDRESS_HEX_LENGTH,
    BATCH_ID_HEX_LENGTH,
    ENCRYPTED_REFERENCE_HEX_LENGTH,
    PSS_TARGET_HEX_LENGTH_MAX,
    PUBKEY_HEX_LENGTH,
    REFERENCE_HEX_LENGTH,
    TAGS_LIMIT_MAX,
    TAGS_LIMIT_MIN,
    AddressPrefix,
    AllTagsOptions,
    BatchId,
    BeeRequestOptions,
    CashoutOptions,
    CollectionUploadOptions,
    FileUploadOptions,
    NumberString,
    PostageBatchOptions,
    PssMessageHandler,
    Reference,
    ReferenceOrENS,
    Tag,
    TransactionHash,
    TransactionOptions,
    UploadOptions,
    UploadResult,
    UploadResultWithCid,
)
from bee_py.utils.error import BeeArgumentError, BeeError
from bee_py.utils.hex import assert_hex_string, is_hex_string, is_prefixed_hex_string


def assert_non_negative_integer(value: Union[int, str], name: str = "Value"):
    """
    Assert that the provided value is a non-negative integer.

    Args:
        value (Union[int, str]): The value to check.
        name (str, optional): The name of the value. Defaults to 'Value'.

    Raises:
        ValueError: If the value is not a non-negative integer.
    """
    if not isinstance(value, (int, str)):
        msg = f"{name} must be a number or a string representing a number"
        raise ValueError(msg)
    value = int(value) if isinstance(value, str) else value
    if value < 0:
        msg = f"{name} has to be bigger or equal to zero"
        raise ValueError(msg)


def make_tag_uid(tag_uid: Union[int, str, None]) -> int:
    """
    Utility function that returns Tag UID

    Args:
        tag_uid (Union[int, str, None]): The tag UID to check.

    Returns:
        int: The tag UID as an integer.

    Raises:
        TypeError: If the tag UID is not a non-negative integer.
    """
    if tag_uid is None:
        msg = "TagUid was expected but got null instead!"
        raise TypeError(msg)

    if isinstance(tag_uid, Tag):
        return tag_uid.uid
    elif isinstance(tag_uid, int):
        assert_non_negative_integer(tag_uid, "UID")
        return tag_uid
    elif isinstance(tag_uid, str):
        try:
            int_value = int(tag_uid)
            if int_value < 0:
                msg = f"TagUid was expected to be positive non-negative integer! Got {int_value}"
                raise TypeError(msg)
            return int_value
        except ValueError:
            msg = "Passed tagUid string is not valid integer!"
            raise TypeError(msg)  # noqa: B904
    msg = "tagUid has to be either Tag or a number (UID)!"
    raise TypeError(msg)


def assert_reference(value: any) -> None:
    try:
        assert_hex_string(value, REFERENCE_HEX_LENGTH)
    except TypeError:
        assert_hex_string(value, ENCRYPTED_REFERENCE_HEX_LENGTH)


def assert_reference_or_ens(value: any) -> ReferenceOrENS:
    if not isinstance(value, str):
        msg = "ReferenceOrEns has to be a string!"
        raise TypeError(msg)

    if is_hex_string(value):
        assert_reference(value)
        return

    if not is_valid_ens_name(value):
        msg = "ReferenceOrEns is not valid Reference, but also not valid ENS domain."
        raise TypeError(msg)


def make_reference_or_ens(value: any, expected_cid_type: ReferenceType) -> ReferenceOrENS:
    """
    Converts a Swarm CID or ENS name to a hex-encoded Swarm Reference.

    Args:
    value (str): The Swarm CID or ENS name.
    expected_cid_type (str): The expected type of the Swarm CID.

    Returns:
    str: The hex-encoded Swarm Reference.
    """
    if not isinstance(value, str):
        msg = "ReferenceCidOrEns has to be a string!"
        raise TypeError(msg)

    try:
        result = decodeCid(value)

        if result.type != expected_cid_type:
            msg = f'CID was expected to be of type {expected_cid_type}, but got instead {result.type if result.type else "non-Swarm CID"}'  # noqa: E501
            raise BeeError(msg)

        return result.reference
    except BeeError as e:
        raise e

    assert_reference_or_ens(value)

    return value


def add_cid_conversion_function(result: UploadResult, cid_type: ReferenceType) -> UploadResultWithCid:
    """
    Adds a getter method to the result object that converts the reference to a CID base32 encoded string.

    Args:
        result (UploadResult): The object to add the getter method to.
        cid_type (ReferenceType): The type of the CID.

    Returns:
        UploadResultWithCid
    """

    def cid():
        return encodeReference(result.reference, cid_type)

    return UploadResultWithCid(cid=cid)


def assert_upload_options():
    ...
