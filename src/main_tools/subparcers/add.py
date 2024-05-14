import argparse
import logging as log
import sys

import src.main_tools.tools as main_tools
from src.API.Classes import Course, Lesson
from src.API.OAuthSession import OAuthSession
from src.gift.gift_processing import get_gift_dicts

def add(options):
    main_tools.check_file(options.course)
    course: Course = main_tools.get_course_from_file(options.course)
    course.auth(main_tools.get_auth())
    try:
        if options.md is not None and options.gift is not None:
            raise ValueError("md and gift can't be loaded at same time")
        if options.md is not None:
            main_tools.check_file(options.md)
            print('Rofls') # скоро оговоримся
        else:
            main_tools.check_file(options.gift)
            steps = get_gift_dicts(options.gift)
        
        if options.step is not None:
            course.add_step(options.section, options.lesson, steps[options.step], options.step)
        else:
            course.add_lesson(options.section, Lesson(options.title,steps=steps),options.lesson)
        if not options.no_ask:
            if options.step is None:
                main_tools.print_tree(course.sections[options.section])
                print(f"lesson {options.lesson} in section {options.section} will be changed")
            else:
                main_tools.print_tree(course)
                print(f"step {options.step} in lesson {options.lesson} in section {options.section} will be changed")
            if main_tools.ask_Y_N("Continuing?"):
                if not options.no_load: 
                    if course.send_all().success:
                        course.save(filename = options.course)
                        print("DONE")
                else:
                    course.save(filename = options.course)
                    print("DONE")
        else:
            if not options.no_load: 
                if course.send_all().success:
                    course.save(filename = options.course)
                    print("DONE")
            else:
                course.save(filename = options.course)
                print("DONE")
    except IndexError as err:
        if not 0<=options.section<=len(course.sections):
            msg = f"course \"{course.title}\" "\
                  f"have only {len(course.sections)} sections"
        elif not -1<=options.lesson<=len(course.sections[options.section].units):
            msg = f"section \"{course.sections[options.section].title}\" "\
                  f"have only {len(course.sections[options.section].units)} lessons"
        else:
            lesson = course.sections[options.section].units[options.lesson].lesson
            if not -1<=options.step<len(lesson.steps):
                msg = f"lesson \"{lesson.title}\" "\
                      f"have only {len(lesson.steps)} steps"
            else:
                msg = str(err)
        log.error(msg)
        raise RuntimeError(msg)

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
        "-N",
        "--no-load",
        action="store_true",
        default=False,
        dest="no_load",
        help="Do not load course to stepik",
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
