from typing import List
from Recording import Recording
from webex_api import extract_id_from_url, generate_recording_from_id
import typer
import requests


def recordings_from_txt(
    file: str,
    course: str,
    academic_year: str
) -> List[Recording]:
    """Get the recordings from the TXT file.

    Args:
        file (str): The file containing the html of the recman page.
        course (str): The course name.
        academic_year (str): The course academic year in the format "2021-22".

    Returns:
        List[Recording]: Recording objects extracted from the file.
    """
    recordings: List[Recording] = []
    with open(file) as f:
        video_ids: List[str] = [extract_id_from_url(line.rstrip()) for line in f]
        typer.echo(f"Found {len(video_ids)} urls in the input file.")
        typer.echo("Generating recording links, this may take a bit...")

        for id in video_ids:
            try:
                recording: Recording = generate_recording_from_id(
                    video_id=id,
                    academic_year=academic_year,
                    course=course
                )
                recordings.append(recording)
            except requests.exceptions.ConnectionError as e:
                typer.echo(str(e))
                raise typer.Exit(code=1)

    return recordings
