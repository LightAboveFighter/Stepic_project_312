import pytest
import yaml
import OAuthSession as auth
import Course as co

session = ""
course = ""

@pytest.mark.local
def test_course():
    global course
    title = "Test course's title"
    descr = "Test course's description"
    c = co.Course(title, descr)
    assert c.structure["Course"]["Title"] == title
    assert c.structure["Course"]["Description"] == descr
    course = c

@pytest.mark.local
def test_create_section():
    global course
    for i in range(4):
        course.create_section(str(i))
    for i in range(4):
        assert course.structure["Course"]["Sections"][i]["Title"] == f"{i}"
    course.create_section("8", 2)
    assert course.structure["Course"]["Sections"][2]["Title"] == "8"


@pytest.mark.local
def test_create_lesson():

    for i in range(4):
        course.create_lesson(str(i*10), i)
        course.create_lesson(str(i*10 + 1), i)
    for i in range(4):
        assert course.structure["Course"]["Sections"][i]["Lessons"][0]["Title"] == str(i*10)
        assert course.structure["Course"]["Sections"][i]["Lessons"][1]["Title"] == str(i*10 + 1)
    course.create_lesson("50", -1, 1)
    assert course.structure["Course"]["Sections"][3]["Lessons"][1]["Title"] == "50"


@pytest.mark.local
def test_save():
    global course
    for i in range(4):
        course.create_section(str(i))
    for i in range(4):
        course.create_lesson(str(i*10), i)
        course.create_lesson(str(i*10 + 1), i)
    for i in range(4):
        assert course.structure["Course"]["Sections"][i]["Lessons"][0]["Title"] == str(i*10)
        assert course.structure["Course"]["Sections"][i]["Lessons"][1]["Title"] == str(i*10 + 1)
    course.create_lesson("50", -1, 1)
    course.save()
    with open(f"{course.structure['Course']['Title']}.yaml", "r") as file:
        data = yaml.safe_load(file)
        assert data == course.structure


@pytest.mark.local
def test_load_from_file():
    c = co.Course("", "")
    c.load_from_file("Test course's title.yaml")
    assert c.structure["Course"]["Sections"][3]["Lessons"][1]["Title"] == "50"
    with open("Test course's title.yaml", "r") as file:
        data = yaml.safe_load(file)
        assert data == c.structure


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
    c = co.Course(title, descr)
    c.auth(session)
    assert c.send_all()[0]["Success"] # Sending course
    assert not( c.structure["Course"]["id"] == None)
    assert c.delete_network_course() == {"Success": True, "json": ""} # Deleting course


@pytest.mark.network
def test_send_section():
    global session
    global course

    title = "Test course's title"
    descr = "Test course's description"
    course = co.Course(title, descr)
    course.create_section("Test section's title")
    course.auth(session)
    assert course.send_all()[1]["Success"]
    assert not( course.structure["Course"]["Sections"][0]["id"] == None)
    assert course.delete_network_section(0) == {"Success": True, "json": ""}


@pytest.mark.network
def test_send_lesson():
    global session
    global course

    course.create_section("Test section")
    course.create_lesson("Test lesson", 0)
    course.auth(session)
    assert course.send_all()[2]["Success"]
    assert not( course.structure["Course"]["Sections"][0]["Lessons"][0]["id"] == None)
    assert course.delete_network_lesson(0, 0) == {"Success": True, "json": ""}