# code courtesy of Eric Sagara

from datetime import datetime, timedelta

import requests

def repeat_download_stream(stream_url, filepath, minutes=1):
    
    timestr = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
    
    filepath = f'./{timestr}_recording.mp3'
    
    end = datetime.now() + timedelta(minutes=minutes)

    response = requests.get(stream_url, stream=True)

    output = open(filepath, 'wb')


    for block in response.iter_content(1024):
       
        output.write(block)
        
        if datetime.now() >= end:
            break

    output.close()

def download_stream0(stream_url, filepath, minutes=1):
    
    end = datetime.now() + timedelta(minutes=minutes)

    response = requests.get(stream_url, stream=True)

    output = open(filepath, 'wb')


    for block in response.iter_content(1024):
       
        output.write(block)
        
        if datetime.now() >= end:
            break

    output.close()


if __name__ == '__main__':
    
    timestr = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
    stream_url = 'https://kzsu-streams.stanford.edu/kzsu-1-128.mp3'
    filepath = f'./{timestr}_recording.mp3'

    download_stream0(stream_url, filepath)
    while True:
        repeat_download_stream(stream_url, filepath, minutes=1)
