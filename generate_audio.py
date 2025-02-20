import os
import csv
import progressbar
from openai import OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

FILENAMES = (
    'neutral.csv',
    'sad.csv'
)

TTS_MODEL = "tts-1-hd"
TTS_VOICE = "fable"
TTS_DIRECTORY = "audio"

LANG_DICT = {
    'fr': 'french',
    'en': 'english',
    'de': 'german'
}
TARGET_LANG = ('fr', 'de')


def openai_tts(text: str, filename: str) -> str:
    with client.audio.speech.with_streaming_response.create(
        model=TTS_MODEL,
        voice=TTS_VOICE,
        input=text
    ) as r:
        r.stream_to_file(filename)


def parse_row(row) -> None:
    if not os.path.exists(TTS_DIRECTORY):
        os.mkdir(TTS_DIRECTORY)

    for lang in TARGET_LANG:
        text = row[lang]
        filename = TTS_DIRECTORY + '/' + row[f'filename_{lang}']
        openai_tts(text, filename)


def parse_file(filename) -> None:
    rows = []
    with open(filename, mode='r') as file:
        reader = csv.DictReader(file)
        rows = [row for row in reader]

    for row in progressbar.progressbar(rows, enable_colors=False):
        parse_row(row)


def main():
    import sys
    filenames = FILENAMES if len(sys.argv) == 1 else sys.argv[1:]
    for fn in filenames:
        print(f"generating audio for file {fn}...")
        parse_file(fn)


if __name__ == "__main__":
    main()
