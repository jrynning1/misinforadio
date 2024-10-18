#! /bin/bash

station="KQSE"


URL="https://ais-sa1.streamon.fm/7118_48k.aac/playlist.m3u8?listenerId=esTrackblock0285212&aw_0_1st.playerid=esPlayer&aw_0_1st.skey=1729220077&us_privacy=1YN-"

DIR="/home/envoy82/code/misinforadio/data/video_storage/"

timestamp=$(date +%y%m%d%H%M%S);

dest=${DIR}${station}_${timestamp}.mp3

vlc $URL --sout="#transcode{vcodec=none,acodec=mp3,ab=128,channels=2,samplerate=44100,scodec=none}:file{mux=mp3,dst=$dest,no-overwrite}" --no-sout-all --sout-keep --run-time=3600 --play-and-exit; sleep 5;