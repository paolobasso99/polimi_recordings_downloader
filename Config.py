class Config:
    """Configuration variables of the application.
    """
    OUTPUT_FOLDER: str = "output"
    DOWNLOAD_INPUT_FILENAME: str = "dowaload_input_file.txt"
    ARIA2C_CONCURRENT_DOWNLOADS: str = str(16)
    ARIA2C_CONNECTIONS: str = str(16)