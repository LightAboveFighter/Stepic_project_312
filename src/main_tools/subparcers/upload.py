import argparse

from src.API.OAuthSession import OAuthSession
import src.main_tools.tools as main_tools
from src.API.Classes import Course, Lesson

def upload(options):
    course: Course = main_tools.get_course_from_file(options.course)
    course.save(filename = options.course)
    course.auth(main_tools.get_auth())
    course.send_all()

def add_subcommand(subparsers, parents):
    parser = subparsers.add_parser("upload", parents=[parents], help="upload existing course from Stepik")
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
    parser.set_defaults(func=upload)
