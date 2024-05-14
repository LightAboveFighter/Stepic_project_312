import argparse
import logging
import sys
import os
from pyparsing import ParseException

from logs.project_logger import activate_logger
from src.gift.gift_processing import get_gift_dicts
from src.API.Classes import Lesson, Course, Section
from src.API.OAuthSession import OAuthSession


def check_file(filename: str):
    '''check the file existence/permitions'''
    if not os.access(filename, os.F_OK):
        raise RuntimeError(f"Cannot open course: No such file named \"{filename}\"")
    if not os.access(filename, os.W_OK) or not os.access(filename, os.R_OK):
        raise RuntimeError(f"Cannot open course file: Permission denied")

def get_course_from_file(filename: str):
    """returns the course from file"""
    check_file(filename)
    course = Course()
    try:
        return course.load_from_file(filename)
    except ParseException:
        raise RuntimeError(f"Cannot open course: file \"{filename}\" is corrupted or cannot be read correctly")


prefix_zero       = "   "
prefix_continue   = "│  "
prefix_continue_T = "├──"
prefix_end        = "└──"

def __print_lesson_insides__(lesson: Lesson,  pref: str = ""):
    steps = lesson.steps
    prefix_step = pref + prefix_continue_T
    prefix_step_end = pref + prefix_end
    for i in range(len(steps)-1):
        print(prefix_step,f"[{i}] " , steps[i].dict_info()["title"] if type(steps[i]) != int else steps[i], sep="")
    print(prefix_step_end,f"[{len(steps)-1}] " , steps[-1].title if type(steps[-1]) != int else steps[-1], sep="")


def __print_sections_insides__(section: Section, pref: str, show_steps: bool = False):
    lessons = [unit.lesson for unit in section.units]
    prefix_lesson = pref + prefix_continue_T
    prefix_lesson_end = pref + prefix_end
    for i in range(len(lessons)-1):
        print(prefix_lesson,f"[{i}] " , lessons[i].title, sep="")
        if show_steps:
            __print_lesson_insides__(lessons[i], pref + prefix_continue)
    print(prefix_lesson_end,f"[{len(lessons)-1}] " , lessons[-1].title, sep="")
    if show_steps:
        __print_lesson_insides__(lessons[-1], pref + prefix_zero)


def print_tree(data, show_steps: bool = False) -> None:
    match data.__class__.__name__:
        case "Course": #full tree
            sections = data.sections
            print(data.title)
            for i in range(len(data.sections)-1):
                print(prefix_continue_T, f"[{i}] " ,sections[i].title, sep="")
                __print_sections_insides__(sections[i], prefix_continue, show_steps)
            print(prefix_end, f"[{len(sections)-1}] " ,sections[-1].title, sep="")
            __print_sections_insides__(sections[-1], prefix_zero, show_steps)
        case "Section":
            print(data.title)
            __print_sections_insides__(data,"",show_steps)
        case "Lesson":
            print(data.title)
            __print_lesson_insides__(data)
            
def add_section_to_course(course: Course, name: str, section_position: int=-1) -> None:
    course.create_section(section_position, Section( title = name))


def add_lesson_to_section(lesson: Lesson ,course: Course, section_position: int, lesson_position: int=-1) -> None:
    course.create_lesson(lesson, section_position)


def ask_Y_N(msg: str) -> bool:
    counter = 0
    while counter < 20:
        user_input = input(f"{msg} [yes/no]: ")
        if user_input.lower() in ["yes", "y"]:
            print("Continuing...")
            return True
        elif user_input.lower() in ["no", "n"]:
            print("Exiting...")
            return False
        else:
            print("Invalid input. Please enter yes/no.")
        counter+=1
    print("Aborting...")
    return False


def ask(msg: str, reply_type=str):
    counter = 0
    while counter < 20:
        user_input = input(msg)
        if user_input == "":
            return None
        try:
            return reply_type(user_input)
        except ValueError:
            print("Invalid input.")
        counter+=1
    print("Aborting...")
    return False


def get_auth(rewrite=False):
    filename = os.path.dirname(sys.argv[0]) + "/src/API/Client_information.yaml"  # path can be broke FIXME
    print(filename)
    if rewrite or not os.access(filename, os.F_OK) or not os.access(filename, os.R_OK):
        print("Secrets not found or need to be rewrited, you can get them form https://stepik.org/oauth2/applications")
        print("DO NOT SHOW THIS STRINGS TO OTHER PEAPLE!")
        auth = OAuthSession(ask("Client id: "),ask("Client secret: "))
        print(f"file written into {filename}\nyou can change it by \"-A\" flag")
        return auth

    return OAuthSession()

