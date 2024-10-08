# misinforadio

Welcome to the misinforadio project. This tool is being developed to assist researchers and reporters to analyze misinformation on radio and television broadcasts.

Please see the [introduction slides](https://new.express.adobe.com/publishedV2/urn:aaid:sc:US:1d203e58-92f2-4038-ad15-5d6f5fd62150?promoid=Y69SGM5H&mv=other) or basic instructions below.

There are currently five steps in the automated analysis pipeline, each with a dedicated python script (or multiple scripts to support additional options). The default process can be completed by adding your OpenAI API key, running the python script "0a_fact_check_insights_embeddings_filtered.py", and then the bash script "1_run_all.sh". Below is a simple description of what this process will do.

Step 1: Generating embeddings of fact-checked statements

Step 2: Converting input files to shortened AAC files

Step 3: Transcription by OpenAI Whisper model

Step 4: Generating embeddings with OpenAI Text Embeddings API

Step 5: Comparing radio segments to fact-checked statements and translating significant matches with LibreTranslate


# Basic Instructions

Make a copy of this GitHub repository by running the following command on the command line:

```
$ git clone https://github.com/jrynning1/misinforadio.git
```

Ensure all required dependencies are installed. Navigate into the directory and run the following commands to initialize a python virtual environment and simplify this process:

```
$ cd misinforadio
$ pipenv install
$ pipenv shell
```
Make an .env file containing your OpenAI API key. This program requires an OpenAI account and a small amount of credit for using the text embedding model.

```
$ echo "OPENAI_API_KEY=<ENTER YOUR API KEY HERE>" > .env
```

Save a dataset of fact checked statements in the misinforadio/data/factchecked_statements folder. Two datasets are currently supported.

- Fact-Check Insights by the Duke Reporters' Lab, available by request at https://www.factcheckinsights.org/ (JSON version)

- PolitiFact fact checks, compiled by Rishabh Misra and available at https://www.kaggle.com/datasets/rmisra/politifact-fact-check-dataset

Navigate to the data/video_import folder and save a copy of any audio or vido files you want to analyze. Misinforadio currently supports MP4, MKV, MOV, MP3, AAV, or WAV files of any length.

Run python script "0a_fact_check_insights_embeddings_filtered.py"

Run bash script "1_run_all.sh"

```
$ cd scripts
$ python 0a_fact_check_insights_embeddings_filtered.py
$ source 1_run_all.sh
```

The final output file will be generated in data/output_csv.

Additional options are available by running individual Python scripts to suit your needs or available resources.
