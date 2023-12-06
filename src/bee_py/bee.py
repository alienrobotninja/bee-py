import os
from typing import Optional, Union

from ape.types import AddressType
from swarm_cid import ReferenceType

from bee_py.chunk.signer import sign
from bee_py.chunk.soc import download_single_owner_chunk, upload_single_owner_chunk_data
from bee_py.feed.feed import Index, IndexBytes, make_feed_reader, make_feed_writer
from bee_py.feed.json import get_json_data, set_json_data
from bee_py.feed.retrievable import get_all_sequence_update_references
from bee_py.feed.topic import make_topic, make_topic_from_string
from bee_py.feed.type import is_feed_type
from bee_py.modules import bytes as bytes_api
from bee_py.modules import bzz as bzz_api
from bee_py.modules import chunk as chunk_api
from bee_py.modules import pinning as pinning_api
from bee_py.modules import pss as pss_api
from bee_py.modules import status as status_api
from bee_py.modules import stewardship as stewardship_api
from bee_py.modules import tag as tag_api
from bee_py.modules.feed import create_feed_manifest
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
from bee_py.utils.data import prepare_websocket_data
from bee_py.utils.error import BeeArgumentError, BeeError
from bee_py.utils.eth import make_eth_address, make_hex_eth_address
from bee_py.utils.type import (
    add_cid_conversion_function,
    assert_all_tags_options,
    assert_collection_upload_options,
    assert_reference,
    assert_reference_or_ens,
    assert_request_options,
    assert_upload_options,
    make_reference_or_ens,
    make_tag_uid,
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

    # URL on which is the main API of Bee node exposed
    url: str
    # Default Signer object used for signing operations, mainly Feeds
    signer: Optional[Signer]
    # Ky instance that defines connection to Bee node
    request_options: BeeRequestOptions

    def __init__(self, url: str, options: Optional[BeeOptions] = None):
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

        self.request_options = BeeRequestOptions.parse_obj(
            {
                "baseURL": self.url,
                "timeout": options.get("timeout", False),
                "headers": options.get("headers", {}),
                "onRequest": options.get("onRequest", None),
            }
        )

    def __get_request_options_for_call(
        self,
        options: Optional[UploadOptions] = None,
    ) -> dict:
        """
        Returns the request options for a call, merging the default options with the provided options.

        Args:
            options (dict, optional): Additional options that affect the request behavior. Defaults to None.

        Returns:
            dict: The merged request options.
        """
        if options:
            return {**self.request_options, **options}
        else:
            return self.request_options

    def upload_data(
        self,
        postage_batch_id: Union[str, BatchId],
        data: Union[str, bytes],
        options: Optional[UploadOptions] = None,
        request_options: Optional[BeeRequestOptions] = None,
    ) -> UploadResult:
        """
        Upload data to a Bee node.

        Args:
            postage_batch_id (str): Postage BatchId to be used to upload the data with.
            data (Any): Data to be uploaded.
            options (dict, optional): Additional options like tag, encryption, pinning,
            content-type and request options. Defaults to None.

        Returns:
            str: reference is a content hash of the data.

        Raises:
            TypeError: If the postage_batch_id, data, or options are not of the correct types.

        See Also:
            Bee docs - Upload and download: https://docs.ethswarm.org/docs/develop/access-the-swarm/upload-and-download
            Bee API reference - `POST /bytes`: https://docs.ethswarm.org/api/#tag/Bytes/paths/~1bytes/post
        """
        if options:
            assert_upload_options(options)
        return bytes_api.upload(request_options, data, postage_batch_id, options)

    def download_data(
        self, reference: Union[ReferenceOrENS, str], options: Optional[BeeRequestOptions] = None
    ) -> bytes:
        """
        Download data as a byte array.

        Args:
            reference (str, bytes): Bee data reference in hex string (either 64 or 128 chars long) or ENS domain.
            options (dict, optional): Options that affect the request behavior. Defaults to None.

        Returns:
            bytes: The downloaded data as a byte array.

        Raises:
            TypeError: If some of the input parameters is not of the expected type.
            BeeArgumentError: If there is passed ENS domain with invalid unicode characters.

        See Also:
            Bee docs - Upload and download: https://docs.ethswarm.org/docs/develop/access-the-swarm/upload-and-download
            Bee API reference - `GET /bytes`: https://docs.ethswarm.org/api/#tag/Bytes/paths/~1bytes~1{reference}/get
        """

        assert_request_options(options)
        assert_reference(reference)

        return bytes_api.downalod(self.__get_request_options_for_call(options), reference)

    def download_readable_data(self, reference: ReferenceOrENS, options: Optional[BeeRequestOptions] = None) -> bytes:
        """
        Downloads data as a Readable stream.

        Args:
            reference (ReferenceOrENS): Bee data reference in hex string (either 64 or 128 chars long) or ENS domain.
            options (BeeRequestOptions): Options that affect the request behavior.

        Raises:
            TypeError: If some of the input parameters are not the expected type.
            BeeArgumentError: If an ENS domain with invalid unicode characters is passed.
        """

        assert_request_options(options)
        assert_reference_or_ens(reference)

        return bytes_api.download_readable(self.__get_request_options_for_call(options), reference)

    def upload_chunk(
        self,
        postage_batch_id: BatchId,
        data: bytes,
        options: Optional[UploadOptions] = None,
        request_options: Optional[BeeRequestOptions] = None,
    ) -> Reference:
        """
        Uploads a chunk to a Bee node.

        Args:
            postage_batch_id (BatchId): The Postage Batch ID to use for uploading the chunk.
            data (bytes): The raw chunk data to be uploaded.
            options (UploadOptions): Additional options for the upload, such as tag, encryption,
            pinning, content-type, and request options.
            request_options (BeeRequestOptions): Options that affect the request behavior.

        Returns:
            Reference: The content hash of the uploaded data.
        """

        if not isinstance(data, bytes):
            msg = "Data must be a bytes object!"
            raise TypeError(msg)

        if len(data) < SPAN_SIZE:
            msg = f"Chunk must have a minimum size of {SPAN_SIZE} bytes. Received chunk size: {len(data)}"
            raise BeeArgumentError(msg)

        if len(data) > CHUNK_SIZE + SPAN_SIZE:
            msg = f"Chunk must have a maximum size of {CHUNK_SIZE} bytes. Received chunk size: {len(data)}"
            raise BeeArgumentError(msg)

        if options is not None:
            assert_upload_options(options)

        return chunk_api.upload(self.__get_request_options_for_call(request_options), data, postage_batch_id, options)

    def download_chunk(self, reference: ReferenceOrENS, options: Optional[BeeRequestOptions] = None) -> Data:
        """
        Downloads a chunk as a byte array.

        Args:
            reference (ReferenceOrENS): Bee chunk reference in hex string (either 64 or 128 chars long) or ENS domain.
            options (BeeRequestOptions): Options that affect the request behavior.

        Raises:
            TypeError: If some of the input parameters are not the expected type.
            BeeArgumentError: If an ENS domain with invalid unicode characters is passed.

        Returns:
            Data obejct: download chunk data in bytes
        """

        assert_request_options(options)
        assert_reference_or_ens(reference)

        return chunk_api.download(self.__get_request_options_for_callback(options), reference)

    def upload_file(
        self,
        postage_batch_id: str,
        data: Union[bytes, str],
        name: Optional[str] = None,
        options: Optional[FileUploadOptions] = None,
        request_options: Optional[BeeRequestOptions] = None,
    ) -> UploadResultWithCid:
        """
        Uploads a single file to a Bee node.

        Args:
            postage_batch_id (str): The Postage Batch ID to use for uploading the data.
            data (bytes, str): The data or file to be uploaded.
            name (str, optional): The optional name of the uploaded file.
            options (FileUploadOptions, optional): Additional options for the upload, such as tag,
            encryption, pinning, content-type, and request options.
            request_options (BeeRequestOptions, optional): Options that affect the request behavior.

        Raises:
            TypeError: If some of the input parameters are not the expected type.
            ValueError: If the `options.tag` and `options.size` are not set consistently or if the
            `name` is not a string.
        Returns:
            UploadResultWithCid
        """

        if options:
            assert_upload_options(options)

        if name and isinstance(name, str):
            msg = "name must be a string or None"
            raise ValueError(msg)

        return add_cid_conversion_function(
            bzz_api.upload_file(
                self.__get_request_options_for_callback(request_options), data, postage_batch_id, name, options
            ),
            ReferenceType.MANIFEST,
        )

    def download_file(
        self,
        reference: ReferenceCidOrENS,
        path: str = "",
        options: Optional[BeeRequestOptions] = None,
    ) -> FileData:
        """
        Downloads a single file.

        Args:
            reference (ReferenceCidOrENS): Bee file reference in hex string (either 64 or 128 chars
            long), ENS domain, or Swarm CID.
            path (str, optional): The path to the file within the manifest, if the reference points to a manifest.
            options (BeeRequestOptions, optional): Options that affect the request behavior.

        Raises:
            TypeError: If some of the input parameters are not the expected type.
            BeeArgumentError: If an ENS domain with invalid unicode characters is passed.

        Returns:
            FileData
        """

        assert_reference_or_ens(reference)
        reference = make_reference_or_ens(reference, ReferenceType.MANIFEST)

        return bzz_api.download_file(self.__get_request_options_for_callback(options), reference, path)

    def download_readable_file(
        self,
        reference: ReferenceCidOrENS,
        path: str = "",
        options: BeeRequestOptions = None,
    ) -> FileData:
        """
        Downloads a single file as a readable stream.

        Args:
            reference (ReferenceCidOrENS): Bee file reference in hex string (either 64 or 128 chars
            long), ENS domain, or Swarm CID.
            path (str, optional): The path to the file within the manifest, if the reference points to a manifest.
            options (BeeRequestOptions, optional): Options that affect the request behavior.

        Raises:
            TypeError: If some of the input parameters are not the expected type.
            BeeArgumentError: If an ENS domain with invalid unicode characters is passed.

        Returns:
            FileData
        """

        assert_reference_or_ens(reference)
        reference = make_reference_or_ens(reference, ReferenceType.MANIFEST)

        return bzz_api.download_file_readable(self.__get_request_options_for_callback(options), reference, path)

    def upload_files(
        self,
        postage_batch_id: str,
        file_list: list[Union[os.PathLike, str]],
        options: CollectionUploadOptions = None,
        request_options: BeeRequestOptions = None,
    ) -> UploadResultWithCid:
        """
        Uploads a collection of files to a Bee node.

        Args:
            postage_batch_id (str): The Postage Batch ID to use for uploading the data.
            file_list (FileList | File[]): A FileList or a list of File objects to be uploaded.
            options (CollectionUploadOptions, optional): Additional options for the upload,
            such as tag, encryption, pinning, and request options.
            request_options (BeeRequestOptions, optional): Options that affect the request behavior.

        Raises:
            TypeError: If some of the input parameters are not the expected type.
        Returns:
            UploadResultWithCid
        """
        if options:
            assert_collection_upload_options(options)

        data = make_collection_from_file_list(file_list)

        upload_result = bzz_api.upload_collection(
            self.__get_request_options_for_callback(request_options), data, postage_batch_id, options
        )
        return add_cid_conversion_function(upload_result, ReferenceType.MANIFEST)

    def upload_collection(
        self,
        postage_batch_id: BatchId,
        collection: Collection,
        options: Optional[CollectionUploadOptions] = None,
    ) -> UploadResultWithCid:
        """
        Uploads a custom collection of data to a Bee node.

        Args:
            postage_batch_id (BatchId): The Postage Batch ID to use for uploading the data.
            collection (Collection): A dictionary of file data, where the keys are
            the file paths and the values are either bytes or Readable objects representing the file
            contents.options (CollectionUploadOptions, optional): Additional options for the upload,
            such as tag, encryption, pinning, and request options.

        Raises:
            TypeError: If some of the input parameters are not the expected type.
        Returns:
            UploadResultWithCid
        """
        assert_collection(collection)

        if options:
            assert_collection_upload_options(options)

        upload_result = bzz_api.upload_collection(self.request_options, collection, postage_batch_id, options)

        return add_cid_conversion_function(upload_result, ReferenceType.MANIFEST)

    def upload_files_from_directory(
        self,
        postage_batch_id: BatchId,
        directory: str,
        options: Optional[CollectionUploadOptions] = None,
        request_options: Optional[BeeRequestOptions] = None,
    ) -> UploadResultWithCid:
        """
        Uploads a collection of files from a directory to a Bee node.

        Args:
            postage_batch_id (BatchId): The Postage Batch ID to use for uploading the data.
            directory (str): The path to the directory containing the files to be uploaded.
            options (CollectionUploadOptions, optional): Additional options for the upload,
            such as tag, encryption, pinning, and request options.
            request_options (BeeRequestOptions, optional): Options that affect the request behavior.

        Raises:
            TypeError: If some of the input parameters are not the expected type.
            FileNotFoundError: If the specified directory does not exist.
        Returns:
            UploadResultWithCid

        See Also:
            * [Bee docs - Keep your data alive / Postage stamps](https://docs.ethswarm.org/docs/develop/access-the-swarm/keep-your-data-alive)
            * [Bee docs - Upload directory](https://docs.ethswarm.org/docs/develop/access-the-swarm/upload-a-directory/)
            * [Bee API reference - `POST /bzz`](https://docs.ethswarm.org/api/#tag/Collection/paths/~1bzz/post)
        """

        if options:
            assert_collection_upload_options(options)
        data = make_collection_from_file_list([directory])

        upload_result = bzz_api.upload_collection(
            self.__get_request_options_for_call(request_options), data, postage_batch_id, options
        )

        return add_cid_conversion_function(upload_result, ReferenceType.MANIFEST)

    def create_tag(self, options: Optional[BeeRequestOptions] = None) -> Tag:
        """
        Creates a new tag for tracking the progress of syncing data across the Bee network.

        Args:
            options (BeeRequestOptions): Options that affect the request behavior.

        Raises:
            TypeError: If some of the input parameters are not the expected type.
        Returns:
            Tag

        See Also:
            * [Bee docs - Upload and download](https://docs.ethswarm.org/docs/develop/access-the-swarm/upload-and-download)
            * [Bee API reference - `PUT /bzz/`](https://docs.ethswarm.org/api/#tag/Collection/paths/~1bzz/{reference}~1{path}/put)
        """
        assert_request_options(options)

        return tag_api.create_tag(self.__get_request_options_for_callback(options))

    def get_all_tags(self, options: Optional[AllTagsOptions] = None) -> list[Tag]:
        """
        Fetches all tags from the Bee node.

        This function retrieves all tags from the Bee node, optionally using the `offset` and `limit`
        parameters to paginate the results.

        Args:
            options (AllTagsOptions): Options that affect the request behavior, including
            `offset` and `limit`.

        Raises:
            TypeError: If some of the input parameters are not the expected type.
            BeeArgumentError: If the `offset` or `limit` options are invalid.
        Returns:
            list[Tag]
        See Also:
            * [Bee docs - Syncing / Tags](https://docs.ethswarm.org/docs/access-the-swarm/syncing)
            * [Bee API reference - `GET /tags`](https://docs.ethswarm.org/api/#tag/Tag/paths/~1tags/get)
        """
        assert_all_tags_options(options)

        return tag_api.get_all_tags(self.__get_request_options_for_callback(options), options.offset, options.limit)
