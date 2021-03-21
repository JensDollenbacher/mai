#! /usr/bin/env python3
# -*- encoding: latin1 -*-pwd


# Socket client example in python

import socket
import sys 
import os 
import time
import logging
import json

import requests

# ---------- receive response from LMS ---------------
def recvall(sock):
    BUFF_SIZE = 4096 # 4 KiB
    data = b''
    while True:
        part = sock.recv(BUFF_SIZE)
        data += part
        if len(part) < BUFF_SIZE:
            # either 0 or end of data
            break

    response = str(data)
    response = response[0:len(response) - 5]
    #response = response.rstrip("\n")
    response = requests.utils.unquote(response)
    logging.debug('RESPONSE :' + response)
    return response

# ---------- send request to LMS ---------------
def sendout(sock, message):
    message = message + "\r\n"
    logging.debug('REQUEST: ' + message)
    try:
        s.sendall(bytes(message, encoding='utf8'))
    except socket.error:
        print ("Send failed")
        sys.exit()

#request = sys.argv[1]


# ---------- main ---------------

logging.basicConfig(level=logging.INFO)


host = '192.168.2.10'
port = 9090
file_loc = ''

# output_json["songinfo"]["lyrics"] = "Hallo"

my_env = 'Mac'
#my_env = 'Raspi'

if my_env == 'Mac':
    file_loc = './'
else:
    file_loc = '/etc/openhab/html/'

# create socket
logging.debug('# Creating socket')
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
    print('Failed to create socket')
    sys.exit()

#print('# Getting remote IP address') 
#try:
#    remote_ip = socket.gethostbyname( host )
#except socket.gaierror:
#    print('Hostname could not be resolved. Exiting')
#    sys.exit()

# Connect to remote server
logging.debug('# Connecting to server, ' + host)
s.connect((host , port))



logging.debug("------------- current artist ------------------")

request = "00:04:20:23:20:b2 artist ?"
sendout(s, request)
reply = recvall(s)
start_pos = reply.find("artist ") + 7
cur_artist = reply[start_pos:len(reply)]
#end_pos = reply.find("\r") - 1
cur_artist = requests.utils.quote(cur_artist)

logging.debug("Current artist: [" + cur_artist + "]")

logging.debug("------------- current title ------------------")

request = "00:04:20:23:20:b2 title ?"
sendout(s, request)
reply = recvall(s)
start_pos = reply.find("title ") + 6
cur_title = reply[start_pos:len(reply)]
#end_pos = reply.find("\r") - 1
cur_title = requests.utils.quote(cur_title)

logging.debug("Current title: [" + cur_title + "]")

logging.debug("------------- playlistinfo ------------------")

request = "00:04:20:23:20:b2 status playlist"
#request = "00:04:20:23:20:b2 status"

sendout(s, request)
time.sleep(1)
# Receive data

reply = ""

reply = recvall(s)

logging.debug("------------- Get current Song ------------------")

start_pos = reply.find("playlist_cur_index:") + 19
end_pos = reply.find(" ", start_pos)
index = reply[start_pos:end_pos]

mysong_start_pos = reply.find("playlist index:" + index)
myid_start_pos = reply.find("id:", mysong_start_pos) + 3
myid_end_pos = reply.find(" ", myid_start_pos)
mysong_id = reply[myid_start_pos:myid_end_pos]

logging.debug("------------- Song ID ------------------")
logging.debug("Song ID = " + mysong_id )

if (mysong_id.find("-") > -1) or (mysong_id.find(":") > -1):
    spotty = True
else:
    spotty = False

logging.debug("------------- lyrics ------------------")


if spotty == False:
    request = "musicartistinfo lyrics track_id:"+mysong_id
else:
    request = "musicartistinfo lyrics artist:" + cur_artist + " title:"+ cur_title

sendout(s, request)

lyrics = recvall(s)

lyrics_avail = ""

if lyrics.find("error:") != -1:
    lyrics = "<html><p style=\"color:white;\"><font face=\"Helvetica\">No lyrics available</font></p></html>"
    lyricsavail = "0"
else:
    lyrics_start_pos= lyrics.find("lyrics:") + 7
    lyrics_end_pos = lyrics.find("title:", lyrics_start_pos) - 1
    lyrics = lyrics[lyrics_start_pos:lyrics_end_pos]
    lyrics = lyrics.replace("\n", "<br/>")
    lyrics = "<html><p style=\"color:white;\"><font face=\"Helvetica\">" + lyrics + "</font></p></html>"
    logging.debug("LYRICS HTML:" + lyrics)
    lyricsavail = "1"

f= open(file_loc + "lyrics.html","w+")
f.write(lyrics)
f.close() 

#print(lyrics)


logging.debug("------------- Artist ID ------------------")

if spotty == False:
    request = "songinfo 0 100 track_id:"+mysong_id
    sendout(s, request)
    reply = recvall(s)

    myartist_start_pos = reply.find("artist_id:") + 10
    myartist_end_pos = reply.find(" ", myartist_start_pos)
    myartist_id = reply[myartist_start_pos:myartist_end_pos]
else:
    logging.debug("No Artist ID available")

#print("Artist ID = " + myartist_id)

logging.debug("------------- Artist Photos ------------------")

if spotty == False:
    request = "musicartistinfo artistphotos artist_id:"+myartist_id
else:
    request = "musicartistinfo artistphotos artist:"+ cur_artist

myTry = 0

while 1:
    myTry = myTry + 1
    #print("Try = " + str(myTry))
    sendout(s, request)
    time.sleep(1)
    #reply = s.recv(40960)
    reply = recvall(s)

    reply_len = len(reply)
    if (reply.find("count:") > 0) or (myTry == 5) or (reply.find("error:") > -1):
        break

cur_pos = 0
myUrl_start_pos = 1
myUrlList = []

while 1:
    myUrl_start_pos = reply.find("url:", cur_pos)

    if myUrl_start_pos == -1:
        break

    myUrl_start_pos = myUrl_start_pos + 4
    myUrl_end_pos = reply.find(" ", myUrl_start_pos)
    myUrl = reply[myUrl_start_pos:myUrl_end_pos]
    cur_pos = myUrl_end_pos + 1
    #print (myUrl)
    #print (cur_pos)
    #print (myUrl_start_pos)
 #   c = sys.stdin.read(1)
    myUrlList.append(myUrl)


logging.debug("------------- Artist Bio ------------------")

if spotty == False:
    request = "musicartistinfo biography artist_id:"+myartist_id
else:
    request = "musicartistinfo biography artist:"+ cur_artist

myTry = 0

while 1:
    myTry = myTry + 1
    sendout(s, request)

    time.sleep(1)
    #reply = s.recv(40960)
    bio = recvall(s)

    if ((bio.find("musicartistinfo biography") > -1) and (bio.find("artist:")) > 0) or (myTry == 5) or (bio.find("error:") > -1):
        break
    else:
        s.close()
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error:
            print('Failed to create socket')
            sys.exit()
        s.connect((host , port))


if bio.find("error:") != -1:
    #bio = "<html><p style=\"color:white;\"><font face=\"Helvetica\">No biography available</font></p></html>"
    #bio = "<html><p style=\"color:white;\"><font face=\"Helvetica\">" + str(myTry) + " --- No biography available</font></p></html>"
    bio = "<html><p style=\"color:white;\"><font face=\"Helvetica\">" + bio + "</font></p></html>"
    #lyricsavail = "0"
else:
    bio_start_pos = bio.find("biography:") + 10
    #print(bio_start_pos)
    bio_end_pos = bio.find("artist_id:", bio_start_pos) - 1
    bio = bio[bio_start_pos:bio_end_pos]
    bio = bio.replace("\n", "<br/>")
    #bio = "<html><p style=\"color:white;\"><font face=\"Helvetica\">" + bio + "</font></p></html>"
    bio = "<html><p style=\"color:white;\"><font face=\"Helvetica\">" + "<br/>" + bio + "</font></p></html>"


f= open(file_loc + "biography.html","w+")
f.write(bio)
f.close() 

s.close()

# json build
pic_count = 0
#jsondoc = "{\"songinfo\" : { \"lyrics\":\"" + lyricsavail + "\","
#jsondoc = jsondoc + "\"photos\":["
#logging.debug("jsondoc = " + jsondoc )

#for picture in myUrlList:
#    jsondoc = jsondoc + "{\"url\":\"" + picture + "\"},"
#    pic_count = pic_count + 1

#if pic_count > 0:
#    jsondoc = jsondoc[0:len(jsondoc)-1]

#jsondoc = jsondoc + "], \"pic_count\" : " + str(pic_count) + "} }"

output_json = {"songinfo": {"lyrics": "0","photos": [], "pic_count": 0}}
output_json["songinfo"]["lyrics"] = lyricsavail
for picture in myUrlList:
    output_json["songinfo"]["photos"].append({"url":picture})
output_json["songinfo"]["pic_count"] = pic_count

#print(jsondoc)
print(json.dumps(output_json))


