from pygiftparser import parser as giftparser
import pprint
import json
import logging as log

if __name__ == "__main__":
    import sys
    sys.path.insert(1, '.')       #FIXME PATH CAN BE EASELY BROKEN

from src.API.Classes import Lesson 
from src.API.Step import create_any_step

from logs.project_logger import activate_logger

'''TODO
True-false DONE
Short answer DONE 
Matching DONE
Missing word interpreted as MultipleChoice
Numerical questions ~DONE tests and CLASS NEADED
Multiple numerical questions DONE
Essay DONE
Description DONE
'''

# global vars
STEPIK_name_types = {"MultipleChoiceCheckbox()": "choice",
                     "MultipleChoiceRadio()": "choice",
                     "TrueFalse()": "choice",
                     "Matching()":"matching",
                     "Numerical()":"number",
                     "MultipleNumerical()":"number",
                     "Essay()":"free-answer",
                     "Description()":"text",
                    }


def __question_validator__(x:dict) -> bool:
    '''returns True if question is valid'''
    pass


def __data_multiple_choice__(x: giftparser.gift.Question) -> dict:
    options = {}
    options["options"] = []
    options["is_always_correct"] = False
    for op in x.answer.options:
        options["options"].append({})
        options["options"][-1]["is_correct"] = op.percentage>0.
        options["options"][-1]["text"] = op.text
        if op.feedback != None:
            options["options"][-1]["feedback"] = op.feedback
        else:
            options["options"][-1]["feedback"] = ""
    tmp = 0
    for op in options["options"]:
        tmp += op["is_correct"]
    options["is_multiple_choice"] = tmp > 1
    return options


def __data_true_false__(x: giftparser.gift.Question):
    log.info("True_False will be interpreted as Choice()")
    options = __data_multiple_choice__(x)
    options["sample_size"] = 2
    options["options"].append({})
    if options["options"][0]["text"] == "True":
        options["options"][1] = {"text":      "False",
                                 "is_correct": False,
                                 "feedback":   ""
                                }
    else:
        options["options"][1] = {"text":      "True",
                                 "is_correct": False,
                                 "feedback":   ""
                                }
    return options


# FIXME Move to file
short_generator_checker_text = '''  
def check(reply):
    return reply in {good_list}
#sep
def solve():
    return '{good_list[0]}'
'''

def __function_short_generator__(x : giftparser.gift.Question):
    good_list = []
    for option in x.answer.options:
        if option.percentage > 0.95:
            # ответ, где кавычки заменены на \кавычки
            text = str(op.text).replace('\'', r'\'').replace('\"', r'\"')
            good_list.append(text)
    return short_generator_checker_text.format(good_list=good_list)


def __data_short__(x: giftparser.gift.Question)->dict:
    return {
            "code": __function_short_generator__(x),
            "case_sensitive": False,
            "is_file_disabled": True,
            "is_text_disabled": False,
            "match_substring": False,
            "pattern": "Hello",
            "use_re": False
            }


def __data_matching__(x:giftparser.gift.Question):
    options = {
        "source":{
            "is_html_enabled": True,
            "preserve_firsts_order": True,
            "pairs": []
            }
    }
    feedback_wrong = ""
    for i in range(len(x.answer.options)):
        tmp = x.answer.get_pair(x.answer.options[i])
        feedbacktmp = (x.answer.options[i]).feedback
        if feedbacktmp is not None:
            feedback_wrong+= tmp["first"] + ": " + feedbacktmp + "\n"
        options["source"]["pairs"].append(tmp)
    options["feedback_wrong"] = feedback_wrong
    return options


def __data_numerical__(x:giftparser.gift.Question):
    log.info("Numerical question will be reinterpreted as Short()")
    options = {
        "feedback_wrong": x.answer.options[0].feedback,
        "source":{
            "options":[{"answer":x.answer.get_number(),"max_error":x.answer.get_error_margin()}]
            }
    }
    return options


def __data_multiple_numerical__(x:giftparser.gift.Question):
    log.info("Numerical question will be reinterpreted as Short()")
    options = {
        "feedback_wrong": x.answer.options[0].feedback,
        "source":{
            "options":[]
            }
    }
    for number in x.answer.numbers:
        if number.options[0].percentage>0.95:
            options["source"]["options"].append({"answer":number.get_number(),"max_error":number.get_error_margin()})
    return options


def __data_essay__(x:giftparser.gift.Question):
    return dict({ 
      "options": None,
      "source": {
        "is_attachments_enabled": False,
        "is_html_enabled": True,
        "manual_scoring": False
      },
    })


def __data_description__(x:giftparser.gift.Question):
    return dict({"options": None})


def __get_question_options__(x: giftparser.gift.Question) -> dict:
    """gets options dict for Stepik json"""
    if (
        str(x.answer.__repr__()) == "MultipleChoiceRadio()"
        or str(x.answer.__repr__()) == "MultipleChoiceCheckbox()"
    ):
        return {"source":__data_multiple_choice__(x)}
    if str(x.answer.__repr__()) == "TrueFalse()":
        return {"source":__data_true_false__(x)}
    if str(x.answer.__repr__()) == "Short()":
        return __data_short__(x)
    if str(x.answer.__repr__()) == "Matching()":
        return __data_matching__(x)
    if str(x.answer.__repr__()) == "Numerical()": 
        return __data_numerical__(x)
    if str(x.answer.__repr__()) == "MultipleNumerical()":
        return __data_multiple_numerical__(x)
    if str(x.answer.__repr__()) == "Essay()":
        return __data_essay__(x)
    if str(x.answer.__repr__()) == "Description()":
        return __data_description__(x)
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
    question_data = question_data | options
    question_type = question_data["name"]
    title = question.name
    if title in question_data["text"]:  #FIXME add to .md 
        log.info(f'title \"{title}\" title is contained in question, maby title is incorrect!')
    return create_any_step(question_type, title if title else "", 0, **{"block":question_data},unique ={"options": (question_data["source"]["options"] if "source" in question_data.keys() else None)})


def get_gift_dicts(filename: str) -> list:
    """returns list if block dicts of question from GIFT file"""
    try:
        with open(filename, "r") as giftfile:
            parse_result = giftparser.parse(giftfile.read())
    except FileNotFoundError:
        log.error( 'File "' + str(filename) + '" not found')
        raise FileNotFoundError
    except PermissionError:
        log.error("Can't open \"" + str(filename) + '" permission denied')
        raise PermissionError
    except Exception as error:
        log.error("Can't parse \"" + str(filename) + '"\n'+ str(error))
        raise RuntimeError
    questions = []
    for question_parsed in parse_result.questions:
        question = __get_question_data__(question_parsed)
        if question is not None:
            questions.append(question)
    giftfile.close()
    return questions


def get_gift_dicts_from_text(text: str) -> list:
    """returns list if block dicts of question from GIFT file"""
    try:
        parse_result = giftparser.parse(text)
    except Exception as error:
        print(
            CRED
            + error_msg + "Can't parse \"" + text + '"\n'
            + str(error)
            + CEND
        )
        raise RuntimeError
    questions = []
    for question_parsed in parse_result.questions:
        question = __get_question_data__(question_parsed)
        if question is not None:
            questions.append(question)
    print(questions)
    return questions



if __name__ == "__main__":
    import argparse
    import pprint
    activate_logger("I")

    def parse_input_arguments():
        parser = argparse.ArgumentParser(description="GIFT Moodle file parser.")
        parser.add_argument(
            "-f", "--file", dest="file", required=True, help="GIFT Moodle file."
        )
        args = parser.parse_args()
        return args

    args = parse_input_arguments()
    for i in get_gift_dicts(args.file):  
        if not i:
            continue
        print(json.dumps(i.dict_info(), indent=4))


