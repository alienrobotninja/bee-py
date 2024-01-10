import os
from time import sleep
from typing import Optional, Union

import websockets
from ape.managers.accounts import AccountAPI
from ape.types import AddressType
from eth_pydantic_types import HexBytes
from requests import HTTPError, Response
from swarm_cid import ReferenceType

from bee_py.chunk.soc import Identifier, download_single_owner_chunk, upload_single_owner_chunk_data
from bee_py.feed import json as json_api
from bee_py.feed.feed import make_feed_reader as _make_feed_reader
from bee_py.feed.feed import make_feed_writer as _make_feed_writer
from bee_py.feed.retrievable import are_all_sequential_feeds_update_retrievable
from bee_py.feed.topic import make_topic, make_topic_from_string
from bee_py.feed.type import DEFAULT_FEED_TYPE
from bee_py.modules import bytes as bytes_api
from bee_py.modules import bzz as bzz_api
from bee_py.modules import chunk as chunk_api
from bee_py.modules import pinning as pinning_api
from bee_py.modules import pss as pss_api
from bee_py.modules import status as status_api
from bee_py.modules import stewardship as stewardship_api
from bee_py.modules import tag as tag_api
from bee_py.modules.debug import stamps
from bee_py.modules.feed import create_feed_manifest as _create_feed_manifest
from bee_py.types.type import (
    CHUNK_SIZE,
    SPAN_SIZE,
    STAMPS_DEPTH_MAX,
    STAMPS_DEPTH_MIN,
    AddressPrefix,
    AllTagsOptions,
    BatchId,
    BeeOptions,
    BeeRequestOptions,
    Collection,
    CollectionUploadOptions,
    Data,
    FeedReader,
    FeedType,
    FeedWriter,
    FileData,
    FileUploadOptions,
    GetAllPinResponse,
    Index,
    IndexBytes,
    JsonFeedOptions,
    NumberString,
    Pin,
    PostageBatch,
    PostageBatchOptions,
    PssMessageHandler,
    PssSubscription,
    Reference,
    ReferenceCidOrENS,
    ReferenceOrENS,
    ReferenceResponse,
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
from bee_py.utils.data import prepare_websocket_data
from bee_py.utils.error import BeeArgumentError, BeeError
from bee_py.utils.eth import make_eth_address, make_hex_eth_address
from bee_py.utils.type import (
    add_cid_conversion_function,
    assert_address_prefix,
    assert_all_tags_options,
    assert_batch_id,
    assert_collection_upload_options,
    assert_data,
    assert_directory,
    assert_feed_type,
    assert_file_data,
    assert_file_upload_options,
    assert_non_negative_integer,
    assert_positive_integer,
    assert_postage_batch_options,
    assert_public_key,
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

    def __init__(self, url: str, options: Optional[Union[BeeOptions, dict]] = None):
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
        if options:
            if not isinstance(options, BeeOptions):
                if not isinstance(options, dict):
                    msg = f"Expected: Options must be of type dict or BeeOptions. Got: {type(options)}"
                    raise TypeError(msg)
        if isinstance(options, BeeOptions):
            options = BeeOptions.model_dump(options)
        if options and "signer" in options:
            self.signer = options["signer"]

        self.request_options = BeeRequestOptions.model_validate(
            {
                "baseURL": self.url,
                **(
                    {
                        "timeout": options.get("timeout", 300),
                        "headers": options.get("headers", {}),
                        "onRequest": options.get("onRequest", True),
                    }
                    if options
                    else {}
                ),
            }
        )

    def __get_request_options_for_call(
        self,
        options: Optional[Union[BeeRequestOptions, JsonFeedOptions]] = None,
    ) -> BeeRequestOptions:
        """
        Returns the request options for a call, merging the default options with the provided options.

        Args:
            options (dict): Additional options that affect the request behavior. Defaults to None.

        Returns:
            dict: The merged request options.
        """
        if options:
            if isinstance(options, (JsonFeedOptions, BeeRequestOptions, AllTagsOptions)):
                options = options.model_dump()  # type: ignore
            if isinstance(
                self.request_options,
                (JsonFeedOptions, BeeRequestOptions, AllTagsOptions),
            ):
                self.request_options = self.request_options.model_dump()  # type: ignore
            return {**self.request_options, **options}  # type: ignore
        else:
            return self.request_options

    def __make_feed_reader(
        self,
        feed_type: Union[FeedType, str],
        topic: Union[bytes, str, Topic],
        owner: Union[AddressType, str, bytes],
        options: Optional[BeeRequestOptions] = None,
    ) -> FeedReader:
        """
        Creates a new feed reader for downloading feed updates.

        Args:
            type: The type of the feed, can be 'epoch' or 'sequence'
            topic: hex string or bytes
            owner: Owner's ethereum address in hex or bytes
            options: Options that affect the request behavior

        Returns:
            A new `FeedReader` instance

        See also: [Bee docs - Feeds](https://docs.ethswarm.org/docs/dapps-on-swarm/feeds)
        """
        assert_request_options(options)

        canonical_topic = make_topic(topic)
        canonical_owner = make_hex_eth_address(owner)

        if isinstance(canonical_owner, HexBytes):
            canonical_owner = canonical_owner.hex()

        return _make_feed_reader(
            self.__get_request_options_for_call(options),
            feed_type,
            canonical_topic,
            canonical_owner,
        )

    def __resolve_signer(self, signer: Optional[Union[Signer, bytes, str]] = None) -> Union[Signer, AccountAPI]:
        """
        Resolves the signer to be used.

        Args:
            signer: An optional signer. Either an instance of `bee.Signer` or a hex string or a
            string containing the hex representation of a private key.

        Returns:
            The resolved signer object.

        Raises:
            BeeError: If either no signer was passed or no default signer was specified for the instance
        """
        if not self.signer:
            msg = "You have to pass Signer as property to either in the Bee constructor!"
            raise ValueError(msg)
        elif self.signer:
            return self.signer
        else:
            msg = "Signer Error"
            raise BeeArgumentError(msg, signer)

    def make_feed_topic(self, topic: Union[Topic, bytes, str]) -> Topic:
        """
        Make a new feed topic from a string

        Because the topic has to be 32 bytes long this function hashes the input string to create a topic string of
        arbitrary length.

        Args:
            topic The input string
        Returns:
            hashed topic data
        """
        if isinstance(topic, Topic):
            topic = topic.value
        if isinstance(topic, bytes):
            topic = topic.decode()

        return make_topic_from_string(topic)

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
            options (dictHTTP error): Additional options like tag, encryption, pinning,
            content-type and request options. Defaults to None.

        Returns:
            str: reference is a content hash of the data.

        Raises:
            TypeError: If the postage_batch_id, data, or options are not of the correct types.

        See Also:
            Bee docs - Upload and download: https://docs.ethswarm.org/docs/develop/access-the-swarm/upload-and-download
            Bee API reference - `POST /bytes`: https://docs.ethswarm.org/api/#tag/Bytes/paths/~1bytes/post
        """
        assert_batch_id(postage_batch_id)
        assert_data(data)
        if options:
            assert_upload_options(options)
        if request_options:
            assert_request_options(request_options)
        return bytes_api.upload(self.__get_request_options_for_call(request_options), data, postage_batch_id, options)

    def download_data(self, reference: ReferenceOrENS, options: Optional[BeeRequestOptions] = None) -> Data:
        """
        Download data as a byte array.

        Args:
            reference (str, bytes): Bee data reference in hex string (either 64 or 128 chars long) or ENS domain.
            options (dictHTTP error): Options that affect the request behavior. Defaults to None.

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
        assert_reference_or_ens(reference)
        if isinstance(reference, dict):
            reference = reference.get("reference", None)
        if isinstance(reference, (ReferenceResponse, Reference)):
            reference = str(reference)

        return bytes_api.download(self.__get_request_options_for_call(options), reference)

    def download_readable_data(
        self, reference: ReferenceOrENS, options: Optional[BeeRequestOptions] = None
    ) -> Response:
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
        postage_batch_id: Union[BatchId, str],
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
            raise BeeArgumentError(msg, data)

        if len(data) > CHUNK_SIZE + SPAN_SIZE:
            msg = f"Chunk must have a maximum size of {CHUNK_SIZE} bytes. Received chunk size: {len(data)}"
            raise BeeArgumentError(msg, data)

        if options:
            assert_upload_options(options)

        return chunk_api.upload(
            self.__get_request_options_for_call(request_options),
            data,
            postage_batch_id,
            options,
        )

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

        return chunk_api.download(self.__get_request_options_for_call(options), reference)

    def upload_file(
        self,
        postage_batch_id: Union[BatchId, str],
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
            name (strHTTP error): The optional name of the uploaded file.
            options (FileUploadOptionsHTTP error): Additional options for the upload, such as tag,
            encryption, pinning, content-type, and request options.
            request_options (BeeRequestOptions): Options that affect the request behavior.

        Raises:
            TypeError: If some of the input parameters are not the expected type.
            ValueError: If the `options.tag` and `options.size` are not set consistently or if the
            `name` is not a string.
        Returns:
            UploadResultWithCid
        """

        assert_batch_id(postage_batch_id)
        assert_file_data(data)
        if request_options:
            assert_request_options(request_options)

        if options:
            assert_file_upload_options(options)

        if name and not isinstance(name, str):
            msg = "name must be a string or None"
            raise TypeError(msg)

        return add_cid_conversion_function(
            bzz_api.upload_file(
                self.__get_request_options_for_call(request_options),
                data,
                postage_batch_id,
                name,
                options,
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
            path (str): The path to the file within the manifest, if the reference points to a manifest.
            options (BeeRequestOptions): Options that affect the request behavior.

        Raises:
            TypeError: If some of the input parameters are not the expected type.
            BeeArgumentError: If an ENS domain with invalid unicode characters is passed.

        Returns:
            FileData
        """
        if options:
            assert_request_options(options)

        # assert_reference_or_ens(reference)
        reference = make_reference_or_ens(reference, ReferenceType.MANIFEST)

        return bzz_api.download_file(self.__get_request_options_for_call(options), reference, path)

    def download_readable_file(
        self,
        reference: ReferenceCidOrENS,
        path: str = "",
        options: Optional[Union[BeeRequestOptions, dict]] = None,
    ) -> FileData:
        """
        Downloads a single file as a readable stream.

        Args:
            reference (ReferenceCidOrENS): Bee file reference in hex string (either 64 or 128 chars
            long), ENS domain, or Swarm CID.
            path (str): The path to the file within the manifest, if the reference points to a manifest.
            options (BeeRequestOptions): Options that affect the request behavior.

        Raises:
            TypeError: If some of the input parameters are not the expected type.
            BeeArgumentError: If an ENS domain with invalid unicode characters is passed.

        Returns:
            FileData
        """

        assert_reference_or_ens(reference)
        reference = make_reference_or_ens(reference, ReferenceType.MANIFEST)

        return bzz_api.download_file_readable(self.__get_request_options_for_call(options), reference, path)  # type: ignore # noqa: 501

    def upload_files(
        self,
        postage_batch_id: Union[BatchId, str],
        file_list: list[Union[os.PathLike, str]],
        options: Optional[CollectionUploadOptions] = None,
        request_options: Optional[BeeRequestOptions] = None,
    ) -> UploadResultWithCid:
        """
        Uploads a collection of files to a Bee node.

        Args:
            postage_batch_id (str): The Postage Batch ID to use for uploading the data.
            file_list (os.PathLike | str): A FileList or a list of File objects to be uploaded.
            options (CollectionUploadOptions): Additional options for the upload,
            such as tag, encryption, pinning, and request options.
            request_options (BeeRequestOptions): Options that affect the request behavior.

        Raises:
            TypeError: If some of the input parameters are not the expected type.
        Returns:
            UploadResultWithCid
        """

        assert_batch_id(postage_batch_id)

        if request_options:
            assert_request_options(request_options)

        if options:
            assert_collection_upload_options(options)
            assert_file_upload_options(options)

        data = make_collection_from_file_list(file_list)  # type: ignore

        upload_result = bzz_api.upload_collection(
            self.__get_request_options_for_call(request_options),
            data,
            postage_batch_id,
            options,
        )
        return add_cid_conversion_function(upload_result, ReferenceType.MANIFEST)

    def upload_collection(
        self,
        postage_batch_id: Union[BatchId, str],
        collection: Collection,
        options: Optional[CollectionUploadOptions] = None,
    ) -> UploadResultWithCid:
        """
        Uploads a custom collection of data to a Bee node.

        Args:
            postage_batch_id (BatchId): The Postage Batch ID to use for uploading the data.
            collection (Collection): A dictionary of file data, where the keys are
            the file paths and the values are either bytes or Readable objects representing the file
            contents.options (CollectionUploadOptions): Additional options for the upload,
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
        postage_batch_id: Union[BatchId, str],
        directory: Union[str, os.PathLike],
        options: Optional[CollectionUploadOptions] = None,
        request_options: Optional[BeeRequestOptions] = None,
    ) -> UploadResultWithCid:
        """
        Uploads a collection of files from a directory to a Bee node.

        Args:
            postage_batch_id (BatchId): The Postage Batch ID to use for uploading the data.
            directory (str): The path to the directory containing the files to be uploaded.
            options (CollectionUploadOptions): Additional options for the upload,
            such as tag, encryption, pinning, and request options.
            request_options (BeeRequestOptions): Options that affect the request behavior.

        Raises:
            TypeError: If some of the input parameters are not the expected type.
            FileNotFoundError: If the specified directory does not exist.
        Returns:
            UploadResultWithCid

        See Also:
            * [Bee docs - Keep your data alive / Postage stamps](https://docs.ethswarm.org/docs/develop/access-the-swarm/keep-your-data-alive)
            * [Bee docs - Upload directory](https://docs.ethswarm.org/docs/develop/access-the-swarm/upload-a-directory/)
            * [Bee API reference - `POST /bzz`](https://docs.ethswarm.org/api/#tag/Collection/paths/~1bzz/post)
        """  # noqa: 501

        assert_batch_id(postage_batch_id)

        if request_options:
            assert_request_options(request_options)

        if options:
            assert_collection_upload_options(options)

        assert_directory(directory)

        data = make_collection_from_file_list(directory)

        upload_result = bzz_api.upload_collection(
            self.__get_request_options_for_call(request_options),
            data,
            postage_batch_id,
            options,
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
        """  # noqa: 501
        assert_request_options(options)

        return tag_api.create_tag(self.__get_request_options_for_call(options))

    def get_all_tags(self, options: Optional[Union[AllTagsOptions, dict]] = None) -> list[Tag]:
        """
        Fetches all tags from the Bee node.

        This function retrieves all tags from the Bee nodely using the `offset` and `limit`
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
            * [Bee docs - Syncing / Tags](https://docs.ethswarm.org/docs/develop/access-the-swarm/syncing)
            * [Bee API reference - `GET /tags`](https://docs.ethswarm.org/api/#tag/Tag/paths/~1tags/get)
        """

        assert_all_tags_options(options)
        assert_request_options(options)

        if isinstance(options, dict):
            options = AllTagsOptions.model_validate(options, strict=True)

        if options.offset and options.limit:  # type: ignore
            return tag_api.get_all_tags(
                self.__get_request_options_for_call(options),  # type: ignore
                options.offset,  # type: ignore
                options.limit,  # type: ignore
            )
        elif options.offset:  # type: ignore
            return tag_api.get_all_tags(self.__get_request_options_for_call(options), options.offset)  # type: ignore
        elif options.limit:  # type: ignore
            return tag_api.get_all_tags(self.__get_request_options_for_call(options), options.limit)  # type: ignore
        return tag_api.get_all_tags(self.__get_request_options_for_call(options))  # type: ignore

    def retrieve_tag(self, tag_uid: Union[int, Tag], options: Optional[BeeRequestOptions] = None):
        """
        Retrieve tag information from Bee node

        Args:
            tag_uid (int|Tag): UID or tag object to be retrieved
            options (BeeRequestOptions, optional): Options that affects the request behavior. Defaults to None

        Returns:
            Promise[Tag]: Tag object containing the retrieved tag information

        Raises:
            TypeError: If tagUid is in not correct format

        See:
            [Bee docs - Syncing / Tags](https://docs.ethswarm.org/docs/access-the-swarm/syncing)
            [Bee API reference - `GET /tags/{uid}`](https://docs.ethswarm.org/api/#tag/Tag/paths/~1tags~1{uid}/get)

        """

        assert_request_options(options)

        tag_uid = make_tag_uid(tag_uid)

        return tag_api.retrieve_tag(self.__get_request_options_for_call(options), tag_uid)

    def delete_tag(
        self,
        uid: Union[Tag, int],
        options: Optional[BeeRequestOptions] = None,
    ) -> None:
        """
        Deletes a tag from the Bee node.

        This function removes the specified tag from the Bee node.

        Args:
            uid (int | Tag): The ID or tag object of the tag to be deleted.
            options (BeeRequestOptions): Options that affect the request behavior.

        Raises:
            HTTP error: If an HTTP error occurs during the request.
            BeeResponseError: If the response from the Bee node indicates an error.
        Returns:
            None
        See Also:
            * [Bee docs - Syncing / Tags](https://docs.ethswarm.org/docs/develop/access-the-swarm/syncing)
            * [Bee API reference - `DELETE /tags/{uid}`](https://docs.ethswarm.org/api/#tag/Tag/paths/~1tags~1{uid}/delete)
            */
        """  # noqa: 501
        assert_request_options(options)
        tag_uid = make_tag_uid(uid)

        return tag_api.delete_tag(self.__get_request_options_for_call(options), tag_uid)

    def update_tag(
        self,
        uid: Union[Tag, int],
        reference: Union[Reference, str],
        request_options: Optional[BeeRequestOptions] = None,
    ) -> None:
        """
        Updates the total chunks count for a tag.

        This function updates the total chunks count for the specified tag. This is
        useful when uploading individual chunks with a tag and updating the total
        count once the final chunk is uploaded.

        Args:
            uid (int | Tag): The ID or tag object of the tag whose total chunks count to be updated.
            reference (Reference | str): The root reference that contains all the chunks to be counted.
            request_options (BeeRequestOptions): Options that affect the request behavior.

        Raises:
            HTTP error: If an HTTP error occurs during the request.
            BeeResponseError: If the response from the Bee node indicates an error.
        Returns:
            None
        See also:
            * [Bee docs - Syncing / Tags](https://docs.ethswarm.org/docs/develop/access-the-swarm/syncing)
            * [Bee API reference - `PATCH /tags/{uid}`](https://docs.ethswarm.org/api/#tag/Tag/paths/~1tags~1{uid}/patch)
        """  # noqa: 501
        assert_reference(reference)
        assert_request_options(request_options)

        tag_uid = make_tag_uid(uid)

        return tag_api.update_tag(self.__get_request_options_for_call(request_options), tag_uid, reference)

    def pin(
        self,
        reference: Union[Reference, str],
        request_options: Optional[BeeRequestOptions] = None,
    ) -> None:
        """
        Pins the local data specified by the given reference to the Bee node.

        This function pins the local data associated with the given reference to the
        Bee node, making it available to other Swarm nodes.

        Args:
            reference (Reference | str): The reference of the data to be pinned.
            request_options (BeeRequestOptions): Options that affect the request behavior.

        Raises:
            TypeError: If the `reference` argument is not a valid `Reference` object or
            a valid string representation of a reference.
            HTTPXError: If an HTTP error occurs during the request.
        Returns:
            None
        See also:
            * [Bee docs - Pinning](https://docs.ethswarm.org/docs/develop/access-the-swarm/pinning)
        """
        assert_reference(reference)

        assert_request_options(request_options)

        return pinning_api.pin(self.__get_request_options_for_call(request_options), reference)

    def unpin(
        self,
        reference: Union[Reference, str],
        request_options: Optional[BeeRequestOptions] = None,
    ) -> None:
        """
        Unpins the local data specified by the given reference from the Bee node.

        This function removes the pinned state of the local data associated with the
        given reference from the Bee node, making it unavailable to other Swarm nodes.

        Args:
            reference (Reference | str): The reference of the data to be unpinned.
            request_options (BeeRequestOptions): Options that affect the request behavior.

        Raises:
            TypeError: If the `reference` argument is not a valid `Reference` object
            or a valid string representation of a reference.
            HTTPXError: If an HTTP error occurs during the request.

        See also:
            * [Bee docs - Pinning](https://docs.ethswarm.org/docs/develop/access-the-swarm/pinning)
        """
        assert_reference(reference)
        assert_request_options(request_options)

        return pinning_api.unpin(self.__get_request_options_for_call(request_options), reference)

    def get_all_pins(self, request_options: Optional[BeeRequestOptions] = None) -> GetAllPinResponse:
        """
        Get list of all locally pinned references

        Args:
            request_options (BeeRequestOptionsHTTP error): Options that affect the request behavior.

        Raises:
            TypeError: If the `reference` argument is not a valid `Reference` object
            or a valid string representation of a reference.
            HTTPXError: If an HTTP error occurs during the request.

        See also:
            * [Bee docs - Pinning](https://docs.ethswarm.org/docs/develop/access-the-swarm/pinning)
        """
        assert_request_options(request_options)

        return pinning_api.get_all_pins(self.__get_request_options_for_call(request_options))

    def get_pin(
        self,
        reference: Union[Reference, str],
        request_options: Optional[BeeRequestOptions] = None,
    ) -> Pin:
        """
        Get the pinning status of the data specified by the given reference.

        This function retrieves information about the pinning status of the local data
        associated with the given reference on the Bee node.

        Args:
            reference (Reference | str): The reference of the data whose pinning status is to be retrieved.
            request_options (BeeRequestOptions, optional): Options that affect the request behavior.

        Raises:
            TypeError: If the `reference` argument is not a valid `Reference` object or
            a valid string representation of a reference.
            BeeArgumentError: If there is a passed ENS domain with invalid unicode characters.
            HTTPXError: If an HTTP error occurs during the request.

        See also:
            * [Bee docs - Pinning](https://docs.ethswarm.org/docs/develop/access-the-swarm/pinning)
        """
        assert_reference(reference)
        assert_request_options(request_options)

        return pinning_api.get_pin(self.__get_request_options_for_call(request_options), reference)

    def reupload_pinned_data(
        self,
        reference: Union[Reference, str],
        request_options: Optional[BeeRequestOptions] = None,
    ) -> None:
        """
        Reuploads a locally pinned data into the network.

        This function instructs the Bee node to reupload the locally pinned data
        associated with the given reference to the Swarm network.

        Args:
            reference (ReferenceOrEns | str): The reference of the data to be reuploaded.
            request_options (BeeRequestOptions, optional): Options that affect the request behavior.

        Raises:
            BeeArgumentError: If the reference is not locally pinned
            TypeError: If the `reference` argument is not a valid `Reference` object
            or a valid string representation of a reference.
            BeeArgumentError: If there is a passed ENS domain with invalid unicode
            characters.

        See also:
            * [Bee API reference - `PUT /stewardship`](https://docs.ethswarm.org/api/#tag/Stewardship/paths/~1stewardship~1{reference}/put)
        """  # noqa: 501
        assert_reference(reference)
        assert_request_options(request_options)

        return stewardship_api.reupload(self.__get_request_options_for_call(request_options), reference)

    def is_reference_retrievable(
        self,
        reference: Union[Reference, str],
        request_options: Optional[BeeRequestOptions] = None,
    ) -> bool:
        """
        Checks if content specified by reference is retrievable from the network.

        This function checks if the specified reference indicates content that can be retrieved from the Swarm network.

        Args:
            reference (ReferenceOrEns | str): The reference to be checked.
            request_options (BeeRequestOptions, optional): Options that affect the
            request behavior.

        Raises:
            TypeError: If the `reference` argument is not a valid `Reference` object
            or a valid string representation of a reference.
            BeeArgumentError: If there is a passed ENS domain with invalid unicode characters.

        See also:
            * [Bee API reference - `GET /stewardship`](https://docs.ethswarm.org/api/#tag/Stewardship/paths/~1stewardship~1{reference}/get)
        """  # noqa: 501
        assert_reference(reference)
        assert_request_options(request_options)

        return stewardship_api.is_retrievable(
            self.__get_request_options_for_call(request_options), reference
        ).is_retrievable

    def is_feed_retrievable(
        self,
        feed_type: Union[FeedType, str],
        owner: AddressType,
        topic: Union[Topic, str, bytes],
        index: Optional[Union[Index, IndexBytes]] = None,
        options: Optional[BeeRequestOptions] = None,
    ) -> bool:
        """
        Checks if feed is retrievable from the network.

        If no index is passed then it checks for "latest" update, which is a weaker guarantee as nobody can be really
        sure what is the "latest" update.

        If index is passed then it validates all previous sequence index chunks if they
        are available as they are required to correctly resolve the feed upto the given index update.

        Args:
            type
            owner
            topic
            index
            options
        """
        # Convert the owner and topic to canonical forms
        canonical_owner = make_eth_address(owner)
        canonical_topic = make_topic(topic)

        # If no index is passed, try downloading the feed and return true if successful
        if not index:
            try:
                self.__make_feed_reader(feed_type, canonical_topic, canonical_owner).download(options)
                return True
            except BeeError as e:
                raise e

        # If index is passed, check the availability of all previous sequence index chunks
        if feed_type != FeedType.SEQUENCE:
            msg = "Only Sequence type of Feeds is supported at the moment"
            raise BeeError(msg)

        return are_all_sequential_feeds_update_retrievable(
            self,
            canonical_owner,
            canonical_topic,
            index,
            self.__get_request_options_for_call(options),
        )

    def pss_send(
        self,
        postage_batch_id: Union[BatchId, str],
        topic: Union[Topic, str, bytes],
        target: AddressPrefix,
        data: Union[str, bytes],
        recipient: Optional[Union[str, HexBytes]] = None,
        options: Optional[BeeRequestOptions] = None,
    ) -> None:
        """
        Sends data to a recipient or a target using the Postal Service for Swarm.
        This function is intended for setting up an encrypted communication channel by sending an one-off message.
        It is not recommended for general messaging, as it is slow and CPU-intensive.

        **Warning:** If the recipient Bee node is a light node, then they will never receive the message.
        This is because light nodes do not fully participate in the data exchange in
        Swarm network and hence the message won't arrive to them.

        **Args:**
            postage_batch_id: Postage BatchId that will be assigned to the sent message
            topic: Topic name
            target: Target message address prefix. Has a limit on length. It is
            recommended to use `Utils.Pss.make_max_target()` to get the most specific target that a Bee node will accept
            data: Message to be sent
            recipient: Recipient's public key (optional)
            options: Options that affect the request behavior

        Raises:
            TypeError: If `data`, `batchId`, `target` or `recipient` are in invalid format

        References:
            [Bee docs - PSS](https://docs.ethswarm.org/docs/dapps-on-swarm/pss)
            [Bee API reference - `POST /pss`](https://docs.ethswarm.org/api/#tag/Postal-Service-for-Swarm/paths/~1pss~1send~1{topic}~1{targets}/post)
        """  # noqa: 501

        assert_request_options(options)
        assert_data(data)
        assert_batch_id(postage_batch_id)
        assert_address_prefix(target)

        if not isinstance(topic, Topic) or not isinstance(topic, str):
            msg = "topic has to be an string or Topic type!"
            raise TypeError(msg)

        if recipient:
            assert_public_key(recipient)
            return pss_api.send(
                self.__get_request_options_for_call(options),
                topic,
                target,
                data,
                postage_batch_id,
                recipient,
            )
        else:
            return pss_api.send(
                self.__get_request_options_for_call(options),
                topic,
                target,
                data,
                postage_batch_id,
            )

    # ! Not yet implemented properly
    async def pss_subscribe(
        self,
        topic: Union[Topic, str, bytes],
        handler: PssMessageHandler,
    ) -> PssSubscription:
        """
        Subscribes to messages for a given topic using the Postal Service for Swarm.

        **Warning:** If the connected Bee node is a light node, then it will never receive any messages!
        This is because light nodes do not fully participate in the data exchange in
        Swarm network and hence the message won't arrive to them.

        Args:
            topic: Topic name
            handler: Message handler interface
        Returns:
            A subscription object that can be used to cancel the subscription

        References:
            [Bee docs - PSS](https://docs.ethswarm.org/docs/dapps-on-swarm/pss)
            [Bee API reference - `GET /pss`](https://docs.ethswarm.org/api/#tag/Postal-Service-for-Swarm/paths/~1pss~1subscribe~1{topic}/get)
        """  # noqa: 501
        if not isinstance(topic, Topic) or not isinstance(topic, str):
            msg = "topic has to be an string or Topic type!"
            raise TypeError(msg)

        ws = await pss_api.subscribe(self.url, topic)
        cancelled = False

        async def cancel():
            nonlocal cancelled
            if not cancelled:
                cancelled = True
                await ws.close()

        subscription = PssSubscription(topic=topic, cancel=cancel)

        async def on_message(data):
            nonlocal cancelled
            # Ignore empty messages
            if len(data) > 0:
                await handler.onMessage(wrap_bytes_with_helpers(data), subscription)

        async def on_error(error_message):
            nonlocal cancelled
            # Ignore errors after subscription was cancelled
            if not cancelled:
                await handler.onError(BeeError(error_message), subscription)

        try:
            while True:
                message = await ws.recv()
                data = prepare_websocket_data(message)
                await on_message(data)
        except websockets.exceptions.ConnectionClosed:
            pass  # Connection closed, cancel subscription
        except Exception as e:
            await on_error(str(e))

        return subscription

    # ! Not yet implemented properly
    async def pss_receive(
        self,
        topic: Union[Topic, str, bytes],
        timeout_msec: int = 0,
    ) -> bytes:
        """
        Receive a message with Postal Service for Swarm.

        Because sending a PSS message is slow and CPU intensive,
        it is not supposed to be used for general messaging but
        most likely for setting up an encrypted communication
        channel by sending a one-off message.

        This is a helper function to wait for exactly one message to
        arrive and then cancel the subscription. Additionally, a
        timeout can be provided for the message to arrive, or else
        an error will be thrown.

        **Warning! If the connected Bee node is a light node, then it will never receive any message!**
        This is because light nodes do not fully participate in the data exchange in the Swarm network,
        and hence the message won't arrive at them.

        Args:
            topic (Union[Topic, str]): Topic name.
            timeout_msec (int): Timeout in milliseconds.

        Returns:
            bytes: Message in byte array.

        See also:
            - [Bee docs - PSS](https://docs.ethswarm.org/docs/dapps-on-swarm/pss)
            - [Bee API reference - `GET /pss`](https://docs.ethswarm.org/api/#tag/Postal-Service-for-Swarm/paths/~1pss~1subscribe~1{topic}/get)
        """  # noqa: 501
        if not isinstance(topic, Topic) or not isinstance(topic, str):
            msg = "topic has to be an string or Topic type!"
            raise TypeError(msg)

        if not isinstance(timeout_msec, int):
            msg = "timeout_msec parameter has to be a number!"
            raise TypeError(msg)

        # async def on_message(ev):
        #     data = await prepare_websocket_data(ev.data)

        #     if data:
        #         await handler.onMessage(data)

        # async def on_error(ev):
        #     # ignore errors after subscription was canceled
        #     if not canceled:
        #         await handler.on_error(BeeError(ev.message))

        # subscription = await self.subscribe(topic, on_message, on_error)

        # try:
        #     if timeout_msec > 0:
        #         await asyncio.sleep(timeout_msec / 1000)
        #         msg = "pss_receive timeout"
        #         raise BeeError(msg)

        #     message = await asyncio.to_thread(subscription.receive)
        #     return message

        # finally:
        #     subscription.cancel()

    def create_feed_manifest(
        self,
        postage_batch_id: Union[str, BatchId],
        feed_type: Union[FeedType, str],
        topic: Union[Topic, str, bytes],
        owner: Union[str, bytes, AddressType],
        options: Optional[BeeRequestOptions] = None,
    ) -> UploadResultWithCid:
        """
        Creates a feed manifest chunk and returns its reference.

        A feed manifest chunk allows a feed to be resolved through `/bzz` endpoint.

        Args:
            postage_batch_id: The postage batch ID to be used when creating the feed manifest.
            type: The type of the feed, either `epoch` or `sequence`.
            topic: The topic of the feed, either as a hex string, bytes object, or
            a string containing the hex representation of the bytes.
            owner: The Ethereum address of the feed owner, either as a hex string,
            bytes object, or a string containing the hex representation of the bytes.
            options: Optional BeeRequestOptions object to configure the request behavior.

        Returns:
            A string containing the reference to the created feed manifest chunk.

        References:
            [Bee docs - Feeds](https://docs.ethswarm.org/docs/dapps-on-swarm/feeds)
            [Bee API reference - `POST /feeds`](https://docs.ethswarm.org/api/#tag/Feed/paths/~1feeds~1{owner}~1{topic}/post)
        """  # noqa: 501

        assert_request_options(options)
        assert_feed_type(feed_type)
        assert_batch_id(postage_batch_id)

        canonical_topic = make_topic(topic)
        canonical_owner = make_hex_eth_address(owner)

        if isinstance(canonical_owner, HexBytes):
            canonical_owner = canonical_owner.hex()

        reference = _create_feed_manifest(
            self.__get_request_options_for_call(options),
            canonical_owner,
            canonical_topic,
            postage_batch_id,
            {"type": feed_type},  # TODO: see this value by printing debug information on bee-js
        )

        return add_cid_conversion_function(UploadResult(reference=reference), ReferenceType.FEED)

    def make_feed_reader(
        self,
        feed_type: Union[FeedType, str],
        topic: Union[Topic, bytes, str],
        signer: Union[Signer, bytes, str],
        options: Optional[BeeRequestOptions] = None,
    ) -> FeedReader:
        """
        Creates a new feed reader for downloading feed updates.

        Args:
            postage_batch_id: The postage batch ID to be used for the feed reader.
            type: The type of the feed, either `epoch` or `sequence`.
            topic: The topic of the feed, either as a hex string, bytes object, or a
            string containing the hex representation of the bytes.
            owner: The Ethereum address of the feed owner, either as a hex string,
            bytes object, or a string containing the hex representation of the bytes.
            options: Optional BeeRequestOptions object to configure the request behavior.

        Returns:
            A FeedReader object for downloading feed updates.

        References:
            [Bee docs - Feeds](https://docs.ethswarm.org/docs/dapps-on-swarm/feeds)
        """

        assert_feed_type(feed_type)
        assert_request_options(options)

        canonical_topic = make_topic(topic).value
        canonical_signer = self.__resolve_signer(signer)

        if isinstance(canonical_topic, Signer):
            canonical_signer = Signer.signers  # type: ignore
        else:
            canonical_signer = canonical_signer.address  # type: ignore

        return _make_feed_reader(
            self.__get_request_options_for_call(options), feed_type, canonical_topic, canonical_signer  # type: ignore
        )

    def make_feed_writer(
        self,
        feed_type: Union[FeedType, str],
        topic: Union[Topic, bytes, str],
        signer: Union[Signer, bytes, str],
        options: Optional[BeeRequestOptions] = None,
    ) -> FeedWriter:
        """
        Creates a new feed writer for updating feeds.

        Args:
            postage_batch_id: The postage batch ID to be used for the feed writer.
            type: The type of the feed, either `epoch` or `sequence`.
            topic: The topic of the feed, either as a hex string, bytes object, or a string
            containing the hex representation of the bytes.
            signer: An optional signer for signing feed updates.
            options: Optional BeeRequestOptions object to configure the request behavior.

        Returns:
            A FeedWriter object for updating feed.

        References:
            [Bee docs - Feeds](https://docs.ethswarm.org/docs/dapps-on-swarm/feeds)
        """
        assert_request_options(options)
        assert_feed_type(feed_type)

        canonical_topic = make_topic(topic)
        canonical_signer = self.__resolve_signer(signer)

        if isinstance(canonical_topic, Signer):
            canonical_signer = Signer.signers

        return _make_feed_writer(
            self.__get_request_options_for_call(options),
            feed_type,
            canonical_topic,
            canonical_signer,
        )

    def set_json_feed(
        self,
        postage_batch_id: Union[str, BatchId],
        topic: str,
        data,
        signer: Union[AddressType, str],
        options: Optional[Union[JsonFeedOptions, dict]] = None,
        request_options: Optional[BeeRequestOptions] = None,
    ) -> Reference:
        """
        Sets JSON data to a feed. JSON-like data types are supported.

        Args:
            writer: The feed writer to be used
            postage_batch_id: The postage batch ID to be used
            data: JSON compatible data
            options:
                signer: Custom instance of Signer or string with private key.
                type: Type of Feed

        Returns:
            A Promise that resolves to the reference of the uploaded feed data.

        References:
            [Bee docs - Feeds](https://docs.ethswarm.org/docs/dapps-on-swarm/feeds)
        """
        assert_request_options(options, "JsonFeedOptions")
        assert_batch_id(postage_batch_id)

        hashed_topic = self.make_feed_topic(topic)
        if isinstance(options, dict):
            options = JsonFeedOptions.model_validate(options)

        if options and options.Type:
            feed_type = options.Type
        else:
            feed_type = DEFAULT_FEED_TYPE

        writer = self.make_feed_writer(feed_type, hashed_topic, signer, request_options)

        return json_api.set_json_data(self, writer, postage_batch_id, data, options, request_options)

    def get_json_feed(
        self,
        topic: Union[Topic, bytes, str],
        options: Optional[Union[JsonFeedOptions, dict]] = None,
    ) -> dict:
        """
        High-level function that allows you to easily get data from feed.
        Returned data are parsed using json.loads().

        This method also supports specification of `signer` object passed to constructor. The order of evaluation is:
        - `options.address`
        - `options.signer`
        - `self.signer`

        At least one of these has to be specified!

        Args:
            topic (Union[Topic, bytes, str]): Human readable string, that is internally hashed so
            there are no constrains there.
            options (JsonFeedOptions): Options for the feed.

        Returns:
            dict: The JSON data from the feed.

        Raises:
            BeeError: If both options "signer" and "address" are specified at one time.
            BeeError: If neither address, signer or default signer is specified.

        See Also:
            Bee docs - Feeds: https://docs.ethswarm.org/docs/dapps-on-swarm/feeds
        """

        assert_request_options(options, "JsonFeedOptions")
        if not options:
            options = {}
        if isinstance(options, dict):
            options = JsonFeedOptions.model_validate(options)

        hashed_topic = self.make_feed_topic(topic)

        if options and options.Type:
            feed_type = options.Type
        else:
            feed_type = DEFAULT_FEED_TYPE

        if options.signer and options.address:
            msg = 'Both options "signer" and "address" can not be specified at one time!'
            raise BeeError(msg)

        address: Union[AddressType, bytes]

        if options.address:
            address = make_eth_address(options.address)
        else:
            try:
                signer = self.__resolve_signer(options.signer)
                if isinstance(signer, Signer):
                    address = signer.signer.address
                else:
                    address = signer.address
            except BeeError as e:
                msg = "Either address, signer or default signer has to be specified!"
                raise BeeError(msg) from e
        reader = self.make_feed_reader(feed_type, hashed_topic, address, options)  # type: ignore

        return json_api.get_json_data(self, reader)

    def make_soc_reader(
        self,
        owner_address: Union[AddressType, str, bytes],
        options: Optional[BeeRequestOptions] = None,
    ) -> SOCReader:
        """
        Returns an object for reading single owner chunks

        Args:
            owner_address: The ethereum address of the owner
            options: Options that affects the request behavior

        Returns:
            An SOCReader object that allows you to download single owner chunks.

        References:
            [Bee docs - Chunk Types](https://docs.ethswarm.org/docs/dapps-on-swarm/chunk-types#single-owner-chunks)
        """

        assert_request_options(options)
        canonical_owner = make_eth_address(owner_address)

        def __download(identifier: Identifier):
            return download_single_owner_chunk(
                self.__get_request_options_for_call(options), canonical_owner, identifier
            )

        owner = make_hex_eth_address(canonical_owner)

        if isinstance(owner, HexBytes):
            owner = owner.hex()

        return SOCReader(owner=owner, download=__download)

    def make_soc_writer(
        self,
        signer: Optional[Union[Signer, bytes, str]],
        options: Optional[BeeRequestOptions] = None,
    ) -> SOCWriter:
        """
        Returns an object for reading and writing single owner chunks.

        Args:
            signer (str): The signer's private key or a Signer instance that can sign data.
            options (dict): Options that affects the request behavior.

        Returns:
            SOCWriter: An object for reading and writing single owner chunks.

        See Also:
            Bee docs - Chunk Types: https://docs.ethswarm.org/docs/dapps-on-swarm/chunk-types#single-owner-chunks
        """
        assert_request_options(options)

        canonical_signer = self.__resolve_signer(signer)
        if isinstance(canonical_signer, Signer):
            canonical_signer = Signer.signer  # type: ignore

        reader = self.make_soc_reader(canonical_signer.address, options)  # type: ignore[attr-defined]

        def __upload(postage_batch_id: Union[str, BatchId], identifier: Identifier, data: bytes):
            return upload_single_owner_chunk_data(
                postage_batch_id=postage_batch_id,
                request_options=self.__get_request_options_for_call(options),
                identifier=identifier,
                data=data,
                signer=canonical_signer,
            )

        return SOCWriter(owner=reader.owner, download=reader.download, upload=__upload)

    def check_connection(self, options: Optional[BeeRequestOptions] = None) -> None:
        """
        Pings the Bee node to see if there's a live Bee node on the URL provided.

        Args:
            options: Options that affects the request behavior

        Returns:
            A Promise that resolves to `True` if the connection was successful, and `False` if it wasn't

        Raises:
            If connection was not successful throw error
        """
        assert_request_options(options)

        status_api.check_connection(self.__get_request_options_for_call(options))

    def is_connected(self, options: Optional[BeeRequestOptions] = None) -> bool:
        """
        Checks the connection to the Bee node to see if it's alive.

        Args:
            options: Options that affects the request behavior

        Returns:
            A boolean indicating the connection status: `True` if connected, `False` if not
        """
        assert_request_options(options, "PostageBatchOptions")

        try:
            status_api.check_connection(self.__get_request_options_for_call(options))
        except HTTPError:
            return False
        return True

    def get_postage_batch(
        self,
        postage_batch_id: Union[BatchId, str],
        options: Optional[Union[BeeRequestOptions, dict]] = None,
    ) -> PostageBatch:
        """Retrieves details for a specific postage batch.

        Args:
            postage_batch_id: The ID of the batch to retrieve.
            options: Optional request options to customize the request.

        Returns:
            The details of the postage batch.

        Raises:
            ValueError: If the batch ID is invalid.

        See Also:
            - Bee docs: https://docs.ethswarm.org/docs/access-the-swarm/keep-your-data-alive
            - Bee Debug API reference: https://docs.ethswarm.org/debug-api/#tag/Postage-Stamps/paths/~1stamps~1{id}/get
        """

        assert_request_options(options)
        assert_batch_id(postage_batch_id)

        return stamps.get_postage_batch(self.__get_request_options_for_call(options), postage_batch_id)  # type: ignore

    def wait_for_usable_postage_stamp(self, batch_id: Union[BatchId, str], timeout: int = 120_000) -> None:
        """Waits for a postage stamp with the given batch ID to become usable.

        Args:
            batch_id: The ID of the postage batch to wait for.
            timeout: The maximum time in milliseconds to wait before raising a timeout error.

        Raises:
            BeeError: If the timeout is reached before the stamp becomes usable.
        """

        # * Check every 1.5 seconds
        TIME_STEP = 1500  # noqa: N806
        for _ in range(0, timeout, TIME_STEP):
            stamp = self.get_postage_batch(batch_id)
            if stamp.usable:
                return
            sleep(TIME_STEP / 1000)

        msg = "Timeout on waiting for postage stamp to become usable"
        raise BeeError(msg)

    def create_postage_batch(
        self,
        amount: Union[NumberString, str],
        depth: int,
        options: Optional[Union[PostageBatchOptions, dict]] = None,
        request_options: Optional[Union[BeeRequestOptions, dict]] = None,
    ) -> str:
        """Creates a new postage batch from the node's available funds.

        **WARNING: This creates transactions that spend money.**

        Args:
            amount: The value per chunk, as a positive integer or string representation.
            depth: The logarithm of the number of chunks that can be stamped with the batch, as a non-negative integer.
            options: Optional options for batch creation.
            request_options: Optional request options to customize the request.

        Returns:
            The ID of the created postage batch.

        Raises:
            BeeArgumentError: If the amount or depth is invalid.
            TypeError: If a non-integer value is passed for amount or depth.

        See Also:
            - Bee docs: https://docs.ethswarm.org/docs/access-the-swarm/keep-your-data-alive
            - Bee Debug API reference: https://docs.ethswarm.org/debug-api/#tag/Postage-Stamps/paths/~1stamps~1{amount}~1{depth}/post
        """  # noqa: 501

        assert_postage_batch_options(options)
        assert_positive_integer(amount)
        assert_non_negative_integer(depth)

        if isinstance(options, dict):
            options = PostageBatchOptions.model_validate(options)

        if depth < STAMPS_DEPTH_MIN:
            msg = f"Depth has to be at least {STAMPS_DEPTH_MIN}"
            raise BeeArgumentError(msg, depth)
        if depth > STAMPS_DEPTH_MAX:
            msg = f"Depth has to be at most {STAMPS_DEPTH_MAX}"
            raise BeeArgumentError(msg, depth)

        stamp = stamps.create_postage_batch(
            self.__get_request_options_for_call(request_options), amount, depth, options  # type: ignore
        )

        if options:
            if options.wait_for_usable:
                self.wait_for_usable_postage_stamp(stamp, options.wait_for_usable_timeout)  # type: ignore

        return stamp
