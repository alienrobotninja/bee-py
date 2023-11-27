import json
from abc import abstractmethod
from enum import Enum
from typing import Annotated, Any, Generic, NewType, Optional, TypeVar, Union

from ape.managers.accounts import AccountAPI
from ape.types import AddressType
from pydantic import BaseModel, Field
from requests import PreparedRequest, Response
from typing_extensions import TypeAlias

from bee_py.utils.hex import bytes_to_hex

# Befine all the types here

Type = TypeVar("Type")
Name = TypeVar("Name")
Length = TypeVar("Length", bound=int)
T: TypeAlias = str

BeeRequestOptions = dict[str, Optional[Union[str, int, dict[str, str], PreparedRequest, Response]]]


BeeRequest = dict[str, Union[str, dict[str, str], Optional[str]]]
BeeResponse = dict[str, Union[dict[str, str], int, str, BeeRequest]]
NumberString = Annotated[str, "NumberString"]

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

SIGNATURE_HEX_LENGTH = 130
SIGNATURE_BYTES_LENGTH = 65

# Minimal depth that can be used for creation of postage batch
STAMPS_DEPTH_MIN = 17

# Maximal depth that can be used for creation of postage batch
STAMPS_DEPTH_MAX = 255

TAGS_LIMIT_MIN = 1
TAGS_LIMIT_MAX = 1000
FEED_INDEX_HEX_LENGTH = 16

TOPIC_BYTES_LENGTH = 32
TOPIC_HEX_LENGTH = 64

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


class PrefixedHexString:
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


class FileHeaders(BaseModel):
    """Represents the headers for a file."""

    name: Optional[str]
    tag_uid: Optional[int]
    content_type: Optional[str]


class OverLayAddress:
    value: str


class Reference:
    """
    Represents a reference that can be either a non-encrypted reference, which is a hex string of length 64,
    or an encrypted reference, which is a hex string of length 128.
    """

    def __init__(self, value):
        self._validate(value)
        self._value = value

    def _validate(self, value):
        if len(value) not in (REFERENCE_HEX_LENGTH, ENCRYPTED_REFERENCE_HEX_LENGTH) or not all(
            c in "0123456789abcdefABCDEF" for c in value
        ):
            msg = "Reference must be a hex string of length 64 or 128"
            raise ValueError(msg)

    def __str__(self):
        return self._value


class ReferenceResponse:
    """Represents a response containing a reference."""

    def __init__(self, reference: Reference):
        """Initializes the ReferenceResponse with the provided reference."""
        self.reference = reference

    @property
    def reference(self) -> Reference:
        """The reference associated with the response."""
        return self._reference

    @reference.setter
    def reference(self, reference: Reference):
        self._reference = reference

    def __str__(self):
        return f"ReferenceResponse(reference={self.reference})"


class Topic:
    def __init__(self, value: str):
        self._validate(value)
        self._value = value

    def _validate(self, value: str):
        if len(value) != self.TOPIC_HEX_LENGTH or not all(c in "0123456789abcdefABCDEF" for c in value):
            msg = f"Topic must be a hex string of length {self.TOPIC_HEX_LENGTH}"
            raise ValueError(msg)

    def __str__(self):
        return self._value


ReferenceOrENS = Union[Reference, str]


def assert_address(value: Any):
    """
    Asserts the value is an Ethereum address.

    Args:
        value: The value to assert.

    Raises:
        ValueError: If the value is not an Ethereum address.
    """
    if not isinstance(value, str) or len(value) != ADDRESS_HEX_LENGTH or not value.startswith("0x"):
        msg = "Value is not an Ethereum address!"
        raise ValueError(msg)


class BeeGenericResponse:
    """Represents a generic response from the Bee API.

    Attributes:
        message: The human-readable message associated with the response.
        code: The numerical code associated with the response.
    """

    def __init__(self, message: str, code: int):
        self.message = message
        self.code = code


class PeerBalance(BaseModel):
    """Represents a peer's balance information."""

    peer: str
    balance: str


class BalanceResponse(BaseModel):
    """Represents a response containing a list of peer balances."""

    balances: list[PeerBalance]


class NodeAddresses(BaseModel):
    overlay: str
    underlay: list[str]
    ethereum: str
    public_key: str = Field(..., alias="publicKey")
    pss_public_key: str = Field(..., alias="pssPublicKey")


class Peer(BaseModel):
    address: str

    def __str__(self):
        return self.address


class Peers(BaseModel):
    peers: list[Peer]

    def __len__(self) -> int:
        return len(self.peers)

    # def __iter__(self):
    #     yield from self.peers

    def __getitem__(self, index):
        return self.peers[index]


class PingResponse(BaseModel):
    rtt: str


class RemovePeerResponse(BaseModel):
    message: str
    code: int


# * Pydantic Field info: https://docs.pydantic.dev/latest/concepts/fields/


class Bin(BaseModel):
    population: int
    connected: int
    disconnected_peers: Optional[list[Peer]] = Field(None, alias="disconnectedPeers")
    connected_peers: Optional[list[Peer]] = Field(None, alias="connectedPeers")


class Topology(BaseModel):
    base_address: str = Field(..., alias="baseAddr")
    population: int
    connected: int
    timestamp: str
    nn_low_watermark: int = Field(..., alias="nnLowWatermark")
    depth: int
    reachability: str
    network_availability: str = Field(..., alias="networkAvailability")
    bins: dict[str, Bin]


class Settlements(BaseModel):
    peer: str
    received: str
    sent: str


class AllSettlements(BaseModel):
    total_received: str = Field(..., alias="totalReceived")
    total_sent: str = Field(..., alias="totalSent")
    settlements: list[Settlements]


class RedistributionState(BaseModel):
    minimum_gas_funds: str = Field(..., alias="minimumGasFunds")
    has_sufficient_funds: bool = Field(..., alias="hasSufficientFunds")
    is_frozen: bool = Field(..., alias="isFrozen")
    is_fully_synced: bool = Field(..., alias="isFullySynced")
    phase: str
    round_: int
    last_won_round: int = Field(..., alias="lastWonRound")
    last_played_round: int = Field(..., alias="lastPlayedRound")
    last_frozen_round: int = Field(..., alias="lastFrozenRound")
    last_selected_round: int = Field(..., alias="lastSelectedRound")
    last_sample_duration: str = Field(..., alias="lastSampleDuration")
    block: int
    reward: str
    fees: str


class TransactionOptions(BaseModel):
    gas_price: str = Field(..., alias="gasPrice")
    gas_limit: str = Field(..., alias="gasLimit")


class GetStake(BaseModel):
    staked_amount: str = Field(..., alias="stakedAmount")


class ChequebookAddressResponse(BaseModel):
    chequebook_address: str = Field(..., alias="chequebookAddress")


class ChequebookBalanceResponse(BaseModel):
    total_balance: str = Field(..., alias="totalBalance")
    available_balance: str = Field(..., alias="availableBalance")


class Cheque(BaseModel):
    beneficiary: str
    chequebook: str
    payout: str


class CashoutResult(BaseModel):
    recipient: str
    last_payout: str = Field(..., alias="lastPayout")
    bounced: bool


class LastCashoutActionResponse(BaseModel):
    peer: str
    uncashed_amount: str = Field(..., alias="uncashedAmount")
    transaction_hash: Optional[str] = Field(..., alias="transactionHash")
    last_cashed_cheque: Optional[Cheque] = Field(..., alias="lastCashedCheque")
    result: Optional[CashoutResult]


class LastChequesForPeerResponse(BaseModel):
    peer: str
    last_received: Cheque = Field(..., alias="lastreceived")
    last_sent: Cheque = Field(..., alias="lastsent")


class LastChequesResponse(BaseModel):
    lastcheques: list[LastChequesForPeerResponse]


TransactionHash = NewType("TransactionHash", str)


class TransactionHashModel(BaseModel):
    transaction_hash: TransactionHash


class TransactionResponse(BaseModel):
    transaction_hash: TransactionHash = Field(..., alias="transactionHash")


class PostageBatch(BaseModel):
    batch_id: str = Field(..., alias="batchID")
    utilization: int
    usable: bool
    label: str
    depth: int
    amount: str
    bucket_depth: int = Field(..., alias="bucketDepth")
    block_number: int = Field(..., alias="blockNumber")
    immutable_flag: bool = Field(..., alias="immutableFlag")
    batch_ttl: int = Field(..., alias="batchTTL")
    exists: bool


class BatchBucket(BaseModel):
    bucket_id: int = Field(..., alias="bucketID")
    collisions: int


class PostageBatchBuckets(BaseModel):
    depth: int
    bucket_depth: int = Field(..., alias="bucketDepth")
    bucket_upper_bound: int = Field(..., alias="bucketUpperBound")
    buckets: Optional[list[BatchBucket]]


class PostageBatchOptions(BaseModel):
    label: Optional[str]
    gas_price: Optional[str] = Field(None, alias="gasPrice")
    immutable_flag: Optional[bool]
    wait_for_usable: Optional[bool] = Field(True, alias="waitForUsable")
    wait_for_usable_timeout: Optional[int] = Field(120, alias="waitForUsableTimeout")


class StampResponse(BaseModel):
    batch_id: str = Field(..., alias="batchID")


class GetAllStampsResponse(BaseModel):
    stamps: list[PostageBatch]


class ChainState(BaseModel):
    block: int
    total_amount: str = Field(..., alias="totalAmount")
    current_price: str = Field(..., alias="currentPrice")


class ReserveState(BaseModel):
    radius: int
    commitment: int
    storage_radius: int = Field(..., alias="storageRadius")


# * @deprecate
class WalletBalanceOLD(BaseModel):
    bzz: str = Field(..., alias="bzz")
    contract_address: str = Field(..., alias="contractAddress")
    x_dai: str = Field(..., alias="xDai")


class WalletBalance(BaseModel):
    bzz_balance: str = Field(..., alias="bzzBalance")
    native_token_balance: str = Field(..., alias="nativeTokenBalance")
    chain_id: int = Field(..., alias="chainID")
    chequebook_contract_address: str = Field(..., alias="chequebookContractAddress")
    wallet_address: str = Field(..., alias="walletAddress")


class ExtendedTag(BaseModel):
    total: int
    split: int
    seen: int
    stored: int
    sent: int
    synced: int
    uid: int
    address: str
    started_at: str = Field(..., alias="startedAt")


class Tag(BaseModel):
    split: int = 0
    seen: int = 0
    stored: int = 0
    sent: int = 0
    synced: int = 0
    uid: int
    started_at: str = Field(..., alias="startedAt")


class TransactionInfo(BaseModel):
    transaction_hash: str = Field(..., alias="transactionHash")
    to: AddressType
    nonce: int
    gas_price: str = Field(..., alias="gasPrice")
    gas_limit: int = Field(..., alias="gasLimit")
    data: str
    created: str
    description: str
    value: str


class PendingTransactionsResponse(BaseModel):
    pending_transactions: list[TransactionInfo] = Field(..., alias="pendingTransactions")


class FeedType(Enum):
    """
    Enum class for feed types.

    Attributes:
        SEQUENCE: Sequential feed type.
        EPOCH: Epoch feed type.
    """

    SEQUENCE = "sequence"
    EPOCH = "epoch"


class FeedUpdateOptions:
    """
    Options for updating a feed.
    """

    def __init__(self, at: Optional[int] = None, _type: Optional[FeedType] = "sequence", index: Optional[str] = None):
        """
        Constructor for FeedUpdateOptions.

        :param at: The start date as a Unix timestamp.
        :type at: Optional[int]
        :param type: The type of the feed (default: 'sequence').
        :_type type: Optional[FeedType]
        :param index: Fetch a specific previous feed's update (default fetches the latest update).
        :type index: Optional[str]
        """
        self.at = at
        self.type = _type
        self.index = index


class FeedReader(BaseModel):
    Type: FeedType
    owner: str
    topic: str

    @abstractmethod
    def download(self, options: Optional[FeedUpdateOptions] = None):
        pass


class FeedUploadOptions(UploadOptions, FeedUpdateOptions):
    pass


class FeedWriter(FeedReader):
    @abstractmethod
    def upload(
        self,
        postage_batch_id: Union[str, BatchId],
        reference: Union[bytes, Reference],
        options: Optional[FeedUploadOptions] = None,
    ) -> Reference:
        pass


class JsonFeedOptions(BaseModel):
    address: Optional[AddressType] = None
    signer: Optional[Union[AccountAPI, str]] = None
    Type: Optional[FeedType] = None


class UploadResult(BaseModel):
    reference: Reference
    tag_uid: Optional[int] = None

    class Config:
        arbitrary_types_allowed = True


class UploadOptions(BaseModel):
    pin: Optional[bool] = False
    encrypt: Optional[bool] = False
    tag: Optional[int] = None
    deferred: Optional[bool] = True


class FileUploadOptions(UploadOptions):
    size: Optional[int] = None
    content_type: Optional[str] = Field(None, alias="contentType")


class CollectionEntry(BaseModel):
    data: T
    path: str


class Collection(BaseModel):
    entries: list[CollectionEntry]


class CollectionUploadOptions(UploadOptions):
    index_document: Optional[str] = Field(None, alias="indexDocument")
    error_document: Optional[str] = Field(None, alias="errorDocument")


class FileData(FileHeaders, BaseModel):
    headers: FileHeaders
    data: T


class UploadHeaders(BaseModel):
    swarm_pin: Optional[str] = None
    swarm_encrypt: Optional[str] = None
    swarm_tag: Optional[str] = None
    swarm_postage_batch_id: Optional[str] = None


class FileUploadHeaders(UploadHeaders):
    content_length: Optional[str] = None
    content_type: Optional[str] = None


class CollectionUploadHeaders(UploadHeaders):
    swarm_index_document: Optional[str] = None
    swarm_error_document: Optional[str] = None


class Pin(BaseModel):
    reference: str


class GetAllPinResponse(BaseModel):
    references: list[Reference]
