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
        academic_year_r = re.compile("^[0-9]{4}-[0-9]{2}$")
        if academic_year_r.match(value) is None:
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
    if name != "SSL_JSESSIONID" and name != "ticket" and name != "MoodleSession":
        raise typer.BadParameter(
            'Possible values are "SSL_JSESSIONID", "ticket" and "MoodleSession".'
        )
    return name
