from time import sleep
from typing import Optional, Union

from ape.types import AddressType

from bee_py.modules.debug import (
    balance,
    chequebook,
    connectivity,
    settlements,
    stake,
    stamps,
    states,
    status,
    tag,
    transactions,
)
from bee_py.types.debug import BeeVersions, DebugStatus, Health, NodeInfo
from bee_py.types.type import (
    STAMPS_DEPTH_MAX,
    STAMPS_DEPTH_MIN,
    AllSettlements,
    AllTagsOptions,
    BalanceResponse,
    BatchId,
    BeeOptions,
    BeeRequestOptions,
    CashoutOptions,
    ChainState,
    ChequebookAddressResponse,
    ChequebookBalanceResponse,
    ExtendedTag,
    JsonFeedOptions,
    LastCashoutActionResponse,
    LastChequesForPeerResponse,
    LastChequesResponse,
    NodeAddresses,
    NumberString,
    PeerBalance,
    Peers,
    PingResponse,
    PostageBatch,
    PostageBatchBuckets,
    PostageBatchOptions,
    RedistributionState,
    RemovePeerResponse,
    ReserveState,
    Settlements,
    Tag,
    Topology,
    TransactionHash,
    TransactionInfo,
    TransactionOptions,
    WalletBalance,
)
from bee_py.utils.error import BeeArgumentError, BeeError
from bee_py.utils.type import (
    assert_address,
    assert_batch_id,
    assert_cashout_options,
    assert_non_negative_integer,
    assert_positive_integer,
    assert_postage_batch_options,
    assert_request_options,
    assert_transaction_hash,
    assert_transaction_options,
)
from bee_py.utils.urls import assert_bee_url, strip_last_slash


class BeeDebug:
    """
    The main component that abstracts operations available on the main Bee Debug API.

    Attributes:
        url: URL on which is the Debug API of Bee node exposed.
        request_options: Ky instance that defines connection to Bee node.
    """

    url: str
    request_options: BeeRequestOptions

    def __init__(self, url: str, options: Optional[Union[BeeOptions, dict]] = None):
        """
        Constructs a new BeeDebug instance.

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
    ) -> Union[BeeRequestOptions, dict]:
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

    def get_node_address(self, options: Optional[Union[BeeRequestOptions, dict]] = None) -> NodeAddresses:
        """
        Gets the node addresses.

        Parameters:
            options (BeeRequestOptions, dict, None): Request options. Defaults to None.

        Returns:
            NodeAddresses: The node addresses.
        """
        assert_request_options(options)

        return connectivity.get_node_addresses(self.__get_request_options_for_call(options))  # type: ignore

    def get_blocklist(self, options: Optional[Union[BeeRequestOptions, dict]] = None) -> Peers:
        """Retrieves the list of blocked peers from the network.

        Args:
            options: Optional request options to customize the request.

        Returns:
            A list of blocked peers.

        Raises:
            AssertionError: If invalid request options are provided.
        """
        assert_request_options(options)

        return connectivity.get_blocklist(self.__get_request_options_for_call(options))  # type: ignore

    def retrieve_extended_tag(
        self, tag_uid: Union[int, Tag], options: Optional[Union[BeeRequestOptions, dict]] = None
    ) -> ExtendedTag:
        """Retrieves extended information about a tag from the Bee node.

        Args:
            tag_uid: The UID or Tag object of the tag to retrieve.
            options: Optional request options to customize the request.

        Returns:
            The extended information about the tag.

        Raises:
            TypeError: If tag_uid is not a number or a Tag object.
            AssertionError: If invalid request options are provided.
        """

        assert_request_options(options)

        if isinstance(tag_uid, Tag):
            tag_uid = tag_uid.uid
        elif isinstance(tag_uid, int):
            assert_non_negative_integer(tag_uid, "UID")
        else:
            msg = "tag_uid must be a Tag object or a non-negative integer."
            raise TypeError(msg)

        return tag.retrieve_extended_tag(self.__get_request_options_for_call(options), tag_uid)  # type: ignore

    def get_peers(self, options: Optional[Union[BeeRequestOptions, dict]] = None) -> Peers:
        """Retrieves a list of peers for the current node.

        Args:
            options: Optional request options to customize the request.

        Returns:
            A list of peers.

        Raises:
            AssertionError: If invalid request options are provided.
        """
        assert_request_options(options)

        return connectivity.get_peers(self.__get_request_options_for_call(options))  # type: ignore

    def remove_peer(
        self, peer: Union[str, AddressType], options: Optional[Union[BeeRequestOptions, dict]] = None
    ) -> RemovePeerResponse:
        """Removes a peer from the current node's peer list.

        Args:
            peer: The peer to remove, as a string or Address object.
            options: Optional request options to customize the request.

        Returns:
            The response from the peer removal operation.

        Raises:
            AssertionError: If invalid request options or peer address are provided.
        """
        assert_request_options(options)
        assert_address(peer)

        return connectivity.remove_peer(self.__get_request_options_for_call(options), peer)  # type: ignore

    def get_topology(self, options: Optional[Union[BeeRequestOptions, dict]] = None) -> Topology:
        """Retrieves the topology information from the network.

        Args:
            options: Optional request options to customize the request.

        Returns:
            The topology information.

        Raises:
            AssertionError: If invalid request options are provided.
        """
        assert_request_options(options)

        return connectivity.get_topology(self.__get_request_options_for_call(options))  # type: ignore

    def ping_peer(
        self, peer: Union[str, AddressType], options: Optional[Union[BeeRequestOptions, dict]] = None
    ) -> PingResponse:
        """Pings a peer to check connectivity.

        Args:
            peer: The peer to ping, as a string or Address object.
            options: Optional request options to customize the request.

        Returns:
            The response from the peer ping operation, indicating connectivity status.

        Raises:
            AssertionError: If invalid request options or peer address are provided.
        """

        assert_request_options(options)
        assert_address(peer)

        return connectivity.ping_peer(self.__get_request_options_for_call(options), peer)  # type: ignore

    # ? Balances Endpoint
    def get_all_balances(self, options: Optional[Union[BeeRequestOptions, dict]] = None) -> BalanceResponse:
        """Retrieves the balances with all known peers, including prepaid services.

        Args:
            options: Optional request options to customize the request.

        Returns:
            The balances with all known peers.

        Raises:
            AssertionError: If invalid request options are provided.
        """
        assert_request_options(options)

        return balance.get_all_balances(self.__get_request_options_for_call(options))  # type: ignore

    def get_peer_balance(
        self, address: Union[AddressType, str], options: Optional[Union[BeeRequestOptions, dict]] = None
    ) -> PeerBalance:
        """Retrieves the balances with a specific peer, including prepaid services.

        Args:
            address: The Swarm address of the peer.
            options: Optional request options to customize the request.

        Returns:
            The balances with the specified peer.

        Raises:
            AssertionError: If invalid request options or peer address are provided.
        """
        assert_request_options(options)
        assert_address(address)

        return balance.get_peer_balance(self.__get_request_options_for_call(options), address)  # type: ignore

    def et_past_due_consumption_balances(
        self, options: Optional[Union[BeeRequestOptions, dict]] = None
    ) -> BalanceResponse:
        """Retrieves the past due consumption balances with all known peers.

        Args:
            options: Optional request options to customize the request.

        Returns:
            The past due consumption balances with all known peers.

        Raises:
            AssertionError: If invalid request options are provided.
        """

        assert_request_options(options)

        return balance.get_past_due_consumption_balances(self.__get_request_options_for_call(options))  # type: ignore

    def get_past_due_consumption_peer_balance(
        self, address: Union[AddressType, str], options: Optional[Union[BeeRequestOptions, dict]] = None
    ) -> PeerBalance:
        """Retrieves the past due consumption balance with a specific peer.

        Args:
            address: The Swarm address of the peer.
            options: Optional request options to customize the request.

        Returns:
            The past due consumption balance with the specified peer.

        Raises:
            AssertionError: If invalid request options or peer address are provided.
        """

        assert_request_options(options)
        assert_address(address)

        return balance.get_past_due_consumption_peer_balance(self.__get_request_options_for_call(options), address)  # type: ignore # noqa: 501

    # ? Chequebook endpoints
    def get_chequebook_address(
        self, options: Optional[Union[BeeRequestOptions, dict]] = None
    ) -> ChequebookAddressResponse:
        """Retrieves the address of the chequebook contract used.

        Returns:
            The address of the chequebook contract, with a 0x prefix.

        Raises:
            AssertionError: If invalid request options are provided.

        Warning:
            The address is returned with a 0x prefix, unlike other calls.
            See https://github.com/ethersphere/bee/issues/1443 for details.
        """

        assert_request_options(options)

        return chequebook.get_chequebook_address(self.__get_request_options_for_call(options))  # type: ignore

    def get_chequebook_balance(
        self, options: Optional[Union[BeeRequestOptions, dict]] = None
    ) -> ChequebookBalanceResponse:
        """Retrieves the balance of the chequebook.

        Returns:
            The balance of the chequebook.

        Raises:
            AssertionError: If invalid request options are provided.
        """

        assert_request_options(options)

        return chequebook.get_chequebook_balance(self.__get_request_options_for_call(options))  # type: ignore

    def get_last_cheques(self, options: Optional[Union[BeeRequestOptions, dict]] = None) -> LastChequesResponse:
        """Retrieves the last cheques for all peers.

        Returns:
            The last cheques for all peers.

        Raises:
            AssertionError: If invalid request options are provided.
        """

        assert_request_options(options)

        return chequebook.get_last_cheques(self.__get_request_options_for_call(options))  # type: ignore

    def get_last_cheques_for_peer(
        self, address: Union[AddressType, str], options: Optional[Union[BeeRequestOptions, dict]] = None
    ) -> LastChequesForPeerResponse:
        """Retrieves the last cheques for a specific peer.

        Args:
            address: The Swarm address of the peer.
            options: Optional request options to customize the request.

        Returns:
            The last cheques for the specified peer.

        Raises:
            AssertionError: If invalid request options or peer address are provided.
        """

        assert_request_options(options)
        assert_address(address)

        return chequebook.get_last_cheques_for_peer(self.__get_request_options_for_call(options), address)  # type: ignore # noqa: 501

    def get_last_cashout_action(
        self, address: Union[AddressType, str], options: Optional[Union[BeeRequestOptions, dict]] = None
    ) -> LastCashoutActionResponse:
        """Retrieves the last cashout action for a specific peer.

        Args:
            address: The Swarm address of the peer.
            options: Optional request options to customize the request.

        Returns:
            The last cashout action for the specified peer.

        Raises:
            AssertionError: If invalid request options or peer address are provided.
        """

        assert_request_options(options)
        assert_address(address)

        return chequebook.get_last_cashout_action(self.__get_request_options_for_call(options), address)  # type: ignore

    def cashout_last_cheque(
        self,
        address: Union[AddressType, str],
        options: Optional[Union[CashoutOptions, dict]] = None,
        request_options: Optional[Union[BeeRequestOptions, dict]] = None,
    ) -> str:
        """Cashes out the last cheque for a specific peer.

        Args:
            address: The Swarm address of the peer.
            options: Optional cashout options, including gas price and gas limit.
                - options.gasPrice: Gas price for the cashout transaction in WEI
                - options.gasLimit Gas limit for the cashout transaction in WEI
            request_options: Optional request options to customize the request.

        Returns:
            The transaction hash of the cashout operation.

        Raises:
            AssertionError: If invalid cashout options, request options, or peer address are provided.
        """

        assert_cashout_options(options)
        assert_address(address)

        return chequebook.cashout_last_cheque(self.__get_request_options_for_call(request_options), address, options)  # type: ignore # noqa: 501

    def deposit_tokens(
        self,
        amount: Union[int, str],
        gas_price: Optional[str] = None,
        options: Optional[Union[BeeRequestOptions, dict]] = None,
    ) -> TransactionHash:
        """Deposits tokens from the overlay address into the chequebook.

        Args:
            amount: The amount of tokens to deposit, as a positive integer or string representation.
            gas_price: Optional gas price in WEI for the transaction call.
            options: Optional request options to customize the request.

        Returns:
            The transaction hash of the deposit operation.

        Raises:
            AssertionError: If invalid request options, amount, or gas price are provided.
        """

        assert_request_options(options)
        assert_non_negative_integer(amount)

        if gas_price:
            assert_non_negative_integer(gas_price)

        return chequebook.deposit_tokens(self.__get_request_options_for_call(options), amount, gas_price)  # type: ignore # noqa: 501

    def withdraw_tokens(
        self,
        amount: Union[int, str],
        gas_price: Optional[str] = None,
        options: Optional[Union[BeeRequestOptions, dict]] = None,
    ) -> TransactionHash:
        """Withdraws tokens from the chequebook to the overlay address.

        Args:
            amount: The amount of tokens to withdraw, as a positive integer or string representation.
            gas_price: Optional gas price in WEI for the transaction call.
            options: Optional request options to customize the request.

        Returns:
            The transaction hash of the withdrawal operation.

        Raises:
            AssertionError: If invalid request options, amount, or gas price are provided.
        """

        assert_request_options(options)
        assert_non_negative_integer(amount)

        if gas_price:
            assert_non_negative_integer(gas_price)

        return chequebook.withdraw_tokens(self.__get_request_options_for_call(options), amount, gas_price)  # type: ignore # noqa: 501

    # ? Settlements endpoint
    def get_settlements(
        self, address: Union[AddressType, str], options: Optional[Union[BeeRequestOptions, dict]] = None
    ) -> Settlements:
        """Retrieves the amount of sent and received tokens from settlements with a specific peer.

        Args:
            address: The Swarm address of the peer.
            options: Optional request options to customize the request.

        Returns:
            The settlements information, including sent and received amounts.

        Raises:
            AssertionError: If invalid request options or peer address are provided.
        """

        assert_request_options(options)
        assert_address(address)

        return settlements.get_settlements(self.__get_request_options_for_call(options), address)  # type: ignore

    def get_all_settlements(self, options: Optional[Union[BeeRequestOptions, dict]] = None) -> AllSettlements:
        """Retrieves settlements with all known peers and total amounts sent or received.

        Args:
            options: Optional request options to customize the request.

        Returns:
            The settlements information for all peers.

        Raises:
            AssertionError: If invalid request options are provided.
        """

        assert_request_options(options)

        return settlements.get_all_settlements(self.__get_request_options_for_call(options))  # type: ignore

    def get_status(self, options: Optional[Union[BeeRequestOptions, dict]] = None) -> DebugStatus:
        """Retrieves the status of the node.

        Args:
            options: Optional request options to customize the request.

        Returns:
            The status information of the node.

        Raises:
            AssertionError: If invalid request options are provided.
        """

        assert_request_options(options)

        return status.get_debug_status(self.__get_request_options_for_call(options))  # type: ignore

    def get_health(self, options: Optional[Union[BeeRequestOptions, dict]] = None) -> Health:
        """Retrieves the health of the node.

        Args:
            options: Optional request options to customize the request.

        Returns:
            The health information of the node.

        Raises:
            AssertionError: If invalid request options are provided.
        """

        assert_request_options(options)

        return status.get_health(self.__get_request_options_for_call(options))  # type: ignore

    def get_readiness(self, options: Optional[Union[BeeRequestOptions, dict]] = None) -> bool:
        """Retrieves the readiness of the node.

        Args:
            options: Optional request options to customize the request.

        Returns:
            True if the node is ready, False otherwise.

        Raises:
            AssertionError: If invalid request options are provided.
        """

        assert_request_options(options)

        return status.get_readiness(self.__get_request_options_for_call(options))  # type: ignore

    def get_node_info(self, options: Optional[Union[BeeRequestOptions, dict]] = None) -> NodeInfo:
        """Retrieves the mode information of the node.

        Args:
            options: Optional request options to customize the request.

        Returns:
            The mode information of the node.

        Raises:
            AssertionError: If invalid request options are provided.
        """

        assert_request_options(options)

        return status.get_node_info(self.__get_request_options_for_call(options))  # type: ignore

    def is_supported_exact_version(self, options: Optional[Union[BeeRequestOptions, dict]] = None) -> bool:
        """**Deprecated:** Checks if the connected Bee node version is supported by bee-py.

        Use `BeeDebug.isSupportedExactVersion()` instead for more accurate version checking.

        Args:
            options: Optional request options to customize the request.

        Returns:
            True if the node version is supported, False otherwise.

        Raises:
            AssertionError: If invalid request options are provided.
        """

        assert_request_options(options)

        try:
            return status.is_supported_exact_version(self.__get_request_options_for_call(options))  # type: ignore
        except Exception as e:
            # logger.info(
            #     "Warning: `is_supported_version()` is deprecated. Use `BeeDebug.is_supported_exact_version()` instead."  # noqa: E501
            # )
            raise e

    def is_supported_main_api_version(self, options: Optional[Union[BeeRequestOptions, dict]] = None) -> bool:
        """Checks if the connected Bee node's main API version is supported by bee-js.

        Useful when not using the `BeeDebug` class for other functionality.

        Args:
            options: Optional request options to customize the request.

        Returns:
            True if the main API version is supported, False otherwise.

        Raises:
            AssertionError: If invalid request options are provided.
        """

        assert_request_options(options)

        return status.is_supported_main_api_version(self.__get_request_options_for_call(options))  # type: ignore

    def is_supported_debug_api_version(self, options: Optional[Union[BeeRequestOptions, dict]] = None) -> bool:
        """Checks if the connected Bee node's Debug API version is supported by bee-js.

        Useful when not using the `Bee` class in your application.

        Args:
            options: Optional request options to customize the request.

        Returns:
            True if the Debug API version is supported, False otherwise.

        Raises:
            AssertionError: If invalid request options are provided.
        """

        assert_request_options(options)

        return status.is_supported_debug_api_version(self.__get_request_options_for_call(options))  # type: ignore

    def is_supported_api_version(self, options: Optional[Union[BeeRequestOptions, dict]] = None) -> bool:
        """Checks if both the Main and Debug API versions of the connected Bee node are supported by bee-js.

        The primary way to ensure compatibility between your application and the Bee node.

        Args:
            options: Optional request options to customize the request.

        Returns:
            True if both API versions are supported, False otherwise.

        Raises:
            AssertionError: If invalid request options are provided.
        """

        assert_request_options(options)

        return status.is_supported_debug_api_version(self.__get_request_options_for_call(options))  # type: ignore

    def get_versions(self, options: Optional[Union[BeeRequestOptions, dict]] = None) -> BeeVersions:
        """Retrieves an object containing version information for the connected Bee node and bee-js.

        Args:
            options: Optional request options to customize the request.

        Returns:
            An object with properties for Bee node versions (prefixed with `bee*`) and supported versions by bee-js (prefixed with `supported*`).

        Raises:
            AssertionError: If invalid request options are provided.
        """  # noqa: E501

        assert_request_options(options)

        return status.get_versions(self.__get_request_options_for_call(options))  # type: ignore

    async def get_reserve_state(self, options: Optional[Union[BeeRequestOptions, dict]] = None) -> ReserveState:
        """Retrieves the reserve state.

        Args:
            options: Optional request options to customize the request.

        Returns:
            The reserve state information.

        Raises:
            AssertionError: If invalid request options are provided.
        """

        assert_request_options(options)

        return states.get_reserve_state(self.__get_request_options_for_call(options))  # type: ignore

    def get_chain_state(self, options: Optional[Union[BeeRequestOptions, dict]] = None) -> ChainState:
        """Retrieves the chain state.

        Args:
            options: Optional request options to customize the request.

        Returns:
            The chain state information.

        Raises:
            AssertionError: If invalid request options are provided.
        """

        assert_request_options(options)

        return states.get_chain_state(self.__get_request_options_for_call(options))  # type: ignore

    def get_wallet_balance(self, options: Optional[Union[BeeRequestOptions, dict]] = None) -> WalletBalance:
        """Retrieves the wallet balances for xDai and BZZ of the Bee node.

        Args:
            options: Optional request options to customize the request.

        Returns:
            An object containing the xDai and BZZ balances.

        Raises:
            AssertionError: If invalid request options are provided.
        """

        assert_request_options(options)

        return states.get_wallet_balance(self.__get_request_options_for_call(options))  # type: ignore

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

    def top_up_batch(
        self,
        postage_batch_id: Union[BatchId, str],
        amount: Union[str, NumberString],
        options: Optional[Union[BeeRequestOptions, dict]] = None,
    ) -> None:
        """Tops up an existing postage batch with additional BZZ tokens.

        WARNING: This creates transactions that spend money.

        Args:
            postage_batch_id: The ID of the batch to top up.
            amount: The amount of BZZ to add to the batch.
            options: Optional request options to customize the request.

        Raises:
            ValueError: If the amount is negative or the batch ID is invalid.

        References:
            - Bee docs: [Bee docs - Keep your data alive / Postage stamps](https://docs.ethswarm.org/docs/access-the-swarm/keep-your-data-alive)
            - Bee Debug API reference: [Bee Debug API reference - `PATCH /stamps/topup/${id}/${amount}`](https://docs.ethswarm.org/debug-api/#tag/Postage-Stamps/paths/~1stamps~1topup~1{id}~1{amount}/patch)
        """  # noqa: 501

        assert_request_options(options)
        assert_non_negative_integer(amount, "Amount")
        assert_batch_id(postage_batch_id)

        stamps.top_up_batch(self.__get_request_options_for_call(options), postage_batch_id, amount)  # type: ignore

    def dilute_batch(
        self,
        postage_batch_id: Union[BatchId, str],
        depth: int,
        options: Optional[Union[BeeRequestOptions, dict]] = None,
    ) -> None:
        """Dilutes an existing postage batch with a new depth, allowing it to be used for more chunks.

        WARNING: This creates transactions that spend money.

        Args:
            postage_batch_id: The ID of the batch to dilute.
            depth: The new depth for the batch, which must be greater than the original depth.
            options: Optional request options to customize the request.

        Raises:
            ValueError: If the depth is negative or the batch ID is invalid.

        References:
            - Bee docs: https://docs.ethswarm.org/docs/access-the-swarm/keep-your-data-alive
            - Bee Debug API reference: https://docs.ethswarm.org/debug-api/#tag/Postage-Stamps/paths/~1stamps~1topup~1{id}~1{amount}/patch
        """  # noqa: 501

        assert_request_options(options)
        assert_non_negative_integer(depth)
        assert_batch_id(postage_batch_id)

        stamps.dilute_batch(self.__get_request_options_for_call(options), postage_batch_id, depth)  # type: ignore

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

    def get_postage_batch_buckets(
        self,
        postage_batch_id: Union[BatchId, str],
        options: Optional[Union[BeeRequestOptions, dict]] = None,
    ) -> PostageBatchBuckets:
        """Retrieves detailed information related to buckets for a specific postage batch.

        Args:
            postage_batch_id: The ID of the batch to retrieve bucket information for.
            options: Optional request options to customize the request.

        Returns:
            The detailed bucket information for the postage batch.

        Raises:
            ValueError: If the batch ID is invalid.

        See Also:
            - Bee docs: https://docs.ethswarm.org/docs/access-the-swarm/keep-your-data-alive
            - Bee Debug API reference: https://docs.ethswarm.org/debug-api/#tag/Postage-Stamps/paths/~1stamps~1{id}~1buckets/get
        """  # noqa: 501

        assert_request_options(options)
        assert_batch_id(postage_batch_id)

        return stamps.get_postage_batch_buckets(self.__get_request_options_for_call(options), postage_batch_id)  # type: ignore # noqa: 501

    def get_all_postage_batches(self, options: Optional[Union[BeeRequestOptions, dict]] = None) -> list[PostageBatch]:
        """Retrieves all postage batches available on the node.

        Args:
            options: Optional request options to customize the request.

        Returns:
            A list of all available postage batches.

        See Also:
            - Bee docs: https://docs.ethswarm.org/docs/access-the-swarm/keep-your-data-alive
            - Bee Debug API reference: https://docs.ethswarm.org/debug-api/#tag/Postage-Stamps/paths/~1stamps/get
        """

        assert_request_options(options)

        return stamps.get_all_postage_batches(self.__get_request_options_for_call(options))  # type: ignore

    def get_all_global_postage_batches(
        self, options: Optional[Union[BeeRequestOptions, dict]] = None
    ) -> list[PostageBatch]:
        """Retrieves all globally available postage batches.

        Args:
            options: Optional request options to customize the request.

        Returns:
            A list of all globally available postage batches.
        """

        assert_request_options(options)

        return stamps.get_global_postage_batches(self.__get_request_options_for_call(options))  # type: ignore

    # ? transcation endpoint
    def get_all_pending_transactions(
        self, options: Optional[Union[BeeRequestOptions, dict]] = None
    ) -> list[TransactionInfo]:
        """Retrieves lists of all current pending transactions that the Bee made.

        Args:
            options: Optional request options to customize the request.

        Returns:
            A list of pending transaction information objects.
        """

        assert_request_options(options)  # Assuming a function to validate options

        return transactions.get_all_transactions(self.__get_request_options_for_call(options))  # type: ignore

    def get_pending_transaction(
        self,
        transaction_hash: Union[str, TransactionHash],
        options: Optional[Union[BeeRequestOptions, dict]] = None,
    ) -> TransactionInfo:
        """Retrieves transaction information for a specific pending transaction.

        Args:
            transaction_hash: The hash of the transaction to retrieve information forebr
        Raises:
            ValueError: If the transaction hash is invalid.
        """

        assert_request_options(options)
        assert_transaction_hash(transaction_hash)

        return transactions.get_transaction(self.__get_request_options_for_call(options), transaction_hash)  # type: ignore # noqa: 501

    def rebroadcast_pending_transaction(
        self,
        transaction_hash: Union[str, TransactionHash],
        options: Optional[Union[BeeRequestOptions, dict]] = None,
    ) -> TransactionHash:
        """Rebroadcasts an already created pending transaction.

        This is useful when a transaction has fallen out of the mempool or needs to be retransmitted for other reasons.

        Args:
            transaction_hash: The hash of the transaction to rebroadcast.
            options: Optional request options to customize the request.

        Returns:
            The transaction hash of the rebroadcast transaction.

        Raises:
            ValueError: If the transaction hash is invalid.
        """

        assert_request_options(options)
        assert_transaction_hash(transaction_hash)

        return transactions.rebroadcast_transaction(self.__get_request_options_for_call(options), transaction_hash)  # type: ignore # noqa: 501

    def cancel_pending_transaction(
        self,
        transaction_hash: str,
        gas_price: Optional[Union[NumberString, str]] = None,
        options: Optional[Union[BeeRequestOptions, dict]] = None,
    ) -> TransactionHash:
        """Cancels a currently pending transaction.

        Args:
            transaction_hash: The hash of the transaction to cancel.
            gas_price: Optional gas price to use for the cancellation transaction.
            options: Optional request options to customize the request.

        Returns:
            The transaction hash of the cancellation transaction.

        Raises:
            ValueError: If the transaction hash is invalid or the gas price is negative.
        """

        assert_request_options(options)
        assert_transaction_hash(transaction_hash)
        if gas_price:
            assert_non_negative_integer(gas_price)

        return transactions.cancel_transaction(
            self.__get_request_options_for_call(options), transaction_hash, gas_price  # type: ignore
        )

    def get_stake(self, options: Optional[Union[BeeRequestOptions, dict]] = None) -> Union[str, NumberString]:
        """Retrieves the staked amount of BZZ (in PLUR units) as a string.

        Args:
            options: Optional request options to customize the request.

        Returns:
            The staked amount of BZZ as a string representing a number.
        """

        assert_request_options(options)

        return stake.get_stake(self.__get_request_options_for_call(options))  # type: ignore

    def deposit_stake(
        self,
        amount: str,
        options: Optional[Union[TransactionOptions, dict]] = None,
        request_options: Optional[Union[BeeRequestOptions, dict]] = None,
    ) -> None:
        """Deposits a given amount of BZZ tokens in PLUR units.

        Caution: Staked BZZ tokens cannot be withdrawn.

        Args:
            amount: The amount of BZZ to stake in PLUR units (minimum 100_000_000_000_000_000 PLUR, equivalent to 10 BZZ).
            options: Optional transaction options to customize the staking transaction.
            request_options: Optional request options to customize the API request.

        Raises:
            ValueError: If the amount is invalid or below the minimum.
        """  # noqa: E501

        assert_request_options(request_options)
        assert_transaction_options(options)
        # * Validate amount (e.g., ensure it's a non-negative integer and meets the minimum requirement)

        stake.stake(self.__get_request_options_for_call(request_options), amount, options)  # type: ignore

    def get_redistribution_state(self, options: Optional[Union[BeeRequestOptions, dict]] = None) -> RedistributionState:
        """Retrieves the current status of the node in the redistribution game.

        Args:
            options: Optional request options to customize the request.

        Returns:
            The redistribution state information.
        """

        assert_request_options(options)

        return stake.get_redistribution_state(self.__get_request_options_for_call(options))  # type: ignore

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
