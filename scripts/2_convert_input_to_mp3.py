# This script converts MP4, MKV, MOV, MP3, or WAV files to batches of 10-minute MP3 files

import subprocess
import os
from pathlib import Path

path = Path().cwd().parent.joinpath('data/video_import')
filenames = sorted((f for f in os.listdir(path) if not f.startswith(".")), key=str.lower)

def video_rename():
    for filename in filenames:
        os.rename(os.path.join(path, filename), os.path
                  .join(path, filename
                        .replace(' ', '_')
                        .replace('(', '')
                        .replace(')', '')))
        
video_rename()

def convert_video_to_audio(video_file_path, audio_file_path):
    command = f"ffmpeg -i {video_file_path} -f segment -segment_time 600 {audio_file_path}_%03d.mp3"
    subprocess.call(command, shell=True)

def batch_convert():
    print("Starting batch conversion (mp4 to mp3)")
    for filename in filenames:
        #filename_without_suffix = filename.replace('.mp4', '')
        new_filename = filename.replace('.mp4', '').replace('.mkv', '').replace('.mov', '').replace('.mp3', '').replace('.wav', '').replace('.aac','')
        path_to_split_audio = Path().cwd().parent.joinpath('data/split_audio')
        convert_video_to_audio(f"{path}/{filename}", f"{path_to_split_audio}/{new_filename}")
        print(f"Finished {filename}")

batch_convert()