from datetime import datetime

from prd.utils import replace_illegal_characters


class Recording:
    """Class representing a recordings."""

    def __init__(
        self,
        video_id: str,
        academic_year: str,
        recording_datetime: datetime,
        course: str,
        subject: str,
        download_url: str,
    ) -> None:
        """Create a Recording.

        Args:
            video_id (str): Id of the Webex video.
            academic_year (str): Academic year string in the format "2021-22".
            recording_datetime (datetime): Recording datetime.
            course (str): Course name.
            subject (str): Subject.
            download_url (str): Download url of the recording.
        """
        self.video_id = video_id.strip()
        self.academic_year = academic_year.strip()
        self.recording_datetime = recording_datetime
        self.course = replace_illegal_characters(course.strip())
        self.subject = subject.strip()
        self.download_url = download_url.strip()

    def get_video_url(self) -> str:
        """Get the url to the recording.

        Returns:
            str: The url to the recording.
        """
        return (
            "https://politecnicomilano.webex.com/recordingservice/sites/politecnicomilano/recording/"
            + self.video_id
        )

    def __lt__(self, other):
        return self.recording_datetime < other.recording_datetime
