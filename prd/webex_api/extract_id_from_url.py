import re
import requests
from requests.models import Response
from urllib.parse import unquote


def extract_id_from_url(url: str, ticket: str) -> str:
    """Extract the video id from a url.
    Urls can be in the formats:
    - https://politecnicomilano.webex.com/politecnicomilano/ldr.php?RCID={VIDEO_ID}
    - https://politecnicomilano.webex.com/recordingservice/sites/politecnicomilano/recording/playback/{VIDEO_ID}
    - https://politecnicomilano.webex.com/recordingservice/sites/politecnicomilano/recording/{VIDEO_ID}/playback
    - https://politecnicomilano.webex.com/recordingservice/sites/politecnicomilano/recording/{VIDEO_ID}
    - https://politecnicomilano.webex.com/webappng/sites/politecnicomilano/recording/playback/{VIDEO_ID}
    - https://politecnicomilano.webex.com/webappng/sites/politecnicomilano/recording/{VIDEO_ID}/playback
    - https://politecnicomilano.webex.com/webappng/sites/politecnicomilano/recording/{VIDEO_ID}

    Args:
        url (str): Url of the recording.
        ticket (str): The "ticket" cookie value.

    Returns:
        str: Video id of the recording.

    Raises:
        ValueError: if the provided url is not recorgnized.
    """
    url = unquote(url)
    url = url.replace("/webappng", "/recordingservice")
    url = url.replace("/sites/politecnicomilano/recording", "")
    url = url.replace("/playback", "")

    if url.startswith(
        "https://politecnicomilano.webex.com/politecnicomilano/ldr.php?RCID="
    ):
        res: Response = requests.get(url, cookies={"ticket": ticket})
        id_search = re.search(
            "https:\/\/politecnicomilano\.webex\.com\/recordingservice\/sites\/politecnicomilano\/recording\/playback\/([a-z,0-9]*)",
            res.text,
        )
        if not (id_search):
            raise RuntimeError("Was not able to extract video id from url.")

        return id_search.group(1)
    elif url.startswith("https://politecnicomilano.webex.com/recordingservice/"):
        search_str: str = (
            "https:\/\/politecnicomilano\.webex\.com\/recordingservice\/([a-z,0-9]*)"
        )

        id_search = re.search(search_str, url)
        if not (id_search):
            raise RuntimeError("Was not able to extract video id from url.")

        return id_search.group(1)
    else:
        raise ValueError("The provided url is not recorgnized.")
