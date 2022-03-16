from Config import Config
from Recording import Recording
from typing import List
import subprocess
from .generate_input_file import generate_input_file
import os


def download(recordings: List[Recording], output: str) -> None:
    """Start download with aria2c.

    Args:
        recordings (List[Recording]): The recordings to download.
        output (str): The output folder.
    """
    generate_input_file(recordings, output)
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
