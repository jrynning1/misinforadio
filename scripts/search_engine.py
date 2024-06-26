import streamlit
import subprocess
import pandas as pd
import os
import numpy as np
from pathlib import Path
from openai import OpenAI
from libretranslatepy import LibreTranslateAPI

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
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "sk-proj-HSrHGyOHtEDtr9loLzRjT3BlbkFJTUFaqCLYDEs3B7qpBz7z"))

while True:

    print('Input questionable statement inside quotation marks ("").')

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

    print(f'transcription embedding array: {transcription_embedding_array}')

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
        results = (
            false_text_df.sort_values("similarities", ascending=False)
        )
        return results

    top_matches_df = search_false_statements()

    """
    top_matches_df['similarity_value'] = top_matches_df['similarities'].apply(lambda x: x.split()[1]).astype(float)
    top_matches_df['factcheck_index'] = top_matches_df['similarities'].apply(lambda x: x.split()[0])
    """
    print(top_matches_df)

    over_50 = top_matches_df.loc[top_matches_df['similarities'] >= .5]

    over_50 = over_50.sort_values('similarities', ascending=False)

    over_50_csv_filepath = Path().cwd().parent.joinpath('data/output_csv/search_results.csv')

    print("Generating csv file...")

    over_50.to_csv(f"{over_50_csv_filepath}")