import os
from Config import Config
import typer
import json

COOKIE_STORE_FILEPATH: str = os.path.join(
    typer.get_app_dir(Config.APP_NAME), Config.COOKIES_STORE_FILENAME
)


def save_cookie(name: str, value: str) -> None:
    """Save a cookie.

    Args:
        name (str): Name of the cookie.
        value (str): Value of the cookie.
    """
    try:
        with open(COOKIE_STORE_FILEPATH) as f:
            data = json.load(f)
    except:
        data = {}
    finally:
        data[name] = value
        with open(COOKIE_STORE_FILEPATH, "w") as f:
            json.dump(data, f)


def get_cookie(name: str) -> str:
    """Get the value of a cookie.

    Args:
        name (str): Name of the cookie.

    Returns:
        str: Value of the cookie.

    Raises:
        ValueError: If the the cookie does not exists.
    """
    cookie_exists: bool = True
    try:
        with open(COOKIE_STORE_FILEPATH, "r") as f:
            try:
                data: dict = json.load(f)
                if name in data.keys():
                    return data[name]
                cookie_exists = False
            except json.decoder.JSONDecodeError:
                cookie_exists = False
    except FileNotFoundError:
        cookie_exists = False

    if not cookie_exists:
        raise ValueError("The cookie " + name + " is not set.")


def check_cookie(name: str) -> None:
    """Check if a cookie exists. If not exit from typer.

    Args:
        name (str): Name of the cookie.

    Raises:
        typer.Exit: Exit from typer if cookie does not exists.
    """
    try:
        get_cookie(name)
    except ValueError as e:
        typer.echo(e)
        raise typer.Exit(1)
