from datetime import datetime
from itertools import repeat
from multiprocessing.pool import ThreadPool
from typing import List
import requests
import re
from bs4 import BeautifulSoup, Tag
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from prd.utils import extract_academic_year_from_datetime
from prd.parsers import Parser
from prd.webex_api import Recording, extract_id_from_url, generate_recording_from_id


class ArchivesParser(Parser):
    """Class to parse archives pages."""

    def __init__(
        self,
        cookie_ticket: str,
        cookie_SSL_JSESSIONID: str
    ):
        """Create the parser.

        Args:
            cookie_ticket (str): The ticket cookie.
            cookie_SSL_JSESSIONID (str): The SSL_JSESSIONID cookie.
        """
        self.cookie_ticket = cookie_ticket
        self.cookie_SSL_JSESSIONID = cookie_SSL_JSESSIONID


    def parse(self, url: str) -> List[Recording]:
        """Parse an url of the recording archives.

        Args:
            url (str): The url of the recording archives.

        Raises:
            ValueError: If the url is not correct.
            RuntimeError: If no recordings are found in the page.

        Returns:
            List[Recording]: The list of recordings.
        """
        # Option check
        if not url.startswith(
            "https://www11.ceda.polimi.it/recman_frontend/recman_frontend/controller/"
        ):
            raise ValueError(
                f"The url must start with 'https://www11.ceda.polimi.it/recman_frontend/recman_frontend/controller/'."
            )

        res: requests.Response = requests.get(
            url, cookies={"SSL_JSESSIONID": self.cookie_SSL_JSESSIONID}
        )
        soup: BeautifulSoup = BeautifulSoup(res.content, "html.parser")
        rows: List[Tag] = soup.select("tbody.TableDati-tbody tr")

        if len(rows) == 0:
            raise RuntimeError(
                "Zero recordings were found, make sure SSL_JSESSIONID is correct."
            )
        print(f"There are {len(rows)} rows in the page")

        # Need to work for both UserListActivity.do and ArchivioListActivity.do
        is_UserListActivity: bool = url.startswith(
            "https://www11.ceda.polimi.it/recman_frontend/recman_frontend/controller/UserListActivity.do"
        )
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
        ) as progress:
            progress.add_task(
                description="Generating recording download links...", total=None
            )
            pool: ThreadPool = ThreadPool()
            recordings: List[Recording] = pool.starmap(
                self._generate_recording_from_row,
                zip(rows, repeat(is_UserListActivity)),
            )

        return recordings

    def _generate_recording_from_row(
        self, row: Tag, is_UserListActivity: bool
    ) -> Recording:
        """Create a Recording object from a row of the recordings table.

        Args:
            row (Tag): Row of the recordings table.
            is_UserListActivity (bool): If the row is from a UserListActivity page.

        Returns:
            Recording: Generated recording object.
        """
        cells = row.select("td")

        video_url: str = self._get_video_url_from_recman_redirection_link(
            "https://www11.ceda.polimi.it" + cells[0].select_one("a.Link")["href"]
        )
        video_id: str = extract_id_from_url(video_url, ticket=self.cookie_ticket)

        if not is_UserListActivity:
            recording_datetime: datetime = datetime.strptime(
                cells[2].text.strip(), "%d/%m/%Y %H:%M"
            )
            course: str = cells[3].text
            subject: str = cells[5].text
            academic_year: str = cells[1].text.replace(" / ", "-")
        else:
            recording_datetime: datetime = datetime.strptime(
                cells[1].text.strip(), "%d/%m/%Y %H:%M"
            )
            course: str = cells[2].text.replace("\n", " ")
            subject: str = cells[4].text.replace("\n", " ")
            academic_year = extract_academic_year_from_datetime(recording_datetime)

        course: str = course.replace("\n", " ")
        subject: str = subject.replace("\n", " ")

        recording: Recording = generate_recording_from_id(
            video_id=video_id,
            ticket=self.cookie_ticket,
            academic_year=academic_year,
            recording_datetime=recording_datetime,
            course=course,
            subject=subject,
        )

        return recording

    def _get_video_url_from_recman_redirection_link(self, link: str) -> str:
        """Get the video url from the link of the redirection to the recording.

        Args:
            link (str): Link of recman redirection to the recording.

        Returns:
            str: The url of the video.

        Raises:
            RuntimeError: If unable to extract url from redirection link.
        """
        res = requests.get(link, cookies={"SSL_JSESSIONID": self.cookie_SSL_JSESSIONID})
        id_search = re.search(
            "location\.href='(.*)';",
            res.text,
        )
        if not (id_search):
            raise RuntimeError(
                "Was not able to extract video url from recman redirection link. Retry."
            )
        return id_search.group(1)
