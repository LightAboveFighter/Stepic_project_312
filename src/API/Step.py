import requests
from src.Help_methods import is_success, request_status, success_status
from src.API.OAuthSession import OAuthSession
from abc import ABC, abstractclassmethod
import json
import yaml
from dataclasses import field, dataclass
from typing import Any, Optional
from src.API.Loading_templates import Step_template


def create_any_step(type: str, *args, **kwargs):
    if type == "text":
        return StepText(*args, kwargs)
    if type == "choice":
        return StepChoice( *args, options=[], params=kwargs)   #заглушка 

@dataclass
class Step(ABC):
    """ body - dict of main class parameters 
    example: {'text':  [str],
                'source':  [Any]}
    """
    title: str
    lesson_id: int
    body: dict
    params: Optional[Any] = field(default_factory = dict)
    id = None

    def __post_init__(self):
        self.id = self.params.get("id")

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
        
        r = requests.post(api_url, headers=session.headers(), json=data)

        if is_success(r, 201):
            self.id = json.loads(r.text)["step-sources"][0]["id"]
        return request_status(r, 201)
    
    def save(self):
        optional = self.params
        data = {
                "stepSource": { ** {
                                "block": {
                                    "name": self._type,
                                    **self.body
                                    },
                                "lesson": self.lesson_id,
                                }, **optional }
                }
        title = self.title
        file = ""
        try:
            file = open(f"src/API/{title}.yaml", "x")
        except:
            file = open(f"src/API/{title}.yaml", "w")

        yaml.safe_dump(data, file)
        file.close()

    def load_from_file(self, filename):
        data = ""
        with open(f"src/API/{filename}", "r") as file:
            data = yaml.safe_load(file)
        return self.load_from_dict(data)
    
    def load_from_dict(self, data: dict):
        params = Step_template().dump(data)
        assert self._type == params["block"]["name"]
        self.body = params["block"].copy()
        del params["block"]
        self.params = params

    def get_type(self):
        return self._type

    def dict_info(self):
        ans = { 
            "title": self.title,
            "id": self.id,
            "lesson": self.lesson_id,
            "block": {
                "name": self._type,
                 **self.body
                },
            **self.params 
            }
        return ans
    

@dataclass(init=False)
class StepText(Step):
    _type = "text"
    
    def __post_init__(self):
        if self.body.get("text") is None:
            raise "StepText must contain text field"
        # self.body["text"] = f"<p>{self.body['text']}<p>"


@dataclass
class StepChoice(Step):
    """ body:  Step's body + source: [ {is_correct, text, feedback: Optional }, ...],
        is_multiple_choice """
    
    @dataclass
    class Option:
        is_correct: bool
        text: str
        feedback: str = ""

        def get_option(self):
            return {
                "is_correct": self.is_correct,
                "text": self.text,
                "feedback": self.feedback
                }
        
    title: str
    lesson_id: int
    body: dict
    options: list[Option] = field(default_factory = list)
    params: Optional[dict] = field(default_factory = dict)
    _type = "choice"
    

    def __post_init__(self):
        self.id = self.params.get("id")
        # self.body["text"] = f"<p>{self.body['text']}<p>"
        choices = {
            "is_always_correct": False,
            "sample_size": len(self.options),
            "is_html_enabled": True,
            "is_options_feedback": all([i.get_option()["feedback"] for i in self.options])
            }
        if self.options:
            choices["options"] = [ i.get_option() for i in self.options ]
        else:
            choices["options"] = self.body["source"]["options"]
        for i in choices.keys():
            self.body["source"][i] = choices[i]
