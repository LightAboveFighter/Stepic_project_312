import argparse
import logging
import sys
from pyparsing import ParseException

from logs.project_logger import activate_logger
from src.gift.gift_processing import get_gift_dicts
from src.API.Classes import Lesson, Course, Section
from src.API.OAuthSession import OAuthSession


def get_course_from_file(filename: str):
    """returns the course from file"""
    course = Course()
    try:
        return course.load_from_file(filename)
    except ParseException:
        raise RuntimeError(f"Cannot open course: file \"{filename}\" is corrupted or cannot be read correctly")
    except FileNotFoundError:
        raise RuntimeError(f"Cannot open course: No such file named \"{filename}\"")
    except PermissionError:
        raise RuntimeError(f"Cannot open course file: Permission denied")

def get_course_tree(course: Course, ) -> None:
    pass

def add_section_to_course(course: Course, name: str, section_position: int=-1) -> None:
    course.create_section(section_position, Section( title = name))


def add_lesson_to_section(lesson: Lesson ,course: Course, section_position: int, lesson_position: int=-1) -> None:
    course.create_lesson(lesson, section_position)


def ask_Y_N() -> bool:
    counter = 0
    while counter < 20:
        user_input = input("Do you want to continue? [yes/no]: ")
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


