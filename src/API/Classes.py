import yaml
import requests
from src.API.OAuthSession import OAuthSession
from src.Help_methods import *
import os
from enum import Enum
from src.API.Step import StepText, Step, create_any_step, load_any_step
import pyparsing as pp
import io
from dataclasses import dataclass
from transliterate import translit
from transliterate.exceptions import LanguageDetectionError
from src.API.Loading_templates import Step_template, Lesson_template, Section_template, \
    Course_template, Lesson_template_source
from pathlib import Path, PurePath


class State(Enum):
    STRICT_DELETE = 1
    REMOVE = 2


class Lesson:

    def __init__(self, title: str = "", id: int = None, steps: list[Step] = None, section_ids: list[int] = None, **params):
        """ section_ids - list of courses' ids, that own the Lesson """
        self.title = title
        self.steps = steps or []
        self.id = id
        self.sect_ids = section_ids or []
        self.params = params

    def _module_step(self):
        step_type = pp.one_of(['QUIZ', 'CHOICE', 'TEXT'], as_keyword=True) ('type')
        step_name = pp.rest_of_line() ('name')
        parse_module = pp.Suppress(pp.Keyword('##')) + pp.Optional(step_type) + pp.Suppress(pp.ZeroOrMore(pp.White())) + pp.Optional(step_name)
        return parse_module

    def dict_info(self, **kwargs) -> dict:
        """ Returns Lesson in the dictionary view.
        + **kwargs: if copy: delete all ids """

        copy = kwargs.get("copy", False)
        if copy and isinstance(self.steps[0], dict):
            steps = []
        else:
            steps = [ 
                (
                    {
                    "id": step["id"],
                    "__del_status__": "STRICT_DELETE" if step.get("__del_status__", False) == State.STRICT_DELETE else None
                    }
                ) if isinstance(step, dict) else step.dict_info(copy=copy) for step in self.steps
            ]
        
        id = self.id if not copy else None
        sect_ids = self.sect_ids if not copy else []
        params = self.params
        if params.get("__del_status__", False):
            params["__del_status__"] = "STRICT_DELETE" if params["__del_status__"] == State.STRICT_DELETE else "REMOVE"

        ans = { "title": self.title, "id": id, "steps": steps, "sect_ids": sect_ids, **params}
        return ans
    
    def get_structure(self, **kwargs) -> dict:
        """ Returns Lesson in the dictionary view without most of fields
        + **kwargs: if copy: delete all ids """

        copy = kwargs.get("copy", False)
        id = self.id if not copy else None
        ans = {"id": id, "steps": []}
        if not copy:
            for step in self.steps:
                ans["steps"].append(step["id"] if isinstance(step, dict) else step.id)
        return ans

    def send(self, session: OAuthSession) -> RequestStatus:
        """ Create or update Lesson on Stepic.org.
        + If self.id is None - Lesson will be created, otherwise it will be updated
        The same applies to objects inside. """

        if self.params.get("__del_status__", False):
            if self.params.get("__del_status__", False) == State.STRICT_DELETE:
                del self.params["__del_status__"]
                return self.delete_network(session, False)
            del self.params["__del_status__"]

        api_url = 'https://stepik.org/api/lessons'
        if  self.id:
            api_url += f"/{self.id}"

        data = {
            'lesson': { **{
                'title': self.title,
                'id': self.id,
                "steps": [ step["id"] if isinstance(step, dict) else step.id for step in self.steps ]
            }, **self.params }
        }

        if self.id:
            r = requests.put(api_url, headers=session.headers(), json=data)
        else:
            r = requests.post(api_url, headers=session.headers(), json=data)
        id = r.json()['lessons'][0]['id']

        test_dict = self.get_structure()
        test_dict["title"] = self.title
        r_dict = Lesson_template().dump(r.json()["lessons"][0])
        del r_dict["courses"]
        repeating = ( r_dict == test_dict )

        if is_success(r, 0) or repeating:
            self.id = id
            steps = []
            for i in range(len(self.steps)):

                if isinstance(self.steps[0], dict):
                    if self.steps[i].get("__del_status__", False) != State.STRICT_DELETE:
                        steps.append(self.steps[i])
                        stat = load_any_step(self.steps[i]["id"], session).send(i, session, self.id)
                        if not stat.success:
                            return stat
                        continue
                    del_stat = StepText(id=self.steps[i]["id"]).delete_network(session)
                    if not del_stat.success:
                        return del_stat

                else:
                    if not self.steps[i].params.get("__del_status__", False):
                        steps.append(self.steps[i])
                    stat = self.steps[i].send(i, session, self.id)
                    if not stat.success:
                        return stat
            self.steps = steps
        if repeating:
            return success_status(True, r.text)
        return request_status(r, 201)
    
    def add_step(self, step: Step, position: int = -1):
        """ Add Step to your Lesson.
        + position:
            if -1:
                append to Lesson's steps
            else:
                insert into Lesson's steps"""

        if position == -1:
            self.steps.append(step)
        else:
            self.steps.insert(position, step)
    
    def delete_step(self, step_pos: int):
        """ Mark to remove in network (Remove Step from Lesson after self.send()) """

        if isinstance(self.steps[step_pos], Step):
            self.steps[step_pos].params["__del_status__"] = State.STRICT_DELETE
            return
        self.steps[step_pos]["__del_status__"] = State.STRICT_DELETE


    def delete_network(self, session: OAuthSession, sect_ids: list[int] = None, danger = False) -> RequestStatus:
        """ Delete your Lesson from Stepic.org. 
        + sect_ids: list of sections, from where Lesson can be deleted
        + if danger: delete Lesson even if it's part of any courses """

        if not danger:
            ids = self.sect_ids
            ok = True
            if sect_ids:
                try:
                    ok = all([ sect_ids.index(id) for id in ids ])
                except ValueError:
                    ok = len(sect_ids) >= len(ids)
            if self.sect_ids and ok:
                raise "Safety delete: can't delete lesson, inside another courses"
        return self.__danger_delete_network__(session)

    def __danger_delete_network__(self, session: OAuthSession) -> RequestStatus:
        """ Delete your Lesson from Stepic.org without any checkings """

        api_url = f"https://stepik.org/api/lessons/{self.id}"
        r = requests.delete(api_url, headers=session.headers())

        if is_success(r, 204):
            self.sect_ids = []
            self.id = None
            if not isinstance(self.steps[0], dict):
                for step in self.steps:
                    step.id = None
                    step.lesson_id = None
        return request_status(r, 204)
    
    def save(self, path: str = None, **kwargs):
        """ Write your Lesson to {Lesson's Title}.yaml in root directory.
        + **kwargs: filename - custom file's name, type and path;
            if copy: delete all ids """
        
        content = self.dict_info(copy=kwargs.get("copy", False))

        if not path:
            i = 0
            path = Path(f"Lesson_{i}.yaml")
            while path.exists():
                i += 1
                path = Path(f"Lesson_{i}.yaml")
            with open(path, "w", encoding="utf-8") as file:
                current_path = Path.cwd()
                path = current_path.joinpath(path)
                path = str(path)
                yaml.dump({"Lesson": content }, file, allow_unicode=True, sort_keys=False)
        else:
            path = Path(path)
            if path.suffixes:
                pathdir = path.parent
                pathdir.mkdir(exist_ok=True)
                with open(path, "w", encoding="utf-8") as file:
                    path = str(path)
                    yaml.dump({"Lesson": content }, file, allow_unicode=True, sort_keys=False)
            else:
                try:
                    path.mkdir()
                    path = path.joinpath("Lesson_0.yaml")
                    with open(path, "w", encoding="utf-8") as file:
                        path = str(path)
                        yaml.dump({"Lesson": content }, file, allow_unicode=True, sort_keys=False)
                except FileExistsError:
                    i = 0
                    path = path.joinpath(f"Lesson_{i}.yaml")
                    while path.exists():
                        i += 1
                        path = path.joinpath(f"Lesson_{i}.yaml")
                    with open(path, "w", encoding="utf-8") as file:
                        path = str(path)
                        yaml.dump({"Lesson": content }, file, allow_unicode=True, sort_keys=False)
            


    def is_tied(self, sect_id: int) -> bool:
        """ Check if Lesson is part of some Section -> Course """
        return sect_id in self.sect_ids
    
    def load_from_file(self, filename: str, **kwargs):
        """ Fill all Lesson's fields with content from file.
        + **kwargs: if copy: delete all ids """

        data = ""
        filename = filename.replace(os.getcwd(), "./")
        with open(filename, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)["Lesson"]
        return self.load_from_dict(data, **kwargs)

    def load_from_parse(self, lesson_path: str = ""):

        sect_ids = []
        params = {}
        title = ""
        id = None
        steps = []
        if not lesson_path:
            self.fill_args(title, id, steps, sect_ids, **params)
            return

        name = pp.rest_of_line ('name')
        parse_name = pp.Suppress(pp.Keyword('#') + pp.ZeroOrMore(pp.White())) + pp.Optional(name)

        id = pp.Word(pp.nums) ('id')
        parse_id = pp.Suppress(pp.Keyword('lesson') + pp.ZeroOrMore(pp.White()) + '=' + pp.ZeroOrMore(pp.White())) + id

        parse_step = self._module_step()

        with io.open(f"Input_files/{lesson_path}", 'r', encoding='utf-8') as f:
            # Writting down name of the lesson
            title = (parse_name.parseString(f.readline())).name
            
            # Writting down id of the lesson 
            for id_line in f:
                if id_line != pp.Empty():
                    # self.id = int((parse_id.parseString(id_line)).id)
                    id = None                                      
                    continue
            
            # Writting down steps of the lesson

            step_lines = ""
            first_cycle = True

            for line in f:
                try:
                    new_step = parse_step.parseString(line)
                    if not first_cycle:
                        self.steps.append(StepText(previous_step.name, None, {"text": step_lines} ))  # for now -- only StepText
                    step_lines = ""
                    first_cycle = False
                    previous_step = new_step
                except pp.ParseException:
                    step_lines += line
            steps.append(StepText(previous_step.name, None, {"text": step_lines} ))

    def load_from_dict(self, data: dict, **kwargs):
        """ Fill all Lesson's fields with content from dictionary.
        + **kwargs: if copy: delete all ids """

        copy = kwargs.get("copy", False)
        self.title = data["title"]
        self.id = data["id"] if not copy else None
        self.sect_ids = data["sect_ids"] if not copy else []

        if len(data["steps"][0].keys()) > 2:
            self.steps = []
            for step in data["steps"]:
                if copy:
                    step["id"] = None
                    step["lesson"] = None

                type = step["block"]["name"]
                unique = step["block"].get("source", None)
                st = create_any_step(type, **step, unique=unique)
            
                self.steps.append(st)
        else:
            self.steps = data["steps"] if not copy else []
            self.steps = [ {
                "id": step["id"],
                "__del_status__": State.STRICT_DELETE if (step.get("__del_status__", None) == "STRICT_DELETE") else None
                } for step in self.steps ]

        data2 = data.copy()
        del data2["title"]
        del data2["id"]
        del data2["sect_ids"]
        del data2["steps"]
        try:
            self.params = Lesson_template_source().dump(data2)
        except TypeError:
            self.params = Lesson_template().dump(data2)
        return self
    
    def load_from_net(self, id: int, session: OAuthSession, **kwargs):
        """ Fill all Lesson's fields with content from Stepic.org.
        + **kwargs: if source: load steps's content.
            Without source self.steps will contain only list[int] with steps' ids """

        url = f"https://stepik.org/api/lessons/{id}"

        r = requests.get(url, headers=session.headers())
        if not is_success(r, 0):
            return success_status(False, "Can't get course's head")
        
        if not kwargs.get("sourse", False):
            content = Lesson_template().dump(r.json()["lessons"][0])
        else:
            content = Lesson_template_source().dump(r.json()["lessons"][0])

        self.id = id
        self.title = content["title"]
        self.sect_ids = content["courses"]
        steps_ids = [ {"id": id} for id in content["steps"] ]

        del content["id"]
        del content["title"]
        del content["courses"]
        del content["steps"]

        self.params = content
        if kwargs.get("source", False):
            self.load_steps([step_id["id"] for step_id in steps_ids], session)
        else:
            self.steps = steps_ids
        return self
    
    def load_steps(self, ids: list[int], session: OAuthSession) -> RequestStatus:
        """ Fill self.steps with content from Stepic.org. """

        ids_url = [ str(i) for i in ids]
        ids_url = "&ids[]=".join(ids_url)
        url = f"https://stepik.org/api/step-sources?ids[]=" + ids_url

        r = requests.get(url, headers=session.headers())
        if not is_success(r, 0):
            return request_status(r, 0)
        
        steps = r.json()["step-sources"]
        if not steps:
            self.steps = [ {"id": id} for id in ids ]
            return

        for i in range(len(steps)):
            params = Step_template().dump(steps[i])
            type = params["block"]["name"]
            body = params["block"]
            del body["name"]
            del params["block"]
            params["lesson"] = self.id

            les_id = self.id
            unique = body["source"]
            
            step = create_any_step(type, f"Step_{i}", les_id, body, unique, **params)
            self.steps.append(step)
        return request_status(r, 0)


class Section:
    pass

@dataclass
class Unit:
    section: Section
    lesson: Lesson
    id: int = None

    def send(self, position: int, session: OAuthSession) -> RequestStatus:
        """ Create and tie lesson to section """

        stat = self.lesson.send(session)
        if not stat.success:
            return stat

        if self.lesson.params.get("__del_status__", False):
            return self.delete_network(session)
        
        api_url = 'https://stepik.org/api/units'
        if id:
            api_url += f"/{self.id}"

        data = {    
            "unit": {
                **self.dict_info(position)
            }
        }

        if id:
            r2 = requests.put(api_url, headers=session.headers(), json=data)
        else:
            r2 = requests.post(api_url, headers=session.headers(), json=data)
            
        if is_success(r2, 0):
            self.id = r2.json()["units"][0]["id"]
            self.lesson.sect_ids.append(self.section.id)
        return request_status(r2, 0)
    
    def delete_network(self, session: OAuthSession) -> RequestStatus:
        """ Likewise Lesson.untie from Section"""

        api_url = f"https://stepik.org/api/units/{self.id}"
        r = requests.delete(api_url, headers=session.headers())

        if is_success(r, 204):
            self.id = None
        return request_status(r, 204)

    def dict_info(self, position) -> dict:
        return {
            "section": self.section.id,
            "lesson": self.lesson.id,
            "position": position
        }
    

class Section:

    def __init__(self, title: str = "", lessons: list[Lesson] = None, **params):
        self.title = title
        lessons = lessons or []

        self.id = None
        if params.get("id", False):
            self.id = params["id"]
            del params["id"]
        self.course = None
        if params.get("course", False):
            self.course = params["course"]
            del params["course"]

        self.params = params
        self.units = []
        for lesson in lessons:
            self.add_lesson(lesson)

    def add_lesson(self, lesson: Lesson, position: int = -1):
        """ Add Lesson to your Section.
        + position:
            if -1:
                append to Lesson's steps
            else:
                insert into Lesson's steps"""

        if position == -1:
            self.units.append( Unit(self, lesson, None) )
        else:
            self.units.insert( position, Unit(self, lesson, None) )

    def add_step(self, les_pos: int, step: Step, position: int = -1):
        """ Add Step to your Lesson. les_pos - indexes as at list[].
        + position:
            if -1:
                append to Lesson's steps
            else:
                insert into Lesson's steps"""

        self.units[les_pos].lesson.add_step(step, position)

    def dict_info(self, **kwargs) -> dict:
        """ Returns Section in the dictionary view.
        + **kwargs: if copy: delete all ids
        path - path to saving lessons"""

        copy = kwargs.get("copy", False)
        title = self.title
        id = self.id if not copy else None
        course = self.course if not copy else None
        params = self.params
        if copy:
            params["course"] = None

        if params.get("__del_status__", False):
            params["__del_status__"] = "STRICT_DELETE"

        ans = { "title": title, "id": id, "lessons": [], "course": course, **params }

        for unit in self.units:

            i = 0
            path = Path(f"Lesson_{i}.yaml")
            filename = kwargs.get("path", ".")
            filename = Path(filename).joinpath(str(path))
            while filename.exists():
                i += 1
                filename = filename.with_name(f"Lesson_{i}.yaml")
            
            filename = str(filename)
            unit.lesson.save(path = filename, copy=kwargs.get("copy", False))
            ans["lessons"].append(
                {
                    "id": unit.lesson.id if not copy else None,
                    "title": unit.lesson.title,
                    "file": filename,
                    "unit": unit.id if not copy else None
                }
            )
        return ans
    
    def get_structure(self, **kwargs) -> dict:
        """ Returns Section in the dictionary view without most of fields
        **kwargs: if copy: delete all ids """

        id = self.id if not kwargs.get("copy", False) else None
        ans = {"id": id, "lessons": []}
        for i in self.units:
            ans["lessons"].append(i.lesson.get_structure(**kwargs))
        return ans
    
    def save(self, path: str = None, **kwargs):
        """ Save your Section to {Section's name}.yaml in root directory.
        All Section's lessons will be saved to same directory as {Section's Title}.yaml
        + **kwargs: filename - custom file's name, type and path;
            if copy: delete all ids """
        
        if not path:
            i = 0
            path = Path(f"Section_{i}.yaml")
            while path.exists():
                i += 1
                path = Path(f"Section_{i}.yaml")
            with open(path, "w", encoding="utf-8") as file:
                current_path = Path.cwd()
                path = current_path.joinpath(path)
                path = path.parent
                path = str(path)
                yaml.dump({"Section": self.dict_info(path=path, copy=kwargs.get("copy", False)) }, file, allow_unicode=True, sort_keys=False)
        else:
            path = Path(path)
            if path.suffixes:
                pathdir = path.parent
                pathdir.mkdir(exist_ok=True)
                with open(path, "w", encoding="utf-8") as file:
                    path = path.parent
                    path = str(path)
                    yaml.dump({"Section": self.dict_info(path=path, copy=kwargs.get("copy", False)) }, file, allow_unicode=True, sort_keys=False)
            else:
                try:
                    path.mkdir()
                    path = path.joinpath("Section_0.yaml")
                    with open(path, "w", encoding="utf-8") as file:
                        path = path.parent
                        path = str(path)
                        yaml.dump({"Section": self.dict_info(path=path, copy=kwargs.get("copy", False)) }, file, allow_unicode=True, sort_keys=False)
                except FileExistsError:
                    i = 0
                    path = path.joinpath(f"Section_{i}.yaml")
                    while path.exists():
                        i += 1
                        path = path.parent
                        path = path.joinpath(f"Section_{i}.yaml")
                    with open(path, "w", encoding="utf-8") as file:
                        path = path.parent
                        path = str(path)
                        yaml.dump({"Section": self.dict_info(path=path, copy=kwargs.get("copy", False)) }, file, allow_unicode=True, sort_keys=False)


    def delete_network(self, session: OAuthSession) -> RequestStatus:
        """ Delete your Section from Stepic.org
        + Call save() method after this, to save id!"""
        id = self.id
        if id:
            api_url = f"https://stepik.org/api/sections/{id}"
            r = requests.delete(api_url, headers=session.headers())

            if is_success(r, 204):
                self.id = None
            return request_status(r, 204)
        return success_status(False, "")
    
    def send(self, position: int, session: OAuthSession, course_id: int = None) -> RequestStatus:
        """ Create or update Section on Stepic.org.
        + If self.id is None - Section will be created, otherwise it will be updated
        ( It can be deleted if it was marked before )
        The same applies to objects inside.
        + given course_id will be written to self.course"""

        if course_id:
            self.course = course_id

        if self.params.get("__del_status__", False):
            for unit in self.units:
                unit.lesson.send(session)
            del self.params["__del_status__"]
            return self.delete_network(session)
        api_url = "https://stepik.org/api/sections"
        if self.id:
            api_url += f"/{self.id}"

        data = {
            "section": {
                "position": position + 1,
                "required_percent": 100,
                "title": self.title,
                "id": self.id,
                "course": self.course,
                **self.params
            }
        }

        head = session.headers()
        head["Cookie"] = session.cookie
        if self.id:
            r = requests.put(api_url, headers=head, json=data)
        else:
            r = requests.post(api_url, headers=head, json=data)

        content = r.json()["sections"][0]
        r_dict = Section_template().dump(content)
        test_dict = self.dict_info()
        test_dict["title"] = self.title
        test_dict["course"] = self.course
        del test_dict["lessons"]

        repeating = ( r_dict == test_dict )

        if is_success(r, 0) or repeating:
            id = r.json()["sections"][0]["id"]
            self.id = id
            units = []
            for i in range(len(self.units)):
                if not self.units[i].lesson.params.get("__del_status__", False):
                    units.append(self.units[i])
                stat = self.units[i].send(i, session)
                if not stat.success:
                    return stat
            self.units = units
        if repeating:
            return success_status(True, r.text)
        return request_status(r, 201)

    def remove_lesson(self, les_pos: int):
        """ Mark your Lesson to untie from your Section. It will be removed after send_all() method.
        + Indexes as at list[] 
        + Indexes of next lessons won't change until send() method!"""

        self.units[les_pos].lesson.params["__del_status__"] = State.REMOVE

    def delete_lesson(self, les_pos: int):
        """ Mark your Lesson to DELETE from Stepic.org. It will be deleted after send_all() method.
        + Attention! After send_all() method lesson will be deleted even if it's part of some Courses'
        + Indexes as at list[] 
        + Indexes of next lessons won't change until send() method!""" 

        self.units[les_pos].lesson.params["__del_status__"] = State.STRICT_DELETE

    def delete_step(self, les_pos: int, step_pos: int):
        """ Mark your Step to delete from your Lesson. It will be deleted after send_all() method.
        + Indexes as at list[]
        + Indexes of next steps won't change until send() method!"""

        self.units[les_pos].lesson.delete_step(step_pos)

    def load_from_file(self, filename: str, **kwargs):
        """ Fill all Section's fields with content from file.
        + **kwargs: if copy: delete all ids """

        data = ""
        with open(filename, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)["Section"]
        return self.load_from_dict(data, **kwargs)

    def load_from_dict(self, data: dict, **kwargs):
        """ Fill all Section's fields with content from dictionary.
        + **kwargs: if copy: delete all ids """

        copy = kwargs.get("copy", False)
        self.title = data["title"]
        self.id = data["id"] if not copy else None
        self.course = data["course"] if not copy else None
        self.units = []
        for i in range(len(data["lessons"])):
            self.add_lesson( Lesson().load_from_file(data["lessons"][i]["file"], **kwargs) ) 
            self.units[-1].id = data["lessons"][i]["unit"]
        data2 = Section_template().dump(data)

        del data2["title"]
        del data2["id"]
        del data2["lessons"]
        del data2["course"]
        self.params = data2
        return self
    
    def load_lessons(self, ids: list[int], session: OAuthSession, **kwargs) -> RequestStatus:
        """ Fill self.units with content from Stepic.org.
        + **kwargs: if source: load steps's content, otherwise: only ids """

        ids_url = [ str(i) for i in ids]
        ids_url = "&ids[]=".join(ids_url)
        url = f"https://stepik.org/api/units?ids[]=" + ids_url

        head = session.headers()
        head["cookie"] = session.cookie
        r = requests.get(url, headers=head)
        if not is_success(r, 0):
            return request_status(r, 0)
        
        units = r.json()["units"]
        for i in range(len(units)):
            les = Lesson()
            les.load_from_net(units[i]["lesson"], session, **kwargs)
            self.add_lesson(les)
            self.units[-1].id = units[i]["id"]
        return request_status(r, 0)
    
class Course:

    def __init__(self, title: str = "", sections: list[Section] = None, **params):
        self.title = title
        self.id = None
        self.sections = sections or []
        self.params = params
        
    def auth(self, session: OAuthSession):
        """ Attaches session to self.session
        + self.session is using in following methods:
            load_from_net, send_all, load_sections, send_heading, send_section, send_lesson,
            delete_network, delete_network_section, delete_network_lesson """
        self.session = session

    def save(self, path: str = None, **kwargs):
        """ Write your Course to {Course's Title}.yaml in root directory
        All Sections' lessons will be saved to same directory as {Course's Title}.yaml
        + **kwargs: filename - custom file's name, type and path;
            if copy: delete all ids """

        if not path:
            i = 0
            path = Path(f"Course_{i}.yaml")
            while path.exists():
                i += 1
                path = Path(f"Course_{i}.yaml")
            with open(path, "w", encoding="utf-8") as file:
                current_path = Path.cwd()
                path = current_path.joinpath(path)
                path = path.parent
                path = str(path)
                yaml.dump({"Course": self.dict_info(path=path, copy=kwargs.get("copy", False)) }, file, allow_unicode=True, sort_keys=False)
        else:
            path = Path(path)
            if path.suffixes:
                pathdir = path.parent
                pathdir.mkdir(exist_ok=True)
                with open(path, "w", encoding="utf-8") as file:
                    path = path.parent
                    path = str(path)
                    yaml.dump({"Course": self.dict_info(path=path, copy=kwargs.get("copy", False)) }, file, allow_unicode=True, sort_keys=False)
            else:
                try:
                    path.mkdir()
                    path = path.joinpath("Course_0.yaml")
                    with open(path, "w", encoding="utf-8") as file:
                        path = path.parent
                        path = str(path)
                        yaml.dump({"Course": self.dict_info(path=path, copy=kwargs.get("copy", False)) }, file, allow_unicode=True, sort_keys=False)
                except FileExistsError:
                    i = 0
                    path = path.joinpath(f"Course_{i}.yaml")
                    while path.exists():
                        i += 1
                        path = path.parent
                        path = path.joinpath(f"Course_{i}.yaml")
                    with open(path, "w", encoding="utf-8") as file:
                        path = path.parent
                        path = str(path)
                        yaml.dump({"Course": self.dict_info(path=path, copy=kwargs.get("copy", False)) }, file, allow_unicode=True, sort_keys=False)


        # title = kwargs.get("filename", f"{self.title}.yaml")
        # if title != kwargs.get("filename", None):
        #     try:
        #         title = translit(title, reversed=True)
        #     except LanguageDetectionError:
        #         pass
            
        # with open(title, "w", encoding="utf-8") as file:
        #     path = kwargs.get("filename", "")
        #     path = path.split(r"/")
        #     if path[-1] != ".":
        #         del path[-1]
        #     path = os.getcwd() + "/" + "/".join(path)
        #     yaml.dump({"Course": self.dict_info(path=path, copy=kwargs.get("copy", False)) }, file, allow_unicode=True, sort_keys=False)

    def dict_info(self, **kwargs) -> dict:
        """ Returns Course in the dictionary view.
        + **kwargs: if copy: delete all ids
        path - path to save Sections' lessons"""

        copy = kwargs.get("copy", False)
        id = self.id if not copy else None

        params = self.params
        if params.get("__del_status__", False):
            params["__del_status__"] = "STRICT_DELETE"

        ans = { **{"title": self.title, "id": id, "sections": [] }, **params }
        for sect in self.sections:
            ans["sections"].append( sect.dict_info(**kwargs) )
        return ans
    
    def get_structure(self, **kwargs) -> dict:
        """ Returns Course in the dictionary view without most of fields
        + **kwargs: if copy: delete all ids """

        copy = kwargs.get("copy", False)
        id = self.id if not copy else None
        ans = {"id": id, "sections": []}
        for sect in self.sections:
            # if sect.id == State.TO_DELETE:
            #     continue
            ans["Sections"].append(sect.get_structure(copy=copy))
        return ans

    def clear_del(self):
        """ Clear all fields
        + mark content to delete it in network """
        if not self.id:
            self.clear()
            return

        self.title = ""
        self.params = {}
        self.params["__del_status__"] = State.STRICT_DELETE
        self.sections = []

    def clear(self):
        """ Clear all fields.
        + It won't mark content to delete it in network """
        self.title = "" 
        self.id = None
        self.params = {}
        self.sections = []

    def delete_network(self, **kwargs) -> RequestStatus:
        """ Delete your Course from Stepic.org
        + **kwargs: session: use given OAuthSession() instead of self.session"""

        id = self.id
        url = f"https://stepik.org/api/courses/{id}"

        try:
            session = kwargs.get("session", None) or self.session
        except AttributeError:
            raise AttributeError("run self.auth() or set **kwargs: session")
        
        r = requests.delete(url, headers=session.headers())

        if is_success(r, 204):
            self.id = None
            for i in self.sections:
                i.id = None
        return request_status(r, 204)

    def delete_section(self, sect_pos: int):
        """ Delete Section from self.sections"""
        if self.sections[sect_pos].id:
            self.sections[sect_pos].params["__del_status__"] = State.STRICT_DELETE
            return
        self.sections.pop(sect_pos)

    def delete_lesson(self, sect_pos: int, les_pos: int):
        """ Mark your Lesson to DELETE from Stepic.org. It will be deleted after send_all() method.
        + Attention! After send_all() method lesson will be deleted even if it's part of some Courses'
        + Indexes as at list[] 
        + Indexes of next lessons won't change until send_all() method!"""   

        self.sections[sect_pos].delete_lesson(les_pos)

    def remove_lesson(self, sect_pos: int, les_pos: int):
        """ Mark your Lesson to untie from your Section. It will be removed after send_all() method.
        + Indexes as at list[] 
        + Indexes of next lessons won't change until send_all() method!"""

        self.sections[sect_pos].remove_lesson(les_pos)

    def delete_step(self, sect_pos: int, les_pos: int, step_pos: int):
        """ Mark your Step to delete from your Lesson. It will be deleted after send_all() method.
        + Indexes as at list[] 
        + Indexes of next steps won't change until send_all() method!"""

        self.sections[sect_pos].delete_step(les_pos, step_pos)

    def add_lesson(self, sect_pos: int, lesson: Lesson, position: int = -1):
        """ Add Lesson to your Section. sect_pos - indexes as at list[].
        + position:
            if -1:
                append to Lesson's steps
            else:
                insert into Lesson's steps"""

        self.sections[sect_pos].add_lesson(lesson, position)

    def add_step(self, sect_pos: int, les_pos: int, step: Step, position: int = -1):
        """ Add Step to your Lesson. sect_pos, les_pos - indexes as at list[].
        + position:
            if -1:
                append to Lesson's steps
            else:
                insert into Lesson's steps"""

        self.sections[sect_pos].add_step(les_pos, step, position)

    def send_all(self, **kwargs) -> RequestStatus:
        """ Create or update Course on Stepic.org.
        If self.id is None - Course will be created, otherwise it will be updated.
        ( It can be deleted, if it was marked before )
        The same applies to objects inside.
        + **kwargs: session: use given OAuthSession() instead of self.session """

        try:
            session = kwargs.get("session", self.session)
        except AttributeError:
            raise AttributeError("run self.auth() or set **kwargs: session")
        
        if self.params.get("__del_status__", False):
            for sect in self.sections:
                for unit in sect.units:
                    unit.lesson.send(session)

            del self.params["__del_status__"]
            return self.delete_network(**kwargs)
        
        head_stat = self.send_heading(**kwargs)
        if not head_stat.success:
            return head_stat
        
        sections = []
        for i in range(len(self.sections)):
            if not self.sections[i].params.get("__del_status__", False):
                sections.append(self.sections[i])
            stat = self.sections[i].send(i, session, self.id)
            if not stat.success:
                return stat
        self.sections = sections
        return head_stat


    def send_heading(self, **kwargs) -> RequestStatus:
        """ Create or update Section's heading on Stepic.org.
        If self.id is None - Course will be created, otherwise it will be updated.
        + **kwargs: session: use given OAuthSession() instead of self.session """

        try:
            session = kwargs.get("session", None) or self.session
        except AttributeError:
            raise AttributeError("run self.auth() or set **kwargs: session")

        api_url = "https://stepik.org/api/courses"
        if self.id:
            api_url += f"/{self.id}"

        payload = {
                "course": { **{
                    "title": self.title,
                    "id": self.id
                    }, **self.params }
                }

        head = session.headers()
        head["Cookie"] = session.cookie

        if self.id:
            r = requests.put(api_url, headers=head, json=payload)
        else:
            r = requests.post(api_url, headers=head, json=payload)


        content = r.json()["courses"][0]
        r_dict = Course_template().dump(content)
        del r_dict["sections"]
        test_dict = {
            "title": self.title,
            "id": self.id,
            **self.params
        }

        repeating = ( r_dict == test_dict )

        if is_success(r, 0) or repeating:
            self.id = r.json()['enrollments'][0]['id']
        if repeating:
            return success_status(True, r.text)
        return request_status(r, 201)

    def load_from_file(self, filename: str, **kwargs):
        """ Fill all Course's fields with content from file.
        + **kwargs: if copy: delete all ids """

        data = ""
        filename = filename.replace(os.getcwd(), ".")
        with open(filename, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)["Course"]
        return self.load_from_dict(data, **kwargs)
    
    def load_from_dict(self, data: dict, **kwargs):
        """ Fill all Course's fields with content from dictionary.
        + **kwargs: if copy: delete all ids """

        copy = kwargs.get("copy", False)
        self.title = data["title"]
        self.id = data.get("id", None) if not copy else None

        self.sections = []
        for i in data["sections"]:
            self.sections.append( Section().load_from_dict(i, copy=copy))
        data2 = Course_template().dump(data)

        del data2["title"]
        del data2["sections"]
        del data2["id"]
        self.params = data2
        return self

    def load_from_net(self, id: int, **kwargs):
        """ Fill all Course's fields with content from Stepic.org.
        + **kwargs: if source: load steps's content.
            session: use given OAuthSession() instead of self.session
            Without source Lesson().steps will contain only list[int] with steps' ids"""

        url = f"https://stepik.org/api/courses/{id}"

        try:
            session = kwargs.get("session", None) or self.session
        except AttributeError:
            raise AttributeError("run self.auth() or set **kwargs: session")

        r = requests.get(url, headers=session.headers())
        if not is_success(r, 0):
            return success_status(False, "Can't get course's head")
        
        self.clear()
        
        content = r.json()["courses"][0] 

        self.id = id
        self.title = content["title"]
        
        sect_ids = content["sections"]
        if  len(sect_ids) == 0:
            return success_status(True, "Course loaded")
        
        self.load_sections(sect_ids, **kwargs)

        del content["id"]
        del content["title"]
        del content["sections"]
        self.params = Course_template().dump(content)
        return self

    def load_sections(self, ids: list[int], **kwargs) -> RequestStatus:
        """ Fill Course.sections with content from Stepic.org.
        + **kwargs: if source: load steps's content, otherwise: only ids
            session: use given OAuthSession() instead of self.session
            Without source Lesson().steps will contain only list[int] with steps' ids"""

        ids_url = [ str(i) for i in ids]
        ids_url = "&ids[]=".join(ids_url)
        url = f"https://stepik.org/api/sections?ids[]=" + ids_url

        try:
            session = kwargs.get("session", None) or self.session
        except AttributeError:
            raise AttributeError("run self.auth() or set **kwargs: session")
        
        head = session.headers()
        head["cookie"] = session.cookie
        r = requests.get(url, headers=head)

        if not is_success(r, 0):
            return request_status(r, 0)
        
        sections = r.json()["sections"]
        for i in sections:
            content = i
            title = content["title"]

            units_ids = content["units"]
            del content["title"]
            del content["units"]
            params = Section_template().dump(content)

            sect = Section(title, **params)
            kwargs = kwargs.copy()
            if kwargs.get("session", False):
                del kwargs["session"]
            sect.load_lessons(units_ids, session, **kwargs)
            self.sections.append(sect)
        return request_status(r, 0)