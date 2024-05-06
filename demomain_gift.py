#!python3
import argparse
import logging
import os
from pathlib import Path

from logs.project_logger import activate_logger
from src.gift.gift_processing import get_gift_dicts
from src.API.Classes import Lesson, Course, Section
from src.API.OAuthSession import OAuthSession

import src.main_tools.tools
from src.main_tools.subparcers import add, structure, update, load




# Украдено у https://github.com/qtile/qtile
def main():
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "-l",
        "--log-level",
        default="WARNING",
        dest="log_level",
        type=str.upper,
        choices=("D", "I", "W", "E", "C"),
        help="Set qtile log level",
    )
    main_parser = argparse.ArgumentParser(
        prog="Stepik project",
    )

    subparsers = main_parser.add_subparsers()
    update.add_subcommand(subparsers, parent_parser)
    load.add_subcommand(subparsers, parent_parser)
    add.add_subcommand(subparsers, parent_parser)
    structure.add_subcommand(subparsers, parent_parser)



    # `qtile help` should print help
    def print_help(options):
        main_parser.print_help()

    help_ = subparsers.add_parser("help", help="Print help message and exit.")
    help_.set_defaults(func=print_help)

    options = main_parser.parse_args()
    if func := getattr(options, "func", None):
        log_level = options.log_level
        activate_logger(log_level if log_level else "E")
        func(options)
    else:
        main_parser.print_usage()
        exit(1)


if __name__ == "__main__":
    main()























'''
activate_logger("D")
parser = argparse.ArgumentParser(
                    description='Demo',
                    epilog='Text at the bottom of help') #FIXME add help

parser.add_argument('-c','--config',
                     help="path to the config file")

subparsers = parser.add_subparsers()

create_sp  = subparsers.add_parser('create', help="creates new course to FILE")
create_sp.set_defaults(cmd="create")
create_sp.add_argument('-f', '--file', required=True,
                        action='store',
                        help='the file where the course will be written')
create_sp.add_argument('-n', '--name',
                    type=str,
                     help='name of the course')


pull_sp  = subparsers.add_parser('pull', help="pull course from net to FILE")
pull_sp.set_defaults(cmd="pull")
pull_sp.add_argument('-f', '--file', required=True,
                        action='store',
                        help='the file where the course will be written')
pull_sp.add_argument('-i', '--id',
                     type=int,
                     help='id of the course')


push_sp  = subparsers.add_parser('push', help="push course from net to FILE")
push_sp.set_defaults(cmd="push")
push_sp.add_argument('-f', '--file', required=True,
                        action='store',
                        help='the file where the course will be written')

add_sp  = subparsers.add_parser('add', help="add lesson to local file")
add_sp.set_defaults(cmd="add")
add_sp.add_argument('-S', '--section',
                    action='store_true',
                    help="section add scenario")
add_sp.add_argument('-L', '--lesson',
                    action='store_true',
                    help="lesson add scenario(Defalt)")
add_sp.add_argument('-f', '--file', required=True,
                    action='store',
                    help='course file')
add_sp.add_argument('-G', '--gift',
                     help='gift file to load')
add_sp.add_argument('-M', '--md',
                     help='markdown file to load')
add_sp.add_argument("-s", '--send',
                    action='store_true', 
                    help="send course to stepik.org after an \"add\"")
add_sp.add_argument("-P", '--section_position',
                    type=int,
                    help="section position in the course")
add_sp.add_argument("-p", '--lesson_position',
                    type=int,
                    help="lesson position in the course")
add_sp.add_argument('-n', '--name',
                    type=str,
                    help="name of the added object")


args = parser.parse_args()


match args.cmd:
    case 'create':
        name = args.name if args.name else tools.ask("course name[defalt \"Untitled\"]: ")
        name = name if name else "Untitled"
        Course(name).save(filename=args.file)
        print("DONE: course created")
    case 'add':
        course = tools.get_course_from_file(args.file)
        if args.section and args.lesson:
            print("You cant add section and lesson at the same time!\nAborting")
            exit(1)
        if not args.lesson:
            section_position = args.section_position
            if not section_position:
                section_position = tools.ask("neaded section position: ", int)
            tools.add_section_to_course(course, args.name if args.name else tools.ask("section name: "), section_position)
            course.save(filename=args.file)
        else:
            if args.gift and args.md:
                print("You cant add GIFT and MD at the same time!\nAborting")
                exit(1)
            elif args.gift:
                lesson = Lesson(title=args.name if args.name else tools.ask("lesson name: "),steps=get_gift_dicts(args.gift))
            elif args.md:
                print("md is not ready")
                exit(1)
            else:
                print("You need to choose gift or md (no argument given)")
                exit(1)
            section_position = args.section_position
            if not section_position:
                section_position = tools.ask("neaded section position: ", int)
            lesson_position = args.lesson_position
            if not lesson_position:
                lesson_position = tools.ask("neaded lesson position[defalt is last]: ")
                if lesson_position is None:
                    lesson_position = -1

            tools.add_lesson_to_section(lesson, course, section_position)
            course.save(filename=args.file)
            print("DONE: course saved")
    case "pull":
        course = Course()
        course.auth(OAuthSession())
        print("it will take time")
        course.load_from_net(args.id if args.id else tools.ask("course id: "))
        course.save(filename=args.file)
        print("DONE: course saved")
    case "push":
        course = tools.get_course_from_file(args.file)
        course.auth(OAuthSession())
        print(course.send_all())
        course.save(filename=args.file)
        print("Done: course sended")

    case _:
        print("Хо??")

'''
'''
parser.add_argument('-G', '--GIFT',
                    help='export from GIFT file')
parser.add_argument('--debug', '-d',
                    action='store_true',
                    help='show debug information')
parser.add_argument('--file', '-f',
                    # dest='file', -- only needed if the long form isn't first
                    help='Course file, that need to be read')
parser.add_argument('--lessonid', '-id',
                    dest='lessonid',
                    help='Lesson id')
parser.add_argument('--title', '-T',
                    dest='title',
                    help='Lesson title')


print(args)
if args.debug:
    activate_logger("D")
else:
    activate_logger("W")
if args.upload:
    title = args.title if args.title is not None else ""
    steps: list    = get_gift_dicts(args.file)
    lesson: Lesson = Lesson(title=title, steps=steps)
    course: Course = Course("title_NEw")
    course.create_section(0, Section("название",[lesson]))
    course.auth(OAuthSession())
    course.save()
    print(course.send_all())
'''

