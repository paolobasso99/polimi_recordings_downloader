from datetime import datetime
from typing import Optional
import requests
from requests.models import Response

from prd.webex_api.Recording import Recording


def generate_recording_from_id(
    video_id: str,
    ticket: str,
    course: str,
    academic_year: str,
    subject: Optional[str] = None,
    recording_datetime: Optional[datetime] = None,
) -> Recording:
    """Generate a Recording given a video id.

    Args:
        video_id (str): Id of the video.
        ticket (str): The "ticket" cookie value.
        course (str): Name of the course.
        academic_year (str): The academic year of the course.
        subject (str, optional): The subjet of the recording. If None use the title of the recording.
        recording_datetime (datetime, optional): The datetime of the recording. If None use get from the API.

    Returns:
        Recording: The Recording object.
    """
    # Get video information from API
    endpoint: str = (
        "https://politecnicomilano.webex.com/webappng/api/v1/recordings/"
        + video_id
        + "/stream?siteurl=politecnicomilano"
    )
    res: Response = requests.get(
        endpoint, cookies={"ticket": ticket}
    )
    if res.headers.get("content-type") != "application/json":
        raise requests.exceptions.ConnectionError(
            "Unable to connect to Webex API. Try refreshing the ticket."
        )
    response_obj = res.json()
    download_url: str = response_obj["downloadRecordingInfo"]["downloadInfo"]["mp4URL"]
    if response_obj["preventDownload"] == True:
        download_url = response_obj["fallbackPlaySrc"]

    if subject is None:
        subject = response_obj["recordName"]
    if recording_datetime is None:
        recording_datetime = datetime.strptime(
            response_obj["createTime"], "%Y-%m-%d %H:%M:%S"
        )

    return Recording(
        video_id=video_id,
        course=course,
        academic_year=academic_year,
        download_url=download_url,
        subject=subject,
        recording_datetime=recording_datetime,
    )
