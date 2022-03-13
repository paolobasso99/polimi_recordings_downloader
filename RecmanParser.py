from datetime import datetime
from typing import List, Optional
import requests
import os
import re
from bs4 import BeautifulSoup, Tag
from multiprocessing.pool import ThreadPool
from Recording import Recording
from progress.bar import Bar
from itertools import repeat
from WebexAPI import WebexAPI


class RecmanParser:
    """Class in charge to parse the HTML from recman in order to find the ids of the videos."""

    def __init__(
        self, file: str = os.path.join(os.path.dirname(__file__), "recman.html")
    ) -> None:
        """Create a RecmanParser instance.

        Args:
            file (str, optional): The file containing the html of the recman page. Defaults to os.path.join(os.path.dirname(__file__), "recman.html").
        """
        self.file: str = file

    def _get_rows(self) -> List[Tag]:
        """Get the rows from the html file.

        Returns:
            List[Tag]: List of rows containing the recordings.
        """
        with open(self.file) as f:
            soup = BeautifulSoup(f, "html.parser")

        table = soup.find("tbody", {"class": "TableDati-tbody"})
        return table.select("tr")

    def _replace_illegal_characters(self, string: str) -> str:
        """Replace the illegal characters in a string. Such characters are < > : \ / \ | ? * .

        Args:
            string (str): The string.

        Returns:
            str: The resulting string without illegal characters"
        """
        TO_REPLACE: List[str] = ["<", ">", ":", "\"", "/", "\\", "|", "?", "*", "."]
        for c in TO_REPLACE:
            string = string.replace(c, "")

        return string

    def _generate_recording_obj_from_row(
        self, row: Tag, bar: Optional[Bar] = None
    ) -> Recording:
        """Create a Recording object from a row of the recordings table.

        Args:
            row (Tag): Row of the recordings table.
            bar (Bar, optional): Progress bar.

        Returns:
            Recording: Generated recording object.
        """
        cells = row.select("td")
        video_id: str = self._get_video_id_from_recman_redirection_link(
            "https://www11.ceda.polimi.it" + cells[0].select_one("a.Link")["href"]
        )
        recording_datetime: datetime = datetime.strptime(
            cells[2].text.strip(), "%d/%m/%Y %H:%M"
        )
        recording: Recording = Recording(
            video_id=video_id,
            accademic_year=cells[1].text.replace(" / ", "-"),
            recording_datetime=recording_datetime,
            course=self._replace_illegal_characters(cells[3].text.replace("\n", " ")),
            subject=cells[5].text.replace("\n", " "),
            download_url=WebexAPI.generate_download_link(video_id),
        )

        if bar is not None:
            bar.next()

        return recording

    def _get_video_id_from_recman_redirection_link(self, link: str) -> str:
        """Get the video id from the link of the redirection to the recording.

        Args:
            link (str): Link of recman redirection to the recording.

        Returns:
            str: The id of the video.

        Raises:
            RuntimeError: If unable to extract id from redirection link.
        """
        res = requests.get(
            link, cookies={"SSL_JSESSIONID": os.getenv("RECMAN_SSL_JSESSIONID")}
        )
        id_search = re.search(
            "location\.href='https:\/\/politecnicomilano\.webex\.com\/recordingservice\/sites\/politecnicomilano\/recording\/playback\/([a-z,0-9]*)';",
            res.text,
        )
        if not(id_search):
            print(
                "ERROR: Was not able to extract video id from recman redirection link."
            )
            raise RuntimeError("Was not able to extract video id from recman redirection link.")

        return id_search.group(1)

    def get_recordings_from_html(self) -> List[Recording]:
        """Get the recordings from the html file.

        Returns:
            List[Recording]: Recording objects extracted from the file.
        """
        print("Recordings parsing from HTML started...")
        rows: List[Tag] = self._get_rows()
        print(f"Found {len(rows)} rows.")
        bar: Bar = Bar("Processing", max=len(rows))
        pool: ThreadPool = ThreadPool()
        print("Resolving recman redirection links and building recordings objects...")
        recordings: List[Recording] = pool.starmap(
            self._generate_recording_obj_from_row, zip(rows, repeat(bar))
        )
        print(f"\nFound {len(recordings)} recordings.")
        return recordings


# Test
if __name__ == "__main__":
    recman_parser: RecmanParser = RecmanParser()
    recordings: List[Recording] = recman_parser.get_recordings_from_html()
