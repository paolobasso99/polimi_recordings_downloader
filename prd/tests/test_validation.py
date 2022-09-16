import pytest
from typer import BadParameter

from prd.validation import validate_academic_year, validate_cookie_name


def test_validate_academic_year():
    assert validate_academic_year("2019-20") == "2019-20"

    with pytest.raises(Exception) as e:
        validate_academic_year("202-1")
    assert type(e.value) == BadParameter

    with pytest.raises(Exception) as e:
        validate_academic_year("2020-1")
    assert type(e.value) == BadParameter

    with pytest.raises(Exception) as e:
        validate_academic_year("2019-18")

    with pytest.raises(Exception) as e:
        validate_academic_year("2019-28")
    assert type(e.value) == BadParameter

def test_validate_cookie_name():
    for s in ["SSL_JSESSIONID", "ticket", "MoodleSession"]:
        assert validate_cookie_name(s) == s

    with pytest.raises(Exception) as e:
        validate_cookie_name("TEST")
    assert type(e.value) == BadParameter