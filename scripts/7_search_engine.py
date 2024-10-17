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

import streamlit
import subprocess
import pandas as pd
import os
import numpy as np
from pathlib import Path
from openai import OpenAI
from libretranslatepy import LibreTranslateAPI
from dotenv import load_dotenv

pd.options.mode.chained_assignment = None  # default='warn'

number_return_values = 1

print("Importing false statements with embeddings...")

embedded_false_statements_path = Path().cwd().parent.joinpath('data/factchecked_statements/embedded_false_statements.csv')

false_text_df = pd.read_csv(embedded_false_statements_path)

statement_embedding_list = []
for embedding in false_text_df['statement_embedding']:
    try:
        statement_embedding_array = np.array(eval(embedding))
        statement_embedding_list.append(statement_embedding_array)
    except:
        statement_embedding_list.append(0)

false_text_df['statement_embedding'] = statement_embedding_list

col = false_text_df.pop("statement")
false_text_df.insert(0,col.name, col)

# add your OpenAI API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

while True:

    print('Input questionable statement and press enter.')

    def get_embedding(text, model="text-embedding-3-small"):
        text = text.replace("\n", " ")
        return client.embeddings.create(input = [text], model=model).data[0].embedding

    transcription = input()

    transcription_embedding_list = [get_embedding(transcription)]

    for embedding in transcription_embedding_list:
        try:
            transcription_embedding_array = np.array(embedding)
        except:
            transcription_embedding_array = 0

    def cosine_similarity(vec1, vec2):
        # Normalize each vector to unit length
        vec1_norm = vec1 / np.linalg.norm(vec1)
        vec2_norm = vec2 / np.linalg.norm(vec2)
    
        # Calculate dot product between normalized vectors
        similarity = np.dot(vec1_norm, vec2_norm)
        return similarity

    # if the transcript segment is shorter than 150 characters, this will use the context segment instead
    def search_false_statements(false_text_df=false_text_df):
        transcription_similarity_list = []
        errors = 0
    # is receiving embeddings above
        for embedding in statement_embedding_list:
            try:
                transcription_similarity = cosine_similarity(embedding, transcription_embedding_array)
                transcription_similarity_list.append(transcription_similarity)
            except:
                errors += 1
                transcription_similarity_list.append("failed to generate similarity")
                
        # print(f"Searched false statements with {errors} errors.")
        false_text_df['similarities'] = transcription_similarity_list
        data = (
            false_text_df.sort_values("similarities", ascending=False)
        )
        results = (transcription, data)
        return results

    results = search_false_statements()

    top_matches_df = results[1]
    
    top_matches_df = top_matches_df[['statement', 'rating', 'url', 'time_since_publication', 'datePublished', 'similarities']]
    

    """
    def hyperlinks_list(x):
        link_list = []
        for url in x:
            link = f"=HYPERLINK(\"{url}\")"
            link_list.append(link)
        return link_list
            
    top_matches_df['url'] = hyperlinks_list(top_matches_df['url'])

    """

    transcription_entry = results[0].replace(' ', '_').replace('.', '').replace('?','').replace('!','')
    



    """
    top_matches_df['similarity_value'] = top_matches_df['similarities'].apply(lambda x: x.split()[1]).astype(float)
    top_matches_df['factcheck_index'] = top_matches_df['similarities'].apply(lambda x: x.split()[0])
    """

    over_40 = top_matches_df.loc[top_matches_df['similarities'] >= .4]

    over_40 = over_40.sort_values('similarities', ascending=False)

    over_50_csv_filepath = Path().cwd().parent.joinpath(f"data/output_csv/{transcription_entry}.csv")

    over_40.to_csv(f"{over_50_csv_filepath}")

    # open new csv file with bash
    subprocess.run(["open", over_50_csv_filepath])
