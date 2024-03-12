import pytest
import yaml
from src.API.OAuthSession import OAuthSession
from src.API.Classes import Course, Section, Lesson

session = ""
course = ""

@pytest.mark.local
def test_course():
    global course
    title = "Test course's title"
    descr = "Test course's description"
    c = Course(title, description = descr)
    assert c.title == title
    assert c.params["description"] == descr
    course = c

@pytest.mark.local
def test_create_section():
    global course
    for i in range(4):
        course.create_section(Section(str(i)))
    for i in range(4):
        assert course.sections[i].title == f"{i}"
    course.create_section(Section("8", 2))
    assert course.sections[2].title == "8"


@pytest.mark.local
def test_create_lesson():
    global course

    for i in range(5):
        course.create_lesson(Lesson(str(i*10)), i)
        course.create_lesson(Lesson(str(i*10 + 1)), i)
    for i in range(5):
        assert course.sections[i].lessons[0].title == str(i*10)
        assert course.sections[i].lessons[1].title == str(i*10 + 1)
    les_title = "Test insert lesson"
    course.create_lesson(Lesson(les_title), -1, 1)
    assert course.sections[4].lessons[1].title == les_title


@pytest.mark.local
def test_save():
    global course

    course.create_lesson(Lesson("Test file lesson"), -1, 1)
    course.save()
    with open(f"src/API/{course.title}.yaml", "r") as file:
        data = yaml.safe_load(file)
        assert data["Course"] == course.dict_info()


@pytest.mark.local
def test_load_from_file():
    c = Course()
    c.load_from_file("Test course's title.yaml")
    assert c.sections[4].lessons[1].title == "Test file lesson"
    with open("src/API/Test course's title.yaml", "r") as file:
        data = yaml.safe_load(file)
        assert data["Course"] == c.dict_info()


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