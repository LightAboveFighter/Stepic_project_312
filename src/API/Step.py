import requests
from Mark_requests import is_success, request_status, success_status
from src.API.OAuthSession import OAuthSession
from abc import ABC, abstractclassmethod
import json


class Step(ABC):

    __type = None

    """
    lesson_id: int
    position: int
    (abstract) type_info: Any or tuple(Any)
    """
    def __init__(self, les_id: int, **params):
        """ params = {'main option': val, 'params': {...} }"""
        self.lesson_id = les_id
        self.set_params(**params)
        self.id = params.get("id")

    @abstractclassmethod 
    def set_params(self, **type_params):
        """ params = {'main option': val, 'params': {...} }"""
        pass

    @abstractclassmethod 
    def send(self, position: int, session):
        pass

    @abstractclassmethod 
    def get_type(self):
        return self.__type

    def dict_info(self):
        ans = { **{"id": self.id}, "lesson_id": self.lesson_id, "type": self.get_type(), **self.params}
        return ans
    

    
class Step_text(Step):
    __type = "text"

    def get_type(self):
        return self.__type

    def set_params(self, **params):
        if not params.get("text"):
            raise "Step_text must contain text field"
        self.params = params

    def send(self, position: int, session: OAuthSession ):

        api_url = "https://stepik.org/api/step-sources"
        text = self.params["text"]
        optional = self.params
        optional.pop("text")
        data = {
                "stepSource": { ** {
                                "block": {
                                    "name": "text",
                                    "text": f"<p>{text}</p>"
                                    },
                                "lesson": self.lesson_id,
                                "position": position
                                }, **self.params }
                }
        
        r = requests.post(api_url, headers=session.headers(), json=data)

        if is_success(r, 201):
            self.id = json.loads(r.text)["step-sources"][0]["id"]
        return request_status(r, 201)