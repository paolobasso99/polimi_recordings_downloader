import subprocess
from typing import List
from RecmanParser import RecmanParser
from Recording import Recording
import os
from Config import Config
from XlsxGenerator import XlsxGenerator
from dotenv import load_dotenv

def generate_dowaload_input_file(recordings: List[Recording]) -> None:
    """Generate the file which will be passed as input to aria2c.

    Args:
        recordings (List[Recording]): List of the recordings.
    """
    print(f"Saving download links to output file...")
    if not os.path.exists(Config.OUTPUT_FOLDER):
        os.makedirs(Config.OUTPUT_FOLDER)
    with open(Config.OUTPUT_FOLDER + "/" + Config.DOWNLOAD_INPUT_FILENAME, "w") as f:
        for r in recordings:
            f.write(f"{r.download_url}\n")
            f.write(
                f"    out={r.course} {r.accademic_year}/{r.recording_datetime.strftime('%Y-%m-%d %H-%M')}.mp4\n"
            )

if __name__ == "__main__":
    load_dotenv()

    # Get recordings
    recman_parser = RecmanParser()
    recordings: List[Recording] = recman_parser.get_recordings_from_html()

    generate_dowaload_input_file(recordings)
    XlsxGenerator.create_xlsx(recordings, Config.OUTPUT_FOLDER)

    print("Starting download with aria2c...")
    p = subprocess.call(
        [
            "aria2c",
            f"--input-file={Config.OUTPUT_FOLDER}/{Config.DOWNLOAD_INPUT_FILENAME}",
            f"--dir={Config.OUTPUT_FOLDER}",
            f"--max-concurrent-downloads={Config.ARIA2C_CONCURRENT_DOWNLOADS}",
            f"--max-connection-per-server={Config.ARIA2C_CONNECTIONS}",
            "--auto-file-renaming=false",
        ]
    )
