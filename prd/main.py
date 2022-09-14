import typer
import pathlib
from typing import List
from rich import print
import os

from prd.cookies import save_cookie, get_cookie
from prd.validation import validate_academic_year
from prd.webex_api import Recording
from prd.config import Config
from prd.parsers import (
    ArchivesParser,
    TxtParser,
    WebeepParser,
    WebpageParser,
)
from prd.create_output import create_output

app: typer.Typer = typer.Typer(add_completion=False)


@app.command()
def archives(
    url: str = typer.Argument(..., help="The URL to the recordings archive"),
    output: str = typer.Option(
        os.path.join(pathlib.Path().resolve(), Config.DEFAULT_OUTPUT_FOLDER),
        help="The output path",
    ),
    aria2c: bool = typer.Option(
        True, help="Download with aria2c or just create a file with the download links"
    ),
    create_xlsx: bool = typer.Option(True, help="Generate xlsx"),
) -> None:
    """Download Polimi lessons recordings from the recordings archives url."""
    # Get cookies
    try:
        cookie_SSL_JSESSIONID: str = get_cookie("SSL_JSESSIONID")
        cookie_ticket: str = get_cookie("ticket")
    except ValueError as e:
        print("[red]" + str(e) + "[/red]")
        raise typer.Exit(1)

    # Get recordings
    print("Recordings parsing from archives URL started")
    parser: ArchivesParser = ArchivesParser(
        cookie_SSL_JSESSIONID=cookie_SSL_JSESSIONID,
        cookie_ticket=cookie_ticket,
    )
    try:
        recordings: List[Recording] = parser.parse(url)
    except Exception as e:
        print("[red]" + str(e) + "[/red]")
        raise typer.Exit(1)

    create_output(
        recordings=recordings, output=output, create_xlsx=create_xlsx, aria2c=aria2c
    )


@app.command()
def webeep(
    url: str = typer.Argument(..., help="The webeep URL"),
    academic_year: str = typer.Option(
        ...,
        callback=validate_academic_year,
        help='The course academic year in the format "2021-22"',
    ),
    output: str = typer.Option(
        os.path.join(pathlib.Path().resolve(), Config.DEFAULT_OUTPUT_FOLDER),
        help="The output path",
    ),
    aria2c: bool = typer.Option(
        True, help="Download with aria2c or just create a file with the download links"
    ),
    create_xlsx: bool = typer.Option(True, help="Generate xlsx"),
) -> None:
    """Download Polimi lessons recordings from a Webeep URL."""
    # Get cookies
    try:
        cookie_ticket: str = get_cookie("ticket")
        cookie_MoodleSession: str = get_cookie("MoodleSession")
    except ValueError as e:
        print("[red]" + str(e) + "[/red]")
        raise typer.Exit(1)

    # Get recordings
    print("Recordings parsing from Webeep page started")
    parser: WebeepParser = WebeepParser(
        cookie_ticket=cookie_ticket, cookie_MoodleSession=cookie_MoodleSession
    )
    try:
        recordings: List[Recording] = parser.parse(url, academic_year)
    except Exception as e:
        print("[red]" + str(e) + "[/red]")
        raise typer.Exit(1)

    create_output(
        recordings=recordings, output=output, create_xlsx=create_xlsx, aria2c=aria2c
    )


@app.command()
def txt(
    file: pathlib.Path = typer.Argument(
        ..., exists=True, file_okay=True, readable=True, help="The input txt file"
    ),
    course: str = typer.Option(..., prompt="Course name:", help="The course name"),
    academic_year: str = typer.Option(
        ...,
        callback=validate_academic_year,
        help='The course academic year in the format "2021-22"',
    ),
    output: str = typer.Option(
        os.path.join(pathlib.Path().resolve(), Config.DEFAULT_OUTPUT_FOLDER),
        help="The output path",
    ),
    aria2c: bool = typer.Option(
        True,
        help="Download with aria2c or just create a file with the download links or video ids",
    ),
    create_xlsx: bool = typer.Option(True, help="Generate xlsx"),
) -> None:
    # Get cookies
    try:
        cookie_ticket: str = get_cookie("ticket")
    except ValueError as e:
        print("[red]" + str(e) + "[/red]")
        raise typer.Exit(1)

    # Get recordings
    print("Recordings parsing from txt file started")
    parser: TxtParser = TxtParser(
        cookie_ticket=cookie_ticket,
    )
    try:
        recordings: List[Recording] = parser.parse(file, course, academic_year)
    except Exception as e:
        print("[red]" + str(e) + "[/red]")
        raise typer.Exit(1)

    create_output(
        recordings=recordings, output=output, create_xlsx=create_xlsx, aria2c=aria2c
    )


@app.command()
def webpage_url(
    url: str = typer.Argument(..., help="The URL of the webpage"),
    course: str = typer.Option(..., prompt="Course name:", help="The course name"),
    academic_year: str = typer.Option(
        ...,
        callback=validate_academic_year,
        help='The course academic year in the format "2021-22"',
    ),
    output: str = typer.Option(
        os.path.join(pathlib.Path().resolve(), Config.DEFAULT_OUTPUT_FOLDER),
        help="The output path",
    ),
    aria2c: bool = typer.Option(
        True,
        help="Download with aria2c or just create a file with the download links or video ids",
    ),
    create_xlsx: bool = typer.Option(True, help="Generate xlsx"),
) -> None:
    """Download Polimi lessons recordings from a webpage url."""
    # Get cookies
    try:
        cookie_ticket: str = get_cookie("ticket")
    except ValueError as e:
        print("[red]" + str(e) + "[/red]")
        raise typer.Exit(1)

    # Get recordings
    print("Recordings parsing from webpage url started")
    parser: WebpageParser = WebpageParser(cookie_ticket=cookie_ticket)
    try:
        recordings: List[Recording] = parser.parse_url(url, course, academic_year)
    except Exception as e:
        print("[red]" + str(e) + "[/red]")
        raise typer.Exit(1)

    create_output(
        recordings=recordings, output=output, create_xlsx=create_xlsx, aria2c=aria2c
    )


@app.command()
def webpage_html(
    file: pathlib.Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        readable=True,
        help="The path to the HTML file",
    ),
    course: str = typer.Option(..., prompt="Course name:", help="The course name"),
    academic_year: str = typer.Option(
        ...,
        callback=validate_academic_year,
        help='The course academic year in the format "2021-22"',
    ),
    output: str = typer.Option(
        os.path.join(pathlib.Path().resolve(), Config.DEFAULT_OUTPUT_FOLDER),
        help="The output path",
    ),
    aria2c: bool = typer.Option(
        True,
        help="Download with aria2c or just create a file with the download links or video ids",
    ),
    create_xlsx: bool = typer.Option(True, help="Generate xlsx"),
) -> None:
    """Download Polimi lessons recordings from a webpage html."""
    # Get cookies
    try:
        cookie_ticket: str = get_cookie("ticket")
    except ValueError as e:
        print("[red]" + str(e) + "[/red]")
        raise typer.Exit(1)

    # Get recordings
    print("Recordings parsing from webpage file started")
    parser: WebpageParser = WebpageParser(cookie_ticket=cookie_ticket)
    try:
        recordings: List[Recording] = parser.parse_file(file, course, academic_year)
    except Exception as e:
        print("[red]" + str(e) + "[/red]")
        raise typer.Exit(1)

    create_output(
        recordings=recordings, output=output, create_xlsx=create_xlsx, aria2c=aria2c
    )


@app.command()
def set_cookie(
    name: str = typer.Argument(
        ...,
        help='Cookie name. Possible values are "SSL_JSESSIONID", "ticket" and "MoodleSession".',
    ),
    value: str = typer.Argument(..., help="Cookie value."),
) -> None:
    """Set the value of a cookie."""
    # Arguments check
    if name != "SSL_JSESSIONID" and name != "ticket" and name != "MoodleSession":
        print(
            f'[red]The name of the cookie is invalid, possible values are "SSL_JSESSIONID", "ticket" and "MoodleSession".[/red]'
        )
        raise typer.Exit(code=1)

    save_cookie(name, value)
    print(f"[green]Cookie {name} set to {value}.[/green]")


if __name__ == "__main__":
    if not os.path.exists(typer.get_app_dir(Config.APP_NAME)):
        os.makedirs(typer.get_app_dir(Config.APP_NAME))
