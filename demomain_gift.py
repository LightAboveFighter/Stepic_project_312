#!python3
import argparse
import logging

from logs.project_logger import activate_logger
from src.gift.gift_processing import get_gift_dicts
from src.API.Classes import Lesson, Course, Section
from src.API.OAuthSession import OAuthSession


parser = argparse.ArgumentParser(
                    description='Gift demo',
                    epilog='Text at the bottom of help') #FIXME add help

parser.add_argument('-u', '--upload', action='store_true',
                    help="mode for upload lesson")
parser.add_argument('-G', '--GIFT',
                    action='store_true',
                    help='export from GIFT file')
parser.add_argument('--debug', '-d',
                    action='store_true',
                    help='show debug information')
parser.add_argument('--file', '-f',
                    # dest='file', -- only needed if the long form isn't first
                    help='file, that need to be read')
parser.add_argument('--lessonid', '-id',
                    dest='lessonid',
                    help='Lesson id')
parser.add_argument('--title', '-T',
                    dest='title',
                    help='Lesson title')


args = parser.parse_args()
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


