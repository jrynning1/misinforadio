from libretranslatepy import LibreTranslateAPI
import pandas as pd

print("Loading potential misinformation file...")

over_50_csv_filepath = Path().cwd().parent.joinpath('data/output_csv/potential_misinformation.csv')

over_50 = pd.read_csv(over_50_csv_filepath)

print("Adding translation...")

lt = LibreTranslateAPI("http://localhost:5000")

def libretranslate_spanish(input_text):
    return lt.translate(f"{input_text}", "es", "en")

def libretranslate_french(input_text):
    return lt.translate(f"{input_text}", "fr", "en")

try:
    over_50['translation'] = over_50['input_statement'].apply(lambda x: libretranslate_french(x))
    over_50['translation'] = over_50['translation'].apply(lambda x: libretranslate_spanish(x))

    over_50 = over_50.sort_values('similarity_value', ascending=False)

    over_50 = over_50[['filename', 'input_statement', 'translation', 'checked_false_statement', 'similarity_value', 'factcheck_index']]

    translation_filepath = Path().cwd().parent.joinpath('data/output_csv/potential_misinformation_with_translations.csv')
except:
    print("Failed to add transcription. Check that LibreTranslate is running.")

print("Generating csv file...")

over_50.to_csv(f"{translation_filepath}")