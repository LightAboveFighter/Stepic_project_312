import requests
from src.Help_methods import is_success, request_status, success_status
from src.API.OAuthSession import OAuthSession
from abc import ABC, abstractclassmethod
import json
import yaml
from dataclasses import field, dataclass, asdict
from typing import Any, Optional


def create_any_step(type: str, *args, **kwargs):
    if type == "text":
        return StepText(*args, **kwargs)
    if type == "choice":
        return StepChoice( *args, options=[], **kwargs )


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

    def __post_init__(self):
        self.id = self.params.get("id")

    def send(self, position: int, session):
        api_url = "https://stepik.org/api/step-sources"
        optional = asdict(self.params)
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
        optional = asdict(self.params)
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
    
    @abstractclassmethod
    def set_body(self):
        pass

    def get_type(self):
        return self._type

    def dict_info(self):
        ans = { **{"title": self.title, "id": self.id}, "lesson_id": self.lesson_id, "type": self._type, **self.body, **self.params }
        return ans
    

@dataclass(init=False)
class StepText(Step):
    _type = "text"
    
    def set_body(self):
        if self.body.get("text") is None:
            raise "StepText must contain text field"
        self.body["text"] = f"<p>{self.body['text']}<p>"


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
        self.body["text"] = f"<p>{self.body['text']}<p>"
        choices = {
            "is_always_correct": False,
            "sample_size": len(self.options),
            "is_html_enabled": True,
            "is_options_feedback": all([self.options[i][2] for i in range(len(self.options))])
            }
        if self.options:
            choices["options"] = [ i.get_option() for i in self.options ]
        else:
            choices["options"] = self.body["source"]["options"]
        self.body["source"] = choices
    
    def set_body(self):
        # self._type = "choice"
        # # if self.body.get("source") is None:            // steel without checking
        # #     raise "StepText must contain text field"
        # self.body["text"] = f"<p>{self.body['text']}<p>"
        # self.body["source"]["options"] = [ self.options[i].get_option() for i in range(len(self.options)) ]
        # self.body["source"]["is_multiple_choice"] = self.is_multiple_choice
        # # self.body["sample_size"] = len( self.body["source"]["options"] )
        pass
