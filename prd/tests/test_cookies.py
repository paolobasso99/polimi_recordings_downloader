import json
import os

from prd.cookies import save_cookie, get_cookie

def test_cookies(mocker, tmp_path):
    mocker.patch("prd.cookies.COOKIE_STORE_FILEPATH", os.path.join(tmp_path, './cookies.json'))
    save_cookie("TESTNAME1", "TESTVALUE1")
    assert get_cookie("TESTNAME1") == "TESTVALUE1"

def test_save_cookie(mocker, tmp_path):
    tmp_cookies_store = os.path.join(tmp_path, './cookies.json')
    mocker.patch("prd.cookies.COOKIE_STORE_FILEPATH", tmp_cookies_store)
    save_cookie("TESTNAME2", "TESTVALUE2")
    with open(tmp_cookies_store) as f:
        data = json.load(f)
        assert data["TESTNAME2"] == "TESTVALUE2"
