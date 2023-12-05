from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import json
from config import PROJECT_PATH
from openpyxl.worksheet.worksheet import Worksheet
import openpyxl
import os

_N = '\n'
file_path = os.path.join(PROJECT_PATH, 'STR.xlsx')


def change_language_markup(user):
    # todo fix
    # User
    __ = STR(user.language_code)
    button_list = [[]]
    for lang, value in __.languages.items():
        if not __.language_code == lang:
            button_list[0].append(value)

    btn = InlineKeyboardMarkup()
    btn.row_width = 2
    for _ in button_list:
        btn.add(*_)

    return btn


# noinspection PyAttributeOutsideInit,DuplicatedCode
class STR:
    languages = {
        'en': InlineKeyboardButton('English', callback_data=f'LANG en'),
        'fa': InlineKeyboardButton('Farisi', callback_data=f'LANG fa'),
    }

    def __init__(self, language_code):
        # self.languages_setter = {
        #     'en': self.set_en,
        # }
        # func = self.languages_setter.get(language_code, self.set_en)
        # func()

        # Force FARISI
        self.set_lang('fa')
        # self.set_lang(language_code)

    def set_lang(self, language_code):
        with open(f"{PROJECT_PATH}/Json/{language_code}.json", 'r', encoding="utf8") as f:
            self.json_file: dict = json.load(f)

        for variable, value in self.json_file.items():
            # print(variable, value)
            setattr(self, variable, value)

        self.keyboard_main_menu = [
            [self.mm_btn_1],
            [self.mm_btn_2, self.mm_btn_3],
            [self.mm_btn_4],
            [self.mm_btn_5],
        ]
        self.admin_keyboard = [
            [self.admin_mm_btn_1],
            [self.admin_mm_btn_2],
            [self.admin_mm_btn_3],
            [self.admin_mm_btn_4],
        ]


def set_lang(language_code: str) -> STR:
    choices = {
        'en': en,
        'fa': fa,
    }

    return choices.get(language_code, en)


def read_from_xlsx():
    try:
        data = []
        dataframes: list = openpyxl.load_workbook(file_path).worksheets
        for dataframe in dataframes:
            dataframe: Worksheet
            # print(list(dataframe.rows)[1:])
            for variable, en, fa in list(dataframe.rows)[1:]:
                if variable.value:
                    data.append((variable.value, en.value, fa.value))
        return data
    except Exception as r:
        print('Exception', r)
        exit()


def make_jsons(xlsx_data):
    languages = ['en', 'fa']
    for lang in languages:
        dictionary = {}
        for variable, en, fa in xlsx_data:
            strings = {'en': en, 'fa': fa, }
            dictionary[variable] = strings.get(lang)
        with open(f"{PROJECT_PATH}/Json/{lang}.json", "w", encoding='UTF-8') as outfile:
            # print(dictionary)
            json.dump(dictionary, outfile, ensure_ascii=False)


def initialize_languages():
    global en, fa
    make_jsons(read_from_xlsx())
    en = STR('en')
    fa = STR('fa')


# Read Xlsx to dict
data = read_from_xlsx()

# Create Json file (for each language)
make_jsons(data)

en = STR('en')
fa = STR('fa')
