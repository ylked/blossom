import csv
import sys
import pygame

LANG = 'de'
VALID_NARRATIVE = ('sad', 'neutral')

CSV_DIRECTORY = 'csv/'
AUDIO_DIRECTORY = 'audio/'


def load_csv(filename):
    rows = []
    with open(filename, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)

        for row in reader:
            rows.append(row)

    return iter(rows)


def get_filename(row, lang):
    return AUDIO_DIRECTORY + row['filename_' + lang]


def show_usage():
    print("Invalid syntax")
    print("Usage : ")
    print(f"python3 {sys.argv[0]} sad|neutral")
    print(f"example : python3 {sys.argv[0]} neutral")


def main():
    if len(sys.argv) != 2 \
            or sys.argv[1] not in VALID_NARRATIVE:
        show_usage()
        exit(-1)

    pygame.mixer.init()

    narrative = sys.argv[1]

    filename = CSV_DIRECTORY + narrative + '.csv'
    rows_iterator = load_csv(filename)

    for row in rows_iterator:
        fn = get_filename(row, LANG)
        print(fn)
        pygame.mixer.Sound(fn).play()

        input("Press Enter to continue...")


if __name__ == '__main__':
    main()
