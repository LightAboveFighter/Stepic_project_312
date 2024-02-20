from Classes import Step_text #FIXME 
from pygiftparser import parser as giftparser
import json

# global vars
STEPIK_name_types = {"MultipleChoiceCheckbox()": "choice",
                     "MultipleChoiceRadio()": "choice",
                    }

def __question_validator__(x:dict) -> bool:
    '''returns True if question is valid'''
    pass

def __get_question_options__(x: gifpars.gift.Question) -> dict:
    """gets options dict for Stepik json"""
    pass

def __get_question_data__(x: gifpars.gift.Question) -> dict:
    """gets block dict for Stepik json"""
    pass

def get_gift_dicts(filename: str) -> list:
    """returns list if block dicts of question from GIFT file"""
    try:
        giftfile = open(filename, "r").read()
    except FileNotFoundError:
        print(
            CRED
            + error_msg + 'File "' + str(filename) + '" not found' 
            + CEND
        )  # TODO change to stderr
        raise FileNotFoundError
    except PermissionError:
        print(
            CRED
            + error_msg + "Can't open \"" + str(filename) + '" permission denied'
            + CEND
        )
        raise PermissionError
    try:
        parse_result: gifpars.gift.Gift = gifpars.parse(giftfile)
    except Exception as error:
        print(
            CRED
            + error_msg + "Can't parse \"" + str(filename) + '"\n'
            + str(error)
            + CEND
        )
        raise RuntimeError
    questions: list = [__get_question_data__(i) for i in parse_result.questions]
    return questions

def get_Step_list(lesson_id: int) -> list:
    pass

if __name__ == "__main__":
    pass

