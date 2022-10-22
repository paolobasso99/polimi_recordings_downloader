class Config:
    """Configuration variables of the application."""

    APP_NAME: str = "polimi_recordings_downloader"
    DEFAULT_OUTPUT_FOLDER: str = "output"
    DOWNLOAD_INPUT_FILENAME: str = "dowaload_links.txt"
    ARIA2C_CONCURRENT_DOWNLOADS: str = str(16)
    ARIA2C_CONNECTIONS: str = str(16)
    COOKIES_STORE_FILENAME: str = "cookies.json"
