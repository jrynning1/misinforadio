'''
This code was written by Jordan Rynning as part of the Misinforadio Project,
which aims to identify misinformation on radio and television recordings.
Copyright (C) 2024  Jordan Rynning

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/.
'''

# This script uses a local installation of Whisper to transcribe audio segments

import pandas as pd
import os
import whisper
from pathlib import Path

all_transcripts = []

split_audio_path = Path().cwd().parent.joinpath('data/split_audio/')

print("Cleaning filenames")

def clean_filenames():
    filenames = os.listdir(split_audio_path)
    for filename in filenames:
        os.rename(os.path.join(split_audio_path, filename), os.path.join(split_audio_path, filename.replace(' ', '_')))

clean_filenames()

# defining function for Whisper requests; for additional options see Whisper documentation
def transcribe(audio_import):
    model = whisper.load_model("base")
    result = model.transcribe(f"{audio_import}")
    return result["text"]

# finding all files in data/split_audio/ folder
split_audio_filenames = sorted((f for f in os.listdir(split_audio_path) if not f.startswith(".")), key=str.lower)

# formatting data returned from Whisper and appending to all_transcripts DataFrame
def batch_transcribe():
    completed = 0
    for file in sorted(split_audio_filenames):
        file_path = Path().cwd().parent.joinpath(f'data/split_audio/{file}') 

        transcription = transcribe(file_path)

        transcription_str = str(transcription)

        transcription_sent = transcription_str.split('. ')

        station_callsign = file.split("_",1)[0]

        tt_dict = {
            "callsign": station_callsign, 
            "file_name": file, 
            "transcription": transcription_sent, 
            }

        all_transcripts.append(tt_dict)
        completed += 1
        print(f"Finished transcribing {file}, completed {completed} of {len(split_audio_filenames)} files [{int((completed / len(split_audio_filenames)*100))}%]")

print("Beginning transcription... this may take some time")

batch_transcribe()

transcript_df = pd.DataFrame(all_transcripts)

print('Generating transcript json')

json_name = 'transcript.json'

output_json_path = Path().cwd().parent.joinpath(f'data/output_json/{json_name}') 

transcript_df.to_json(output_json_path)
