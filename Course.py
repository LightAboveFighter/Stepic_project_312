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

    def __init__(self, title: str, description = ""):
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
        #                         "id": 1226398
        #                     },
        #                     {
        #                         "Title": "TITLE",
        #                         "id": 30485038
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
            self.structure["Course"]["Sections"].insert(position+1, {"Title": title, "id": None, "Lessons": []})
        self.structure["Course"]["Sections"].append({"Title": title, "id": None, "Lessons": []})

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
        print(head)
        print(self.session.cookie)
        r = requests.post(api_url, headers=head, data=payload)

        if is_success(r, 201):
            self.structure["Course"]["Sections"][position]["id"] = json.loads(r.text)["sections"][0]["id"]
        return request_status(r, 201)

    def create_lesson(self, title: str, section_num:int, position = -1):
        """ insert if position != -1 
            append if position = -1 """
        
        if position != -1:
            self.structure["Course"]["Sections"][section_num]["Lessons"].insert(position, {"Title": title, "id": None})
        self.structure["Course"]["Sections"][section_num]["Lessons"].append({"Title": title, "id": None})
    
    def __send_lesson__(self, section: int, lesson_pos: int):

        if self.structure["Course"]["Sections"][section]["Lessons"][lesson_pos]["id"] is not None:
            return {"Success": True, "json": {"Status": "Already sent"}}
        
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

        api_url = 'https://stepik.org/api/units'
        data = {
            "unit": {
                "position": lesson_pos+1,
                "lesson": lesson_id,
                "section": self.structure["Course"]["Sections"][section]["id"]
            }
        }

        r2 = requests.post(api_url, headers=self.session.headers(), json=data)

        if is_success(r, 201, r2, 0):     # r.status_code() should be 201 (HTTP Created)
            self.structure["Course"]["Sections"][section]["Lessons"][lesson_pos]["id"] = lesson_id
        return request_status(r, 201, r2, 0)

    # def create_step(self, Step):

    def send_all(self):
        """ Save and send all elems without id to stepik.org
            Return logs """
        self.save()
        logs = []
        content = self.structure["Course"]
        logs.append(self.__send_course__())
        if not(logs[0]["Success"]): return logs
        print(self.structure["Course"]["id"])
        for i in range(len(content["Sections"])):
            logs.append(self.__send_section__(i))
            if not(logs[-1]["Success"]):
                return logs
            for j in range(len(content["Sections"][i]["Lessons"])):
                logs.append(self.__send_lesson__(i, j))
                if not(logs[-1]["Success"]): return logs
                # for k in range(content["Section"][i]["Lessons"][j]["Steps"].len()):
                #     self.__send_step__()
        return logs

    def delete_network(self):
        id = self.structure["Course"]["id"]
        url = f"https://stepik.org/api/courses/{id}"

        r = requests.delete(url, headers=self.session.headers())
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
        
