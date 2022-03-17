from datetime import datetime
from multiprocessing.pool import ThreadPool
from typing import List
import requests
from cookies import get_cookie
import re
from bs4 import BeautifulSoup, Tag
from Recording import Recording
from webex_api import extract_id_from_url, generate_recording_from_id


def get_rows(file: str) -> List[Tag]:
    """Get the rows from the HTML file.

    Args:
        file (str): The file containing the HTML of the recman page.

    Returns:
        List[Tag]: List of rows containing the recordings.
    """
    with open(file) as f:
        soup = BeautifulSoup(f, "html.parser")

    table = soup.find("tbody", {"class": "TableDati-tbody"})
    return table.select("tr")


def generate_recording_from_row(row: Tag) -> Recording:
    """Create a Recording object from a row of the recordings table.

    Args:
        row (Tag): Row of the recordings table.

    Returns:
        Recording: Generated recording object.
    """
    cells = row.select("td")
    recording_datetime: datetime = datetime.strptime(
        cells[2].text.strip(), "%d/%m/%Y %H:%M"
    )
    video_url: str = get_video_url_from_recman_redirection_link(
        "https://www11.ceda.polimi.it" + cells[0].select_one("a.Link")["href"]
    )
    video_id: str = extract_id_from_url(video_url)
    recording: Recording = generate_recording_from_id(
        video_id=video_id,
        accademic_year=cells[1].text.replace(" / ", "-"),
        recording_datetime=recording_datetime,
        course=cells[3].text.replace("\n", " "),
        subject=cells[5].text.replace("\n", " "),
    )

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
    res = requests.get(
        link, cookies={"SSL_JSESSIONID": get_cookie("SSL_JSESSIONID")}
    )
    id_search = re.search(
        "location\.href='(.*)';",
        res.text,
    )
    if not (id_search):
        raise RuntimeError(
            "Was not able to extract video url from recman redirection link. Try to redownload the HTML."
        )
    return id_search.group(1)


def recordings_from_html(file: str) -> List[Recording]:
    """Get the recordings from the HTML file.

    Args:
        file (str): The file containing the HTML of the recman page.

    Returns:
        List[Recording]: Recording objects extracted from the file.
    """
    rows: List[Tag] = get_rows(file)
    pool: ThreadPool = ThreadPool()
    recordings: List[Recording] = pool.starmap(generate_recording_from_row, zip(rows))
    return recordings
