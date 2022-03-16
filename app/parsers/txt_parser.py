from typing import List
from Recording import Recording
from webex_api import extract_id_from_url, generate_recording_from_id
import typer


def recordings_from_txt(
    file: str,
    course: str,
    accademic_year: str
) -> List[Recording]:
    """Get the recordings from the TXT file.

    Args:
        file (str): The file containing the html of the recman page.
        course (str): The course name.
        accademic_year (str): The course accademic year in the format "2021-22".

    Returns:
        List[Recording]: Recording objects extracted from the file.
    """
    recordings: List[Recording] = []
    with open(file) as f:
        video_ids: List[str] = [extract_id_from_url(line.rstrip()) for line in f]
        typer.echo(f"Found {len(video_ids)} urls in the input file.")
        typer.echo(f"Generating recordings...")
        recordings = [generate_recording_from_id(
            video_id=id,
            accademic_year=accademic_year,
            course=course
        ) for id in video_ids]

    return recordings
