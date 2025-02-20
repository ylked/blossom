import tkinter as tk
import tkinter.font as font
import PIL.ImageTk
import PIL.Image
import csv
from dataclasses import dataclass
from enum import Enum
import os


CSV_DIRECTORY = 'csv/'
AUDIO_DIRECTORY = 'audio/'
ICONS_DIRECTORY = 'icons/'
ICONS_SIZE = 100


class Language(Enum):
    FR = 'fr'
    EN = 'en'
    DE = 'de'


class CsvFile:
    def __init__(self, filename, with_score=False, with_icons=False):
        self.rows = []
        self._with_score = with_score
        self._with_icons = with_icons
        with open(filename, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            self.rows = [
                GenericCsvRow(
                    row['tag'],
                    row['en'],
                    row['de'],
                    row['fr'],
                    row['filename_en'],
                    row['filename_de'],
                    row['filename_fr'],
                    row['score'] if with_score else None,
                    row['icon'] if with_icons else None
                ) for row in reader
            ]

    def has_icons(self):
        return self._with_icons

    def has_score(self):
        return self._with_score


@dataclass
class GenericCsvRow:
    tag: str
    text_en: str
    text_de: str
    text_fr: str
    audio_en: str
    audio_de: str
    audio_fr: str
    score: int | None
    icon: str | None

    def _get_attribute(self, lang: Language, attribute_name: str):
        attr_name = attribute_name + '_' + lang.value
        return self.__getattribute__(attr_name)

    def text(self, lang: Language) -> str:
        return self._get_attribute(lang, 'text')

    def audio(self, lang: Language) -> str:
        return self._get_attribute(lang, 'audio')


@dataclass
class SimpleRow:
    tag: str
    text: str
    audio: str
    score: int | None
    icon: str | None

    def from_row(row: GenericCsvRow, lang: Language):
        return SimpleRow(
            row.tag,
            row.text(lang),
            row.audio(lang),
            row.score,
            row.icon
        )


class Content:
    def __init__(self, csv: CsvFile):
        self._csv = csv
        self._lang = Language.EN
        self.reset_iterator()

    def set_lang(self, lang: Language):
        self._lang = lang

    # def __iter__(self):
    #     for row in self._csv.rows:
    #         yield SimpleRow.from_row(row, self._lang)

    def __iter__(self):
        return self

    def __next__(self):
        row = next(self._iterator)
        return SimpleRow.from_row(row, self._lang)

    def reset_iterator(self):
        self._iterator = iter(self._csv.rows)

    def has_icons(self):
        return self._csv.has_icons()

    def has_score(self):
        return self._csv.has_score()


class Questions(Content):
    pass


class Answers(Content):
    pass


class Icon:
    def __init__(self, filename: str):
        assert os.path.exists(filename)
        img = PIL.Image.open(filename)
        img = img.resize(self._get_dim(img))
        self.img = PIL.ImageTk.PhotoImage(img)
        self.fn = filename

    def _get_dim(self, img):
        w, h = img.size
        return ICONS_SIZE, int(h/w * ICONS_SIZE)

    def __str__(self):
        return f"icon {self.fn}"


class Survey:
    def __init__(self, questions: Questions, answers: Answers):
        self.questions = questions
        self.answers = answers
        self.score = 0

    def save_answer(self, answer: SimpleRow):
        assert answer.score is not None, \
            f"Answer '{answer.text}' does not have a score, check CSV file"
        self.score += answer.score

    def set_lang(self, lang: Language):
        self.questions.set_lang(lang)
        self.answers.set_lang(lang)


class Gui:
    def __init__(self, survey: Survey):
        if survey.answers.has_icons():
            for ans in survey.answers:
                assert ans.icon is not None

        self.survey: Survey = survey
        self.root: tk.Tk = tk.Tk()
        self.root.geometry("1400x600")
        self.question_frame = tk.Frame(
            self.root,
            borderwidth=1,
            relief='sunken',
            padx='30px',
            pady='50px',
        )
        self.buttons_frame = tk.Frame(
            self.root,
            padx='30px',
            pady='50px',
        )
        self.question_frame.pack(
            fill=tk.X,
            pady=40,
            padx=60,
        )

        # spacer
        tk.Frame(self.root).pack(fill=tk.BOTH, expand=True)

        self.buttons_frame.pack(fill=tk.X, expand=True)

        self.survey.answers.reset_iterator()
        self.icons = [
            Icon(ICONS_DIRECTORY + ans.icon)
            for ans in self.survey.answers
        ] if self.survey.answers.has_icons() else []
        self.survey.answers.reset_iterator()

        self.buttons: list[tk.Button] = list([
            tk.Button(
                self.buttons_frame,
                text=ans.text,
                command=lambda ans=ans: self.validate(ans),
                bd=0,
                highlightthickness=0,
                takefocus=0,
                padx=30,
                pady=20,
                image=self.icons[i].img if self.survey.answers.has_icons(
                ) else None,
                compound=tk.LEFT
            )
            for i, ans in enumerate(self.survey.answers)
        ])
        self.root.update_idletasks()

        i = 0
        for b in self.buttons:
            self.buttons_frame.columnconfigure(i, weight=1)
            b.grid(
                row=0,
                column=i,
                padx=10,
            )
            i += 1

        self.question = tk.Label(
            self.question_frame,
            text=next(self.survey.questions).text,
            font=font.Font(family='Helvetica', size=20),
            wraplength=400,
        )
        self.question.pack()

    def finish(self):
        self.question['text'] = "You have finished"
        self.buttons_frame.pack_forget()

    def set_lang(self, lang: Language):
        self.survey.set_lang(lang)

    def validate(self, answer: SimpleRow):
        print(f"answered : {answer.text} (score={answer.score})")
        try:
            self.question['text'] = next(self.survey.questions).text
        except StopIteration:
            self.finish()

    def run(self):
        self.root.mainloop()


questions = Questions(CsvFile('csv/questionnaire2.csv'))
answers = Answers(CsvFile('csv/responses2.csv',
                  with_score=True, with_icons=True))

survey = Survey(questions, answers)
survey.set_lang(Language.FR)

gui = Gui(survey)
gui.run()
