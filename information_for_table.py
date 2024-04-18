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
        self.course_name = ""
        self.class_id = class_id
        self.student_ids = self.get_student_ids()
        self.student_names_and_ids = self.get_names()
        self.course_id = self.get_course_id()

    def get_student_ids(self)->list:
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

    def get_names(self)->dict:
        ''' Creates the list of students' names, connected with ids'''
        api = "https://stepik.org/api/users?"
        for i in self.student_ids:
            api += f'ids%5B%5D={i}&'
        api = api[:-1]
        r = requests.get(api, headers=self.session.headers())
        work = r.json()
        names_and_ids = {}
        for user in work["users"]:
            names_and_ids.update({user["id"]: user["full_name"]})
        return names_and_ids

    def get_course_id(self)->str:
        ''' Finds course_id by class_id'''
        api = f"https://stepik.org/api/classes/{self.class_id}"
        r = requests.get(api, headers=self.session.headers())
        work = r.json()
        return work["classes"][0]["course"]

    def update_info_lessons(self)->list:
        ''' Returns all information about structure of course(sections/lessons/steps) '''
        a = cl.Course()
        yaml_name = f"course_{self.course_id}.yaml"
        if os.path.exists(yaml_name):
            a.load_from_file(yaml_name)
        else:
            a.load_from_net(self.course_id, sourse=False, session=self.session)
            a.save(filename=yaml_name[:-5]) #Саня дописывает ".yaml" сам. Не знаю зачем
        self.course_name = a.title
        d = a.dict_info()
        lessons_ids = []
        for i in d["sections"]:
            one_section_lesson_ids = []
            for j in i["lessons"]:
                one_section_lesson_ids.append(j["id"])
            lessons_ids.append(one_section_lesson_ids)
        return lessons_ids

    def get_table(self)->None:
        ''' Creates a yaml with scores, ids and names for every student '''
        api = f"https://stepik.org/api/course-grades?course={self.course_id}&is_teacher=false&klass={self.class_id}&order=-score%2C-id&page=1&search="
        r = requests.get(api, headers=self.session.headers())
        data = r.json()
        course_grades = data["course-grades"]
        klass_file = []
        for student in course_grades:
            student_in_file = {}
            student_id = student["user"]
            student_in_file["id"] = student_id
            student_in_file["name"] = self.student_names_and_ids.get(student_id)
            for i in student["results"]:
                student_in_file[i] = {"done": student["results"][i]["is_passed"], "score": student["results"][i]["score"]}
            klass_file.append(student_in_file)
        with open(f'klass_{self.class_id}.yaml', "w", encoding='utf-8') as file:
            yaml.dump(klass_file, file, allow_unicode=True, encoding='utf-8')
            
