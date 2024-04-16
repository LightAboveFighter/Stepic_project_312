import src.API.Classes as cl
import src.API.OAuthSession as auth
from src.API.Step import StepChoice as SC

from dataclasses import dataclass, field
import requests
import json
import yaml
import os

@dataclass
class Student:
    id: int
    name: str = ''
    score: int = 0    # возможно захотим хранить все баллы за курс

@dataclass
class Submission:
    score: int = 0
    submission: list[int] = field(default_factory=list)


class Class:
    def __init__(self, class_id, session: auth.OAuthSession):
        self.session = session
        self.class_id = class_id
        self.student_ids = self.get_student_ids()
        self.class_name = self.get_names()
        self.course_id = self.get_course_id()
        self.sections_lessons_steps = self.update_info_lessons()

    def get_student_ids(self):  #creates the list of students' ids 
        """Student list in class class_id."""
        id_list = []
        page = 0
        while True:
            page += 1
            api = f"https://stepik.org/api/students?klass={self.class_id}&page={page}"
            r = requests.get(api, headers=self.session.headers())
            work = r.json()
            for student in work['students']:
                id_list.append(student['user'])
            if not work['meta']['has_next']:
                break
        return id_list

    def get_names(self):    #creates the list of students' names
        api = "https://stepik.org/api/users?"
        for i in self.student_ids:
            api += f'ids%5B%5D={i}&'
        api = api[:-1]
        r = requests.get(api, headers=self.session.headers())
        work = r.json()
        names_list = []
        for user in work["users"]:
            names_list.append(user["full_name"])
        return names_list

    def get_course_id(self):    #finds course_id by class_id
        api = f"https://stepik.org/api/classes/{self.class_id}"
        r = requests.get(api, headers=self.session.headers())
        work = r.json()
        return work["classes"][0]["course"]

    def update_info_lessons(self):  #returns all information about structure of course(sections/lessons/steps)
        a = cl.Course()
        yaml_name = f"{self.course_id}.yaml"
        if os.path.exists(yaml_name):
            a.load_from_file(yaml_name)
        else:
            a.load_from_net(self.course_id, False, self.session)
            a.save(yaml_name)
        d = a.dict_info()
        lessons_ids = []
        for i in d["Sections"]:
            section_ids = []
            for j in i["Lessons"]:
                section_ids.append(j["id"])
            lessons_ids.append(section_ids)
        return lessons_ids

    def get_table(self):    #creates a yaml with scores, ids and names for every student
        api = f"https://stepik.org/api/course-grades?course={self.course_id}&is_teacher=false&klass={self.class_id}&order=-score%2C-id&page=1&search="
        r = requests.get(api, headers=self.session.headers())
        data = r.json()
        course_grades = data["course-grades"]
        klass_file = []
        for student in course_grades:
            student_in_file = {}
            student_id = student["user"]
            number_in_student_list = self.student_ids.index(student_id)
            student_in_file["user"] = student_id
            student_in_file["name"] = self.class_name[number_in_student_list]
            for i in student["results"]:
                student_in_file[i] = student["results"][i]["is_passed"]
            klass_file.append(student_in_file)
        with open("klass.yaml", "w") as file:
            yaml.dump(klass_file, file, allow_unicode=True)
            
your_class_id = 0
t = Class(your_class_id, auth.OAuthSession()) #enter your_class_id and, if you need, args to OAuthSession
t.get_table()