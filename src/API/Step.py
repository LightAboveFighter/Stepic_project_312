import requests
from src.Help_methods import is_success, request_status
from abc import ABC
import json
import yaml
from dataclasses import field, dataclass
from typing import Any, Optional
from src.API.Loading_templates import Step_template, ChoiceUnique, CodeUnique


def create_any_step(type: str, *args, **kwargs):
    """ Creates needable Step with type
    *args, **kwargs: abstract Step's arguments """

    title, lesson_id, body, unique = ( args[i] if i < len(args) else None for i in range(4) )

    unique = kwargs.get("unique") or unique

    args_corr = (kwargs.get("title") or title, kwargs.get("lesson") or lesson_id, kwargs.get("block") or body)
    kwargs.pop("title", None)
    kwargs.pop("lesson", None)
    kwargs.pop("block", None)
    kwargs.pop("unique", None)

    if type == "choice":
        return StepChoice( *args_corr, StepChoice.Unique(**ChoiceUnique().dump(unique)), kwargs ) 
    if type == "code":
        return StepCode( *args_corr, StepCode.Unique( **CodeUnique().dump(unique)), kwargs )
    
    args_corr = args_corr[ : 3]
    return StepText(*args_corr, params=kwargs)


@dataclass
class Step(ABC):
    """ body - block field of Step's API request
    Unique: StepAnyType.Unique() Can be filled with Loading_templates module
    P.S: id can be set in params """

    title: str
    lesson_id: int
    body: dict
    unique: Any = None
    params: Optional[Any] = field(default_factory = dict)
    id = None

    def __post_init__(self):
        self.id = self.params.get("id")

    def send(self, position: int, session):
        """ Create or update Step on Stepic.org.
        If self.id is None - Step will be created, otherwise it will be updated """

        api_url = "https://stepik.org/api/step-sources"
        if self.params.get("id", False):
            api_url += f"/{self.id}"
        
        optional = self.params
        data = {
                "stepSource": { ** {
                                "block": {
                                    "name": self._type,
                                    **self.body
                                    },
                                "lesson": self.lesson_id,
                                "position": position+1
                                }, **optional }
                }
        
        if self.params.get("id", False):
            r = requests.put(api_url, headers=session.headers(), json=data)
        else:
            r = requests.post(api_url, headers=session.headers(), json=data)

        if is_success(r, 201):
            self.id = json.loads(r.text)["step-sources"][0]["id"]
        return request_status(r, 201)
    
    def save(self, **kwargs):
        """ Save your Step to {Step's name}.yaml in root directory.
        **kwargs: filename: custom file's name, type and path """

        optional = self.params
        data = {
                "stepSource": { ** {
                                "block": {
                                    "name": self._type,
                                    **self.body
                                    },
                                "lesson": self.lesson_id
                                }, **optional }
                }
        if kwargs.get("copy", False):
            data["lesson"] = None
            data["id"] = None

        title = f"{self.title}.yaml" if not kwargs.get("filename", False) else kwargs["filename"]
        with open(title, "w") as file:
            yaml.safe_dump(data, file)

    def load_from_file(self, filename, **kwargs):
        """ Fill all Step's fields with content from file.
        **kwargs: if copy: delete all ids """

        data = ""
        with open(filename, "r") as file:
            data = yaml.safe_load(file)
        return self.load_from_dict(data, **kwargs)
    
    def load_from_dict(self, data: dict, **kwargs):
        """ Fill all Step's fields with content from dictionary.
        **kwargs: if copy: delete all ids """

        params = Step_template().dump(data)
        if kwargs.get("copy", False):
            params["id"] = None
            params["lesson"] = None

        assert self._type == params["block"]["name"]
        del params["block"]["name"]
        self.body = params["block"]
        del params["block"]
        self.params = params

    def get_type(self):
        """ Return Step's type """
        return self._type

    def dict_info(self, **kwargs):
        """ Returns Step in the dictionary view.
        **kwargs: if copy: delete all ids """

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
        if kwargs.get("copy", False):
            ans["id"] = None
            ans["lesson"] = None
        return ans
    

@dataclass()
class StepText(Step):
    """ body - block field of Step's API request
    Unique: StepAnyType.Unique() Can be filled with Loading_templates module
        P.S: id can be set in params """
        
    title: str
    lesson_id: int
    body: dict
    params: Optional[Any] = field(default_factory = dict)
    _type = "text"
    
    def __post_init__(self):
        if self.body.get("text") is None:
            raise "StepText must contain text field"
        # self.body["text"] = f"<p>{self.body['text']}<p>"


@dataclass
class StepChoice(Step):
    """ body - block field of Step's API request body.
    Unique: StepChoice.Unique() Can be filled with Loading_templates.ChoiceUnique()
        P.S: id can be set in params 
    Body can be set as: body["source"]: { [ {is_correct, text, feedback: Optional }, ...], is_multiple_choice }"""
    
    _type = "choice"
    
    @dataclass
    class Unique:
        """ options: [ { is_correct, text, feedback } ]"""

        @dataclass
        class Option:
            text: str
            is_correct: bool = False
            feedback: str = ""
        
            def get_option(self):
                return {
                    "is_correct": self.is_correct,
                    "text": self.text,
                    "feedback": self.feedback
                    }

        preserve_order: bool = False
        options: list[tuple] = field(default_factory= list)

        def __post_init__(self):
            self.options = [ self.Option(*i) if isinstance(i, tuple) else self.Option(**i) for i in self.options  ]

        def get_dict(self):
            return {
                "preserve_order": self.preserve_order,
                "options": [ i.get_option() for i in self.options]
            }

    def __post_init__(self):
        self.id = self.params.get("id")
        source = self.unique.get_dict()
        choices = { **{
            "is_always_correct": False,
            "sample_size": len(self.unique.options),
            "is_html_enabled": True,
            "is_options_feedback": all([i.get_option()["feedback"] for i in self.unique.options]),
            },
             **source,
            }

        for i in choices.keys():
            self.body["source"][i] = choices[i]

class StepCode(Step):
    """ body - block field of Step's API request body.
    Unique: StepCode.Unique() Can be filled with Loading_templates.CodeUnique()
        P.S: id can be set in params 
    Body can be set as: body["source"]: {
        "code": str,
        "execution_time_limit": int,
        "execution_memory_limit": int,
        "templates_data": str,
        "test_cases": [[str]],   
        "samples_count": int,
        "is_time_limit_scaled": bool,
        "test_archive": [],
        "is_memory_limit_scaled": bool,
        "manual_time_limits": [],
        "manual_memory_limits": []
    }"""

    _type = "code"

    @dataclass
    class Unique:

        code: str
        execution_time_limit: int
        execution_memory_limit: int
        templates_data: str
        test_cases: list[list[str]]
        samples_count: int = None          #amount if tests you will show to student
        is_time_limit_scaled: bool = False
        is_memory_limit_scaled: bool = False
        manual_time_limits: list = field(default_factory=list)
        manual_memory_limits: list = field(default_factory=list)

        def __post_init__(self):
            for i in self.test_cases:
                assert len(i) == 2   # TestCase must have two fields: question and answer
            self.samples_count = self.samples_count or len(self.test_cases)

        def get_dict(self):
            return {
                "code": self.code,
                "execution_time_limit": self.execution_time_limit,
                "execution_memory_limit": self.execution_memory_limit,
                "templates_data": self.templates_data,
                "test_cases": self.test_cases,
                "samples_count": self.samples_count,
                "is_time_limit_scaled": self.is_time_limit_scaled,
                "test_archive": [],        #for sending files
                "is_memory_limit_scaled": self.is_memory_limit_scaled,
                "manual_time_limits": self.manual_time_limits,
                "manual_memory_limits": self.manual_memory_limits
            }

    def __post_init__(self):
        self.id = self.params.get("id")
        source = self.unique.get_dict()
        self.body["source"] = source


# @dataclass
# class StepVideo(Step):

#     _type = "video"

#     @dataclass
#     class Unique:

#         @dataclass
#         class Video:
#             filename: str            
#             id: int = None
        
#         video: Video
#         subtitles: dict
#         """format:  ru: 'text', en: 'text', etc."""

#         def get_dict(self):
#             return {
#                 "subtitles":
#             }