import argparse
import logging as log
import sys

import src.main_tools.tools as main_tools
from src.API.Classes import Course, Lesson
from src.API.OAuthSession import OAuthSession
from src.gift.gift_processing import get_gift_dicts

def add(options):
    course: Course = main_tools.get_course_from_file(options.course)
    course.auth(OAuthSession())
    try:
        if options.md is not None and options.gift is not None:
            raise ValueError("md and gift can't be loaded at same time")
        if options.md is not None:
            print('Rofls') # скоро оговоримся
        else:
            steps = get_gift_dicts(options.gift)
            lesson = course.sections[options.section].lessons[options.lesson]
        
        if options.step is not None:
            lesson.steps.insert(options.step, steps[options.step])
        else:
            course.sections[options.section].lessons.insert(options.lesson, Lesson(options.title,steps=steps))
        if not options.no_ask:
            if options.step is None:
                main_tools.print_tree(course.sections[options.section])
                print(f"lesson {options.lesson} in section {options.section} will be changed")
            else:
                main_tools.print_tree(lesson)
                print(f"step {options.step} in lesson {options.lesson} in section {options.section} will be changed")
            if main_tools.ask_Y_N("Continuing?"):
                course.save(filename = options.course)
                course.send_all()
        else:
            course.save(filename = options.course)
            course.send_all()
    except IndexError as err:
        if len(course.sections)<=options.section:
            msg = f"course \"{course.title}\" "\
                  f"have only {len(course.sections)} sections"
        elif len(course.sections[options.section].lessons)<=options.lesson:
            msg = f"section \"{course.sections[options.section].title}\" "\
                  f"have only {len(course.sections[options.section].lessons)} lessons"
        elif len(lesson.steps)<=options.step:
            msg = f"lesson \"{lesson.title}\" "\
                  f"have only {len(lesson.steps)} steps"
        else:
            msg = str(err)
        log.error(msg)
        print("ERROR:", msg, file=sys.stderr)
        raise RuntimeError()

def add_subcommand(subparsers, parents):
    parser = subparsers.add_parser("add", parents=[parents], help="add an existing lesson or step")
    # parser.add_argument(
    #     "-c",
    #     "--config",
    #     action="store",
    #     # default=get_config_file(),
    #     dest="configfile",
    #     help="Use the specified configuration file.",
    # )
    parser.add_argument(
        "-C",
        "--course",
        required=True,
        action="store",
        default=None,
        dest="course",
        help="course file",
    )
    parser.add_argument(
        "-S",
        "--section_id",
        required=True,
        type=int,
        action="store",
        dest="section",
        help="section id to work with" 
    )
    parser.add_argument(
        "-L",
        "--lesson",
        required=True,
        type=int,
        action="store",
        default=None,
        dest="lesson",
        help="lesson id to work with" 
    )
    parser.add_argument(
        "-t",
        "--title",
        action="store",
        default="",
        dest="title",
        help="new title of lesson",
    )
    parser.add_argument(
        "-m",
        "--md",
        action="store",
        default=None,
        dest="md",
        help="markdown file to read",
    )
    parser.add_argument(
        "-g",
        "--gift",
        action="store",
        default=None,
        dest="gift",
        help="gift file to read",
    )
    parser.add_argument(
        "-s",
        "--step",
        action="store",
        type=int,
        default=None,
        dest="step",
        help="step id to work with",
    )
    parser.add_argument(
        "-n",
        "--no-ask",
        action="store_true",
        default=False,
        dest="no_ask",
        help="Do not ask for confirm",
    )
    parser.set_defaults(func=add)
