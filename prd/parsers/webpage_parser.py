from pathlib import Path
from typing import List, Tuple, Optional
from multiprocessing.pool import ThreadPool
from itertools import repeat
import re
import requests
from bs4 import BeautifulSoup, Tag
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from prd.parsers import Parser
from prd.webex_api import Recording
from prd.webex_api import extract_id_from_url, generate_recording_from_id


class WebpageParser(Parser):
    """Class to parse webpages."""

    def __init__(self, cookie_ticket: str):
        """Create the parser.

        Args:
            cookie_ticket (str): The ticket cookie.
        """
        self.cookie_ticket = cookie_ticket

    def _get_id_from_anchor(self, anchor: Tag) -> Tuple[bool, Optional[str]]:
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

            return (
                True,
                extract_id_from_url(url=direct_url, ticket=self.cookie_ticket),
            )
        except ValueError:
            return (False, None)

    def _get_video_ids_from_soup(self, soup: BeautifulSoup) -> List[str]:
        """Get the video ids in the links in a webpage from the soup.

        Args:
            soup (BeautifulSoup): The BeautifulSoup object of a webpage.

        Returns:
            List[str]: List of video ids.
        """
        anchors = soup.select("a", href=True)
        print(f"Found {len(anchors)} links in the page")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
        ) as progress:
            progress.add_task(description="Filtering only Webex links...", total=None)
            pool: ThreadPool = ThreadPool()
            video_ids: List[str] = pool.starmap(
                self._get_id_from_anchor,
                zip(anchors),
            )

            video_ids = list(filter(lambda item: item[0] == True, video_ids))
            video_ids = [v[1] for v in video_ids]

        return video_ids

    def parse(
        self, soup: BeautifulSoup, course: str, academic_year: Optional[str] = None
    ) -> List[Recording]:
        """Get the recordings from a webpage soup.

        Args:
            soup (BeautifulSoup): The soup.
            course (str): The course name.
            academic_year (Optional[str], optional): The academic year in the format "2021-22". Defaults to None.

        Returns:
            List[Recording]: The list of the recording objects.
        """
        video_ids: List[str] = self._get_video_ids_from_soup(soup)
        print(f"Found {len(video_ids)} links to Webex in the page")

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
                generate_recording_from_id,
                zip(
                    video_ids,
                    repeat(self.cookie_ticket),
                    repeat(course),
                    repeat(academic_year),
                ),
            )

        return recordings

    def parse_url(self, url: str, course: str, academic_year: str) -> List[Recording]:
        """Get the recordings from a webpage URL.

        Args:
            url (str): The url containing the links to the recordings.
            course (str): The course name.
            academic_year (str): The course academic year in the format "2021-22".

        Returns:
            List[Recording]: Recording objects.
        """
        res: requests.Response = requests.get(url)
        if res.status_code != 200:
            raise RuntimeError(
                f"Unable to open the page, got status {res.status_code}."
            )
        soup: BeautifulSoup = BeautifulSoup(res.content, "html.parser")

        return self.parse(soup, course, academic_year)

    def parse_file(
        self, file: Path, course: str, academic_year: str
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

        return self.parse(soup, course, academic_year)
