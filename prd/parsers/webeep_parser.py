from multiprocessing.pool import ThreadPool
from itertools import repeat
from typing import List, Tuple, Optional
import requests
import re
from bs4 import BeautifulSoup, Tag
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn


from prd.parsers import Parser
from prd.webex_api import Recording, extract_id_from_url, generate_recording_from_id


class WebeepParser(Parser):
    """Class to parse Webeep recordings page."""

    def __init__(
        self,
        cookie_ticket: str,
        cookie_MoodleSession: str,
    ):
        """Create the parser.

        Args:
            cookie_ticket (str): The ticket cookie.
            cookie_MoodleSession (str): The MoodleSession cookie.
        """
        self.cookie_ticket = cookie_ticket
        self.cookie_MoodleSession = cookie_MoodleSession

    def _generate_recording_from_redirection_link(
        self, link: str, course: str, academic_year: str
    ) -> Tuple[bool, Optional[Recording]]:
        """Create a Recording object from a Webeep redirection link.

        Args:
            link (str): Webeep redirection link to the recording.
            course (str): The name of the course.
            academic_year (str): The course academic year in the format "2021-22".

        Returns:
            Tuple(bool, Optional[Recording]): The first element indicates if a
                recording has been found, the second is the Recording object.
        """
        res: requests.Response = requests.get(
            link, cookies={"MoodleSession": self.cookie_MoodleSession}
        )
        soup = BeautifulSoup(res.content, "html.parser")

        video_url_anchor: Tag | None = soup.select_one(".urlworkaround a", href=True)
        if video_url_anchor is None:
            return (False, None)

        video_url: str = soup.select_one(".urlworkaround a", href=True)["href"]
        try:
            video_id: str = extract_id_from_url(
                url=video_url, ticket=self.cookie_ticket
            )
        except ValueError:
            return (False, None)

        subject: str = soup.select_one("#page-header h4").text

        recording: Recording = generate_recording_from_id(
            video_id=video_id,
            ticket=self.cookie_ticket,
            academic_year=academic_year,
            course=course,
            subject=subject,
        )

        return (True, recording)

    def parse(self, url: str) -> List[Recording]:
        """Get the recordings from the Webeep page.

        Args:
            url (str): The Webeep url containing the links to the recordings.

        Raises:
            RuntimeError: if unable to open the Webeep page.
            ValueError: If the url is not correct.

        Returns:
            List[Recording]: Recording objects.
        """
        if not url.startswith("https://webeep.polimi.it/"):
            raise ValueError("The url must start with 'https://webeep.polimi.it/'.")

        redirection_links: List[str] = []
        res: requests.Response = requests.get(
            url,
            cookies={"MoodleSession": self.cookie_MoodleSession},
            allow_redirects=False,
        )
        if res.status_code == 303:
            raise RuntimeError(
                "Unable to open the Webeep page, check MoodleSession cookie."
            )
        soup: BeautifulSoup = BeautifulSoup(res.content, "html.parser")
        course: str = soup.select_one("#page-header h2").text
        academic_year: str = re.search('\s\[(\d+-\d+)\]', course).group(1)
        course = re.sub(r'\s\[\d+-\d+\]', '', course)

        for a in soup.select(".single-section a.aalink", href=True):
            redirection_links.append(a["href"])
        print(
            f"Found {len(redirection_links)} links in the page (not all are recordings)."
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
            recordings: List[Tuple(bool, Optional[Recording])] = pool.starmap(
                self._generate_recording_from_redirection_link,
                zip(redirection_links, repeat(course), repeat(academic_year)),
            )
            recordings = list(filter(lambda item: item[0] == True, recordings))
            recordings = [r[1] for r in recordings]

        return recordings
