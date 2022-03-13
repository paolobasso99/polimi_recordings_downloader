import os
import requests
from requests.models import Response

class WebexAPI:
    """Interact with Webex API to find download links.
    """
    def generate_download_link(video_id: str) -> str:
        """Generate a download link given a video id.

        Args:
            video_id (str): Id of the video.

        Returns:
            str: Download link.
        """
        endpoint: str = (
            "https://politecnicomilano.webex.com/webappng/api/v1/recordings/"
            + video_id
            + "/stream?siteurl=politecnicomilano"
        )
        res: Response = requests.get(endpoint, cookies={"ticket": os.getenv("WEBEX_TICKET")})

        if res.headers.get('content-type') != 'application/json':
            raise requests.exceptions.ConnectionError("Unable to connect to Webex API. Try refreshing the ticket.")

        response_obj = res.json()
        return response_obj["downloadRecordingInfo"]["downloadInfo"]["mp4URL"]