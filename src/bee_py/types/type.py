import json
from enum import Enum
from typing import Annotated, Any, Callable, Generic, NewType, Optional, TypeVar, Union

from ape.managers.accounts import AccountAPI
from eth_typing import ChecksumAddress as AddressType

# from eth_pydantic_types import HexBytes
# from eth_pydantic_types import HexBytes as BaseHexBytes
from pydantic import BaseModel, Field, validator
from swarm_cid.swarm_cid import CIDv1
from typing_extensions import TypeAlias

from bee_py.utils.error import BeeError

Type = TypeVar("Type")
Name = TypeVar("Name")
Length = TypeVar("Length", bound=int)
T: TypeAlias = Union[str, bytes]
NumberString = Annotated[str, "NumberString"]
# Signer = TypeVar("Signer", bound=AccountAPI)

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
TAGS_LIMIT_MAX = 1001
FEED_INDEX_HEX_LENGTH = 16

TOPIC_BYTES_LENGTH = 32
TOPIC_HEX_LENGTH = 64

# Type aliases
BatchId: TypeAlias = str
AddressPrefix: TypeAlias = str


class Signer(BaseModel):
    signer: AccountAPI


class BeeRequest(BaseModel):
    """
    Bee request model.

    Attributes:
        url: The URL of the request.
        method: The HTTP method of the request.
        headers: The headers of the request.
        params: The parameters of the request.
    """

    url: str
    method: str
    headers: Optional[dict[str, str]] = None
    params: Optional[dict[str, str]] = None


class BeeResponse(BaseModel):
    """
    Bee response model.

    Attributes:
        headers: The headers of the response.
        status: The status code of the response.
        statusText: The status text of the response.
        request: The request that was made.
    """

    headers: dict[str, str]
    status: int
    status_text: Optional[str] = Field(default="", alias="statusText")
    request: BeeRequest


class BeeRequestOptions(BaseModel):
    base_url: Optional[str] = Field(default="", alias="baseURL")
    timeout: Optional[int] = 300
    retry: int = 0
    headers: dict = {}
    on_request: bool = Field(default=True, alias="onRequest")


class PssSubscription(BaseModel):
    """
    Pss subscription model.

    Attributes:
       topic: The topic of the subscription.
       cancel: A function to cancel the subscription.
    """

    topic: str
    cancel: Callable[[], None]


class PssMessageHandler(BaseModel):
    """
    Pss message handler model.

    Attributes:
      onMessage: A function to handle messages.
      onError: A function to handle errors.
    """

    onMessage: Callable[[str, PssSubscription], None]  # noqa: N815
    onError: Callable[[BeeError, PssSubscription], None]  # noqa: N815


class BeeOptions(BeeRequestOptions):
    signer: Optional[Union[str, bytes]] = None


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


class Data(BaseModel):
    data: bytes

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
        return self.data.hex()

    def to_json(self) -> dict[str, Any]:
        """Converts the binary data into string which is then parsed into JSON.

        Returns:
          The decoded JSON object.
        """
        if isinstance(self.data, bytes):
            self.data = self.data.decode("utf-8")  # type: ignore
        if "{" in self.data:  # type: ignore
            return json.loads(self.data)

        # Split the string into a list of words
        words = self.data.split()
        # Convert the list into a dictionary
        dict_obj = {words[0]: " ".join(words[1:])}  # type: ignore
        # Convert the dictionary to a JSON object
        json_object = json.dumps(dict_obj)

        return json.loads(json_object)


class UploadOptions(BaseModel):
    pin: Optional[bool] = False
    encrypt: Optional[bool] = False
    tag: Optional[int] = None
    deferred: Optional[bool] = True

    @validator("pin", pre=True, always=True)
    def validate_pin(cls, value):  # noqa: N805
        if not isinstance(value, bool):
            msg = "Pin field must be a boolean"
            raise ValueError(msg)
        return value

    @validator("encrypt", pre=True, always=True)
    def validate_encrypt(cls, value):  # noqa: N805
        if not isinstance(value, bool):
            msg = "Encrypt field must be a boolean"
            raise ValueError(msg)
        return value

    @validator("tag", pre=True, always=True)
    def validate_tag(cls, value):  # noqa: N805
        if value is not None and not isinstance(value, int):
            msg = "Tag field must be an integer or None"
            raise ValueError(msg)
        return value

    @validator("deferred", pre=True, always=True)
    def validate_deferred(cls, value):  # noqa: N805
        if not isinstance(value, bool):
            msg = "Deferred field must be a boolean"
            raise ValueError(msg)
        return value


class FileHeaders(BaseModel):
    """Represents the headers for a file."""

    name: Optional[str]
    tag_uid: Optional[int]
    content_type: Optional[str]


class OverLayAddress(BaseModel):
    value: str


class Reference(BaseModel):
    """
    Represents a reference that can be either a non-encrypted reference, which is a hex string of length 64,
    or an encrypted reference, which is a hex string of length 128.
    """

    value: str

    @validator("value")
    def validate_value(cls, v):  # noqa: N805
        if len(v) not in (
            REFERENCE_HEX_LENGTH,
            ENCRYPTED_REFERENCE_HEX_LENGTH,
        ) or not all(c in "0123456789abcdefABCDEF" for c in v):
            msg = "Reference must be a hex string of length 64 or 128"
            raise ValueError(msg)
        return v

    def __str__(self):
        return self.value

    def __len__(self):
        return len(self.value)

    def __call__(self):
        return self.value


class ReferenceResponse(BaseModel):
    """
    Represents a response containing a reference.
    """

    reference: str

    def __str__(self):
        return self.reference


class Topic(BaseModel):
    """
    Represents a topic.

    Attributes:
        value: The value of the topic.
    """

    value: str

    @validator("value")
    def validate_value(cls, v):  # noqa: N805
        if len(v) != TOPIC_HEX_LENGTH or not all(c in "0123456789abcdefABCDEF" for c in v):
            msg = f"Topic must be a hex string of length {TOPIC_HEX_LENGTH}"
            raise ValueError(msg)
        return v

    def __str__(self):
        return self.value


def assert_address(value: Any):
    """
    Asserts the value is an Ethereum address.

    Args:
        value: The value to assert.

    Raises:
        ValueError: If the value is not an Ethereum address.
    """
    if not isinstance(value, str) or len(value) != ADDRESS_HEX_LENGTH:
        msg = "Value is not an Ethereum address!"
        raise ValueError(msg)


class BeeGenericResponse(BaseModel):
    """
    Represents a generic response from the Bee API.

    Attributes:
        message: The human-readable message associated with the response.
        code: The numerical code associated with the response.
    """

    message: str
    code: int


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
    disconnected_peers: Optional[list[Peer]] = Field(default=[], alias="disconnectedPeers")
    connected_peers: Optional[list[Peer]] = Field(default=[], alias="connectedPeers")


class Topology(BaseModel):
    base_address: str = Field(default="", alias="baseAddr")
    population: int
    connected: int
    timestamp: str
    nn_low_watermark: int = Field(default=0, alias="nnLowWatermark")
    depth: int
    reachability: str
    network_availability: str = Field(default="", alias="networkAvailability")
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
    gas_price: Optional[int] = Field(None, alias="gasPrice")
    gas_limit: Optional[int] = Field(None, alias="gasLimit")


CashoutOptions = TransactionOptions


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
    transaction_hash: Optional[str] = Field(default="", alias="transactionHash")
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
    label: Optional[str] = Field(None)
    gas_price: Optional[Union[str, int]] = Field(default="", alias="gasPrice")
    immutable_flag: Optional[bool] = Field(False)
    wait_for_usable: Optional[bool] = Field(default=True, alias="waitForUsable")
    wait_for_usable_timeout: Optional[int] = Field(default=120, alias="waitForUsableTimeout")


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

    # deprecated
    bzz: Optional[str] = None
    xDai: Optional[str] = None  # noqa: N815
    contract_address: Optional[str] = Field(default="", alias="contractAddress")


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
    # ? deprecated added for backwards compatibility
    total: int = 0
    processed: int = 0


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
    pending_transactions: list[TransactionInfo] = Field(default=[], alias="pendingTransactions")


class FeedType(Enum):
    """
    Enum class for feed types.

    Attributes:
        SEQUENCE: Sequential feed type.
        EPOCH: Epoch feed type.
    """

    def __str__(self):
        return self.value

    SEQUENCE = "sequence"
    EPOCH = "epoch"


class FeedUpdateOptions(UploadOptions, BaseModel):
    """
    Options for updating a feed.

    :param at: The start date as a Unix timestamp.
    :type at: Optional[int]
    :param type: The type of the feed (default: 'sequence').
    :type type: Optional[FeedType]
    :param index: Fetch a specific previous feed's update (default fetches the latest update).
    :type index: Optional[str]
    """

    at: Optional[int] = None
    _type: Optional[FeedType] = FeedType.SEQUENCE
    index: Optional[str] = None


class CreateFeedOptions(BaseModel):
    """
    Options for creating a feed.
    """

    _type: Optional[FeedType]


class FeedUpdateHeaders(BaseModel):
    """
    Headers for a feed update.
    """

    feed_index: str
    feed_index_next: str


class FetchFeedUpdateResponse(ReferenceResponse, FeedUpdateHeaders):
    """
    Response for fetching a feed update.
    """

    pass


class FeedUploadOptions(BaseModel):
    """
    Options for uploading a feed.

    :param upload_options: Options for the upload.
    :type upload_options: UploadOptions
    :param feed_update_options: Options for updating the feed.
    :type feed_update_options: FeedUpdateOptions
    """

    upload_options: UploadOptions
    feed_update_options: FeedUpdateOptions

    class Config:
        arbitrary_types_allowed = True


class FeedReader(BaseModel):
    Type: Union[FeedType, str]
    owner: Optional[str] = ""
    topic: Union[Topic, str]
    request_options: Optional[BeeRequestOptions] = None

    # * This is not the best way to handle this callable method. But for now this works
    download: Callable = ""  # type: ignore
    # upload: Callable


class FeedWriter(FeedReader):
    """
    Represents a feed writer.

    Attributes:
        type: The type of the feed.
        owner: The owner of the feed.
        topic: The topic of the feed.
        upload: The upload function.
    """

    # * Callable[[Union[str, BatchId], Union[bytes, Reference], Optional[FeedUploadOptions], Reference]]
    upload: Callable
    signer: Union[Signer, AccountAPI]


class JsonFeedOptions(BaseModel):
    address: Optional[AddressType] = None
    signer: Optional[str] = None  # Optional[Union[AccountAPI, str]] = None
    Type: Optional[FeedType] = None


class UploadResult(BaseModel):
    reference: Reference
    tag_uid: Optional[int] = Field(default=None, alias="tagUid")

    class Config:
        arbitrary_types_allowed = True


class UploadResultWithCid(UploadResult):
    """
    Function that converts the reference into Swarm CIDs

    @throws TypeError if the reference is encrypted reference (eq. 128 chars long) which is not supported in CID
    @see https://github.com/aviksaikat/swarm-cid-py
    """

    cid: Callable[[], CIDv1]


class FileUploadOptions(UploadOptions):
    size: Optional[int] = None
    content_type: Optional[str] = None


class CollectionEntry(BaseModel):
    data: T
    path: str


class Collection(BaseModel):
    entries: list[CollectionEntry]


class CollectionUploadOptions(UploadOptions):
    index_document: Optional[str] = Field(default="", alias="indexDocument")
    error_document: Optional[str] = Field(default="", alias="errorDocument")


class FileData(BaseModel):
    headers: FileHeaders
    data: bytes


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

    class Config:
        arbitrary_types_allowed = True


class SOCReader(BaseModel):
    """
    SOCReader model.

    Attributes:
      owner: The owner of the SOCReader.
      download: A function to download a single owner chunk.
    """

    owner: AddressType
    download: Callable


class SOCWriter(SOCReader):
    """
    SOCWriter model.

    Attributes:
     upload: A function to upload a single owner chunk.
    """

    # upload: Callable[[Union[str, BatchId], bytes, bytes, UploadOptions], Reference]
    upload: Callable


class AllTagsOptions(BaseModel):
    limit: int = Field(default=0, gt=TAGS_LIMIT_MIN, lt=TAGS_LIMIT_MAX)
    offset: int = Field(default=0, ge=0)

    @validator("limit", "offset")
    def must_be_defined(cls, v):  # noqa: N805
        if not v:
            msg = "AllTagsOptions.limit and offset have to be defined!"
            raise TypeError(msg)
        return v


class FeedManifestResult(BaseModel):
    """
    reference: Reference of the uploaded data
    cid: Function that converts the reference into Swarm Feed CID.

    https://github.com/aviksaikat/swarm-cid-py
    """

    reference: Reference
    cid: Callable[[], str]


# * Type that represents either Swarm's reference in hex string or
# * ESN domain (something.eth).
ReferenceOrENS = Union[Reference, str]
# * Type that represents either Swarm's reference in hex string,
# * ESN domain (something.eth) or CID using one of the Swarm's codecs.
ReferenceCidOrENS = Union[ReferenceOrENS, str]


class Epoch(BaseModel):
    """
    Epoch model.

    :param time: The time of the epoch.
    :type time: int
    :param level: The level of the epoch.
    :type level: int
    """

    time: int
    level: int


IndexBytes = NewType("IndexBytes", bytes)
Index = Union[int, Epoch, bytes, str]

# class Index(BaseModel):
#     """
#     Index model.

#     :param index: The index can be a number, an epoch, index bytes or a string.
#     :type index: Union[int, Epoch, bytes, str]
#     """

#     index: Union[int, Epoch, bytes, str]


class FeedUpdate(BaseModel):
    """
    Represents a feed update.

    Attributes:
        timestamp: The timestamp of the update.
        reference: The reference of the update.
    """

    timestamp: int
    reference: bytes
