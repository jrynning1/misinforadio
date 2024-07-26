# misinforadio

Welcome to the misinforadio project. This tool is being developed to assist researchers and reporters to analyze misinformation on radio and television broadcasts.

There are currently five steps in the automated analysis pipeline, each with a dedicated python script (or multiple scripts to support additional options). The default process can be completed by running the bash script "0_run_all.sh". Below is a simple description of waht this process will do.

Step 1: Generating Ebmeddings of Fact Checked Statements

Step 2: Converting Input Files to Shortened AAC Files

Step 3: Transcription by OpenAI Whisper model

Step 4: Generating Embeddings with OpenAI Embeddings API

Step 5: Comparing Radio Segments to Fact Checked Statements and Translating Significant Matches with LibreTranslate


# Basic Instructions

Make a copy of this GitHub repository by running the following command on the command line:

```
$ git clone https://github.com/jrynning1/misinforadio.git
```

Ensure all required dependencies are installed. I suggest navigating into the directory and run the following commands to initialize a python virtual environment and simplify this process:

```
$ cd misinforadio
$ pipenv install
$ pipenv shell
```

Save a dataset of fact checked statements in the misinforadio/data/factchecked_statements folder. Two datasets are currently supported.

- Fact-Check Insights by the Duke Reporters' Lab, available by request at https://www.factcheckinsights.org/ (JSON version)

- PolitiFact fact checks, compiled by Rishabh Misra and available at https://www.kaggle.com/datasets/rmisra/politifact-fact-check-dataset

Navigate to the data/video_import folder and save a copy of any audio or vido files you want to analyze.

Run python script "0_run_all.sh"

```
$ cd scripts
$ source 0_run_all.sh
```

The final output file will be generated in data/output_csv.

Additional options are available by running individual Python scripts to suit your needs or available resources. Further documentation to come.
