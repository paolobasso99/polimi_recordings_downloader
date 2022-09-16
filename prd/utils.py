from typing import List
from datetime import datetime


def replace_illegal_characters(string: str) -> str:
    """Replace the illegal characters in a string. Such characters are < > : " / \\ | ? * .

    Args:
        string (str): The string.

    Returns:
        str: The resulting string without illegal characters"
    """
    TO_REPLACE: List[str] = ["<", ">", ":", '"', "/", "\\", "|", "?", "*", "."]
    for c in TO_REPLACE:
        string = string.replace(c, "")

    return string


def extract_academic_year_from_datetime(dt: datetime) -> str:
    """Extract the academic year in the format "2020-21" from a datetime.

    Args:
        dt (datetime): The datetime.

    Returns:
        str: The academic year in the format "2020-22".
    """
    starting_year: str = dt.strftime("%Y")
    end_year: str = dt.replace(year=dt.year + 1).strftime("%y")
    if dt.month < 8:
        end_year = dt.strftime("%y")
        starting_year = dt.replace(year=dt.year - 1).strftime("%Y")
    return starting_year + "-" + end_year
