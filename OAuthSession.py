import requests
import json
import yaml

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
    text = r[0].text
    for i in range(2, len(r), 2):
        text += r[i].text

    return {"Success": is_success(*r), "json": text}    

class OAuthSession:

    def __init__(self, client_id, client_secret):
        auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
        resp = requests.post('https://stepik.org/oauth2/token/', data={'grant_type': 'client_credentials'}, auth=auth)
        self.__token = json.loads(resp.text)['access_token']

        next_api = "https://stepik.org/teach/courses"
        r = requests.get(next_api, {'X-CSRFToken': 'Fetch'})
        self.cookie = {"csrftoken": r.cookies["csrftoken"], "sessionid": r.cookies["sessionid"]}

        with open("Client_information.yaml", "w") as file:
            yaml.dump({"client_id": client_id, "client_secret": client_secret}, file)

    @property
    def token(self):
        return self.__token
    
    @token.setter
    def set_token(self):
        file = open("Client_information.yaml", "r")
        data = yaml.safe_load(file)
        client_id = data["client_id"]
        client_secret = data["client_data"]

        auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
        resp = requests.post('https://stepik.org/oauth2/token/', data={'grant_type': 'client_credentials', 'x-csrf-token': 'Fetch'}, auth=auth)
        self.__token = json.loads(resp.text)['access_token']
        print(resp.text)
        print(auth.text)

    def headers(self):
        return {'Authorization': 'Bearer '+ self.token}


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
        title = self.structure["Course"]["Title"]
        file = open(f"{title}.yaml", "x")
        yaml.dump(self.structure, file)

    def __send_course__(self):
        title = self.structure["Course"]["Title"]
        description = self.structure["Course"]["Description"]

        api_url = "https://stepik.org/api/courses"
        data = {
                "course": {
                    "grading_policy_source": "no_deadlines",
                    "course_type": "basic",
                    "description": description,
                    "title": title,
                    }
                }
        head = self.session.headers()
        head["X-CSRFToken"] = self.session.cookie["csrftoken"]
        print(head)
        print(self.session.cookie)
        r = requests.post(api_url, head, json=data, cookies=self.session.cookie)

        if is_success(r, 201):
            id = r.json()["enrollments"]["id"]
            self.structure["Course"]["id"] = id
        # return {"Success": self.is_success(r, 201), "json": r.text}
        return request_status(r, 201)

    def create_section(self, title: str, position = -1):
        if position != -1:
            self.structure["Course"]["Sections"].insert(position+1, {"Title": title, "id": None, "Lessons": []})
        self.structure["Course"]["Sections"].append({"Title": title, "id": None, "Lessons": []})

    def __send_section__(self, position: int):
        course = self.structure["Course"]
        course_id = course["id"]
        description = course["Sections"][position]["id"]
        title = course["Sections"][position]["Title"]

        api_url = "https://stepik.org/api/sections"
        data = {
                    "section": {
                        "position": position+1,
                        "title": title,
                        "description": description,
                        "course": course_id
                    }
                }
        print(data)
        r = requests.post(api_url, self.session.headers(), json=data, )

        if is_success(r, 201):
            self.structure["Course"]["Sections"][position]["id"] = r.json()["sections"]["id"]
        # return {"Success": self.is_success(r, 201), "json": r.text}
        return request_status(r, 201)

    def create_lesson(self, title: str, section_num:int, position = -1):

        if position != -1:
            self.structure["Course"]["Sections"][section_num]["Lessons"].insert(position, {"Title": title, "id": None})
        self.structure["Course"]["Sections"][section_num]["Lessons"].append({"Title": title, "id": None})

    # def __send_section__(self, section: int):
    #     title = self.structure["Course"]["Sections"][section]["Title"]
    
    def __send_lesson__(self, section: int, lesson_pos: int):
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
        print(data)

        r2 = requests.post(api_url, headers=self.session.headers(), json=data)

        if is_success(r, 201, r2, 0):     # r.status_code() should be 201 (HTTP Created)
            
            self.structure["Course"]["Sections"][section]["Lessons"][lesson_pos]["id"] = lesson_id
        # return {"Success": self.is_success(r, 201, r2, 0), "json": r.text + r2.text}
        return request_status(r, 201, r2, 0)

    # def create_step(self, Step):

    def send_all(self):
        logs = []
        content = self.structure["Course"]
        print(self.session.token)
        # logs.append(self.__send_course__())
        # if not(logs[0]["Success"]): return logs
        print(self.structure["Course"]["id"])
        for i in range(len(content["Sections"])):
            logs.append(self.__send_section__(i))
            if not(logs[-1]["Success"]):
                print(1111)
                return logs
            for j in range(len(content["Sections"][i]["Lessons"])):
                logs.append(self.__send_lesson__(i, j))
                if not(logs[-1]["Success"]): return logs
                # for k in range(content["Section"][i]["Lessons"][j]["Steps"].len()):
                #     self.__send_step__()
        return logs


    def load_from_file(self, filename: str):
        file = open(filename, "r")
        self.structure = yaml.safe_load(file)
        
# c = Course("Py Course", "This is Py description")
# c.create_section("DD section")
# c.create_section("2 obj")
# c.create_section("3333")
# c.create_lesson("Lesson Pypypy", 1)
# c.create_lesson("Ryryry", 1)
# c.create_lesson("pyyyyyyyyyyyy", 0)
# c.create_lesson("1lesson", 2)
# c.create_lesson("2lessson", 2)
# c.create_lesson("3lesson", 2)
# c.create_lesson("4lesson", 2)
# c.create_lesson("5lesson", 2)
# c.save()
                
c = Course("")
c.load_from_file("Py Course.yaml")
c.auth(s)
print(c.send_all())