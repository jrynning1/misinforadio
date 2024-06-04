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

def transcribe(audio_import):
    model = whisper.load_model("base")
    result = model.transcribe(f"{audio_import}")
    return result["text"]

split_audio_filenames = sorted((f for f in os.listdir(split_audio_path) if not f.startswith(".")), key=str.lower)

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