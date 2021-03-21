#! /usr/bin/env python3
# -*- encoding: latin1 -*-pwd


# Socket client example in python

#import socket
import sys 
import os 
import time
import logging
import json
import platform
import requests

# ---------- functions ----------

def getDataFromLMS(req):
    json_resp = requests.post(lms_url, data=json.dumps(req), headers={"Content-Type":"application/json"})
    if json_resp.status_code != 200:
        return {"result": {"error":"HTTP Status is " + json_resp.status_code}}

    return json.loads(json_resp.content)

# ---------- main ---------------

logging.basicConfig(level=logging.INFO)

# basic configuration
host = '192.168.2.10'
port = 9090
web_port = 9000
file_loc = ''
lms_url = "http://" + host + ":" + str(web_port) + "/jsonrpc.js"
player = "00:04:20:23:20:b2"

# Dev on Mac, but runs later on openhabian Raspberry
my_env = platform.system()

if my_env == 'Darwin':
    # write HTML files in local directory
    file_loc = './'
else:
    # write HTML files in OpenHab static content directory
    file_loc = '/etc/openhab/html/'

# Get Artists from LMS
logging.debug("------------- current artist ------------------")

json_req = { 
    "method": "slim.request",
    "params":
    [
        player,
        [
            "artist",
            "?"
        ]
    ]
}

json_artist = getDataFromLMS(json_req)
cur_artist = json_artist["result"]["_artist"]

logging.debug("Current artist: [" + cur_artist + "]")

# Get Title from LMS
logging.debug("------------- current title ------------------")

json_req = { 
    "method": "slim.request",
    "params":
    [
        player,       
        [
            "title",
            "?"
        ]
    ]
}

json_title = getDataFromLMS(json_req)
cur_title = json_title["result"]["_title"]


logging.debug("Current title: [" + cur_title + "]")

# Get Lyrics from LMS
logging.debug("------------- lyrics ------------------")

# used for debugging - invalid artist and title
# cur_artist = "Heinz"
# cur_title = "Becker"

json_req = { 
    "method": "slim.request",
    "params":
    [
        player,       
        [
            "musicartistinfo",
            "lyrics",
            "artist:" + cur_artist,
            "title:" + cur_title
        ]
    ]
}

json_lyrics = getDataFromLMS(json_req)

lyrics_avail = "1"

if "error" in json_lyrics["result"]:
    lyrics_avail = "0"

# Build HTML page to display in HabPanel
if lyrics_avail == "0":
    lyrics = "<html><p style=\"color:white;\"><font face=\"Helvetica\">No lyrics available</font></p></html>"
else:
    lyrics = json_lyrics["result"]["lyrics"]
    lyrics = lyrics.replace("\n", "<br/>")
    lyrics = "<html><p style=\"color:white;\"><font face=\"Helvetica\">" + lyrics + "</font></p></html>"

f= open(file_loc + "lyrics.html","w+")
f.write(lyrics)
f.close() 

# Get Photos from LMS
logging.debug("------------- Artist Photos ------------------")

json_req = { 
    "method": "slim.request",
    "params":
    [
        player,       
        [
            "musicartistinfo",
            "artistphotos",
            "artist:" + cur_artist
        ]
    ]
}

json_photos = getDataFromLMS(json_req)

# Get Biography from LMS
logging.debug("------------- Artist Bio ------------------")

json_req = { 
    "method": "slim.request",
    "params":
    [
        player,       
        [
            "musicartistinfo",
            "biography",
            "artist:" + cur_artist
        ]
    ]
}

json_bio = getDataFromLMS(json_req)

bio_avail = "1"

if "error" in json_bio["result"]:
    bio_avail = "0"

# Build HTML page to display in HabPanel
if bio_avail == "0":
    #bio = "<html><p style=\"color:white;\"><font face=\"Helvetica\">No biography available</font></p></html>"
    #bio = "<html><p style=\"color:white;\"><font face=\"Helvetica\">" + str(myTry) + " --- No biography available</font></p></html>"
    bio = "<html><p style=\"color:white;\"><font face=\"Helvetica\">No Biography</font></p></html>"
else:
    bio = json_bio["result"]["biography"]
    bio = bio.replace("\n", "<br/>")
    #bio = "<html><p style=\"color:white;\"><font face=\"Helvetica\">" + bio + "</font></p></html>"
    bio = "<html><p style=\"color:white;\"><font face=\"Helvetica\">" + "<br/>" + bio + "</font></p></html>"


f= open(file_loc + "biography.html","w+")
f.write(bio)
f.close() 

# Build Json doc for OpenHab
pic_count = 0

output_json = {"songinfo": {"artist":"","title":"","lyrics": "0","biography": "0","photos": [], "pic_count": 0}}
output_json["songinfo"]["artist"] = cur_artist
output_json["songinfo"]["title"] = cur_title
output_json["songinfo"]["lyrics"] = lyrics_avail
output_json["songinfo"]["biography"] = bio_avail

# loop over list of artist photos
for picture in json_photos["result"]["item_loop"]:
    output_json["songinfo"]["photos"].append(picture["url"])
    pic_count = pic_count + 1
output_json["songinfo"]["pic_count"] = pic_count

print(json.dumps(output_json))


