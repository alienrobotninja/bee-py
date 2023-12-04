from typing import Optional

from ape.types import AddressType
from swarm_cid import ReferenceType

from bee_py.chunk.signer import sign
from bee_py.chunk.soc import download_single_owner_chunk, upload_single_owner_chunk_data
from bee_py.feed.feed import Index, IndexBytes, make_feed_reader, make_feed_writer
from bee_py.feed.json import get_json_data, set_json_data
from bee_py.feed.retrievable import get_all_sequence_update_references
from bee_py.feed.topic import make_topic, make_topic_from_string
from bee_py.feed.type import is_feed_type
from bee_py.modules.bytes import *
from bee_py.modules.bzz import *
from bee_py.modules.chunk import *
from bee_py.modules.feed import create_feed_manifest
from bee_py.modules.pinning import *
from bee_py.modules.pss import *
from bee_py.modules.status import *
from bee_py.modules.stewardship import *
from bee_py.modules.tag import *
from bee_py.types.type import (  # Reference,
    CHUNK_SIZE,
    DEFAULT_FEED_TYPE,
    SPAN_SIZE,
    AddressPrefix,
    AllTagsOptions,
    BatchId,
    BeeOptions,
    BeeRequestOptions,
    Collection,
    CollectionUploadOptions,
    Data,
    FeedManifestResult,
    FeedReader,
    FeedType,
    FeedWriter,
    FileData,
    FileUploadOptions,
    JsonFeedOptions,
    Pin,
    PssMessageHandler,
    PssSubscription,
    Reference,
    ReferenceCidOrENS,
    ReferenceOrENS,
    Signer,
    SOCReader,
    SOCWriter,
    Tag,
    Topic,
    UploadOptions,
    UploadResult,
    UploadResultWithCid,
)
from bee_py.utils.bytes import wrap_bytes_with_helpers
from bee_py.utils.collection import assert_collection, make_collection_from_file_list
from bee_py.utils.collection_node import make_collection_from_fs
from bee_py.utils.data import prepare_web_socket_data
from bee_py.utils.error import BeeArgumentError, BeeError
from bee_py.utils.eth import make_eth_address, make_hex_eth_address
from bee_py.utils.file import is_file
from bee_py.utils.type import (
    addCidConversionFunction,
    assertAddressPrefix,
    assertAllTagsOptions,
    assertBatchId,
    assertCollectionUploadOptions,
    assertData,
    assertFileData,
    assertFileUploadOptions,
    assertPssMessageHandler,
    assertPublicKey,
    assertReference,
    assertReferenceOrEns,
    assertRequestOptions,
    assertUploadOptions,
    make_tag_uid,
    makeReferenceOrEns,
)
from bee_py.utils.urls import assert_bee_url, strip_last_slash


class Bee:
    """
    The main component that abstracts operations available on the main Bee API.

    Not all methods are always available as it depends on what mode is Bee node launched in.
    For example, gateway mode and light node mode has only a limited set of endpoints enabled.

    Attributes:
        url: URL on which is the main API of Bee node exposed.
        signer: Default Signer object used for signing operations, mainly Feeds.
        request_options: Ky instance that defines connection to Bee node.
    """

    def __init__(self, url: str, options: Optional[dict] = None):
        """
        Constructs a new Bee instance.

        Args:
            url: URL on which is the main API of Bee node exposed.
            options: Additional options for the Bee instance.
        """
        assert_bee_url(url)

        # Remove last slash if present, as our endpoint strings starts with `/...`
        # which could lead to double slash in URL to which Bee responds with
        # unnecessary redirects.
        self.url = strip_last_slash(url)

        if options and "signer" in options:
            self.signer = sign(options["signer"])

        self.request_options = {
            "baseURL": self.url,
            "timeout": options.get("timeout", False),
            "headers": options.get("headers", None),
            "onRequest": options.get("onRequest", None),
            "adapter": options.get("adapter", None),
        }

    def download_chunk(self):
        ...
