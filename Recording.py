from datetime import datetime


class Recording:
    """Class representing the recordings.
    """
    def __init__(
        self,
        video_id: str,
        accademic_year: str,
        recording_datetime: datetime,
        course: str,
        subject: str,
        download_url: str
    ) -> None:
        """Create a Recording.

        Args:
            video_id (str): Id of the Webex video.
            accademic_year (str): Accademic year string in the format "2021-22".
            recording_datetime (datetime): Recording datetime.
            course (str): Course name.
            subject (str): Subject.
            download_url (str): Download url of the recording.
        """
        self.video_id = video_id.strip()
        self.accademic_year = accademic_year.strip()
        self.recording_datetime = recording_datetime
        self.course = course.strip()
        self.subject = subject.strip()
        self.download_url = download_url.strip()

    def __lt__(self, other):
        return self.recording_datetime < other.recording_datetime
