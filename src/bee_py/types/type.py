import json
from typing import Any, Callable, Generic, Optional, TypeVar, Union

from requests import PreparedRequest, Response
from typing_extensions import TypeAlias

from bee_py.utils.hex import bytes_to_hex

Type = TypeVar("Type")
Name = TypeVar("Name")
Length = TypeVar("Length", bound=int)
T = TypeVar("T", bound=Callable)

BeeRequestOptions = dict[str, Optional[Union[str, int, dict[str, str], PreparedRequest, Response]]]


BeeRequest = dict[str, Union[str, dict[str, str], Optional[str]]]
BeeResponse = dict[str, Union[dict[str, str], int, str, BeeRequest]]


SPAN_SIZE = 8
SECTION_SIZE = 32
BRANCHES = 128
CHUNK_SIZE = SECTION_SIZE * BRANCHES

ADDRESS_HEX_LENGTH = 64
PSS_TARGET_HEX_LENGTH_MAX = 6
PUBKEY_HEX_LENGTH = 66
BATCH_ID_HEX_LENGTH = 64
REFERENCE_HEX_LENGTH = 64
ENCRYPTED_REFERENCE_HEX_LENGTH = 128
REFERENCE_BYTES_LENGTH = 32
ENCRYPTED_REFERENCE_BYTES_LENGTH = 64

# Minimal depth that can be used for creation of postage batch
STAMPS_DEPTH_MIN = 17

# Maximal depth that can be used for creation of postage batch
STAMPS_DEPTH_MAX = 255

TAGS_LIMIT_MIN = 1
TAGS_LIMIT_MAX = 1000
FEED_INDEX_HEX_LENGTH = 16


# Type aliases
BatchId: TypeAlias = str
AddressPrefix: TypeAlias = str


class BrandedType(Generic[Type, Name]):
    """A type that is branded with a name.

    Args:
        Type: The type that is being branded.
        Name: The name of the brand.
    """

    __value: Type
    __tag__: Name

    def __init__(self, value: Type, tag: Name):
        self.__value = value
        self.__tag__ = tag

    @property
    def value(self) -> Type:
        return self.__value

    @property
    def tag(self) -> Name:
        return self.__tag__


class BrandedString(Generic[Name]):
    """A branded string type.

    Args:
        Name: The name of the brand.
    """

    __value: str
    __tag__: Name

    def __init__(self, value: str, tag: Name):
        self.__value = value
        self.__tag__ = tag

    @property
    def value(self) -> str:
        return self.__value

    @property
    def tag(self) -> Name:
        return self.__tag__


class FlavoredType(Generic[Type, Name]):
    """A type that is flavored with a name.

    Args:
        Type: The type that is being flavored.
        Name: The name of the flavor.
    """

    __value: Type
    __tag__: Union[None, Name]

    def __init__(self, value: Type, tag: Union[None, Name] = None):
        self.__value = value
        self.__tag__ = tag

    @property
    def value(self) -> Type:
        return self.__value

    @property
    def tag(self) -> Union[None, Name]:
        return self.__tag__


class HexString(Generic[Length]):
    """
    A class to represent a hex string without the `0x` prefix.

    Args:
        value: The hex string without the `0x` prefix.
        length: The length of the hex string in bytes.

    Raises:
        ValueError: If the hex string does not start with the `0x` prefix or if
        the length of the hex string is not a multiple of 2.

    Properties:
        value: The hex string without the `0x` prefix.
        length: The length of the hex string in bytes.
    """

    __value: str
    __length: Length

    def __init__(self, value: str, length: Length):
        if not value.startswith("0x"):
            msg = "HexString must start with the 0x prefix"
            raise ValueError(msg)
        if len(value) != length * 2 + 2:
            msg = "HexString must have a length of 64 characters"
            raise ValueError(msg)

        self.__value = value
        self.__length = length

    @property
    def value(self) -> str:
        return self.__value

    @property
    def length(self) -> Length:
        return self.__length


class PrefixedHexString(Generic[T]):
    """
    Type for HexString with prefix.

    The main hex type used internally should be non-prefixed HexString
    and therefore this type should be used as least as possible.
    Because of that it does not contain the Length property as the variables
    should be validated and converted to HexString ASAP.

    Args:
        value: The hex string with the prefix.
    """

    __value: T

    def __init__(self, value: T):
        if not isinstance(value, str) or not value.startswith("0x"):
            msg = "PrefixedHexString must start with the 0x prefix"
            raise ValueError(msg)

        self.__value = value

    @property
    def value(self) -> T:
        return self.__value


class Data:
    """A class representing binary data with additional helper methods."""

    def __init__(self, data):
        self.data = data

    def text(self) -> str:
        """Converts the binary data using UTF-8 decoding into string.

        Returns:
          The decoded string.
        """

        return self.data.decode("utf-8")

    def hex(self) -> str:  # noqa: A003
        """Converts the binary data into hex-string.

        Returns:
          The hexadecimal string representation of the data.
        """

        return bytes_to_hex(self.data)

    def json(self) -> dict[str, Any]:
        """Converts the binary data into string which is then parsed into JSON.

        Returns:
          The decoded JSON object.
        """
        if isinstance(self.data, bytes):
            self.data = self.data.decode("utf-8")
        if "{" in self.data:
            return json.loads(self.data)

        # Split the string into a list of words
        words = self.data.split()
        # Convert the list into a dictionary
        dict_obj = {words[0]: " ".join(words[1:])}
        # Convert the dictionary to a JSON object
        json_object = json.dumps(dict_obj)

        return json.loads(json_object)


def is_object(value: Any) -> bool:
    """
    Checks if a value is an object.

    Args:
    value: The value to check.

    Returns:
    True if the value is an object, False otherwise.
    """
    return value is not None and isinstance(value, dict)


class UploadOptions:
    """Represents the options for uploading a file to Bee."""

    pin: Optional[bool]
    encrypt: Optional[bool]
    tag: Optional[int]
    deferred: Optional[bool]

    def __init__(
        self,
        pin: Optional[bool] = None,
        encrypt: Optional[bool] = None,
        tag: Optional[int] = None,
        deferred: Optional[bool] = True,  # noqa: FBT002
    ):
        self.pin = pin
        self.encrypt = encrypt
        self.tag = tag
        self.deferred = deferred


class FileHeaders:
    """Represents the headers for a file."""

    name: Optional[str]
    tag_uid: Optional[int]
    content_type: Optional[str]

    def __init__(self, name: Optional[str] = None, tag_uid: Optional[int] = None, content_type: Optional[str] = None):
        self.name = name
        self.tagUid = tag_uid
        self.contentType = content_type


class OverLayAddress:
    value: str
