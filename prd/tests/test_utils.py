from datetime import datetime

from prd.utils import extract_academic_year_from_datetime, replace_illegal_characters


def test_extract_academic_year_from_datetime():
    assert extract_academic_year_from_datetime(datetime(2022, 7, 30, 10, 10, 10)) == "2021-22"
    assert extract_academic_year_from_datetime(datetime(2022, 8, 30, 10, 10, 10)) == "2022-23"

def test_replace_illegal_characters():
    assert replace_illegal_characters("<>:\"/\\|TEST,'^?*.") == "TEST,'^"