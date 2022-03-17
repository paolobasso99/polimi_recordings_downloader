import re
import requests
from requests.models import Response
from cookies import get_cookie


def extract_id_from_url(url: str) -> str:
    """Extract the video id from a url.
    Urls can be in the formats:
    - https://politecnicomilano.webex.com/politecnicomilano/ldr.php?RCID={VIDEO_ID}
    - https://politecnicomilano.webex.com/recordingservice/sites/politecnicomilano/recording/playback/{VIDEO_ID}
    - https://politecnicomilano.webex.com/recordingservice/sites/politecnicomilano/recording/{VIDEO_ID}/playback

    Args:
        url (str): Url of the recording.

    Returns:
        str: Video id of the recording.

    Raises:
        ValueError: if the provided url is not recorgnized.
    """
    if url.startswith(
        "https://politecnicomilano.webex.com/politecnicomilano/ldr.php?RCID="
    ):
        res: Response = requests.get(url, cookies={"ticket": get_cookie("ticket")})
        id_search = re.search(
            "https:\/\/politecnicomilano\.webex\.com\/recordingservice\/sites\/politecnicomilano\/recording\/playback\/([a-z,0-9]*)",
            res.text,
        )
        if not (id_search):
            raise RuntimeError("Was not able to extract video id from url.")

        return id_search.group(1)
    elif url.startswith(
        "https://politecnicomilano.webex.com/recordingservice/sites/politecnicomilano/recording/"
    ):
        search_str: str = "https:\/\/politecnicomilano\.webex\.com\/recordingservice\/sites\/politecnicomilano\/recording\/playback\/([a-z,0-9]*)"
        if url.endswith("/playback"):
            search_str: str = "https:\/\/politecnicomilano\.webex\.com\/recordingservice\/sites\/politecnicomilano\/recording\/([a-z,0-9]*)\/playback"

        id_search = re.search(search_str, url)
        if not (id_search):
            raise RuntimeError("Was not able to extract video id from url.")

        return id_search.group(1)
    else:
        raise ValueError("The provided url is not recorgnized.")
