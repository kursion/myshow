#/usr/bin/python

import urllib.request
import os, json, argparse, sys, shutil, time
import xml.etree.ElementTree as ET
from subprocess import call, STDOUT, Popen
import importlib

titleFilter = "720p"


class MyShow:
    'MyShow application to download torrent automatically from a rss flux'
    VERSION = "0.0.1"
    FNULL = open(os.devnull, 'w') # To hide the output
    FILENAMES = {
        "hashed": "hashed.dat",
        "series": "series.json"
    }
    STATE = {
        "started": {"deluged": False, "deluge-web": False, "autoupdate": False}
    }
    BIN = {
        "deluged": "deluged",
        "deluge-web": "deluge-web"
    }
    ERRORS = {
        "deluge": "Please install deluge (for windows users add the folder to the PATH).",
        "python2": "Python 2 is needed for deluge. The command 'python2' wasn't found. Please install python2. For windows users add python2 into your PATH as 'python2'.",
        "python2-mako": "Mako is not install for python2. This package is used for deluge-web. Please install it to start the web interface. On Linux: 'pip2 install mako'.",
        "series_not_found": "Series variable in series file not found.",
    }
    SERIES = {}

    def __init__(self):
        self.ARGS = self._parseArgs() # Cmd arguments
        self._checkPythonDependencies()
        self._initHashed()
        self._processArgs()

    def _initHashed(self):
        f = open(MyShow.FILENAMES["hashed"], "a+").close()
        if self.ARGS.verbosity: print("[OK]\tChecking", MyShow.FILENAMES["hashed"])

    def _parseArgs(self):
        parser = argparse.ArgumentParser(description='Automatically download your rss torrents')
        parser.add_argument('--init', help='Init myshow with \'series.json\' (without downloading on first run)', action='store_true')
        parser.add_argument('-u', '--update', help='Check and download new series once', action='store_true')
        parser.add_argument('-a', '--auto', help='Automatically update based on hourly interval', action='store_true')
        parser.add_argument('-d', '--deluged', help='Start deluged', action='store_true')
        parser.add_argument('-dw', '--deluge-web', help='Start deluge-web (default port: 8112)', action='store_true')
        parser.add_argument('-n', '--new', help='Add a new serie')
        parser.add_argument('-i', '--interval', help='Interval of updates in hour (default: 1)', default=1)
        parser.add_argument('-v', '--version', help='Show version number of MyShow', action="store_true")
        parser.add_argument('--verbosity', help='Verbose mode', action="store_true")
        return parser.parse_args()

    def _processArgs(self):
        'Action to take for each argument passed'
        ARGS = self.ARGS
        if not ARGS.interval.isdigit():
            print("[X]\tInterval should be a number not '"+ARGS.interval+"'")
            sys.exit(1)
        elif int(ARGS.interval) < 1:
            print("[X]\tMinimum interval time should be 1")
            sys.exit(1)
        if ARGS.version: print("Version: ", MyShow.VERSION)
        if ARGS.deluged or ARGS.auto: self.startDeluged() # Start deluged
        if ARGS.deluge_web: self.startDelugeWeb() # Start deluge-web
        if ARGS.auto:
            if ARGS.init: self.updateSeries(initOnly=ARGS.init)
            self.updateSeriesAuto()
        elif ARGS.update or ARGS.init: self.updateSeries(initOnly=ARGS.init)
        if ARGS.new: print("TODO ADD a serie")

    def _terminate(self, msg, code=0):
        if msg is not None: print("[X]\t"+msg, "Terminating... [CODE="+str(code)+"]")
        pkill = shutil.which("pkill")
        if pkill:
            if call(["pkill", MyShow.BIN["deluged"]]) != 0: print("[X]\tCouldn't terminated deluged")
            if call(["pkill", MyShow.BIN["deluge-web"]]) != 0: print("[X]\tCouldn't terminated deluged")
        sys.exit(code)

    def _checkPython2Module(self, module):
        'Test if a python 2 module exists'
        ppython2 = shutil.which("python2")
        if ppython2 is None:
            self._terminate(self.ERRORS["python2"], 2)
        if call(["python2", "-c", "'import "+module+"'"], stdout=MyShow.FNULL, stderr=STDOUT) == 0: return True
        else: return False

    def _checkPythonDependencies(self):
        'This is very ugly and boring to do... thanks python2 and deluge'
        if self.ARGS.verbosity:
            print("Checking python dependencies")

        if self.ARGS.deluge_web:
            psudo = shutil.which("sudo")
            ppip2 = shutil.which("pip2")
            if not self._checkPython2Module('mako'):
                if not ppip2:
                    self._terminate(MyShow.ERRORS["python2-mako"], 2)
                else:
                    if self.ARGS.verbosity: print("Installing python2-mako for web interface")
                    pip2cmd = ["pip2", "install", "mako"]
                    code = call(pip2cmd, stdout=MyShow.FNULL, stderr=STDOUT)
                    if code != 0 and psudo != None:
                        pip2cmd = ["sudo"]+pip2cmd
                        code = call(pip2cmd, stdout=MyShow.FNULL, stderr=STDOUT)
                    if code != 0:
                        self._terminate("Couldn't install python2-make for deluge-web.", 2)
        if self.ARGS.deluged or self.ARGS.deluge_web:
            if not self._checkPython2Module("service_identity"):
                if self.ARGS.verbosity: print("Installing python2-service_identity for web deluge")
                pip2cmd = ["pip2", "install", "service_identity"]
                code = call(pip2cmd, stdout=MyShow.FNULL, stderr=STDOUT)
                if code != 0 and psudo != None:
                    pip2cmd = ["sudo"]+pip2cmd
                    code = call(pip2cmd, stdout=MyShow.FNULL, stderr=STDOUT)
                if code != 0:
                    print("WARNING: couldn't install service_identity. This is an optionnal package for deluge")

    def _startProcess(self, processName, args=None, kill=True, detached=False):
        ' Start a process name if it exists'
        MyShow.STATE["started"][processName] = True
        bin = shutil.which(processName)
        pkill = shutil.which("pkill")
        if not bin:
            if processName in MyShow.ERRORS.keys():
                if processName in ["deluged", "deluge-web", "deluge-console"]: errName = "deluge"
                else: errName = processName
                self._terminate(MyShow.ERRORS[errName], 1)
            else:
                raise Exception("Couldn't find process name", processName)
        if kill and pkill: call(["pkill", processName])
        if self.ARGS.verbosity:
            print("[?]\tStarting", processName, "("+bin+")")
            if detached:
                return Popen([processName])
            code = call([processName])
        else:
            if detached:
                return Popen([processName], stdout=MyShow.FNULL, stderr=STDOUT)
            code = call([processName], stdout=MyShow.FNULL, stderr=STDOUT)
        if code != 0:
            self._terminate("An error occured while trying to start "+processName, code)

    def _getRSS(self, url):
        response = urllib.request.urlopen(url)
        data = response.read()
        return data.decode('utf-8')

    def _parseXML(self, xml):
        root = ET.fromstring(xml)[0]
        mlinks = [] # magnet links
        for child in root.iter('item'):
            title = child.find("title").text
            link = child.find("link").text
            hash = child.find("{http://showrss.info/}info_hash").text
            mlinks.append({"mlink": link, "hash": hash, "title": title})
        return mlinks

    def _filterLinks(self, mlinks):
        f = open(MyShow.FILENAMES["hashed"], "r")
        filteredLinks = []
        episodes = f.readlines()
        f.close()

        f = open(MyShow.FILENAMES["hashed"], "a")
        for mlink in mlinks:
            if titleFilter in mlink["title"]:
                ep = mlink["title"]+":"+mlink["hash"]+"\n"
                if not ep in episodes:
                    if self.ARGS.verbosity:
                        print("[OK]\tNew episode:", mlink["title"])
                    f.write(ep)
                    filteredLinks.append(mlink)
        f.close()
        return filteredLinks

    def startDeluged(self):
        'Starting deluged process'
        self._startProcess(MyShow.BIN["deluged"])
        if self.ARGS.verbosity: print("[OK]\tDeluged started")

    def _delugeAdd(self, mlinks):
        for link in mlinks:
            print("Adding to deluge", link["title"])
            if self.ARGS.verbosity:
                code = call(["deluge-console", "add", link["mlink"]], stdout=MyShow.FNULL, stderr=STDOUT)
            else:
                code = call(["deluge-console", "add", link["mlink"]])
            if code != 0:
                print("Magnet failed: ", link["mlink"])
                print("WARNING: couldn't add serie", link["title"], "to deluge (CODE=", code,")")

    def startDelugeWeb(self):
        'Starting deluge-web process (default port is 8112)'
        running = False
        process = self._startProcess(MyShow.BIN["deluge-web"], detached=True)
        while not running:
            try:
                os.kill(process.pid, 0)
                running = True
            except:
                if self.ARGS.verbosity: print("[?]\tWaiting for deluge-web to start...")
                time.sleep(4)
        if self.ARGS.verbosity: print("[OK]\tDeluge-web started in detached mode. Default port is generally: 8112")

    def getSeries(self):
        if self.ARGS.verbosity: print("[?]\tGetting series")
        try:
            json_series = open(MyShow.FILENAMES["series"])
        except:
            self._terminate("No filename '"+MyShow.FILENAMES["series"]+"' found.")
        try:
            series = json.load(json_series)
        except:
            self._terminate("Wrong json format for '"+MyShow.FILENAMES["series"]+"'.")
        if "series" not in series.keys():
            self._terminate(MyShow.ERRORS["series_not_found"])
        self.checkSeriesFormat(series["series"])
        MyShow.SERIES = series["series"] # TODO: this is maybe not needed :/
        if self.ARGS.verbosity:
            nbrSeries = len(MyShow.SERIES)
            if nbrSeries > 0:
                print("[OK]\tfound", nbrSeries, "series", MyShow.SERIES.keys())
            else:
                self._terminate("No series found in "+self.FILENAMES["series"]+".")

        return series["series"]

    def checkSeriesFormat(self, series):
        for k in series:
            if k.strip() == "":
                self._terminate("Serie name '"+k+"' is wrong. It should be the title of your serie.")
            if "http" not in series[k][:4]:
                self._terminate("Serie URL '"+series[k]+"' is wrong. It should be an URL for your serie.")

    def updateSeries(self, initOnly=True):
        '''Update series. If initOnly is set to true, MyShow won't dowload any series'''
        if self.ARGS.verbosity:
            if initOnly: print("Initializing MyShow...")
            else: print("Updating MyShow to the latests series")
        series = self.getSeries()
        nbrNewEpisodes = 0
        for serieName in series:
            url = series[serieName]
            rssXML = self._getRSS(url)
            mlinks = self._parseXML(rssXML)
            filteredLinks = self._filterLinks(mlinks)

            nbrLinks = len(filteredLinks)
            nbrNewEpisodes += nbrLinks
            if not initOnly and nbrLinks>0:
                self._delugeAdd(filteredLinks)
                if self.ARGS.verbosity: print(serieName, "downloading", nbrLinks, "new episodes !")
        if nbrNewEpisodes == 0 and self.ARGS.verbosity and not initOnly: print("Not a single new episode to watch :(")
        if self.ARGS.verbosity and initOnly: print("""~~~ Warning ~~~
MyShow was initialized. Run it with the '--update' option
to download latest series from today or with the '--auto' option
to check periodically for new series to download
~~~~~~~~~~~~~~~""")

    def updateSeriesAuto(self):
        waitTime = int(self.ARGS.interval)*3600
        waitTime = 30
        print("[OK]\tUpdating every:", waitTime/3600, "hours")
        while 1:
            try:
                time.sleep(waitTime)
                print("~ Updating ~")
                self.updateSeries(False)
            except KeyboardInterrupt:
                self._terminate("\n\nByebye.")


if __name__ == '__main__':
    ms = MyShow()

