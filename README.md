# Blossom UI

## Requirements

### Environnment

- Python 3.10
- pip

### Auto translation and text-to-speech

Translation and TTS both use OpenAI API to work. A valid API key with enough credits is required to use those 
scripts. The GUI questionnaire app or the robot voice app **do not** need it since they do not use OpenAI API.

Add the API key into a `.env` file at the root of the repository (alongside the scripts) 
under the `OPENAI_API_KEY` variable:

```.env
OPENAI_API_KEY=insert your key here
```

> [!CAUTION]
> Running the translation script will overwrite the content of the CSV files and the 
> audio script will overwrite the audio files. Keep a backup of your data before
> running this script if you manually added or edited entries!


## Installation

Clone the repository in the directory of your choice and navigate to it
```sh
git clone git@github.com:ylked/blossom.git`
cd blossom
```

Create a new python virtual env and activate it
```sh
python3 -m venv venv
source venv/bin/activate
```

Install dependencies
```sh
pip3 install -r requirements.txt
```

You are now ready to run the app.

## Running

### Activating the virtual env

Every time you exit the terminal, you must reactivate the virtual environment before
launching the python scripts:

```sh
source venv/bin/activate
```

### Questionnaire

To launch the GUI app, run:

```sh
python3 gui.py
```

> [!TIP]
> Do not forget to activate the virtual environment before running the app (see above) 😉

The answers of the participant will be saved into the `answers/answersX.txt`, where `X` is the questionnaire number (1 or 2).

Once you reach the screen showing "You have finished", you can safely close the window.
Please note that the results are only saved once at the end, just before you see this screen. If
the window is closed during the questions answering, the results of the current participant are lost. 


### Robot voice

To launch the robot voice app in the *neutral* scenario, run:

```sh
python3 robot.py neutral
```

To run it using the *sad* scenario, run:

```sh
python3 robot.py sad
```

The robot will now speak. 
To pass to the next dialogue phase once it has finished, simply click the 'Enter' key. 


