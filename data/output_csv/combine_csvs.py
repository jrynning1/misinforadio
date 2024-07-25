# Run this script to combine all output CSV files in this folder.

import pandas as pd
from pathlib import Path
import os
import glob

output_csv_path = Path().cwd()

output_csv_filenames = glob.glob(os.path.join(output_csv_path, '*.csv'))

df = pd.read_csv(output_csv_filenames[0])

for filename in output_csv_filenames[1:]:
    try:
        temp_df = pd.read_csv(filename)
        df = pd.concat([df, temp_df], ignore_index=True)
    except:
        print(f"Error reading CSV {filename}.")

df = df[df['input_statement'].str.len() >= 25]

df = df.sort_values('similarity_value', ascending=False)

df.to_csv('combined_potential_misinformation.csv')