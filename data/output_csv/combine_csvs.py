# Run this script to combine all output CSV files in this folder.

import pandas as pd
from pathlib import Path
import os

output_csv_filenames = Path().cwd()

output_csv_filenames = os.listdir(output_csv_filenames)

df = pd.DataFrame()

for file in output_csv_filenames:
    temp_df = pd.read_csv(file)
    pd.concat([df, temp_df])

df = df.sorted('similarity_value', ascending=False)

df.to_csv('combined_potential_misinformation.csv')