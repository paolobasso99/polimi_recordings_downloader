from Config import Config
from Recording import Recording
from typing import List
import os

def generate_input_file(recordings: List[Recording], output: str) -> None:
    """Generate the file which will be passed as input to aria2c.

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
            f.write(
                f"    out={r.course} {r.accademic_year}/{r.recording_datetime.strftime('%Y-%m-%d %H-%M')}.mp4\n"
            )
