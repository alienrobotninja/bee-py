import pytest

from bee_py.utils.http import http

MOCK_SERVER_URL = "http://localhost:12345/"


def test_http_with_requests_mock(requests_mock, ky_options):
    HTML_RESPONSE = "<html><body><h1>Some error!</h1></body></html>"  # noqa: N806
    requests_mock.get("http://localhost:12345/endpoint", text=HTML_RESPONSE)

    config = {"url": MOCK_SERVER_URL + "endpoint", "method": "get"}
    response = http(ky_options, config)

    assert response.status_code == 200
    assert response.content == HTML_RESPONSE.encode("utf-8")


def test_handle_non_json_response_for_404(requests_mock, ky_options):
    HTML_RESPONSE = "<html><body><h1>Some error!</h1></body></html>"  # noqa: N806
    requests_mock.get("http://localhost:12345/endpoint", text=HTML_RESPONSE, status_code=404)

    config = {"url": "/endpoint", "responseType": "json", "method": "get"}
    with pytest.raises(TypeError):
        http(ky_options, config)