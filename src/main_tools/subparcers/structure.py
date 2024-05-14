
import argparse

import src.main_tools.tools as main_tools
from src.API.Classes import Course, Lesson

def structure(options):
    course: Course = main_tools.get_course_from_file(options.course)
    main_tools.print_tree(course, show_steps=True)
    # if options.lesson is not None:
    #     main_tools.print_tree(course.lesson[options.lesson], show_steps=True)
    # else:
    #     main_tools.print_tree(course)

    

def add_subcommand(subparsers, parents):
    parser = subparsers.add_parser("struc", parents=[parents], help="Update(by replace) an existing lesson or step")
    parser.add_argument(
        "-C",
        "--course",
        required=True,
        action="store",
        default=None,
        dest="course",
        help="course file",
    )
    # parser.add_argument(
    #     "-L",
    #     "--lesson_id",
    #     type=int,
    #     action="store",
    #     default=None,
    #     dest="lesson",
    #     help="lesson id to work with" 
    # )
    parser.set_defaults(func=structure)
