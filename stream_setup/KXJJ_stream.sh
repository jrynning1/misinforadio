#! /bin/bash

station="KXJJ"

URL="https://stream.radio.co/s6cf405076/listen"

DIR="/home/envoy82/code/misinforadio/data/video_storage/"

timestamp=$(date +%y%m%d%H%M%S)

dest=${DIR}${station}_${timestamp}.mp3

cvlc $URL --sout="#transcode{vcodec=none,acodec=mp3,ab=128,channels=2,samplerate=44100,scodec=none}:file{mux=mp3,dst=$dest,no-overwrite}" --no-sout-all --sout-keep --run-time=3600 --play-and-exit