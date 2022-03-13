# Polimi recordings archives downloader
This Python application is used to download a batch of lessons recordings from the Polimi recording archives.

## Set up
### System dependencies
- [Python](https://www.python.org/downloads/)
- [aria2](https://github.com/aria2/aria2/releases/): this needs to be in your $PATH (for example, put aria2c.exe to C:\Program Files\aria2c and add this filder to $PATH)

### Python dependencies
- **(Optional) Create a virtual environment**: inside the project folder use `python -m venv .venv`. Activate the environment using `.venv\Scripts\activate.bat` on Windows or `source tutorial-env/bin/activate` on Unix/MacOS. See [here](https://docs.python.org/3/tutorial/venv.html) for more informations about virtual envirorments.
- **Install libraries**: `pip install -r requirements.txt`

## Usage
This downloader parses an HTML page from the recordings archives to fetch the download links of the videos.

In order to download a batch of recordings some steps are required:
1. With your browser navigare to the recordings archive and search for a course to download. Try to have all the recordings in a single page.
2. When you found the recordings open the "all" page size in a new tab. This step is required because when filtering the html content is changed dynamically.
![Open "all" page size in new tab](assets/open-all-new-tab.png)
3. Download the HTML page to a `recman.html` file inside the project folder. Right click > View Page Source then copy and paste the content or save using Ctrl+S.
4. Copy `.env.example` to an `.env` file
5. Copy the SSL_JSESSIONID cookie to the `RECMAN_SSL_JSESSIONID` env variale inside `.env`
6. Open a webex link from the recordings archive and perform the login. Then you can copy the `ticket` cookie to the `WEBEX_TICKET` env variale inside `.env`
7. Run `main.py`: `python main.py`.

### Output
Inside an `output` folder there will be:
- A `dowaload_input_file.txt` file which is the one fed to `aria2`
- One folder for each course parsed in the HTML. Inside this folder there will be the recordings and an `xlsx` file with the recordings metadata.

## Tips
### Retrying downloads without reparsing, directly from dowaload_input_file.txt
Use the command `aria2c --input-file=output/dowaload_input_file.txt --auto-file-renaming=false --dir=output --max-concurrent-downloads=16 --max-connection-per-server=16`.
