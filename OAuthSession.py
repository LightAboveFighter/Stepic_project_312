import requests
import json
import yaml

class OAuthSession:

    def __init__(self, client_id, client_secret):
        auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
        resp = requests.post('https://stepik.org/oauth2/token/', data={'grant_type': 'client_credentials'}, auth=auth)
        self.__token = json.loads(resp.text)['access_token']

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
        resp = requests.post('https://stepik.org/oauth2/token/', data={'grant_type': 'client_credentials'}, auth=auth)
        self.__token = json.loads(resp.text)['access_token']

    def headers(self):
        return {'Authorization': 'Bearer '+ self.token()}


class Course:

    def __init__(self, title: str, session: OAuthSession):
        self.session = session
        # id = create_course(title)  Создание экземпляра этого класса равносильно созданию курса
        # id = 196585
        # {
        #     "Course": {
        #         "Title": "Stepic course 2023",
        #         "id": 309485230948,                            Пример структуры курса
        #         "Sections": [
        #             {
        #             "Title": "Module 1",
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
                        "Sections": []
                        }
                    }
    def __is_success__(*r):
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
    
    def save(self):
        title = self.structure["Course"]["Title"]
        file = open(f"{title}.yaml", "x")
        yaml.dump(self.structure, file)

    def create_section(self, title: str, position = -1):
        if position != -1:
            self.structure["Course"]["Sections"].insert(position+1, {"Title": title, "id": None})
        self.structure["Course"]["Sections"].append({"Title": title, "id": None})

    def create_lesson(self, title: str, section_num:int, position = -1):

        if position != -1:
            self.structure["Course"]["Sections"][section_num]["Lessons"].insert(position+1, {"Title": title, "id": None})
        self.structure["Course"]["Sections"][section_num]["Lessons"].append({"Title": title, "id": None})

    # def __send_section__(self, section: int):
    #     title = self.structure["Course"]["Sections"][section]["Title"]
    
    def __send_lesson__(self, section: int, lesson: int):
        title = self.structure["Course"]["Sections"][section]["Lessons"][lesson]["Title"]

        api_url = 'https://stepik.org/api/lessons'
        data = {
            'lesson': {
                'title': title
            }
        }
        # Use POST to create new objects
        r = requests.post(api_url, headers=self.session.headers, json=data)
        lesson_id = r.json()['lessons'][0]['id']

        api_url = 'https://stepik.org/api/units'
        data = {
            "unit": {
                "position": lesson,
                "lesson": lesson_id,
                "section": self.structure["Course"]["Sections"][section]["id"]
            }
        }

        r2 = requests.post(api_url, headers=self.session.headers(), json=data)

        if self.__is_success__(r, 201, r2, 0):     # r.status_code() should be 201 (HTTP Created)
            self.structure["Course"]["Sections"][section]["Lessons"][lesson]["id"] = lesson_id
        return {"Success": self.__is_success__(r, 201, r2, 0), "json": r.text + r2.text}

    # def create_step(self, Step):
    
