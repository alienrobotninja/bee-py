from typing import Optional

from bee_py.chunk.signer import sign
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
