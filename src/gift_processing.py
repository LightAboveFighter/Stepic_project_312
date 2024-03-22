from pygiftparser import parser as giftparser
import json
import sys
sys.path.insert(1, '.')       #FIXME PATH CAN BE EASELY BROKEN
from src.API.Classes import Step_text #FIXME 


'''TODO
True-false DONE
Short answer 
Matching
Missing word 
Numerical questions
Essay
Description -- not a question
'''

# global vars
error_msg = "ERROR while processing the gift file: "
CRED = "\033[91m"  # start red stdout
CEND = "\033[0m"  # stop CRED
STEPIK_name_types = {"MultipleChoiceCheckbox()": "choice",
                     "MultipleChoiceRadio()": "choice",
                     "TrueFalse()": "choice",
                    }
STEPIK_sampe_size = 10


def __question_validator__(x:dict) -> bool:
    '''returns True if question is valid'''
    pass

def __data_multiple_choice__(x: giftparser.gift.Question) -> dict:
    options = {}
    options["options"] = []
    options["is_always_correct"] = False
    for i in x.answer.options:
        options["options"].append({})
        options["options"][-1]["is_correct"] = abs(i.percentage)>0.95
        options["options"][-1]["text"] = i.text
        if i.feedback != None:
            options["options"][-1]["feedback"] = i.feedback
        else:
            options["options"][-1]["feedback"] = ""
    options["sample_size"] = min(len(x.answer.options), STEPIK_sampe_size)
    tmp = 0
    for i in options["options"]:
        tmp += i["is_correct"]
    options["is_multiple_choice"] = tmp > 1
    return options

def __data_true_false__(x: giftparser.gift.Question):
    options = __data_multiple_choice__(x)
    options["options"].append({})
    if options["options"][0]["text"] == "True":
        options["options"][1]["text"] = "False"
        options["options"][1]["is_correct"] = False
        options["options"][1]["feedback"] = ""
    else:
        options["options"][1]["text"] = "True"
        options["options"][1]["is_correct"] = False
        options["options"][1]["feedback"] = ""
    return options


def __get_question_options__(x: giftparser.gift.Question) -> dict:
    """gets options dict for Stepik json"""
    if (
        str(x.answer.__repr__()) == "MultipleChoiceRadio()"
        or str(x.answer.__repr__()) == "MultipleChoiceCheckbox()"
    ):
        return __data_multiple_choice__(x)
    if str(x.answer.__repr__()) == "TrueFalse()":
        return __data_true_false__(x)
    else:
        return {"ISBROKEN": True, "type":str(x.answer.__repr__())}  # FIXME



def __get_question_data__(question: giftparser.gift.Question) -> dict:
    """gets block dict for Stepik json"""
    question_data: dict = {}
    if not(question.answer.__repr__() in STEPIK_name_types.keys()):
        question_data["name"] = None
    else:
        question_data["name"] = STEPIK_name_types[question.answer.__repr__()]
    question_data["text"] = question.text + (' _______ ' + question.text_continue if question.text_continue else '')
    options: dict = __get_question_options__(question)
    question_data["source"] = options # FIXME from config
    return question_data


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
        parse_result = giftparser.    parse(giftfile)
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
    import argparse
    import pprint

    def parse_input_arguments():
        parser = argparse.ArgumentParser(description="GIFT Moodle file parser.")
        parser.add_argument(
            "-f", "--file", dest="file", required=True, help="GIFT Moodle file."
        )
        args = parser.parse_args()
        return args

    args = parse_input_arguments()
    for i in get_gift_dicts(args.file):  
        print("\n\n",i['name'])
        print(json.dumps(i, indent=4))

