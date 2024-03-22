import requests
from Mark_requests import is_success, request_status, success_status
from src.API.OAuthSession import OAuthSession
from abc import ABC, abstractclassmethod
import json


class Step(ABC):

    """
    lesson_id: int
    position: int
    (abstract) type_info: Any or tuple(Any)
    """
    def __init__(self, les_id: int, id = None, body = {}, **params):
        """ body - dict of main class parameters """
        self.lesson_id = les_id
        self.params = params
        self.body = body
        self.configure()
        self.id = id

    def send(self, position: int, session):
        api_url = "https://stepik.org/api/step-sources"
        optional = self.params
        data = {
                "stepSource": { ** {
                                "block": {
                                    "name": self._type,
                                    **self.body
                                    },
                                "lesson": self.lesson_id,
                                "position": position
                                }, **optional }
                }
        print(data)
        
        r = requests.post(api_url, headers=session.headers(), json=data)

        if is_success(r, 201):
            self.id = json.loads(r.text)["step-sources"][0]["id"]
        return request_status(r, 201)
    
    @abstractclassmethod
    def check_body(self):
        pass

    def get_type(self):
        return self._type

    def dict_info(self):
        ans = { **{"id": self.id},
               "lesson_id": self.lesson_id,
               "type": self._type,
               **self.body,
               **self.params
               }
        return ans
    

    
class Step_text(Step):
    
    def configure(self):
        self._type = "text"
        if self.body.get("text") is None:
            raise "Step_text must contain text field"
        self.body["text"] = f"<p>{self.body['text']}<p>"