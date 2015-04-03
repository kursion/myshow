# myshow
A little script that will automatically download torrent serie's episodes
based on a rss flux.

*NOTE: for the moment only showrss.info is supported.*

# Dependencies
- Linux (not tested with other plateforms but it should work with some adaptations)
- python3 for myshow (https://www.python.org/)
- python2 for deluge (https://www.python.org/)
- deluge (http://deluge-torrent.org/)
- [optional] pip2 to automatically install python2 dependencies (https://pypi.python.org/pypi)
- [optional] showRSS.info account (http://showrss.info/?cs=feeds)
- [optional] python2-service_identity for deluge (https://pypi.python.org/pypi/service_identity)
- [optional] python2-mako for deluge-web (http://www.makotemplates.org/)

# Installation
Be sure to install all dependencies and check if the command `> deluged`
is working correctly in your terminal. MyShow will try to automatically
install python2 dependencies if you installed pip2 and python2.

*You might get a warning for 'service_identity' while running myshow. This warning comes
from deluge-web. Install the dependencie service_identity (`pip2 install service_identity`)
if it failed with the automatic installation from myshow.
 `UserWarning: You do not have the service_identity module installed.`.
This is not important. Deluge deamon (deluged) is working correctly.*

# Check if myshow works
Check if the command works correctly

`> python myshow.py -v` or `> python3 myshow.py -v`

You should have something like this
```
> python myshow.py -v
[?] Checking python dependencies
[OK]  Checking hashed.dat
```

If so, then myshow is ready to do the job.

# MyShow commands
```
usage: myshow.py [-h] [--init] [-u] [-a] [-d] [-dw] [-n NEW] [-i INTERVAL]
                 [--version] [-v]

Automatically download your rss torrents

optional arguments:
  -h, --help            show this help message and exit
  --init                Init myshow with 'series.json' (without downloading on
                        first run)
  -u, --update          Check and download new series once (deluged
                        automatically launched)
  -a, --auto            Automatically update based on hourly interval (deluged
                        automatically launched)
  -d, --deluged         Start deluged
  -dw, --deluge-web     Start deluge-web (default port: 8112)
  -n NEW, --new NEW     Add a new serie
  -i INTERVAL, --interval INTERVAL
                        Interval of updates in hour (default: 1)
  --version             Show version number of MyShow
  -v, --verbose         Verbose mode
```

# Adding series / Track a serie

1. Go to http://showrss.info and create an account (no email needed)
2. Navigate to **feeds** in the top menu (http://showrss.info/?cs=feeds)
3. Select **A single show** (your serie) and click on **Get feed address**
4. Copy the **public feed** address for that specific serie (eg:
 *http://showrss.info/feeds/1014.rss*)

Then add the serie to myshow with initialization:
`python3 myshow.py -a http://showrss.info/feeds/1014.rss --init -v`

- `-n`: will append the new feed to be tracked by myshow.
- `--init`: will catch the latest feed. This step is to down in order to
avoid downloading all episodes.
- `-v`: will launch myshow in verbose mode.

You should have something like this
```
python3 myshow.py -n http://showrss.info/feeds/1014.rss -u --init -v
[?] Checking python dependencies
[OK]  Checking hashed.dat
[?] Getting series
[OK]  found 3 series
 Arrow
 The Vampire Diaries
 Game of Thrones
http://showrss.info/feeds/1014.rss
{'Arrow': 'http://showrss.info/feeds/505.rss', 'The Vampire Diaries': 'http://showrss.info/feeds/205.rss', '12 Monkeys': 'http://showrss.info/feeds/1014.rss', 'Game of Thrones': 'http://showrss.info/feeds/350.rss'}
Initializing MyShow...
[?] Getting series
[OK]  found 4 series
 Arrow
 The Vampire Diaries
 12 Monkeys
 Game of Thrones
[OK]  New episode: 12 Monkeys 1x09 Tomorrow 720p
[OK]  New episode: 12 Monkeys 1x08 Yesterday 720p
[OK]  New episode: 12 Monkeys 1x07 The Keys 720p
[OK]  New episode: 12 Monkeys 1x06 The Red Forest 720p
[OK]  New episode: 12 Monkeys 1x05 The Night Room 720p
[OK]  New episode: 12 Monkeys 1x04 Atari 720p
[OK]  New episode: 12 Monkeys 1x03 Cassandra Complex 720p
[OK]  New episode: 12 Monkeys 1x02 720p
```



Now MyShow will track: 12 Monkeys, Arrow and Vampire Diaries episodes.
Since we specified the `--init` option, myshow will prevent downloading the latest episode
directly. Thus when running myshow with the update option (see section: **Run myshow**)


# Run myshow
Just run this command

`> python myshow.py -u -v`

in order to check for new series and start downloading new episodes in deluge.

*The downloaded file should be in "Deluge download folder".
You can check this by opening deluge and look at the configuration options. Normally,
it should be downloaded into your `home/username/Downloads` folderi by default.*

# Run periodically
Simply launch the script with the option `--auto`. By defaut the interval is set to
one hour. But you can specify yours using the `-i INTERVAL` option. Example for two hours
interval:

`> python3 myshow.py -a -v -i 2`

Every 2 hours, myshow will get the list of the RSS flux and check for new episodes. If
it detectes an undownloaded episode, it will add the torrent to *deluged*.

# Deluge web interface
You can also tell myshow to run the deluge-web interface by passing the option `-dw` or `--deluge-web`.
Example:

`> python3 myshow.py -a -v -i 2 -dw`

The default port is *8112*, and the default password is *deluge*

# Decrease resources notes
For low settings, you should modify deluge to consume less resources. The first time I saw
"Deluge is a lightweight client for torrent", I told myself: "Perfect for my project !". But
I found out that deluged and deluged-web needed more thant 500Mb of RAM memory in order to
work. Well, this isn't true. Here is a simple guide to low down deluge resources:

- Launche the web interface (`python3 myshow.py -dw`) and connect on "127.0.0.1:8112" with your favorite browser. It can
take up to 1-2 minutes in order to launch deluge-web.
- Go to "Preferences" (at the top) and choose the "Bandwidth" category.
- Low down the following options to decrease deluged resources: Max Connections, Max Upload slots,
Max Half-Open Connections, Maximum Connection Attempts per Second in the **Global Bandwitch Usage** section.

# Deluge-web example for Raspberry PI
Here is an example of configuration for RaspberryPI:
```
Global Bandwith Usage
Maximum Connections: 60
Maximum Upload Slots: 2
Maximum Download Speed (KiB/s): 2000     [this depends on your bandwitdh]
Maximum Upload Speed (KiB/s): 10         [this depends on your bandwidth]
Maximum Half-Open Connection: 30
Maximum Connection Attempts per Second: 5
Uncheck "Ignore limits on local network"
Check "Rate limit IP overhead"
```

# Things to do
- Parsers folder to have multiple source (not only showrss.info)
- Installer for /usr/bin


