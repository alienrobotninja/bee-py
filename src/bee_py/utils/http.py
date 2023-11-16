import requests

DEFAULT_HTTP_CONFIG = {
    "headers": {
        "accept": "application/json, text/plain, */*",
    },
}


def http(options: dict, config: dict) -> requests.Response:
    """Makes an HTTP request.

    Args:
      options: User defined settings.
      config: Internal settings and/or Bee settings.

    Returns:
      A requests.Response object.
    """

    try:
        request_config = {
            "headers": DEFAULT_HTTP_CONFIG["headers"].copy(),
            **config,
            **options,
        }
        request_config = maybe_run_on_request_hook(options, request_config)
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

    if options.get("onRequest"):
        new_request_config = request_config.copy()
        hook_result = {
            "method": request_config.get("method", "GET"),
            "url": request_config["url"],
            "headers": request_config["headers"],
            "params": request_config.get("params"),
        }

        if hook_result:
            new_request_config["url"] = hook_result.get("url")
            new_request_config["headers"] = hook_result.get("headers")
            new_request_config["params"] = hook_result.get("params")

            # Remove baseURL from the final result
            new_request_config.pop("baseURL", None)
            new_request_config.pop("onRequest", None)

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
