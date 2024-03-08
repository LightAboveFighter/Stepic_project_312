from abc import ABC, abstractclassmethod
import yaml
import requests
import OAuthSession as auth
import Mark_requests as mk
import json
import os

class Step(ABC):
    """
    lesson_id: int
    position: int
    (abstract) type_info: Any or tuple(Any)
    """
    def __init__(self, les_id: int, position: int, **type_params):
        self.lesson_id = les_id
        self.pos = position
        self.type_info = type_params

    @abstractclassmethod
    def dict_info():
        pass


class Lesson:

    def __init__(self, title = "", id = None, steps = [], section_ids = [], **params):
        """ **kwargs:
        'section_ids' - [section's id] to tie lesson without 'Course' class
        """
        self.title = title
        self.steps = steps
        self.id = id
        self.sect_ids = section_ids
        self.params = params
        # if kwargs["section_id"]:
        #     self.sect_ids = kwargs["section_id"]
        # else:
        #     self.sect_ids = []

    def dict_info(self):
        ans = { **{"Title": self.title, "id": self.id, "Steps": [], "Sect_ids": self.sect_ids }, **self.params}
        for i in range(len(self.steps)):
            ans["Steps"].append(self.steps[i].dict_info())
        return ans

    def send(self, session: auth.OAuthSession):

        if  self.id is not None:
            return mk.success_status(True, "Already sent")

        api_url = 'https://stepik.org/api/lessons'
        data = {
            'lesson': { **{
                'title': self.title
            }, **self.params }
        }
        r = requests.post(api_url, headers=session.headers(), json=data)
        id = r.json()['lessons'][0]['id']

        if mk.is_success(r, 201):
            self.id = id

        # r.status_code() should be 201 (HTTP Created)
        return mk.request_status(r, 201)

    def delete_network(self, session: auth.OAuthSession, danger = False):
        if danger:
            if self.sect_id:
                raise "Safety delete: can't delete lesson, inside another courses"
        self.__danger_delete_network__(session)

    def __danger_delete_network__(self, session: auth.OAuthSession):

        api_url = f"https://stepik.org/api/lessons/{self.id}"
        r = requests.delete(api_url, headers=session.headers())

        if mk.is_success(r, 204):
            self.sect_ids = []
            self.id = None
        return mk.request_status(r, 204)
    
    def save(self):
        """ Write your lesson to 'Lesson's Title'.yaml """
        title = self.title
        file = ""
        try:
            file = open(f"{title}.yaml", "x")
        except:
            file = open(f"{title}.yaml", "w")

        yaml.dump({"Lesson": self.dict_info() }, file)

    def update(self):
        if os.path.exists(f"{self.title}.yaml"):
            self.save()

    def is_tied(self, sect_id: int):
        return sect_id in self.sect_ids

    def tie(self, sect_id: int, position: int, session: auth.OAuthSession):

        if not self.is_tied(sect_id):
            api_url = 'https://stepik.org/api/units'
            data = {
                "unit": {
                    "position": position,
                    "lesson": self.id,
                    "section": sect_id
                }
            }

            r2 = requests.post(api_url, headers=session.headers(), json=data)
            if mk.is_success(r2, 0):
                self.sect_ids.append(sect_id)
            return mk.request_status(r2, 0)
        return mk.success_status(True, "Already tied")
    
    def load_from_file(self, filename: str):
        data = ""
        with open(filename, "r") as file:
            data = yaml.safe_load(file)
        self.load_from_dict(data)

    def load_from_dict(self, data: dict):
        self.title = data["Title"]
        self.id = data["id"]
        self.sect_ids = data["Sect_ids"]
        self.steps = []
        for i in range(len(data["Steps"])):
            self.steps.append(Step().load_from_dict(data["Steps"][i]))

        data2 = data
        del data2["Title"]
        del data2["id"]
        del data2["Sect_ids"]
        del data2["Steps"]
    

class Section:

    def __init__(self, title = "", position = -1, lessons = [], **params):
        self.title = title
        self.pos = position
        self.lessons = lessons
        self.id = None
        self.params = params

    def dict_info(self):

        ans = { **{"Title": self.title, "id": self.id, "Lessons": []}, **self.params }
        for i in range(len(self.lessons)):
            ans["Lessons"].append(self.lessons[i].dict_info())
        return ans
    
    def save(self):
        """ Write your section to 'Section's Title'.yaml """
        title = self.title
        file = ""
        try:
            file = open(f"{title}.yaml", "x")
        except:
            file = open(f"{title}.yaml", "w")

        yaml.dump({"Section": self.dict_info() }, file)
    
    def update(self):
        if os.path.exists(f"{self.title}.yaml"):
            self.save()

    def delete_network(self, session):
        id = self.id
        if not id == None:
            api_url = f"https://stepik.org/api/sections/{id}"
            r = requests.delete(api_url, headers=session.headers())

            if mk.is_success(r, 204):
                self.id = None
                for i in range(len(self.lessons)):
                    index = self.lessons[i].sect_ids.index(id)
                    self.lessons[i].sect_ids.pop(index)
                self.update()
            return mk.request_status(r, 204)
        return mk.success_status(False, "")
    
    def send(self, course_id: int, session: auth.OAuthSession):

        if self.id is not None:
            skip = True
            for i in range(len(self.lessons)):
                if not self.lessons[i].is_tied(self.id):
                    skip = False
                    break
            if skip:
                return mk.success_status(True, "Already sent") #{"Success": True, "json": {"Status": "Already sent"}}
        else:
            title = self.title

            api_url = "https://stepik.org/api/sections"
            payload = json.dumps( 
                {
                        "section": { **{
                            "position": self.pos,
                            "required_percent": 100,
                            "title": title,
                            # "description": description,
                            "course": course_id
                        }, **self.params }
                    }
            )
            head = session.headers()
            head["Cookie"] = session.cookie

            r = requests.post(api_url, headers=head, data=payload)
            if mk.is_success(r, 201):
                id = json.loads(r.text)["sections"][0]["id"]
                self.id = id
                for i in range(len(self.lessons)):
                    self.lessons[i].tie(self.id, i, session)
            return mk.request_status(r, 201)
        
        for i in len(self.lessons):
            if self.lessons[i].is_tied(self.id):
                self.lessons[i].tie(self.id, i, session)
        # return mk.request_status(r, 201)
        return mk.success_status(True, "Already sent, modify lessons")
    
    def send_lesson(self, les_pos: int, session: auth.OAuthSession):
        self.lessons[les_pos].send(session)
        self.lessons[les_pos].tie(self.id, les_pos, session)

    def delete_local_lesson(self, les_pos: int):
        if self.lessons[les_pos].id is None:
            self.lessons.pop(les_pos)

    def delete_network_lesson(self, les_pos, session: auth.OAuthSession, danger = False):
        self.lessons[les_pos].delete_network(session, danger)

    def load_from_file(self, filename: str):
        data = ""
        with open(filename, "r") as file:
            data = yaml.safe_load(file)
        self.load_from_dict(data)

    def load_from_dict(self, data: dict, pos = -1):
        self.title = data["Title"]
        self.pos = pos
        self.id = data["id"]
        self.lessons = []
        for i in range(len(data["Lessons"])):
            self.lessons.append( Lesson().load_from_dict(data["Lessons"][i]))

        data2 = data
        del data2["Title"]
        del data2["id"]
        del data2["Lessons"]
        self.params = data2
    
class Course:

    def __init__(self, title = "", sections = [], **params):
        self.title = title
        self.id = None
        self.sections = sections
        self.params = params

    def auth(self, s: auth.OAuthSession):
        self.session = s

    def save(self):
        """ Write your course to 'Course's Title'.yaml """
        title = self.title
        file = ""
        try:
            file = open(f"{title}.yaml", "x")
        except:
            file = open(f"{title}.yaml", "w")

        yaml.dump({"Course": self.dict_info() }, file)

    def dict_info(self):
        ans = { **{"Title": self.title, "id": self.id, "Sections": [] }, **self.params }
        for i in range(len(self.sections)):
            ans["Sections"].append( self.sections[i].dict_info() )
        return ans
    
    def create_section(self, section: Section):
        """ insert if position != -1 
            append if position = -1 """
        
        if section.pos != -1:
            self.sections.insert( section.pos, section)
        else:
            self.sections.append( section )
            section.pos = len( self.sections ) - 1
    
    def create_lesson(self, les: Lesson, sect_pos: int, position = -1):
        """ insert if position != -1 
            append if position = -1 """
        
        if position != -1:
            self.sections[sect_pos].lessons.insert( position, les)
        else:
            self.sections[sect_pos].lessons.append( les )

    def delete_local(self):
        self.title = 0
        self.id = None
        self.params = {}
        self.sections = []
        self.save()

    # def delete_network(self):


    def delete_local_section(self, sect_pos: int):
        if self.sections[sect_pos].id is None:
            self.sections.pop(sect_pos)

    def delete_network_section(self, sect_pos: int):
        res = self.sections[sect_pos].delete_network(self.session)["Success"]
        if res["Success"]:
            self.delete_section_local(sect_pos)
            self.save()
        return res
    
    def delete_local_lesson(self, sect_pos: int, les_pos: int):
        self.sections[sect_pos].delete_local_lesson(les_pos)
    
    def delete_network_lesson(self, sect_pos: int, les_pos: int, danger = False):
        """ danger - in case you know what are yu doing """
        self.sections[sect_pos].delete_network_lesson(les_pos, self.session, danger)

    def send_all(self):

        self.send_heading()

        for i in range(len(self.sections)):
            self.send_section(i, False)
            for j in range(len(self.sections[i].lessons)):
                self.sections[i].send_lesson(j, self.session)
        self.save()

    def send_heading(self, save = False):

        # if self.structure["Course"]["id"] is not None:
        if self.id is not None:
            return {"Success": True, "json": {"Status": "Already sent"}}

        # title = self.structure["Course"]["Title"]
        title = self.title
        # description = self.structure["Course"]["Description"]

        api_url = "https://stepik.org/api/courses"
        payload = json.dumps( 
            {
                "course": { **{
                    # "grading_policy_source": "no_deadlines",
                    # "course_type": "basic",
                    # "description": description,
                    "title": title,
                    }, **self.params }
                }
        )
        head = self.session.headers()
        head["Cookie"] = self.session.cookie

        r = requests.post(api_url, headers=head, data=payload)

        if mk.is_success(r, 201):
            id = json.loads(r.text)['enrollments'][0]['id']
            # self.structure["Course"]["id"] = id
            self.id = id
        if save: self.save()
        return mk.request_status(r, 201)
    
    def send_section(self, sect_pos: int, save = True):
        self.sections[sect_pos].send(self.id, self.session)
        if save: self.save()

    def send_lesson(self, sect_pos: int, les_pos: int, save = True):
        self.sections[sect_pos].send_lesson(les_pos, self.session)
        if save: self.save()

    def load_from_file(self, filename: str):
        data = ""
        with open(filename, "r") as file:
            data = yaml.safe_load(file)["Course"]
        self.load_from_dict(data)
    
    def load_from_dict(self, data: dict):
        self.title = data["Title"]
        self.id = data["id"]

        self.sections = []
        for i in range(len(data["Sections"])):
            self.sections.append( Section().load_from_dict(data["Sections"][i]))

        del data["Title"]
        del data["Sections"]
        del data["id"]
        self.params = data


    
    # def load_from_file(self, filename: str):
    #     structure = ""
    #     with open(filename, "r") as file:
    #         structure = yaml.safe_load(file)
    #     self.title = structure["Title"]
    #     self.id = structure["id"]
    #     self.sections = []
    #     for i in structure["Sections"]:
    #         self.sections.appe



class Step_text(Step):

    def dict_info(self):
        return self.type_info