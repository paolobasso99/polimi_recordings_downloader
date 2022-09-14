from multiprocessing.pool import ThreadPool
from itertools import repeat
from typing import List, Tuple, Optional
import requests
from bs4 import BeautifulSoup
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn


from prd.parsers import Parser
from prd.webex_api import Recording, extract_id_from_url, generate_recording_from_id


class WebeepParser(Parser):
    """Class to parse Webeep recordings page."""

    def _get_redirection_links(self, url: str) -> List[str]:
        """Get the redirection links from Webeep.

        Args:
            url (str): The URL to the Webeep page.

        Raises:
            RuntimeError: if unable to open the page.

        Returns:
            List[str]: List of Webeep redirection links.
        """
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
        for a in soup.select(".single-section a.aalink", href=True):
            redirection_links.append(a["href"])

        return redirection_links

    def _generate_recording_from_redirection_link(
        self, link: str, academic_year: str
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
            link, cookies={"MoodleSession": self.cookie_MoodleSession}
        )
        soup = BeautifulSoup(res.content, "html.parser")

        video_url: str = soup.select_one(".urlworkaround a", href=True)["href"]
        try:
            video_id: str = extract_id_from_url(
                url=video_url, ticket=self.cookie_ticket
            )
        except ValueError:
            return (False, None)

        subject: str = soup.select_one("#region-main h2").text
        course: str = soup.select_one(".page-header-headings h1").text

        recording: Recording = generate_recording_from_id(
            video_id=video_id,
            ticket=self.cookie_ticket,
            academic_year=academic_year,
            course=course,
            subject=subject,
        )

        return (True, recording)

    def parse(self, url: str, academic_year: Optional[str] = None) -> List[Recording]:
        """Get the recordings from the Webeep page.

        Args:
            url (str): The Webeep url containing the links to the recordings.
            academic_year (Optional[str], optional): The academic year in the format "2021-22". Defaults to None.

        Raises:
            ValueError: If the url is not correct.

        Returns:
            List[Recording]: Recording objects.
        """
        if not url.startswith("https://webeep.polimi.it/"):
            raise ValueError("The url must start with 'https://webeep.polimi.it/'.")

        redirection_links: List[str] = self._get_redirection_links(url)
        print(
            f"Found {len(redirection_links)} links in the page (not all are recordings)."
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
        ) as progress:
            progress.add_task(description="Generating recording download links...", total=None)
            pool: ThreadPool = ThreadPool()
            recordings: List[Tuple(bool, Optional[Recording])] = pool.starmap(
                self._generate_recording_from_redirection_link,
                zip(redirection_links, repeat(academic_year)),
            )
            recordings = list(filter(lambda item: item[0] == True, recordings))
            recordings = [r[1] for r in recordings]

        return recordings
