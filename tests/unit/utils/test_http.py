from bee_py.utils.http import http

BEE_API_URL = "http://localhost:12345/"


def test_http_with_requests_mock(requests_mock, ky_options):
    HTML_RESPONSE = "<html><body><h1>Some error!</h1></body></html>"  # noqa: N806
    requests_mock.get("http://localhost:12345/endpoint", text=HTML_RESPONSE)

    config = {"url": BEE_API_URL + "endpoint", "method": "get"}
    response = http(ky_options, config)

    assert response.status_code == 200
    assert response.content == HTML_RESPONSE.encode("utf-8")


def test_handle_non_json_response_for_404(requests_mock, ky_options):
    HTML_RESPONSE = "<html><body><h1>Some error!</h1></body></html>"  # noqa: N806
    requests_mock.get("http://localhost:12345/endpoint", text=HTML_RESPONSE, status_code=404)

    config = {"url": BEE_API_URL + "endpoint", "method": "get"}
    response = http(ky_options, config)

    assert response.status_code == 404
