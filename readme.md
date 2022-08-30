# Polimi recordings downloader
This Python application is used to download a batch of lessons recordings from the Polimi recording archives.

## Set up
### System dependencies
- [Python](https://www.python.org/downloads/)
- [aria2](https://github.com/aria2/aria2/releases/): this needs to be in your $PATH (for example, put aria2c.exe inside C:\Program Files\aria2c and add this filder to $PATH)

### Python dependencies
- **(Optional) Create a virtual environment**: inside the project folder use `python -m venv .venv`. Activate the environment using `.venv\Scripts\activate.bat` on Windows or `source .venv/bin/activate` on Unix/MacOS. See [here](https://docs.python.org/3/tutorial/venv.html) for more informations about virtual envirorments. If you know how to use [Poetry](https://python-poetry.org/) you could use that instead.
- **Install libraries**: `pip install -r requirements.txt`

## Usage
Run `python prd --help` for information about usage and additional options.

This app can download the recordings from:
1. An HTML file of the recordings archives where there are all the links to the recordigs you want to download
2. A txt file with the links to the recordings
3. An URL to a Webeep "Recordings" page where the professor links the recordings.

### GUIDE 1: Download from recording archives HTML
This mode parses an HTML file from the recordings archives to fetch the download links of the videos.

In order to download a batch of recordings some steps are required:
1. With your browser [open the recordings archives](https://servizionline.polimi.it/portaleservizi/portaleservizi/controller/preferiti/Preferiti.do?evn_srv=evento&idServizio=2314). From the browser copy the `SSL_JSESSIONID` cookie value and set it using: `python prd set-cookie SSL_JSESSIONID "{COOKIE_VALUE}"`.
2. With your browser [open Webex](https://politecnicomilano.webex.com/webappng/sites/politecnicomilano/dashboard?siteurl=politecnicomilano) and login. From the browser copy the `ticket` cookie value and set it using: `python prd set-cookie ticket "{COOKIE_VALUE}"`.
3. With your browser navigare to the [recordings archive](https://servizionline.polimi.it/portaleservizi/portaleservizi/controller/preferiti/Preferiti.do?evn_srv=evento&idServizio=2314) and search for a course to download. Try to have all the recordings in a single page.
4. When you found the recordings **open the "all" page size in a new tab**. This step is required because when filtering the html content is changed dynamically and we need all the links on the source HTML.
![Open "all" page size in new tab](assets/open-all-new-tab.png)
5. Download the HTML page to a file. Right click > View Page Source then copy and paste the content or save using Ctrl+S.
6. Run `python prd archives {HTML_FILE}`.

### GUIDE 2: Download from a list of Webex urls
This mode parses an TXT file with the urls to some recordings in the format:
- `https://politecnicomilano.webex.com/politecnicomilano/ldr.php?RCID={VIDEO_ID}`
- `https://politecnicomilano.webex.com/recordingservice/sites/politecnicomilano/recording/playback/{VIDEO_ID}`
- `https://politecnicomilano.webex.com/recordingservice/sites/politecnicomilano/recording/{VIDEO_ID}/playback`
- `https://politecnicomilano.webex.com/webappng/sites/politecnicomilano/recording/{VIDEO_ID}/playback`
- `https://politecnicomilano.webex.com/webappng/sites/politecnicomilano/recording/playback/{VIDEO_ID}`

This command supports only downloading one course at the time.

Some steps are required:
1. With your browser [open Webex](https://politecnicomilano.webex.com/webappng/sites/politecnicomilano/dashboard?siteurl=politecnicomilano) and login. From the browser copy the `ticket` cookie value and set it using: `python prd set-cookie ticket "{COOKIE_VALUE}"`.
2. Run `python prd urls --course="My beutiful course" --academic-year="2021-22" {TXT_FILE}`.

### GUIDE 3: Download from Webeep "Recordings" page
1. With your browser [open Webeep](https://webeep.polimi.it). From the browser copy the `MoodleSession` cookie value and set it using: `python prd set-cookie MoodleSession "{COOKIE_VALUE}"`.
2. With your browser [open Webex](https://politecnicomilano.webex.com/webappng/sites/politecnicomilano/dashboard?siteurl=politecnicomilano) and login. From the browser copy the `ticket` cookie value and set it using: `python prd set-cookie ticket "{COOKIE_VALUE}"`.
3. With your browser navigare to the Webeep recordings section and copy the url of the page.
4. Run `python prd webeep --academic-year="2021-22" {WEBEEP_URL}`.

#### Output
Inside the output folder there will be:
- A `dowaload_links.txt` file which is the one fed to `aria2`. If the option `--no-aria2c` is used this file will contain a list of download links to be passed to another program (for example, [Free Download Manager](https://www.freedownloadmanager.org/)) to download the recordings.
- One folder for each course parsed in the HTML. Inside this folder there will be the recordings and an `xlsx` file with the recordings metadata (unless `--no-create-xlsx` is used).

## Tips
### Retrying downloads without reparsing, directly from dowaload_input_file.txt
Use the command `aria2c --input-file=output/dowaload_links.txt --auto-file-renaming=false --dir=output --max-concurrent-downloads=16 --max-connection-per-server=16`.
