import requests
from src.Help_methods import is_success, request_status
from abc import ABC
import json
import yaml
from src.markdown.data_steps import *
# from src.API.Classes import State
from src.API.OAuthSession import OAuthSession
from dataclasses import field, dataclass
from typing import Any, Optional
from src.API.Loading_templates import Step_template, ChoiceUnique, CodeUnique

def create_any_step(type: str, *args, **kwargs):
    """ Creates needable Step with type
    + *args, **kwargs: abstract Step's arguments """

    title, lesson_id, body, unique = ( args[i] if i < len(args) else None for i in range(4) )

    unique = kwargs.get("unique") or unique

    args_corr = (kwargs.get("title") or title, kwargs.get("lesson") or lesson_id, kwargs.get("block") or body)
    kwargs.pop("title", None)
    kwargs.pop("lesson", None)
    kwargs.pop("block", None)
    kwargs.pop("unique", None)
    kwargs.pop("position", None)

    if type == "choice":
        return StepChoice( *args_corr, StepChoice.Unique(**ChoiceUnique().dump(unique)), **kwargs ) 
    if type == "code":
        return StepCode( *args_corr, StepCode.Unique( **CodeUnique().dump(unique)), **kwargs )
    
    args_corr = args_corr[ : 3]
    return StepText(*args_corr, None, **kwargs)

def load_any_step(id: int, session: OAuthSession):

    api_url = f"https://stepik.org/api/step-sources?ids[]={id}"

    r = requests.get(api_url, headers=session.headers())

    if is_success(r, 0):
        content = json.loads(r.text)["step-sources"][0]
        type = content["block"]["name"]
        unique = content["block"].get("source", {})
        return create_any_step(type, **content, unique=unique)
    return StepText(body={"text": "Empty step"})



@dataclass(repr = True)
class Step(ABC):
    """ body - block field of Step's API request
    Unique: StepAnyType.Unique() Can be filled with Loading_templates module
    + P.S: id can be set in params """

    # title: str = ""
    # lesson_id: int = None
    # body: dict = None
    # unique: Any = None
    # params: Optional[Any] = field(default_factory = dict)
    # id: int = None

    def __init__(self, title: str = "", lesson_id: int = None, body: dict = None, unique: Any = None, **params):
        self.title = title
        self.lesson_id = lesson_id
        self.body = body or {}
        self.unique = unique
        self.params = params
        self.id = None
        if self.params.get("id", False):
            self.id = params["id"]
            del self.params["id"]

    # def __post_init__(self, a, b, c, d, e):
    #     self.id = None
    #     if self.params:
    #         self.id = self.params.get("id", None)
    #         del self.params["id"]

    def send(self, position: int, session: OAuthSession, lesson_id: int = None):
        """ Create/update/delete Step on Stepic.org.
        + If self.id is None - Step will be created, otherwise it will be updated
        + Given lesson_id will be written to self.lesson_id """

        if lesson_id:
            self.lesson_id = lesson_id if not self.params.get("__del_status__", False) else None

        if self.params.get("__del_status__", False):
            del self.params["__del_status__"]
            return self.delete_network(session)

        api_url = "https://stepik.org/api/step-sources"
        if self.id:
            api_url += f"/{self.id}"
        optional = self.params
        data = {
                "stepSource": {
                                "block": {
                                    "name": self._type,
                                    **self.body
                                    },
                                "lesson": self.lesson_id,
                                "position": position+1,
                                **optional
                                }
                }
        
        if self.id:
            r = requests.put(api_url, headers=session.headers(), json=data)
        else:
            r = requests.post(api_url, headers=session.headers(), json=data)
        if is_success(r, 0):
            self.id = json.loads(r.text)["step-sources"][0]["id"]
        return request_status(r, 201)
    
    def delete_network(self, session: OAuthSession):
        """ Delete Step from network """

        api_url = f"https://stepik.org/api/step-sources/{self.id}"

        r = requests.delete(api_url, headers=session.headers())
        if is_success(r, 204):
            self.id = None
        return request_status(r, 204)
    
    def save(self, **kwargs):
        """ Save your Step to {Step's name}.yaml in root directory.
        + **kwargs: filename: custom file's name, type and path """

        optional = self.params
        data = {
                "stepSource": {
                                "block": {
                                    "name": self._type,
                                    **self.body
                                    },
                                "lesson": self.lesson_id,
                                "id": self.id,
                                **optional 
                                }
                }
        if kwargs.get("copy", False):
            data["lesson"] = None
            data["id"] = None

        title = f"{self.title}.yaml" if not kwargs.get("filename", False) else kwargs["filename"]
        with open(title, "w") as file:
            yaml.dump(data, file, sort_keys=False)

    def load_from_file(self, filename, **kwargs):
        """ Fill all Step's fields with content from file.
        + **kwargs: if copy: delete all ids """

        data = ""
        with open(filename, "r") as file:
            data = yaml.safe_load(file)
        return self.load_from_dict(data, **kwargs)
    
    def load_from_parse():
        pass
    
    def load_from_dict(self, data: dict, **kwargs):
        """ Fill all Step's fields with content from dictionary.
        + **kwargs: if copy: delete all ids """

        params = Step_template().dump(data)
        if kwargs.get("copy", False):
            params["id"] = None
            params["lesson"] = None

        assert self._type == params["block"]["name"]
        del params["block"]["name"]
        self.title = data["title"]
        self.id = params["id"]
        self.body = params["block"]
        del params["block"]
        del params["id"]
        self.params = params
        return self

    def get_type(self):
        """ Return Step's type """
        return self._type

    def dict_info(self, **kwargs):
        """ Returns Step in the dictionary view.
        + **kwargs: if copy: delete all ids """

        params = self.params
        if params.get("__del_status__", False):
            params["__del_status__"] = "STRICT_DELETE"
        

        ans = { 
            "title": self.title,
            "id": self.id,
            "lesson": self.lesson_id,
            "block": {
                "name": self._type,
                 **self.body
                },
            **params 
            }
        
        if kwargs.get("copy", False):
            ans["id"] = None
            ans["lesson"] = None
        return ans
    

@dataclass
class StepText(Step):
    """ body - block field of Step's API request
    Unique: None
    + P.S: id can be set in params """
        
    def __init__(self, *args, **kwargs):
        self._type = "text"
        super().__init__(*args, **kwargs)

    def load_from_parse(self, step: DataStepText):
        self.body["text"] = step.text
    
    # def __post_init__(self):
    #     if self.body:
    #         if self.body.get("text") is None:
    #             raise "StepText must contain text field"


@dataclass
class StepChoice(Step):
    """ body - block field of Step's API request body.
    Unique: StepChoice.Unique() Can be filled with Loading_templates.ChoiceUnique()
    + P.S: id can be set in params 
    + Body can be set as: body["source"]: { [ {is_correct, text, feedback: Optional }, ...], is_multiple_choice }"""
    
    def __init__(self, *args, **kwargs):
        self._type = "choice"
        super().__init__(*args, **kwargs)
        source = self.unique.get_dict()
        choices = {
            "is_always_correct": False,
            "sample_size": len(self.unique.options),
            "is_html_enabled": True,
            "is_options_feedback": all([i.get_option()["feedback"] for i in self.unique.options]),
            **source,
            }
        self.body["source"] = self.body.get("source", {})
        for i in choices.keys():
            self.body["source"][i] = choices[i]
    
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

        # preserve_order: bool = False
        # options: list[tuple] = field(default_factory = list)

        def __init__(self, preserve_order: bool = False, options: list[tuple] = None):
            self.preserve_order = preserve_order
            self.options = options or []
            self.options = [ self.Option(*i) if isinstance(i, tuple) else self.Option(**i) for i in self.options  ]

        # def __post_init__(self):
        #     self.options = [ self.Option(*i) if isinstance(i, tuple) else self.Option(**i) for i in self.options  ]

        def get_dict(self):
            return {
                "preserve_order": self.preserve_order,
                "options": [ i.get_option() for i in self.options]
            }
        

    def load_from_parse(self, step: DataStepChoice):
        self.body["text"] = step.text
        self.unique = self.Unique(step.step_addons["SHUFFLE"] != "true",
                                  [ (option.text, option.is_correct, option.feedback) for option in step.variants]
                                  )
        self.title = step.step_name


    # def __post_init__(self):
        # self.id = self.params.get("id")
        # source = self.unique.get_dict()
        # choices = { **{
        #     "is_always_correct": False,
        #     "sample_size": len(self.unique.options),
        #     "is_html_enabled": True,
        #     "is_options_feedback": all([i.get_option()["feedback"] for i in self.unique.options]),
        #     },
        #      **source,
        #     }

        # for i in choices.keys():
        #     self.body["source"][i] = choices[i]

@dataclass
class StepCode(Step):
    """ body - block field of Step's API request body.
    Unique: StepCode.Unique() Can be filled with Loading_templates.CodeUnique()
    + P.S: id can be set in params 
    + Body can be set as: body["source"]: {
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

    def __init__(self, *args, **kwargs):
        self._type = "code"
        super().__init__(*args, **kwargs)
        source = self.unique.get_dict()
        self.body["source"] = source

    @dataclass
    class Unique:

        # code: str
        # execution_time_limit: int
        # execution_memory_limit: int
        # templates_data: str
        # test_cases: list[list[str]]
        # samples_count: int = None          #amount if tests you will show to student
        # is_time_limit_scaled: bool = False
        # is_memory_limit_scaled: bool = False
        # manual_time_limits: list = field(default_factory=list)
        # manual_memory_limits: list = field(default_factory=list)

        def __init__(self, code: str,
                    execution_time_limit: int,
                    execution_memory_limit: int,
                    templates_data: str,
                    test_cases: list[list[str]],
                    samples_count: int = None,
                    is_time_limit_scaled: bool = False,
                    is_memory_limit_scaled: bool = False,
                    manual_time_limits: list = None,
                    manual_memory_limits: list = None):
            self.code = code
            self.execution_time_limit = execution_time_limit
            self.execution_memory_limit = execution_memory_limit
            self.templates_data = templates_data
            self.test_cases = test_cases
            self.samples_count = samples_count
            self.is_time_limit_scaled = is_time_limit_scaled
            self.is_memory_limit_scaled = is_memory_limit_scaled
            self.manual_time_limits = manual_time_limits or []
            self.manual_memory_limits = manual_memory_limits or []
            for i in self.test_cases:
                assert len(i) == 2   # TestCase must have two fields: question and answer
            self.samples_count = self.samples_count or len(self.test_cases)

        # def __post_init__(self):
        #     for i in self.test_cases:
        #         assert len(i) == 2   # TestCase must have two fields: question and answer
        #     self.samples_count = self.samples_count or len(self.test_cases)

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
        
    def load_from_parse(self, step: DataStepTaskinline):
        self.body["text"] = step.text
        self.unique = self.Unique(step.code, None, None, "", [ [input, output] for input, output in zip(step.inputs, step.outputs) ], None, None,
                                  False, [], []
                                  )
        self.title = step.step_name

    # def __post_init__(self):
        # self.id = self.params.get("id")
        # source = self.unique.get_dict()
        # self.body["source"] = source