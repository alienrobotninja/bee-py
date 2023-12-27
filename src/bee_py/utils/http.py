from typing import Optional, Union
from urllib.parse import urljoin

import requests
from deepmerge import always_merger  # type: ignore

from bee_py.types.type import BeeRequestOptions

DEFAULT_HTTP_CONFIG = {
    "headers": {
        "accept": "application/json, text/plain, */*",
    },
}


def sanitise_config(options: Union[BeeRequestOptions, dict]) -> Union[BeeRequestOptions, dict]:
    bad_configs = ["address", "signer", "Type", "limit", "offset"]
    if isinstance(options, BeeRequestOptions):
        options = options.model_dump()

    query_params = []
    keys_to_remove = []

    for key, value in options.get("params", {}).items():
        if key and key not in bad_configs:
            if key not in [True, False]:
                if key == "type":
                    if not isinstance(value, str):
                        value = str(value.value)  # noqa: PLW2901
                query_params.append(f"{key}={value}")
                if key != "type":
                    keys_to_remove.append(key)

    for key in keys_to_remove:
        options["params"].pop(key, None)

    for bad_key in bad_configs:
        options.pop(bad_key, None)

    return options


def http(
    options: Union[BeeRequestOptions, dict],
    config: dict,
    sanitise: Optional[bool] = True,  # noqa: FBT002
) -> requests.Response:
    """Makes an HTTP request.

    Args:
      options: User defined settings.
      config: Internal settings and/or Bee settings.
      sanitise: remove signer & other unintended settings from config

    Returns:
      A requests.Response object.
    """

    # * convert the bee request options to a dictionary
    if isinstance(options, BeeRequestOptions):
        tmp_options = options.model_dump()
        # * Dictionary to map old keys to new keys
        key_mapping = {"base_url": "baseURL", "on_request": "onRequest"}

        # * Replace keys
        options = {key_mapping.get(k, k): v for k, v in tmp_options.items()}
    else:  # noqa: PLR5501
        if options:
            tmp_options = options
            key_mapping = {"base_url": "baseURL", "on_request": "onRequest"}
            options = {key_mapping.get(k, k): v for k, v in tmp_options.items()}

    try:
        intermediate_dict = always_merger.merge(config, options)
        request_config = always_merger.merge(intermediate_dict, {"headers": DEFAULT_HTTP_CONFIG["headers"].copy()})

        request_config = maybe_run_on_request_hook(options, request_config)

        if sanitise:
            request_config = sanitise_config(request_config)
        if "http" not in request_config["url"]:
            msg = f"Invalid URL: {request_config['url']}"
            raise TypeError(msg)
        response = requests.request(**request_config)
        return response
    except Exception as e:
        raise e


def maybe_run_on_request_hook(options: dict, request_config: dict) -> dict:
    """Runs the onRequest hook if it is defined.

    Args:
      options: User defined settings.
      request_config: The request configuration.
    """
    if not options:
        return {}
    if options.get("onRequest"):
        new_request_config = request_config.copy()
        hook_result = {
            "method": request_config.get("method", "GET"),
            "url": urljoin(request_config.get("baseURL", ""), request_config.get("url", "")),
            "headers": request_config.get("headers", {}),
            "params": request_config.get("params", {}),
        }

        if hook_result:
            new_request_config["url"] = hook_result.get("url")
            new_request_config["headers"] = hook_result.get("headers")
            new_request_config["params"] = hook_result.get("params")

            # Remove baseURL from the final result
            new_request_config.pop("baseURL", None)
            new_request_config.pop("onRequest", None)
            new_request_config.pop("retry", None)
        return new_request_config

    return request_config


def maybe_run_on_request_hook2(options: dict, request_config: dict) -> None:
    """Runs the onRequest hook if it is defined.

    Args:
      options: User defined settings.
      request_config: The request configuration.
    """

    if options.get("onRequest"):
        options["onRequest"](request_config)
