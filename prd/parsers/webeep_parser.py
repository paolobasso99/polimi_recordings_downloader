from multiprocessing.pool import ThreadPool
from itertools import repeat
from typing import List, Tuple, Optional
import requests
import typer
from cookies import get_cookie
from bs4 import BeautifulSoup
from Recording import Recording
from webex_api import extract_id_from_url, generate_recording_from_id


def get_redirection_links(url: str) -> List[str]:
    """Get the redirection links from Webeep.

    Args:
        url (str): The URL to the Webeep page.

    Returns:
        List[str]: List of Webeep redirection links.
    """
    redirection_links: List[str] = []
    res: requests.Response = requests.get(
        url,
        cookies={"MoodleSession": get_cookie("MoodleSession")},
        allow_redirects=False,
    )
    if res.status_code == 303:
        typer.echo("Unable to open the Webeep page, check MoodleSession cookie.")
        raise typer.Exit(code=1)
    soup: BeautifulSoup = BeautifulSoup(res.content, "html.parser")
    for a in soup.select(".single-section a.aalink", href=True):
        redirection_links.append(a["href"])

    return redirection_links


def generate_recording_from_redirection_link(
    link: str, academic_year: str
) -> Tuple[bool, Optional[Recording]]:
    """Create a Recording object from a Webeep redirection link.

    Args:
        link (str): Webeep redirection link to the recording.
        academic_year (str): The course academic year in the format "2021-22".

    Returns:
        Tuple(bool, Optional[Recording]): The first element indicates if a
            recording has been found, the second is the Recording object.
    """
    res: requests.Response = requests.get(
        link, cookies={"MoodleSession": get_cookie("MoodleSession")}
    )
    soup = BeautifulSoup(res.content, "html.parser")

    video_url: str = soup.select_one(".urlworkaround a", href=True)["href"]
    try:
        video_id: str = extract_id_from_url(video_url)
    except ValueError:
        return (False, None)

    subject: str = soup.select_one("#region-main h2").text
    course: str = soup.select_one(".page-header-headings h1").text

    try:
        recording: Recording = generate_recording_from_id(
            video_id=video_id,
            academic_year=academic_year,
            course=course,
            subject=subject,
        )
    except requests.exceptions.ConnectionError as e:
        typer.echo(str(e))
        raise typer.Exit(code=1)

    return (True, recording)


def recordings_from_webeep(url: str, academic_year: str) -> List[Recording]:
    """Get the recordings from the Webeep page.

    Args:
        url (str): The file Webeep url containing the links to the recordings.
        academic_year (str): The course academic year in the format "2021-22".

    Returns:
        List[Recording]: Recording objects.
    """
    redirection_links: List[str] = get_redirection_links(url)
    typer.echo(
        f"Found {len(redirection_links)} links in the page (not all are recordings)."
    )

    typer.echo("Generating recording links, this may take a bit...")
    pool: ThreadPool = ThreadPool()
    recordings: List[Tuple(bool, Optional[Recording])] = pool.starmap(
        generate_recording_from_redirection_link,
        zip(redirection_links, repeat(academic_year)),
    )

    recordings = list(filter(lambda item: item[0] == True, recordings))
    return [r[1] for r in recordings]
