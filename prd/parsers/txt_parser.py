from multiprocessing.pool import ThreadPool
from itertools import repeat
from pathlib import Path
from typing import List, Optional
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from prd.webex_api import Recording
from prd.webex_api import extract_id_from_url, generate_recording_from_id
from prd.parsers import Parser


class TxtParser(Parser):
    """Class to parse txt files."""

    def parse(self, file: Path, course: str, academic_year: Optional[str] = None) -> List[Recording]:
        """Get the recordings from the TXT file.

        Args:
            file (Path): The file containing the html of the recman page.
            course (str): The course name.
            academic_year (Optional[str], optional): The academic year in the format "2021-22". Defaults to None.

        Returns:
            List[Recording]: Recording objects extracted from the file.
        """
        # Get video ids from file
        video_ids: List[str] = []
        with open(file) as f:
            for i, line in enumerate(f):
                line = line.rstrip()
                if line.startswith("http"):
                    video_ids.append(extract_id_from_url(url=line, ticket=self.cookie_ticket))
                elif len(line) == 32:
                    video_ids.append(line)
                elif len(line) != 32 and len(line) > 0:
                    print(
                        f'[red]Invalid line found, line number {i+1} is "{line}",[/red] Continuing...'
                    )

        print(f"Found {len(video_ids)} urls in the input file")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
        ) as progress:
            progress.add_task(description="Generating recording download links...", total=None)
            pool: ThreadPool = ThreadPool()
            recordings: List[Recording] = pool.starmap(
                generate_recording_from_id,
                zip(video_ids, repeat(self.cookie_ticket), repeat(course), repeat(academic_year)),
            )

        return recordings
