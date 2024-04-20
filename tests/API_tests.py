import pytest
import yaml
from src.API.OAuthSession import OAuthSession
from src.API.Classes import Course, Section, Lesson
from src.API.Step import *

session = ""
course = ""

"""------------StepText's test------------"""

def create_steptext():
    title = "StepText's title"
    lesson_id = 1234
    body = {"text": "StepText's text"}
    params = {"id": 987, "cost": 100}
    right = {"title": title, "lesson": lesson_id, "block": {**body, "name": "text"}, **params}
    return StepText(title, lesson_id, body, None, params), right

@pytest.mark.local
def test_steptext_create():
    a, right = create_steptext()

    assert right == a.dict_info()
    right["lesson"] = None
    right["id"] = None
    assert right == a.dict_info(copy=True)

@pytest.mark.local
def test_steptext_load_from_dict():
    a, right = create_steptext()
    assert a == StepText().load_from_dict(right)


@pytest.mark.network
def test_auth():
    global session
    session = OAuthSession()
    assert not( session.token == "" )


@pytest.mark.network
def test_full_send_delete_course():
    global session

    title = "Test course's title"
    descr = "Test course's description"
    c = Course(title, description=descr)
    c.auth(session)
    c.send_all() # Sending course
    assert not( c.id == None)
    assert c.delete_network() == {"Success": True, "json": ""} # Deleting course


@pytest.mark.network
def test_send_section():
    global session
    global course

    title = "Test course's title"
    descr = "Test course's description"
    course = Course(title, description=descr)
    course.create_section(Section("Test section's title"))
    course.auth(session)
    course.send_all()
    assert not( course.sections[0].id == None)
    assert course.delete_network_section(0) == {"Success": True, "json": ""}


@pytest.mark.network
def test_send_lesson():
    global session
    global course

    course.create_section(Section("Test section"))
    course.create_lesson(Lesson("Test lesson"), 0)
    course.auth(session)
    course.send_all()
    assert not( course.sections[0].lessons[0].id == None)
    assert course.delete_network_lesson(0, 0) == {"Success": True, "json": ""}