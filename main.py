import pytest
import OAuthSession as auth
import Course as co
import Classes
import yaml

""" Для корректной работы моих функций вам нужно создать свое Степик API приложение
    по следующей ссылке: https://stepik.org/oauth2/applications/ (client type = confidential, authorization grant type = client credentials)
    Свой client_id и client_secret нельзя публиковать, поэтому я использовал input()
"""

client_id = input("Client_id: ")           # Для pytest поставьте сюда свой id и secret, но потом не забудьте стереть эти значения
client_secret = input("Client_secret: ")    # OAuthSession создает по заданным id и secret файл с их значениями
                                            # В последующие разы эти значения можно брать оттуда, файл добавлен в .gitignore

# Если какой то из тестов не прошелся - в степике у вас могут оказаться лишние созданные курсы
""" -------------------------------------------------- Tests for correct working  --------------------------------------------------------- """

def test_course():
    title = "Tsrgs"
    descr = "drtdrth"
    c = co.Course(title, descr)
    assert c.structure["Course"]["Title"] == title
    assert c.structure["Course"]["Description"] == descr

def test_create_section():
    c = co.Course("", "")
    for i in range(4):
        c.create_section(str(i))
    for i in range(4):
        assert c.structure["Course"]["Sections"][i]["Title"] == f"{i}"
    c.create_section("8", 2)
    assert c.structure["Course"]["Sections"][3]["Title"] == "8"

def test_create_lesson():
    c = co.Course("", "")
    for i in range(4):
        c.create_section(str(i))
    for i in range(4):
        c.create_lesson(str(i*10), i)
        c.create_lesson(str(i*10 + 1), i)
    for i in range(4):
        assert c.structure["Course"]["Sections"][i]["Lessons"][0]["Title"] == str(i*10)
        assert c.structure["Course"]["Sections"][i]["Lessons"][1]["Title"] == str(i*10 + 1)
    c.create_lesson("50", -1, 1)
    assert c.structure["Course"]["Sections"][3]["Lessons"][1]["Title"] == "50"

def test_save():
    title = "Check file-delete it"
    descr = "rtdrthdtrhd"
    c = co.Course(title, descr)
    for i in range(4):
        c.create_section(str(i))
    for i in range(4):
        c.create_lesson(str(i*10), i)
        c.create_lesson(str(i*10 + 1), i)
    for i in range(4):
        assert c.structure["Course"]["Sections"][i]["Lessons"][0]["Title"] == str(i*10)
        assert c.structure["Course"]["Sections"][i]["Lessons"][1]["Title"] == str(i*10 + 1)
    c.create_lesson("50", -1, 1)
    c.save()
    with open(f"{title}.yaml", "r") as file:
        data = yaml.safe_load(file)
        assert data == c.structure

def test_load_from_file():
    c = co.Course("", "")
    c.load_from_file("Check file-delete it.yaml")
    assert c.structure["Course"]["Sections"][3]["Lessons"][1]["Title"] == "50"
    with open("Check file-delete it.yaml", "r") as file:
        data = yaml.safe_load(file)
        assert data == c.structure

def test_auth():
    s = auth.OAuthSession(client_id, client_secret)
    assert not( s.token == "" )

def test_send_delete_course():
    title = "Check file-delete it"
    descr = "rtdrthdtrhd"
    c = co.Course(title, descr)
    s = auth.OAuthSession(client_id, client_secret)
    c.auth(s)
    assert c.send_all()[0]["Success"] # Sending course
    assert not( c.structure["Course"]["id"] == None)
    assert c.delete_network() == {"Success": True, "json": ""} # Deleting course

def test_send_section():
    title = "Check file-delete it"
    descr = "rtdrthdtrhd"
    c = co.Course(title, descr)
    c.create_section("dhdf")
    s = auth.OAuthSession(client_id, client_secret)
    c.auth(s)
    assert c.send_all()[1]["Success"]
    assert not( c.structure["Course"]["Sections"][0]["id"] == None)
    c.delete_network()

def test_send_lesson():
    title = "Check file-delete it"
    descr = "rtdrthdtrhd"
    c = co.Course(title, descr)
    c.create_section("sgs")
    c.create_lesson("drgrd", 0)
    s = auth.OAuthSession(client_id, client_secret)
    c.auth(s)
    assert c.send_all()[2]["Success"]
    assert not( c.structure["Course"]["Sections"][0]["Lessons"][0]["id"] == None)
    c.delete_network()

""" -------------------------------------------------- Tests for correct working  --------------------------------------------------------- """


print("Hello world!")
