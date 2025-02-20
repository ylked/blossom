import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as font
import PIL.ImageTk
import PIL.Image
import csv
from dataclasses import dataclass
from enum import Enum
import os
import pygame
import dotenv
dotenv.load_dotenv()


CSV_DIRECTORY = 'csv/'
AUDIO_DIRECTORY = 'audio/'
ICONS_DIRECTORY = 'icons/'
ANSWERS_DIRECTORY = 'answers/'
ICONS_SIZE = 100

SURVEYS_FILENAMES = {
    'Questionnaire 1': ('questionnaire1.csv', 'responses1.csv', 'answers1.csv'),
    'Questionnaire 2': ('questionnaire2.csv', 'responses2.csv', 'answers2.csv'),
}


class Language(Enum):
    FR = 'fr'
    EN = 'en'
    DE = 'de'


class Gender(Enum):
    MALE = 'm'
    FEMALE = 'f'
    NOT_SPECIFIED = 'x'


class NarrativeType(Enum):
    SAD = 'sad'
    NEUTRAL = 'neutral'
    NOT_SPECIFIED = 'na'


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
class SingleQuestionAnswer:
    question: str
    answer: str


@dataclass
class UserSurveyAnswer:
    participant_id: str
    age: int
    gender: Gender
    lang: Language
    score: int
    narrative_type: NarrativeType
    answers: list[SingleQuestionAnswer]

    def add_result(self, answer: SingleQuestionAnswer):
        self.answers.append(answer)


class UserAnswersCsvFile:
    def __init__(self, filename, questions_rows):
        self.filename = filename
        self.fields = self._get_fields(questions_rows)
        if not os.path.exists(filename):
            with open(filename, 'x') as f:
                writer = csv.DictWriter(f, self.fields)
                writer.writeheader()

    def _get_fields(self, questions_rows):
        fields = ['id', 'age', 'gender', 'score', 'lang', 'narrative_type']
        fields += [row.tag for row in questions_rows]
        return fields

    def _get_row_from_result(self, answer: UserSurveyAnswer):
        d = {
            'id': answer.participant_id,
            'age': answer.age,
            'gender': answer.gender.value,
            'lang': answer.lang.value,
            'score': answer.score,
            'narrative_type': answer.narrative_type.value,
        }
        d.update({an.question: an.answer for an in answer.answers})
        return d

    def save_result(self, answers: UserSurveyAnswer):
        assert os.path.exists(self.filename)
        row = self._get_row_from_result(answers)
        with open(self.filename, 'a') as f:
            writer = csv.DictWriter(f, self.fields)
            writer.writerow(row)


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

    def all_rows(self):
        return [SimpleRow.from_row(row, self._lang) for row in self._csv.rows]

    def reset_iterator(self):
        self._iterator = iter(self._csv.rows)

    def has_icons(self):
        return self._csv.has_icons()

    def has_score(self):
        return self._csv.has_score()


class Questions(Content):
    pass


class PossibleAnswers(Content):
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
    def __init__(self, questions: Questions, answers: PossibleAnswers):
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
    def __init__(self, survey: Survey = None, user_answers: UserAnswersCsvFile = None):
        if survey.answers.has_icons():
            for ans in survey.answers:
                assert ans.icon is not None

        # self.user_answers_file = user_answers
        # self.survey: Survey = survey
        self.root: tk.Tk = tk.Tk()
        self.root.geometry("1400x600")
        self.current_question = ""

        self.intro_frame = tk.Frame(self.root)
        self.survey_frame = tk.Frame(self.root)

        # self._build_survey_frame(self.survey_frame)
        self._build_intro_frame(self.intro_frame)

        # self.show_survey()
        self.show_intro()

    def _build_survey_frame(self, root):
        questions = Questions(
            CsvFile(CSV_DIRECTORY + SURVEYS_FILENAMES[self.questionnaire.get()][0]))
        answers = PossibleAnswers(CsvFile(CSV_DIRECTORY + SURVEYS_FILENAMES[self.questionnaire.get()][1],
                                          with_score=True, with_icons=True))
        self.user_answers_file = UserAnswersCsvFile(
            ANSWERS_DIRECTORY + SURVEYS_FILENAMES[self.questionnaire.get()][2],
            questions.all_rows()
        )
        self.survey = Survey(questions, answers)
        self.survey.set_lang(Language(self.selected_lang.get()))

        self.question_frame = tk.Frame(
            root,
            borderwidth=1,
            relief='sunken',
            padx='30px',
            pady='50px',
        )
        self.buttons_frame = tk.Frame(
            root,
            padx='30px',
            pady='50px',
        )
        self.question_frame.pack(
            fill=tk.X,
            pady=40,
            padx=60,
        )

        # spacer
        tk.Frame(root).pack(fill=tk.BOTH, expand=True)

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

        q = next(self.survey.questions)
        self.question_label = tk.Label(
            self.question_frame,
            text=q.text,
            font=font.Font(family='Helvetica', size=20),
            wraplength=400,
        )
        self.question_label.pack()
        self.current_question = q

        self.user_answers = UserSurveyAnswer(
            self.participant_id.get(),
            self.age.get(),
            Gender[self.gender.get()],
            Language(self.selected_lang.get()),
            0,
            NarrativeType[self.narrative_type.get()],
            []
        )

        pygame.mixer.init()
        self.play_sound(q.audio)

    def _build_intro_frame(self, root):
        form_frame = tk.Frame(
            root,
            pady=50,
            padx=50,
        )
        start_button_frame = tk.Frame(
            root,
            pady=50,
            padx=50,
        )

        tk.Label(
            form_frame,
            text='Language',
        ).grid(row=0, column=0)

        tk.Label(
            form_frame,
            text='ID'
        ).grid(row=1, column=0)

        tk.Label(
            form_frame,
            text='Age',
        ).grid(row=2, column=0)

        tk.Label(
            form_frame,
            text='Gender',
        ).grid(row=3, column=0)

        tk.Label(
            form_frame,
            text='Narative Type',
        ).grid(row=4, column=0)

        tk.Label(
            form_frame,
            text='Questionnaire',
        ).grid(row=5, column=0)

        self.selected_lang = tk.StringVar()
        self.participant_id = tk.StringVar()
        self.age = tk.IntVar()
        self.gender = tk.StringVar()
        self.narrative_type = tk.StringVar()
        self.questionnaire = tk.StringVar()

        lang_select = ttk.Combobox(
            form_frame,
            textvariable=self.selected_lang,
            values=list(lang.value for lang in Language),
        )
        lang_select.state(["readonly"])
        lang_select.grid(row=0, column=1)

        participant_id_entry = tk.Entry(
            form_frame,
            textvariable=self.participant_id,
            bd=0,
            highlightthickness=0,
            takefocus=0,
        )
        participant_id_entry.grid(row=1, column=1)

        age_entry = tk.Entry(
            form_frame,
            textvariable=self.age,
            bd=0,
            highlightthickness=0,
            takefocus=0,
        )
        age_entry.grid(row=2, column=1)

        gender_select = ttk.Combobox(
            form_frame,
            textvariable=self.gender,
            values=list(gender.name for gender in Gender),
        )
        gender_select.grid(row=3, column=1)

        narrative_select = ttk.Combobox(
            form_frame,
            textvariable=self.narrative_type,
            values=list(narrative.name for narrative in NarrativeType)
        )
        narrative_select.grid(row=4, column=1)

        questionnaire_select = ttk.Combobox(
            form_frame,
            textvariable=self.questionnaire,
            values=list(SURVEYS_FILENAMES.keys())
        )
        questionnaire_select.grid(row=5, column=1)

        start_btn = tk.Button(
            start_button_frame,
            text='Start',
            command=lambda: self.start_survey(),
            bd=0,
            highlightthickness=0,
            takefocus=0,
        )

        form_frame.pack()
        tk.Frame(root).pack(fill=tk.BOTH, expand=True)
        start_button_frame.pack()

        start_btn.pack()

    def start_survey(self):
        self.intro_frame.pack_forget()
        # self.set_lang(Language(self.selected_lang.get()))
        self._build_survey_frame(self.survey_frame)
        self.survey_frame.pack(fill=tk.BOTH, expand=True)

    def show_intro(self):
        self.survey_frame.pack_forget()
        self.intro_frame.pack(fill=tk.BOTH, expand=True)

    def finish(self):
        self.user_answers_file.save_result(self.user_answers)
        self.question_label['text'] = "You have finished"
        self.buttons_frame.pack_forget()

    def set_lang(self, lang: Language):
        self.survey.set_lang(lang)

    def play_sound(self, filename):
        s = pygame.mixer.Sound(AUDIO_DIRECTORY + filename)
        s.play()

    def validate(self, answer: SimpleRow):
        print(f"answered : {answer.text} (score={answer.score})")
        try:
            self.user_answers.add_result(SingleQuestionAnswer(
                self.current_question.tag,
                answer.tag)
            )
            self.user_answers.score += int(answer.score)
            self.current_question = next(self.survey.questions)
            self.question_label['text'] = self.current_question.text
            self.play_sound(self.current_question.audio)
        except StopIteration:
            self.finish()

    def run(self):
        self.root.update()
        self.root.update_idletasks()
        self.root.mainloop()


questions = Questions(CsvFile('csv/questionnaire2.csv'))
answers = PossibleAnswers(CsvFile('csv/responses2.csv',
                                  with_score=True, with_icons=True))

user_answers = UserAnswersCsvFile('answers/answer1.csv', questions.all_rows())
survey = Survey(questions, answers)
survey.set_lang(Language.FR)

gui = Gui(survey, user_answers)
gui.run()
