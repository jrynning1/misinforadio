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

from libretranslatepy import LibreTranslateAPI
import pandas as pd
from pathlib import Path

print("Enter LibreTranslate language code -- \"es\" for spanish, \"fr\" for french, etc.")
input_language = input()

print("Loading potential misinformation file...")

over_50_csv_filepath = Path().cwd().parent.joinpath('data/output_csv/potential_misinformation_with_context.csv')

over_50 = pd.read_csv(over_50_csv_filepath)

print("Adding translation...")

lt = LibreTranslateAPI("http://localhost:5000")

def libretranslate_spanish(input_text):
    return lt.translate(f"{input_text}", "es", "en")

def libretranslate_french(input_text):
    return lt.translate(f"{input_text}", "fr", "en")

def libretranslate_input(input_text, input_language="es"):
    return lt.translate(f"{input_text}", input_language, "en")

errors = 0
translation_list = []
counter = 0

for statement in over_50['input_statement']:
    try:
        translate_selected = libretranslate_input(statement, input_language)
        #french = libretranslate_french(statement)
        #spanish = libretranslate_spanish(french)
        translation_list.append(translate_selected)
        counter += 1
        print_text = f"Finished translating {counter} of {len(over_50['input_statement'])} statements -- {int((counter)/len(over_50['input_statement'])*100)}% complete         "
        print("\r", print_text, end="")
    except:
        translation_list.append("translation failed")
        errors += 1
        counter += 1
        print(f"Error translating statement {counter}")
print(f"Finished translating with {errors} errors.")
over_50['translation'] = translation_list

if errors > (len(over_50['input_statement'])/2):
    print("Over 50 percent of translations failed. Double check your input language.")
else:
    print("Generating csv file...")

    translation_filepath = Path().cwd().parent.joinpath('data/output_csv/potential_misinformation_with_translations.csv')
    
    over_50.to_csv(f"{translation_filepath}")
