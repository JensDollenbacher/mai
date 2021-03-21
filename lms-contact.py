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

# ---------- main ---------------

logging.basicConfig(level=logging.INFO)


host = '192.168.2.10'
port = 9090
web_port = 9000
file_loc = ''
lms_url = "http://" + host + ":" + str(web_port) + "/jsonrpc.js"
player = "00:04:20:23:20:b2"

my_env = platform.system()

if my_env == 'Darwin':
    file_loc = './'
else:
    file_loc = '/etc/openhab/html/'

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

json_resp = requests.post(lms_url, data=json.dumps(json_req), headers={"Content-Type":"application/json"})
if json_resp.status_code != 200:
    print("Fuck")

json_artist = json.loads(json_resp.content)
cur_artist = json_artist["result"]["_artist"]

logging.debug("Current artist: [" + cur_artist + "]")

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

json_resp = requests.post(lms_url, data=json.dumps(json_req), headers={"Content-Type":"application/json"})
if json_resp.status_code != 200:
    print("Fuck")

json_artist = json.loads(json_resp.content)
cur_title = json_artist["result"]["_title"]


logging.debug("Current title: [" + cur_title + "]")

logging.debug("------------- lyrics ------------------")

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

json_resp = requests.post(lms_url, data=json.dumps(json_req), headers={"Content-Type":"application/json"})

if json_resp.status_code != 200:
    print("Fuck")
    # This means something went wrong.
    #raise ApiError('GET /tasks/ {}'.format(resp.status_code))

json_lyrics = json.loads(json_resp.content)

lyrics_avail = "1"

if "error" in json_lyrics["result"]:
    lyrics_avail = "0"


if lyrics_avail == "0":
    lyrics = "<html><p style=\"color:white;\"><font face=\"Helvetica\">No lyrics available</font></p></html>"
else:
    lyrics = json_lyrics["result"]["lyrics"]
    lyrics = lyrics.replace("\n", "<br/>")
    lyrics = "<html><p style=\"color:white;\"><font face=\"Helvetica\">" + lyrics + "</font></p></html>"

f= open(file_loc + "lyrics.html","w+")
f.write(lyrics)
f.close() 

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

json_resp = requests.post(lms_url, data=json.dumps(json_req), headers={"Content-Type":"application/json"})

if json_resp.status_code != 200:
    print("Fuck")
    # This means something went wrong.
    #raise ApiError('GET /tasks/ {}'.format(resp.status_code))

json_photos = json.loads(json_resp.content)


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

json_resp = requests.post(lms_url, data=json.dumps(json_req), headers={"Content-Type":"application/json"})

if json_resp.status_code != 200:
    print("Fuck")
    # This means something went wrong.
    #raise ApiError('GET /tasks/ {}'.format(resp.status_code))

json_bio = json.loads(json_resp.content)

bio_avail = "1"

if "error" in json_bio["result"]:
    bio_avail = "0"


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

# json build
pic_count = 0

output_json = {"songinfo": {"lyrics": "0","photos": [], "pic_count": 0}}
output_json["songinfo"]["lyrics"] = lyrics_avail

for picture in json_photos["result"]["item_loop"]:
    output_json["songinfo"]["photos"].append(picture["url"])
    pic_count = pic_count + 1
output_json["songinfo"]["pic_count"] = pic_count

print(json.dumps(output_json))


