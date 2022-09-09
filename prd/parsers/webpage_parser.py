from typing import List, Tuple, Optional
from multiprocessing.pool import ThreadPool
from itertools import repeat
import re
import requests
import typer
from bs4 import BeautifulSoup, Tag
from Recording import Recording
from webex_api import extract_id_from_url, generate_recording_from_id


def get_id_from_anchor(anchor: Tag) -> Tuple[bool, Optional[str]]:
    """
    Get a video id from an anchor, if the link is to Webex.

    Args:
        anchor (Tag): The anchor tag.

    Returns:
        Tuple(bool, Optional[Recording]): The first element indicates if an id
        has been found, the second is the id itself.
    """
    if not anchor.has_attr("href"):
        return (False, None)

    pattern_google_redirect = re.compile(
        "https?\:\/\/www\.google\.com\/url\?q\=(https?\:\/\/politecnicomilano.webex.com\/[^&]*)&.*"
    )
    try:
        direct_url: str = anchor["href"]
        if pattern_google_redirect.match(anchor["href"]):
            direct_url = pattern_google_redirect.search(anchor["href"]).group(1)

        return (True, extract_id_from_url(direct_url))
    except ValueError:
        return (False, None)


def get_video_ids_from_soup(soup: BeautifulSoup) -> List[str]:
    """Get the video ids in the links in a webpage from the soup.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object of a webpage.

    Returns:
        List[str]: List of video ids.
    """
    anchors = soup.select("a", href=True)
    typer.echo(
        f"Found {len(anchors)} links in the page, need to get only the Webex ones..."
    )
    pool: ThreadPool = ThreadPool()
    video_ids: List[str] = pool.starmap(
        get_id_from_anchor,
        zip(anchors),
    )

    video_ids = list(filter(lambda item: item[0] == True, video_ids))
    return [v[1] for v in video_ids]


def get_video_ids_from_webpage_url(url: str) -> List[str]:
    """Get the video ids in the links in a webpage from its url.

    Args:
        url (str): The URL to the page.

    Returns:
        List[str]: List of video ids.
    """
    res: requests.Response = requests.get(url)
    if res.status_code != 200:
        typer.echo(f"Unable to open the page, got status {res.status_code}.")
        raise typer.Exit(code=1)
    soup: BeautifulSoup = BeautifulSoup(res.content, "html.parser")

    return get_video_ids_from_soup(soup)


def recordings_from_webpage_url(
    url: str, course: str, academic_year: str
) -> List[Recording]:
    """Get the recordings from a webpage URL.

    Args:
        url (str): The url containing the links to the recordings.
        course (str): The course name.
        academic_year (str): The course academic year in the format "2021-22".

    Returns:
        List[Recording]: Recording objects.
    """
    video_ids: List[str] = get_video_ids_from_webpage_url(url)
    typer.echo(f"Found {len(video_ids)} links to Webex in the page.")

    typer.echo("Generating recording download links, this may take a bit...")
    try:
        pool: ThreadPool = ThreadPool()
        recordings: List[Recording] = pool.starmap(
            generate_recording_from_id,
            zip(video_ids, repeat(course), repeat(academic_year)),
        )
    except requests.exceptions.ConnectionError as e:
        typer.echo(str(e))
        raise typer.Exit(code=1)

    return recordings


def recordings_from_webpage_file(
    file: str, course: str, academic_year: str
) -> List[Recording]:
    """Get the recordings from an HTML file.

    Args:
        file (str): The path to the file.
        course (str): The course name.
        academic_year (str): The course academic year in the format "2021-22".

    Returns:
        List[Recording]: Recording objects.
    """
    with open(file) as f:
        soup = BeautifulSoup(f, "html.parser")
    
    video_ids: List[str] = get_video_ids_from_soup(soup)
    typer.echo(f"Found {len(video_ids)} links to Webex in the page.")

    typer.echo("Generating recording download links, this may take a bit...")
    try:
        pool: ThreadPool = ThreadPool()
        recordings: List[Recording] = pool.starmap(
            generate_recording_from_id,
            zip(video_ids, repeat(course), repeat(academic_year)),
        )
    except requests.exceptions.ConnectionError as e:
        typer.echo(str(e))
        raise typer.Exit(code=1)

    return recordings
