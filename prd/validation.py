import typer
import re


def validate_academic_year(value: str) -> str:
    """Validate academic year option.

    Args:
        value (str): The value of the academic year option.

    Raises:
        typer.BadParameter: If the value is not valid.

    Returns:
        str: The value itself.
    """
    if value is not None:
        academic_year_r = re.compile("^20([0-9]{2})-([0-9]{2})$")
        if academic_year_r.match(value) is None:
            raise typer.BadParameter(
                'The course academic year must be in the format "2021-22".'
            )

        result: re.Match[str] = academic_year_r.search(value)
        y1: int = int(result.group(1))
        y2: int = int(result.group(2))
        if y1 + 1 != y2:
            raise typer.BadParameter(
                'The course academic year must be in the format "2021-22".'
            )

    return value


def validate_cookie_name(name: str) -> str:
    """Validate name option of set-cookie.

    Args:
        name (str): The cookie name

    Raises:
        typer.BadParameter: If the cookie name is invalid.

    Returns:
        str: The name as is.
    """
    if name not in ["SSL_JSESSIONID", "ticket", "MoodleSession"]:
        raise typer.BadParameter(
            'Possible values are "SSL_JSESSIONID", "ticket" and "MoodleSession".'
        )
    return name
