import os
import subprocess
from typing import List
from rich.progress import track
from rich import print

from prd.config import Config
from prd.webex_api import Recording


def generate_input_file(recordings: List[Recording], output: str) -> None:
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


def aria2c_download(recordings: List[Recording], output: str) -> None:
    """Start download with aria2c.

    Args:
        recordings (List[Recording]): The recordings to download.
        output (str): The output folder.
    """
    generate_input_file(recordings, output)
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
