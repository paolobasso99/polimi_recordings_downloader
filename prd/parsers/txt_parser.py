from itertools import repeat
from typing import List
from Recording import Recording
from webex_api import extract_id_from_url, generate_recording_from_id
import typer
import requests
from multiprocessing.pool import ThreadPool

def get_video_ids_from_file(file:str) -> List[str]:
    """Get the video ids from a txt file.

    Args:
        file (str): The file path.

    Returns:
        List[str]: A list of video ids.
    """
    video_ids: List[str] = []
    with open(file) as f:
        for i, line in enumerate(f):
            line = line.rstrip()
            if line.startswith("http"):
                video_ids.append(extract_id_from_url(line))
            elif len(line) == 32:
                video_ids.append(line)
            elif len(line) != 32 and len(line) > 0:
                typer.echo(f'Invalid line found, line number {i+1} is "{line}".')
        
    return video_ids
    


def recordings_from_txt(file: str, course: str, academic_year: str) -> List[Recording]:
    """Get the recordings from the TXT file.

    Args:
        file (str): The file containing the html of the recman page.
        course (str): The course name.
        academic_year (str): The course academic year in the format "2021-22".

    Returns:
        List[Recording]: Recording objects extracted from the file.
    """
    video_ids: List[str] = get_video_ids_from_file(file)
    typer.echo(f"Found {len(video_ids)} urls in the input file.")
    typer.echo("Generating recording download links, this may take a bit...")

    try:
        pool: ThreadPool = ThreadPool()
        recordings: List[Recording] = pool.starmap(
            generate_recording_from_id,
            zip(video_ids, repeat(course), repeat(academic_year)),
        )
    except requests.exceptions.ConnectionError as e:
        typer.echo(str(e))
        raise typer.Exit(code=1)

    return recordings
