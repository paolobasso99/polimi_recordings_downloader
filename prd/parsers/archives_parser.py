from datetime import datetime
from itertools import repeat
from multiprocessing.pool import ThreadPool
from typing import List
import requests
import typer
from cookies import get_cookie
import re
from bs4 import BeautifulSoup, Tag
from Recording import Recording
import re
from webex_api import extract_id_from_url, generate_recording_from_id


def extract_academic_year_from_datetime(dt: datetime) -> str:
    """Extract the academic year in the format "2020-21" from a datetime.

    Args:
        dt (datetime): The datetime.

    Returns:
        str: The academic year in the format "2020-22".
    """
    starting_year: str = dt.strftime("%y")
    end_year: str = dt.replace(year=dt.year + 1).strftime("%y")
    if dt.month < 8:
        end_year = starting_year
        starting_year = dt.replace(year=dt.year - 1).strftime("%y")
    return starting_year + end_year


def generate_recording_from_row(row: Tag, is_UserListActivity: bool) -> Recording:
    """Create a Recording object from a row of the recordings table.

    Args:
        row (Tag): Row of the recordings table.
        is_UserListActivity (bool): If the row is from a UserListActivity page.

    Returns:
        Recording: Generated recording object.
    """
    cells = row.select("td")

    video_url: str = get_video_url_from_recman_redirection_link(
        "https://www11.ceda.polimi.it" + cells[0].select_one("a.Link")["href"]
    )
    video_id: str = extract_id_from_url(video_url)

    i: int = int(is_UserListActivity)
    recording_datetime: datetime = datetime.strptime(
        cells[2 - i].text.strip(), "%d/%m/%Y %H:%M"
    )
    course: str = cells[3 - i].text.replace("\n", " ")
    subject: str = cells[5 - i].text.replace("\n", " ")

    academic_year: str = cells[1].text.replace(" / ", "-")
    if is_UserListActivity:
        academic_year = extract_academic_year_from_datetime(recording_datetime)

    try:
        recording: Recording = generate_recording_from_id(
            video_id=video_id,
            academic_year=academic_year,
            recording_datetime=recording_datetime,
            course=course,
            subject=subject,
        )
    except requests.exceptions.ConnectionError as e:
        typer.echo(str(e))
        raise typer.Exit(code=1)

    return recording


def get_video_url_from_recman_redirection_link(link: str) -> str:
    """Get the video url from the link of the redirection to the recording.

    Args:
        link (str): Link of recman redirection to the recording.

    Returns:
        str: The url of the video.

    Raises:
        RuntimeError: If unable to extract url from redirection link.
    """
    res = requests.get(link, cookies={"SSL_JSESSIONID": get_cookie("SSL_JSESSIONID")})
    id_search = re.search(
        "location\.href='(.*)';",
        res.text,
    )
    if not (id_search):
        raise RuntimeError(
            "Was not able to extract video url from recman redirection link. Try to redownload the HTML."
        )
    return id_search.group(1)


def recordings_from_archives(url: str) -> List[Recording]:
    """Get the recordings from the HTML file.

    Args:
        url (str): The url of the recman page.

    Returns:
        List[Recording]: Recording objects extracted from the file.
    """
    is_UserListActivity: bool = url.startswith(
        "https://www11.ceda.polimi.it/recman_frontend/recman_frontend/controller/UserListActivity.do"
    )
    res: requests.Response = requests.get(
        url, cookies={"SSL_JSESSIONID": get_cookie("SSL_JSESSIONID")}
    )
    soup: BeautifulSoup = BeautifulSoup(res.content, "html.parser")
    rows: List[Tag] = soup.select("tbody.TableDati-tbody tr")

    if len(rows) == 0:
        typer.echo("Zero recordings were found, make sure SSL_JSESSIONID is correct.")
        raise typer.Exit(code=1)

    typer.echo("Generating recording download links, this may take a bit...")
    pool: ThreadPool = ThreadPool()
    recordings: List[Recording] = pool.starmap(
        generate_recording_from_row, zip(rows, repeat(is_UserListActivity))
    )
    return recordings
