#! /bin/bash

station="<Insert station callsign>"


URL="<Insert stream URL>"

DIR="<Insert save location for recording>"

while :
do
	timestamp=$(date +%y%m%d%H%M%S);
	dest=${DIR}${station}_${timestamp}.mp3
	vlc $URL --sout="#transcode{vcodec=none,acodec=mp3,ab=128,channels=2,samplerate=44100,scodec=none}:file{mux=mp3,dst=$dest,no-overwrite}" --no-sout-all --sout-keep --run-time=3600 --play-and-exit;
done