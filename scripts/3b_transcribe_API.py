import pandas as pd
import os
from openai import OpenAI
from pathlib import Path

client = OpenAI(api_key='sk-proj-HSrHGyOHtEDtr9loLzRjT3BlbkFJTUFaqCLYDEs3B7qpBz7z')

all_transcripts = []

split_audio_path = Path().cwd().parent.joinpath('data/split_audio/')

print("Cleaning filenames")

def clean_filenames():
    filenames = sorted((f for f in os.listdir(split_audio_path) if not f.startswith(".")), key=str.lower)
    for filename in filenames:
        os.rename(os.path.join(split_audio_path, filename), os.path.join(split_audio_path, filename.replace(' ', '_')))

clean_filenames()

def transcribe(audio_import):
    transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_import,
        response_format="verbose_json",
        timestamp_granularities=["segment"]
  )
    return transcription

split_audio_filenames = os.listdir(split_audio_path)

def batch_transcribe():
    completed = 0
    for file in sorted(split_audio_filenames):
        file_path = Path().cwd().parent.joinpath(f'data/split_audio/{file}') 

        #file_path = f"{split_audio_path}/{file}"

        transcription = transcribe(file_path)

        transcription_str = str(transcription.text)

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