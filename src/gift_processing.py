from Classes import Step_text #FIXME 
from pygiftparser import parser as giftparser
import json

# global vars
STEPIK_name_types = {"MultipleChoiceCheckbox()": "choice",
                     "MultipleChoiceRadio()": "choice",
                    }



def __get_question_options__(x: gifpars.gift.Question) -> dict:
    """get options from question in Stepik json format"""
    pass

def __get_question_data__(x: gifpars.gift.Question) -> dict:
    pass

def get_gift_dicts(filename: str) -> list:
    pass


if __name__ == "__main__":
    pass

