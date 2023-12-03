import pytest

from bee_py.modules.status import check_connection


@pytest.mark.asyncio
def test_check_connection(bee_ky_options):
    check_connection(bee_ky_options)
