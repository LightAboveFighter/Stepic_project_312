import argparse

from src.API.OAuthSession import OAuthSession
import src.main_tools.tools as main_tools
from src.API.Classes import Course, Lesson

def load(options):
    course: Course = Course()
    course.auth(OAuthSession())
    course.load_from_net(options.id)
    course.save(filename=options.course)
    
    pass

def add_subcommand(subparsers, parents):
    parser = subparsers.add_parser("load", parents=[parents], help="load existing course from Stepik")
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
        "-i",
        "--id",
        action="store",
        required=True,
        type=int,
        default=None,
        dest="id",
        help="step id to work with",
    )
    parser.set_defaults(func=load)
