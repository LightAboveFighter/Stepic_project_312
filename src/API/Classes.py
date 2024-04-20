import yaml
import requests
from src.API.OAuthSession import OAuthSession
from src.Help_methods import is_success, request_status, success_status
import json
import os
from src.API.Step import StepText, Step, create_any_step
import pyparsing as pp
import io
from transliterate import translit
from transliterate.exceptions import LanguageDetectionError
from src.API.Loading_templates import Step_template, Lesson_template, Section_template, \
    Course_template, Lesson_template_source, Section_template_source, Course_template_source

class Lesson:
    '''title: str
    steps: list or []
    id: int
    sect_ids: list or []
    params: dict'''

    def __init__(self, title = "", id = None, steps: list[Step] = [], section_ids = None, **params):
        """ **kwargs:
        'section_ids - [section's id] to tie lesson without 'Course' class
        """
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

    def dict_info(self, **kwargs):
        """ **kwargs: if copy: delete all ids """

        copy = kwargs.get("copy", False)
        steps = [ i if isinstance(i, int) else i.dict_info(copy=copy) for i in self.steps ]

        if copy:
            for i in range(len(steps)):
                if isinstance(steps[i], int):
                    steps[i] = None
        print(steps)
        
        id = self.id if not copy else None
        sect_ids = self.sect_ids if not copy else []

        ans = { **{"title": self.title, "id": id, "steps": steps, "sect_ids": sect_ids }, **self.params}
        return ans
    
    def get_structure(self, **kwargs):
        """ **kwargs: if copy: delete all ids """

        copy = kwargs.get("copy", False)
        id = self.id if not copy else None
        ans = {"id": id, "steps": []}
        if not copy:
            for i in self.steps:
                ans["steps"].append(i if isinstance(i, int) else i.id)

    def send(self, session: OAuthSession):

        api_url = 'https://stepik.org/api/lessons'
        if  self.id:
            api_url += f"/{self.id}"

        data = {
            'lesson': { **{
                'title': self.title,
                'id': self.id,
                "steps": [ i if isinstance(i, int) else i.id for i in self.steps ]
            }, **self.params }
        }

        if self.id:
            r = requests.put(api_url, headers=session.headers(), json=data)
        else:
            r = requests.post(api_url, headers=session.headers(), json=data)
        id = r.json()['lessons'][0]['id']

        if is_success(r, 0):
            self.id = id
            for i in self.steps:
                i.lesson_id = self.id
            for i in range(len(self.steps)):
                self.steps[i].send(i, session)

        return request_status(r, 201)

    def delete_network(self, session: OAuthSession, danger = False):
        if danger:
            if self.sect_id:
                raise "Safety delete: can't delete lesson, inside another courses"
        return self.__danger_delete_network__(session)

    def __danger_delete_network__(self, session: OAuthSession):

        api_url = f"https://stepik.org/api/lessons/{self.id}"
        r = requests.delete(api_url, headers=session.headers())

        if is_success(r, 204):
            self.sect_ids = []
            self.id = None
        return request_status(r, 204)
    
    def save(self, **kwargs):
        """ Write your lesson to 'Lesson's Title'.yaml
        **kwargs: filename - custom file's name and path;
        if copy: delete all ids """

        title = kwargs.get("filename", f"{self.title}.yaml")
        if title != kwargs.get("filename", None):
            try:
                title = translit(title, reversed=True)
            except LanguageDetectionError:
                pass
        
        content = self.dict_info(copy=kwargs.get("copy", False))

        with open(title, "w", encoding="utf-8") as file:
            yaml.dump({"Lesson": content }, file, allow_unicode=True)


    def is_tied(self, sect_id: int):
        return sect_id in self.sect_ids

    def tie(self, sect_id: int, position: int, session: OAuthSession):

        if not self.is_tied(sect_id):
            api_url = 'https://stepik.org/api/units'
            data = {
                "unit": {
                    "position": position,
                    "lesson": self.id,
                    "section": sect_id
                }
            }

            r2 = requests.post(api_url, headers=session.headers(), json=data)
            if is_success(r2, 0):
                self.sect_ids.append(sect_id)
            return request_status(r2, 0)
        return success_status(True, "Already tied")
    
    def load_from_file(self, filename: str, **kwargs):
        """ **kwargs: if copy: delete all ids """

        data = ""
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

                                # self.sect_ids = section_ids or []
                                # self.params = params

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
        """ **kwargs: if copy: delete all ids """

        copy = kwargs.get("copy", False)
        self.title = data["title"]
        self.id = data["id"] if not copy else None
        self.sect_ids = data["sect_ids"] if not copy else []

        if isinstance(data["steps"][0], int):
            self.steps = data["steps"] if not copy else []
        else:
            self.steps = []
            for i in data["steps"]:
                if isinstance(i, int):
                    if not copy:
                        self.steps.append(i)
                    continue
                if copy:
                    i["id"] = None
                    i["lesson"] = None

                type = i["block"]["name"]
                unique = i["block"]["source"].copy()
                st = create_any_step(type, **i, unique=unique)

                self.steps.append(st)

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
        """ **kwargs: if source: load steps's content """

        url = f"https://stepik.org/api/lessons/{id}"

        r = requests.get(url, headers=session.headers())
        if not is_success(r, 0):
            return success_status(False, "Can't get course's head")
        
        content = Lesson_template().dump(json.loads(r.text)["lessons"][0])

        self.id = id
        self.title = content["title"]
        
        self.sect_ids = content["courses"]
        steps_ids = content["steps"]

        del content["id"]
        del content["title"]
        del content["courses"]
        del content["steps"]

        self.params = content
        if kwargs.get("source", False):
            self.load_steps(steps_ids, session)
        else:
            self.steps = steps_ids
        

    
    def load_steps(self, ids: list[int], session: OAuthSession):

        ids_url = [ str(i) for i in ids]
        ids_url = "&ids[]=".join(ids_url)
        url = f"https://stepik.org/api/step-sources?ids[]=" + ids_url

        r = requests.get(url, headers=session.headers())
        if not is_success(r, 0):
            return request_status(r, 0)
        
        steps = json.loads(r.text)["step-sources"]
        if not steps:
            self.steps = ids
            return

        for i in range(len(steps)):
            params = Step_template().dump(steps[i])
            type = params["block"]["name"]
            body = params["block"].copy()
            del body["name"]
            del params["block"]
            params["lesson"] = self.id

            les_id = self.id
            unique = body["source"]
            
            step = create_any_step(type, f"Step_{i}", les_id, body, unique, **params)
            self.steps.append(step)
    

class Section:

    def __init__(self, title = "", lessons = None, **params):
        self.title = title
        self.lessons = lessons or []
        self.id = None
        self.params = params

    def dict_info(self, **kwargs):
        """ **kwargs: if copy: delete all ids """

        copy = kwargs.get("copy", False)
        title = self.title if not copy else None
        id = self.id if not copy else None
        params = self.params
        if copy:
            params["course"] = None
        ans = { **{"title": title, "id": id, "lessons": []}, **params }
        for i in self.lessons:
            ans["lessons"].append(i.dict_info(**kwargs))
        return ans
    
    def get_structure(self, **kwargs):
        """ **kwargs: if copy: delete all ids """

        id = self.id if not kwargs.get("copy", False) else None
        ans = {"id": id, "lessons": []}
        for i in self.lessons:
            ans["lessons"].append(i.get_structure(**kwargs))
        return ans
    
    def save(self, **kwargs):
        """ Write your section to 'Section's Title'.yaml
        **kwargs: filename - custom file's name and path
        if copy: delete all ids """


        title = kwargs.get("filename", f"{self.title}.yaml")
        if title != kwargs.get("filename", None):
            try:
                title = translit(title, reversed=True)
            except LanguageDetectionError:
                pass

        with open(title, "w", encoding="utf-8") as file:
            yaml.dump({"Section": self.dict_info(copy=kwargs.get("copy", False)) }, file, allow_unicode=True)


    def delete_network(self, session):
        id = self.id
        if not id == None:
            api_url = f"https://stepik.org/api/sections/{id}"
            r = requests.delete(api_url, headers=session.headers())

            if is_success(r, 204):
                self.id = None
                for i in self.lessons:
                    index = i.sect_ids.index(id)
                    i.sect_ids.pop(index)
                self.save()
            return request_status(r, 204)
        return success_status(False, "")
    
    def send(self, course_id: int, position: int, session: OAuthSession):

        api_url = "https://stepik.org/api/sections"
        if self.id:
            api_url += f"/{self.id}"

        payload = json.dumps( 
            {
                "section": 
                { 
                    **{
                    "position": position + 1,
                    "required_percent": 100,
                    "title": self.title,
                    "id": self.id,
                    "course": course_id
                    }, **self.params
                }
            }
        )
        head = session.headers()
        head["Cookie"] = session.cookie
        if self.id:
            r = requests.put(api_url, headers=head, data=payload)
        else:
            r = requests.post(api_url, headers=head, data=payload)

        if is_success(r, 0):
            id = json.loads(r.text)["sections"][0]["id"]
            self.id = id
            for i in range(len(self.lessons)):
                self.lessons[i].send(session)
                if not self.lessons[i].is_tied(self.id):
                    self.lessons[i].tie(self.id, i, session)
        return request_status(r, 201)
    
    def send_lesson(self, les_pos: int, session: OAuthSession):
        self.lessons[les_pos].send(session)
        self.lessons[les_pos].tie(self.id, les_pos, session)

    def delete_local_lesson(self, les_pos: int):
        if self.lessons[les_pos].id is None:
            self.lessons.pop(les_pos)

    def delete_network_lesson(self, les_pos, session: OAuthSession, danger = False):
        return self.lessons[les_pos].delete_network(session, danger)

    def load_from_file(self, filename: str, **kwargs):
        """ **kwargs: if copy: delete all ids """

        data = ""
        with open(filename, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)["Section"]
        return self.load_from_dict(data, **kwargs)

    def load_from_dict(self, data: dict, **kwargs):
        """ **kwargs: if copy: delete all ids """

        copy = kwargs.get("copy", False)
        self.title = data["title"]
        self.id = data["id"] if not copy else None
        self.lessons = []
        for i in data["lessons"]:
            self.lessons.append( Lesson().load_from_dict(i, **kwargs))

        try:
            data2 = Section_template().dump(data)
        except TypeError:
            data2 = Section_template_source().dump(data)

        del data2["title"]
        del data2["id"]
        del data2["lessons"]
        if copy:
            data2["course"] = None
        self.params = data2
        return self
    
    def load_lessons(self, ids: list[int], session: OAuthSession, **kwargs):
        """ **kwargs: if source: load steps's content """

        ids_url = [ str(i) for i in ids]
        ids_url = "&ids[]=".join(ids_url)
        url = f"https://stepik.org/api/units?ids[]=" + ids_url

        head = session.headers()
        head["cookie"] = session.cookie
        r = requests.get(url, headers=head)
        if not is_success(r, 0):
            return request_status(r, 0)
        
        lessons = json.loads(r.text)["units"]
        for i in lessons:
            les = Lesson()
            les.load_from_net(i["lesson"], session, **kwargs)

            self.lessons.append(les)

    
class Course:

    def __init__(self, title = "", sections = None, **params):
        self.title = title
        self.id = None
        self.sections = sections or []
        self.params = params

    def auth(self, session: OAuthSession):
        self.session = session

    def save(self, **kwargs):
        """ Write your course to 'Course's Title'.yaml
        **kwargs: filename - custom file's name and path
        if copy: delete all ids """

        title = kwargs.get("filename", f"{self.title}.yaml")
        if title != kwargs.get("filename", None):
            try:
                title = translit(title, reversed=True)
            except LanguageDetectionError:
                pass
            
        with open(title, "w", encoding="utf-8") as file:
            yaml.dump({"Course": self.dict_info(copy=kwargs.get("copy", False)) }, file, allow_unicode=True)

    def dict_info(self, **kwargs):
        """ **kwargs: if copy: delete all ids """

        copy = kwargs.get("copy", False)
        id = self.id if not copy else None
        ans = { **{"title": self.title, "id": id, "sections": [] }, **self.params }
        for i in self.sections:
            ans["sections"].append( i.dict_info(copy=copy) )
        return ans
    
    def get_structure(self, **kwargs):
        """ **kwargs: if copy: delete all ids """

        copy = kwargs.get("copy", False)
        id = self.id if not copy else None
        ans = {"id": id, "sections": []}
        for i in self.sections:
            ans["Sections"].append(i.get_structure(copy=copy))
        return ans
    
    def create_section(self, position: int, section: Section):
        """ insert if position != -1 
            append if position = -1 """
        
        if position != -1:
            self.sections.insert( position, section)
        else:
            self.sections.append( section )
    
    def create_lesson(self, les: Lesson, sect_pos: int, position = -1):
        """ insert if position != -1 
            append if position = -1 """
        
        if position != -1:
            self.sections[sect_pos].lessons.insert( position, les)
        else:
            self.sections[sect_pos].lessons.append( les )

    def delete_local(self):
        self.title = 0
        self.id = None
        self.params = {}
        self.sections = []
        self.save()

    def delete_network(self):
        id = self.id
        url = f"https://stepik.org/api/courses/{id}"

        r = requests.delete(url, headers=self.session.headers())

        if is_success(r, 204):
            self.id = None
            for i in self.sections:
                for j in i.lessons:
                    index = j.sect_ids.index( i.id )
                    j.sect_ids.pop(index)
                i.id = None
            self.save()
        return request_status(r, 204)


    def delete_local_section(self, sect_pos: int):
        if self.sections[sect_pos].id is None:
            self.sections.pop(sect_pos)

    def delete_network_section(self, sect_pos: int):
        res = self.sections[sect_pos].delete_network(self.session)
        if res["Success"]:
            self.delete_local_section(sect_pos)
            self.save()
        return res
    
    def delete_local_lesson(self, sect_pos: int, les_pos: int):
        self.sections[sect_pos].delete_local_lesson(les_pos)
    
    def delete_network_lesson(self, sect_pos: int, les_pos: int, danger = False):
        """ danger - in case you know what you are doing """

        return self.sections[sect_pos].delete_network_lesson(les_pos, self.session, danger)

    def send_all(self, **kwargs):
        """ **kwargs: session - OAuthSession() """

        try:
            kwargs.get("session", None) or self.session
        except AttributeError:
            raise AttributeError("run self.auth() or set **kwargs: session")
        
        self.send_heading(**kwargs)
        for i in range(len(self.sections)):
            self.send_section(i, **kwargs)
        self.save()

    def send_heading(self, **kwargs):
        """ **kwargs: session - OAuthSession() """

        try:
            session = kwargs.get("session", None) or self.session
        except AttributeError:
            raise AttributeError("run self.auth() or set **kwargs: session")

        api_url = "https://stepik.org/api/courses"
        if self.id:
            api_url += f"/{self.id}"

        payload = json.dumps( 
            {
                "course": { **{
                    "title": self.title,
                    "id": self.id
                    }, **self.params }
                }
        )
        head = session.headers()
        head["Cookie"] = session.cookie

        if self.id:
            r = requests.put(api_url, headers=head, data=payload)
        else:
            r = requests.post(api_url, headers=head, data=payload)

        if is_success(r, 201):
            id = json.loads(r.text)['enrollments'][0]['id']
            self.id = id
        return request_status(r, 201)
    
    def send_section(self, sect_pos: int, **kwargs):
        """ **kwargs: session - OAuthSession() """
        try:
            session = kwargs.get("session", None) or self.session
        except AttributeError:
            raise AttributeError("run self.auth() or set **kwargs: session")
        self.sections[sect_pos].send(self.id, sect_pos, session)

    def send_lesson(self, sect_pos: int, les_pos: int, **kwargs):
        """ **kwargs: session - OAuthSession() """
        try:
            session = kwargs.get("session", None) or self.session
        except AttributeError:
            raise AttributeError("run self.auth() or set **kwargs: session")
        self.sections[sect_pos].send_lesson(les_pos, session)

    def load_from_file(self, filename: str, **kwargs):
        """ **kwargs: if copy: delete all ids """

        data = ""
        with open(filename, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)["Course"]
        return self.load_from_dict(data, **kwargs)
    
    def load_from_dict(self, data: dict, **kwargs):
        """ **kwargs: if copy: delete all ids """

        copy = kwargs.get("copy", False)
        self.title = data["title"]
        self.id = data.get("id", None) if not copy else None

        self.sections = []
        for i in data["sections"]:
            self.sections.append( Section().load_from_dict(i, copy=copy))

        del data["title"]
        del data["sections"]
        del data["id"]
        self.params = data
        return self

    def load_from_net(self, id: int, **kwargs):
        """ **kwargs: if source: load steps's content;
        session: use given OAuthSession() """

        url = f"https://stepik.org/api/courses/{id}"

        try:
            session = kwargs.get("session", None) or self.session
        except AttributeError:
            raise AttributeError("run self.auth() or set **kwargs: session")

        r = requests.get(url, headers=session.headers())
        if not is_success(r, 0):
            return success_status(False, "Can't get course's head")
        
        content = json.loads(r.text)["courses"][0] 

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

    def load_sections(self, ids: list[int], **kwargs):
        """ Add group of sections from net
        **kwargs: if source: load steps's content """

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
            return request_status(r)
        
        sections = json.loads(r.text)["sections"]
        for i in sections:
            content = i
            title = content["title"]

            lessons_ids = content["units"]
            del content["title"]
            del content["units"]
            params = Section_template().dump(content)

            sect = Section(title, **params)
            kwargs = kwargs.copy()
            if kwargs.get("session", False):
                del kwargs["session"]
            sect.load_lessons(lessons_ids, session, **kwargs)
            self.sections.append(sect)