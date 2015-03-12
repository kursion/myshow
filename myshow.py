#/usr/bin/python

import urllib.request
import os, json
import xml.etree.ElementTree as ET
from subprocess import call, STDOUT

titleFilter = "720p"

FNULL = open(os.devnull, 'w') # To hide the output

series = {}

def init():
    global series
    f = open("hashed.dat", "a+")
    f.close()
    os.system("deluged 2> /dev/null")
    json_series = open("series.json")
    series = json.load(json_series)
    series = series["series"]

def getRSS(url):
    response = urllib.request.urlopen(url)
    data = response.read()
    return data.decode('utf-8')

def parseXML(xml):
    root = ET.fromstring(xml)[0]
    links = []
    for child in root.iter('item'):
        title = child.find("title").text
        link = child.find("link").text
        hash = child.find("{http://showrss.info/}info_hash").text
        links.append({"link": link, "hash": hash, "title": title})
    return links

def filterLinks(links):
    f = open("hashed.dat", "r")
    filteredLinks = []
    episodes = f.readlines()
    f.close()

    f = open("hashed.dat", "a")
    for link in links:
        if titleFilter in link["title"]:
            ep = link["title"]+":"+link["hash"]+"\n"
            if not ep in episodes:
                print("New episode:", link["title"])
                f.write(ep)
                filteredLinks.append(link)
    f.close()
    return filteredLinks

def delugeAdd(links):
    for link in links:
        print("Adding to deluge", link["title"])
        #call(["deluge-console", "add", link["link"]], stdout=FNULL, stderr=STDOUT)
        call(["deluge-console", "add", link["link"]])

init()
totalOperation = 0
for serieName in series:
    url = series[serieName]
    rssXML = getRSS(url)
    # print(rss)
    links = parseXML(rssXML)
    # print(links)
    filteredLinks = filterLinks(links)
    totalOperation += len(filteredLinks)
    # print(filteredLinks)
    delugeAdd(filteredLinks)
    print(serieName, ":", url, "| new episodes:", len(filteredLinks))

if totalOperation == 0:
    print("Nothing new for the moment")

FNULL.close()
