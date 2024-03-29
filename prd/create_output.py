import os
import subprocess
from typing import List
from rich import print
from rich.progress import track

from prd.webex_api import Recording
from prd.config import Config
from prd.xlsx import generate_xlsx


def generate_download_links_file(recordings: List[Recording], output: str) -> None:
    """Generate the file with the download links.

    Args:
        recordings (List[Recording]): List of the recordings.
        output (str): The output folder.
    """
    if not os.path.exists(Config.DEFAULT_OUTPUT_FOLDER):
        os.makedirs(Config.DEFAULT_OUTPUT_FOLDER)
    with open(os.path.join(output, Config.DOWNLOAD_INPUT_FILENAME), "w") as f:
        for r in track(recordings, description="Generating download links file..."):
            f.write(f"{r.download_url}\n")


def generate_aria2c_input_file(recordings: List[Recording], output: str) -> None:
    """Generate the file which will be passed as input to aria2c.

    Args:
        recordings (List[Recording]): List of the recordings.
        output (str): The output folder.
    """
    if not os.path.exists(Config.DEFAULT_OUTPUT_FOLDER):
        os.makedirs(Config.DEFAULT_OUTPUT_FOLDER)
    with open(os.path.join(output, Config.DOWNLOAD_INPUT_FILENAME), "w", encoding="utf-8") as f:
        for r in track(recordings, description="Generating aria2c input file..."):
            f.write(f"{r.download_url}\n")
            f.write(
                f"    out={r.course} {r.academic_year}/{r.recording_datetime.strftime('%Y-%m-%d %H-%M')}.mp4\n"
            )


def start_aria2c_download(recordings: List[Recording], output: str) -> None:
    """Start download with aria2c.

    Args:
        recordings (List[Recording]): The recordings to download.
        output (str): The output folder.
    """
    generate_aria2c_input_file(recordings, output)
    print("[green]aria2c input file generated")
    print("Starting aria2c...")
    subprocess.call(
        [
            "aria2c",
            f"--input-file={os.path.join(output, Config.DOWNLOAD_INPUT_FILENAME)}",
            f"--dir={output}",
            f"--max-concurrent-downloads={Config.ARIA2C_CONCURRENT_DOWNLOADS}",
            f"--max-connection-per-server={Config.ARIA2C_CONNECTIONS}",
            "--auto-file-renaming=false",
        ]
    )


def create_output(
    recordings: List[Recording], output: str, create_xlsx: bool, aria2c: bool
) -> None:
    """Create the output.

    Args:
        recordings (List[Recording]): The recordings.
        output (str): The output path.
        create_xlsx (bool): True to create xlsx. Defaults to True.
        aria2c (bool): True to download with aria2c. Defaults to True.
    """
    print(f"[green]Found {len(recordings)} recordings.[/green]")
    if len(recordings) > 0:
        # Generate xlsx
        if create_xlsx:
            generate_xlsx(recordings, output)

        # aria2c download
        if aria2c:
            start_aria2c_download(recordings, output)
        else:
            generate_download_links_file(recordings, output)
