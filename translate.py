import csv
import os
from openai import OpenAI
import progressbar

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# the file containing the translation prompt
PROMPT_FILENAME = 'translate_prompt.txt'

# list of all the files to be translated
FILENAMES = (
    'csv/neutral.csv',
    'csv/sad.csv',
    'csv/questionnaire1.csv',
    'csv/questionnaire2.csv',
    'csv/responses1.csv',
    'csv/responses2.csv',
)

# corresponding list from tag and language full name
LANG_DICT = {
    'fr': 'french',
    'en': 'english',
    'de': 'german'
}

# the languages the texts will be translated to
TARGET_LANG = ('fr', 'de')

# the language of the original text
SOURCE_LANG = 'en'


def openai_translate(prompt: str) -> str:
    """
    Query OpenAI API to translate the text.

    Args:
        prompt (str): the full prompt, including instruction, target language
        and text to translate.

    Returns:
        str: the translated text.
    """

    with open(PROMPT_FILENAME, 'r') as f:
        p = f.read()

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "developer",
                "content": p
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    translation = completion.choices[0].message.content
    return translation


def translate(lang: str, text: str) -> str:
    """
    Translates the provided text in the specified language.

    Args:
        lang (str): the target language, as a 2-letters code
            (e.g. 'en' for english)
        text (str): the text to be translated

    Returns:
        str: the translated text
    """

    prompt = f"please translate this text in {LANG_DICT[lang]} : " + text
    return openai_translate(prompt)


def parse_row(row: dict[str, str]) -> dict[str, str]:
    """
    Parses a single csv file rows. It translates the original text
    into all the target languages.

    Args:
        row (dict[str, str]): a row as a dictionnary associating the column
            name with its value

    Returns:
        dict[str, str]: the updated (translated) row
    """

    for lang in TARGET_LANG:
        row[lang] = translate(lang, row[SOURCE_LANG])

    return row


def parse_file(filename: str) -> None:
    """
    Parses all the rows of the specified files.
    It translated the rows into the target languages and overwrites
    the original file with updated values.

    Args:
        filename (str): the filename of the csv file.

    Returns:
        None
    """

    rows = []
    new_rows = []
    fields = []
    with open(filename, mode='r') as file:
        reader = csv.DictReader(file)
        fields = reader.fieldnames

        rows = [row for row in reader]

    for row in progressbar.progressbar(rows, enable_colors=False):
        new_row = parse_row(row)
        new_rows.append(new_row)

    with open(filename, mode='w') as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(new_rows)


def main():
    import sys
    filenames = FILENAMES if len(sys.argv) == 1 else sys.argv[1:]
    for fn in filenames:
        print(f"translating file {fn}...")
        parse_file(fn)


if __name__ == "__main__":
    main()
