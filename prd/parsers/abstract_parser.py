from typing import Optional, List

from prd.webex_api import Recording


class Parser:
    """Abstract class of a parser."""

    def __init__(
        self,
        cookie_ticket: str,
        cookie_SSL_JSESSIONID: Optional[str] = None,
        cookie_MoodleSession: Optional[str] = None,
    ):
        """Create the parser.

        Args:
            cookie_ticket (str): The ticket cookie.
            cookie_SSL_JSESSIONID (Optional[str], optional): The SSL_JSESSIONID cookie. Defaults to None.
            cookie_MoodleSession (Optional[str], optional): The MoodleSession cookie. Defaults to None.

        Raises:
            ValueError: If the cookie ticket is not set.
        """
        if cookie_ticket is None or len(cookie_ticket) == 0:
            raise ValueError("The cookie ticket must be set.")
        self.cookie_ticket = cookie_ticket
        self.cookie_SSL_JSESSIONID = cookie_SSL_JSESSIONID
        self.cookie_MoodleSession = cookie_MoodleSession

    def parse(
        self, source, course: Optional[str] = None, academic_year: Optional[str] = None
    ) -> List[Recording]:
        """Parse the source.

        Args:
            source: The source.
            course (Optional[str], optional): The course name.. Defaults to None.
            academic_year (Optional[str], optional): The academic year in the format "2021-22". Defaults to None.

        Raises:
            NotImplementedError: This method must be implemented.

        Returns:
            List[Recording]: The list of recordings.
        """
        raise NotImplementedError("The method parse must be implemented.")
