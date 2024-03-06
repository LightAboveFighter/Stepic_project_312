import OAuthSession
import yaml
import requests
import json

def is_success(*r):
    """ r - (requests.post object, strict requirment, ...)
    If strict requirment = 0 - every success code will be enough """
    for i in range(1, len(r)+1, 2):
        if r[i] == 0:
            if not(r[i-1]):
                return False
            return True
        if r[i-1].status_code != r[i]:
            return False
    return True

def request_status(*r):
    """ r - (requests.post object, strict requirment, ...)
    If strict requirment = 0 - every success code will be enough 
    Return {"Success": , "json": }"""
    text = r[0].text
    for i in range(2, len(r), 2):
        text += r[i].text

    return {"Success": is_success(*r), "json": text}   

class Course:

    def __init__(self, title = "", description = ""):
                                            # Создание экземпляра этого класса равносильно созданию курса
        # {
        #     "Course": {
        #         "Title": "Stepic course 2023",
        #         "id": 309485230948,                            Пример структуры курса
        #         "Description": "",
        #         "Sections": [
        #             {
        #             "Title": "Module 1",
        #             "id": 6745674674654567467
        #             "Lessons": [
        #                     {
        #                         "Title": "one",
        #                         "id": 1226398,
        #                         "Tied": True 
        #                     },
        #                     {
        #                         "Title": "TITLE",
        #                         "id": 30485038,
        #                         "Tied": True 
        #                     }
        #                 ]
        #             }
        #         ]
        #     }
        # }
        self.structure = {
                    "Course": {
                        "Title": title,
                        "id": None,
                        "Description": description,
                        "Sections": []
                        }
                    }
        
    # def __getitem(self, section_num: int):
    #     return self.structure["Course"]["Sections"][section_num]
    
    # def __getitem(self, section_num: int, lesson_num: int):
    #     return self.structure["Course"]["Sections"][section_num]["Lessons"][lesson_num]
    
    # def __getitem(self, section_num: int, lesson_num: int, step_num: int):
    #     return self.structure["Course"]["Sections"][section_num]["Lessons"][lesson_num]["Steps"][step_num]
        
    def auth(self, s: OAuthSession):
        self.session = s
    
    def save(self):
        """ Write your course to 'Course's Title'.yaml """
        title = self.structure["Course"]["Title"]
        try:
            file = open(f"{title}.yaml", "x")
        except:
            pass
        file = open(f"{title}.yaml", "w")

        yaml.dump(self.structure, file)

    def __send_course__(self):

        if self.structure["Course"]["id"] is not None:
            return {"Success": True, "json": {"Status": "Already sent"}}

        title = self.structure["Course"]["Title"]
        description = self.structure["Course"]["Description"]

        api_url = "https://stepik.org/api/courses"
        payload = json.dumps( 
            {
                "course": {
                    "grading_policy_source": "no_deadlines",
                    "course_type": "basic",
                    "description": description,
                    "title": title,
                    }
                }
        )
        head = self.session.headers()
        head["Cookie"] = self.session.cookie

        r = requests.post(api_url, headers=head, data=payload)

        if is_success(r, 201):
            id = json.loads(r.text)['enrollments'][0]['id']
            self.structure["Course"]["id"] = id
        return request_status(r, 201)

    def create_section(self, title: str, position = -1):
        """ insert if position != -1 
            append if position = -1 """
        
        if position != -1:
            self.structure["Course"]["Sections"].insert(position, {"Title": title, "id": None, "Lessons": []})
        else:
            self.structure["Course"]["Sections"].append({"Title": title, "id": None, "Lessons": []})

    def delete_network_section(self, section_pos: int):
        id = self.structure["Course"]["Sections"][section_pos]["id"]

        api_url = f"https://stepik.org/api/sections/{id}"
        r = requests.delete(api_url, headers=self.session.headers())

        if is_success(r, 204):
            self.structure["Course"]["Sections"][section_pos]["id"] = None
            for i in range( len( self.structure["Course"]["Sections"][section_pos]["Lessons"])):
                self.session["Course"]["Sections"][section_pos]["Lessons"][i]["Tied"] = False
            self.save()
        return request_status(r, 204)

    def __send_section__(self, position: int):

        if self.structure["Course"]["Sections"][position]["id"] is not None:
            return {"Success": True, "json": {"Status": "Already sent"}}

        course = self.structure["Course"]
        course_id = course["id"]
        description = course["Sections"][position]["id"]
        title = course["Sections"][position]["Title"]

        api_url = "https://stepik.org/api/sections"
        payload = json.dumps( 
            {
                    "section": {
                        "position": position+1,
                        "required_percent": 100,
                        "title": title,
                        "description": description,
                        "course": course_id
                    }
                }
        )
        head = self.session.headers()
        head["Cookie"] = self.session.cookie

        r = requests.post(api_url, headers=head, data=payload)

        if is_success(r, 201):
            self.structure["Course"]["Sections"][position]["id"] = json.loads(r.text)["sections"][0]["id"]
        return request_status(r, 201)

    def create_lesson(self, title: str, section_num:int, position = -1):
        """ insert if position != -1 
            append if position = -1 """
        
        if position != -1:
            self.structure["Course"]["Sections"][section_num]["Lessons"].insert(position, {"Title": title, "id": None, "Tied": False})
        else:
            self.structure["Course"]["Sections"][section_num]["Lessons"].append({"Title": title, "id": None, "Tied": False})

    def __tie_lesson__(self, lesson_id: int, section: int, lesson_pos: int):
        api_url = 'https://stepik.org/api/units'
        data = {
            "unit": {
                "position": lesson_pos+1,
                "lesson": lesson_id,
                "section": self.structure["Course"]["Sections"][section]["id"]
            }
        }

        r2 = requests.post(api_url, headers=self.session.headers(), json=data)
        return r2
    
    def __send_lesson__(self, section: int, lesson_pos: int):

        p = self.structure["Course"]["Sections"][section]["Lessons"][lesson_pos]
        if  p["id"] is not None:
            if p["Tied"]:
                return {"Success": True, "json": {"Status": "Already sent"}}
            r = self.__tie_lesson__(p["id"], section, lesson_pos)
            if is_success(r, 0):
                self.structure["Course"]["Sections"][section]["Lessons"][lesson_pos]["Tied"] = True
            return request_status(r, 0)
        
        title = self.structure["Course"]["Sections"][section]["Lessons"][lesson_pos]["Title"]

        api_url = 'https://stepik.org/api/lessons'
        data = {
            'lesson': {
                'title': title
            }
        }
        # Use POST to create new objects
        r = requests.post(api_url, headers=self.session.headers(), json=data)
        lesson_id = r.json()['lessons'][0]['id']

        r2 = self.__tie_lesson__(lesson_id, section, lesson_pos)

        if is_success(r, 201, r2, 0):     # r.status_code() should be 201 (HTTP Created)
            self.structure["Course"]["Sections"][section]["Lessons"][lesson_pos]["Tied"] = True
            self.structure["Course"]["Sections"][section]["Lessons"][lesson_pos]["id"] = lesson_id
        return request_status(r, 201, r2, 0)
    
    def delete_network_lesson(self, section: int, lesson_pos: int):
        lesson_id = self.structure["Course"]["Sections"][section]["Lessons"][lesson_pos]["id"]

        api_url = f"https://stepik.org/api/lessons/{lesson_id}"
        r = requests.delete(api_url, headers=self.session.headers())

        if is_success(r, 204):
            self.structure["Course"]["Sections"][section]["Lessons"][lesson_pos]["Tied"] = False
            self.structure["Course"]["Sections"][section]["Lessons"][lesson_pos]["id"] = None
            self.save()
        return request_status(r, 204)

    # def create_step(self, Step):

    def send_all(self):
        """ Save and send all elems without id to stepik.org
            Return logs """
        self.save()
        logs = []
        content = self.structure["Course"]
        logs.append(self.__send_course__())
        if not(logs[0]["Success"]): 
            self.save()
            return logs
        for i in range(len(content["Sections"])):
            logs.append(self.__send_section__(i))
            if not(logs[-1]["Success"]):
                self.save()
                return logs
            for j in range(len(content["Sections"][i]["Lessons"])):
                logs.append(self.__send_lesson__(i, j))
                if not(logs[-1]["Success"]):
                    self.save()
                    return logs
                # for k in range(content["Section"][i]["Lessons"][j]["Steps"].len()):
                #     self.__send_step__()
        self.save()

        return logs

    def delete_network_course(self):
        id = self.structure["Course"]["id"]
        url = f"https://stepik.org/api/courses/{id}"

        r = requests.delete(url, headers=self.session.headers())

        if is_success(r, 204):
            self.structure["Course"]["id"] = None
            for i in range( len( self.structure["Course"]["Sections"] )):
                self.structure["Course"]["Sections"][i]["id"] = None
                for j in range( len( self.structure["Course"]["Sections"][i]["Lessons"])):
                    self.structure["Course"]["Sections"][i]["Lessons"][j]["Tied"] = False
                    self.save()
        return request_status(r, 204)

    def load_from_file(self, filename: str):
        file = open(filename, "r")
        self.structure = yaml.safe_load(file)

    # def load_from_network(self, course_id: int):
        
    #     api_url = f"https://stepik.org/api/courses/{course_id}"
    #     r = requests.get(api_url, headers=self.session.headers())

    #     data5 = json.loads(r.text)
    #     local = {"Course": {"Title": None, "Description": None, "id": course_id, "Sections": []} }
    #     section_ids = data["courses"]["sections"]
    #     for i in range(len(section_ids)):
    #         local["Course"]["Sections"][i]["id"] = section_ids[i]
        
