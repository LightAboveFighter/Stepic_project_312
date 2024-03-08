import pytest
import yaml
import OAuthSession as auth
import Classes as cl

session = ""
course = ""

@pytest.mark.local
def test_course():
    global course
    title = "Test course's title"
    descr = "Test course's description"
    c = cl.Course(title, description = descr)
    assert c.title == title
    assert c.params["description"] == descr
    course = c

@pytest.mark.local
def test_create_section():
    global course
    for i in range(4):
        course.create_section(cl.Section(str(i)))
    for i in range(4):
        assert course.sections[i].title == f"{i}"
    course.create_section(cl.Section("8", 2))
    assert course.sections[2].title == "8"


@pytest.mark.local
def test_create_lesson():
    global course

    for i in range(5):
        course.create_lesson(cl.Lesson(str(i*10)), i)
        course.create_lesson(cl.Lesson(str(i*10 + 1)), i)
    for i in range(5):
        assert course.sections[i].lessons[0].title == str(i*10)
        assert course.sections[i].lessons[1].title == str(i*10 + 1)
    les_title = "Test insert lesson"
    course.create_lesson(cl.Lesson(les_title), -1, 1)
    assert course.sections[4].lessons[1].title == les_title


@pytest.mark.local
def test_save():
    global course

    course.create_lesson(cl.Lesson("Test file lesson"), -1, 1)
    course.save()
    with open(f"{course.title}.yaml", "r") as file:
        data = yaml.safe_load(file)
        assert data["Course"] == course.dict_info()


@pytest.mark.local
def test_load_from_file():
    c = cl.Course()
    c.load_from_file("Test course's title.yaml")
    assert c.sections[4].lessons[1].title == "Test file lesson"
    with open("Test course's title.yaml", "r") as file:
        data = yaml.safe_load(file)
        assert data == c.dict_info()


@pytest.mark.network
def test_auth():
    global session
    session = auth.OAuthSession()
    assert not( session.token == "" )


@pytest.mark.network
def test_full_send_delete_course():
    global session

    title = "Test course's title"
    descr = "Test course's description"
    c = cl.Course(title, descr)
    c.auth(session)
    assert c.send_all()[0]["Success"] # Sending course
    assert not( c.id == None)
    assert c.delete_network_course() == {"Success": True, "json": ""} # Deleting course


@pytest.mark.network
def test_send_section():
    global session
    global course

    title = "Test course's title"
    descr = "Test course's description"
    course = cl.Course(title, descr)
    course.create_section(cl.Section("Test section's title"))
    course.auth(session)
    assert course.send_all()[1]["Success"]
    assert not( course.structure["Course"]["Sections"][0]["id"] == None)
    assert course.delete_network_section(0) == {"Success": True, "json": ""}


@pytest.mark.network
def test_send_lesson():
    global session
    global course

    course.create_section(cl.Section("Test section"))
    course.create_lesson("Test lesson", 0)
    course.auth(session)
    assert course.send_all()[2]["Success"]
    assert not( course.sections[0].lesson[0].id == None)
    assert course.delete_network_lesson(0, 0) == {"Success": True, "json": ""}