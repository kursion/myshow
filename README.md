# myshow
A little script that will automatically download torrent serie's episodes
based on http://showRSS.info rss list.

# Dependencies
- Linux (not tested with other plateforms but it should work with some adaptations)
- python 3 (https://www.python.org/)
- deluge (http://deluge-torrent.org/)
- showRSS.info account (http://showrss.info/?cs=feeds)

# Installation
Be sure to install all dependencies and check if the command `> deluged`
 is working correctly in your terminal.

*You might get a warning
 `UserWarning: You do not have the service_identity module installed.`.
This is not important. Deluge deamon (deluged) is working correctly.*

Check if the command works correctly

`> python myshow.py` or `> python3 myshow.py`

If so, then myshow is ready to do the job.

# Adding series / Track a serie

1. Go to http://showrss.info and create an account (no email needed)
2. Navigate to **feeds** in the top menu (http://showrss.info/?cs=feeds)
3. Select **A single show** (your serie) and click on **Get feed address**
4. Copy the **public feed** address for that specific serie (eg: *http://showrss.info/feeds/1014.rss*)

Open `series.json` file with a text editor and add a new entry for that serie.
*Don't forget to add a coma after each entry*

##### before:
```json
{
  "series": {
    "Arrow": "http://showrss.info/feeds/505.rss",
    "The Vampire Diaries": "http://showrss.info/feeds/205.rss",
  }
}
```

##### after:
```json
{
  "series": {
    "Arrow": "http://showrss.info/feeds/505.rss",
    "The Vampire Diaries": "http://showrss.info/feeds/205.rss",
    "12 Monkey": "http://showrss.info/feeds/1014.rss",

  }
}
```

# Run myshow
Just run this command
`> python3 myshow`

*Undownloaded episode in 720p. The downloaded file should be in "Deluge download folder".
You can check this by opening deluge and look at the configuration options. Normally,
it should be downloaded into your `home/username/Downloads` folder.*

Beaware that the first time, myshow will download every episode that showRSS.info will
present.

# Run every hours
Simply launch the **autoupdate.sh** script so myshow
will be executed very hours.

`./autoupdate.sh`

# Things to do
- Configuration file
- Parameters
- Add, remove command for series
- Init (to ignore downloading everything)
- Configuration date for each series
- First S00E00 to download


