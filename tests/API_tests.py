import pytest
import os
from src.API.OAuthSession import OAuthSession
from src.API.Classes import Lesson
from src.API.Step import *

lesson = None

@pytest.mark.local
def test_lesson_dict():
    global lesson
    title = "Lesson's Title"
    id = 12
    cost = 15
    step_title = "Step's title"
    step_text = "StepText's content"
    steps = [StepText(step_title, body = {"text": step_text}, cost = cost)]
    sect_ids = [123123, 233443]
    lesson = Lesson(title, id, steps, sect_ids)
    right_dict = {
        "title": title,
        "id": id,
        "steps": [
            {
                "title": step_title,
                "id": None,
                "lesson": None,
                "block": {
                    "name": "text",
                    "text": step_text
                },
                "cost": cost
            }
        ],
        "sect_ids": sect_ids
    }
    assert lesson.dict_info() == right_dict
    right_dict["id"] = None
    right_dict["steps"][0]["lesson"] = None
    right_dict["steps"][0]["id"] = None
    right_dict["sect_ids"] = []
    assert lesson.dict_info(copy=True) == right_dict

@pytest.mark.local
def test_save_lesson():
    global lesson

    file1 = "Custom_name_type.txt"
    file2 = "Load_without_ids.png"
    file3 = "Without_ids.cpp"

    lesson.save()
    lesson.save(filename=file1)
    lesson.save(filename=file2)
    lesson.save(filename=file3, copy=True)

    lesson1 = Lesson().load_from_file(f"{lesson.title}.yaml")
    lesson2 = Lesson().load_from_file(file1)
    lesson3 = Lesson().load_from_file(file2, copy=True)
    lesson4 = Lesson().load_from_file(file3)

    assert lesson.dict_info() == lesson1.dict_info()
    assert lesson.dict_info() == lesson2.dict_info()
    assert lesson.dict_info(copy=True) == lesson3.dict_info()
    assert lesson.dict_info(copy=True) == lesson4.dict_info()

    os.remove(f"./{lesson.title}.yaml")
    os.remove(file1)
    os.remove(file2)
    os.remove(file3)

@pytest.mark.network
def test_send_load_lesson():
    global lesson
    title = "Lesson's title"
    id = None
    cost = 15
    step_title = "Step_0"
    step_text = "StepText's content"
    steps = [StepText(step_title, body = {"text": step_text}, cost = cost)]
    sect_ids = [123123, 233443]
    lesson = Lesson(title, id, steps, sect_ids)

    assert lesson.send(OAuthSession()).success

@pytest.mark.network
def test_load_lesson():
    global lesson

    lesson2 = Lesson().load_from_net(lesson.id, OAuthSession(), source = True)

    dict2 = lesson.dict_info()
    dict2["steps"][0]["block"]["source"] = {}
    dict2["steps"][0]["block"]["options"] = {}
    dict2["sect_ids"] = []

    dict2_copy = lesson.dict_info(copy=True)
    dict2_copy["steps"][0]["block"]["source"] = {}
    dict2_copy["steps"][0]["block"]["options"] = {}
    dict2_copy["sect_ids"] = []

    assert lesson2.dict_info(copy = True) == dict2_copy
    assert lesson2.dict_info() == dict2

@pytest.mark.network
def test_load_lesson_no_source():
    global lesson

    lesson2 = Lesson().load_from_net(lesson.id, OAuthSession())

    no_source_dict = lesson.dict_info()
    no_source_dict["steps"] = [ {
        "id": step["id"],
        "__del_status__": None
        }
        for step in no_source_dict["steps"] ]
    
    no_source_dict["sect_ids"] = []
    assert no_source_dict == lesson2.dict_info()

    no_source_dict["steps"] = []
    no_source_dict["id"] = None

    assert no_source_dict == lesson2.dict_info(copy = True)

@pytest.mark.network
def test_delete_lesson():
    global lesson

    assert lesson.__danger_delete_network__(OAuthSession()).success