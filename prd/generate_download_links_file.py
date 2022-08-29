from Config import Config
from Recording import Recording
from typing import List
import os

def generate_download_links_file(recordings: List[Recording], output: str) -> None:
    """Generate the file with the download links.

    Args:
        recordings (List[Recording]): List of the recordings.
        output (str): The output folder.
    """
    if not os.path.exists(Config.DEFAULT_OUTPUT_FOLDER):
        os.makedirs(Config.DEFAULT_OUTPUT_FOLDER)
    with open(
        os.path.join(output, Config.DOWNLOAD_INPUT_FILENAME), "w"
    ) as f:
        for r in recordings:
            f.write(f"{r.download_url}\n")
