import OAuthSession
import yaml
import requests
import json
import Classes as cl
import Mark_requests as mk  

class Course_manager:

    def __init__(self, course: cl.Course):
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
        #                         "id": 1226398,
        #                         "Tied": True 
        #                     },
        #                     {
        #                         "Title": "TITLE",
        #                         "id": 30485038,
        #                         "Tied": True 
        #                     }
        #                 ]
        #             }
        #         ]
        #     }
        # }
        self.course = course
        
    def auth(self, s: OAuthSession):
        self.session = s

    # def dict_info(self):

    #     ans = self.course.dict_info()
    #     # for i in range( len( ans["Sections"])):
    #     #     sect = ans["Sections"][i]
    #     #     ans["Sections"][i] = sect.dict_info()
    #     # for j in range(len(self.course.sections)):
    #     #     for i in range(len(self.course.sections[j]["Lessons"])):
    #     #         ans["Sections"][j]["Lessons"][i]["Tied"] = ( self.course.sections.id in self.course.sections[j].lessons[i].sect_ids )
    #     return ans
    
    def save(self):
        """ Write your course to 'Course's Title'.yaml """
        # title = self.structure["Course"]["Title"]
        title = self.course.title
        file = ""
        try:
            file = open(f"{title}.yaml", "x")
        except:
            file = open(f"{title}.yaml", "w")

        yaml.dump({"Course": self.course.dict_info() }, file)

    def __send_course__(self):

        # if self.structure["Course"]["id"] is not None:
        if self.course.id is not None:
            return {"Success": True, "json": {"Status": "Already sent"}}

        # title = self.structure["Course"]["Title"]
        title = self.course.title
        # description = self.structure["Course"]["Description"]

        api_url = "https://stepik.org/api/courses"
        payload = json.dumps( 
            {
                "course": { **{
                    # "grading_policy_source": "no_deadlines",
                    # "course_type": "basic",
                    # "description": description,
                    "title": title,
                    }, **self.course.params }
                }
        )
        head = self.session.headers()
        head["Cookie"] = self.session.cookie

        r = requests.post(api_url, headers=head, data=payload)

        if mk.is_success(r, 201):
            id = json.loads(r.text)['enrollments'][0]['id']
            # self.structure["Course"]["id"] = id
            self.course.id = id
        return mk.request_status(r, 201)
    
    def create_section(self, section: cl.Section):
        """ insert if position != -1 
            append if position = -1 """
        
        if section.pos != -1:
            # self.structure["Course"]["Sections"].insert(section.pos, {"Title": section.title, "id": None, "Lessons": []})
            self.course.sections.insert( section.pos, section.dict_info())
            # for i in section.lessons:
            #     self.create_lesson(les=i, sect_pos=section.pos)
        else:
            # self.structure["Course"]["Sections"].append({"Title": section.title, "id": None, "Lessons": []})
            self.course.sections.append( section )
            section.pos = len( self.course.sections ) - 1
            # for i in section.lessons:
            #     self.create_lesson(les=i, sect_pos=section.pos)

    # def create_section(self, title: str, position = -1):
    #     """ insert if position != -1 
    #         append if position = -1 """
        
    #     if position != -1:
    #         self.structure["Course"]["Sections"].insert(position, {"Title": title, "id": None, "Lessons": []})
    #     else:
    #         self.structure["Course"]["Sections"].append({"Title": title, "id": None, "Lessons": []})

    def delete_network_section(self, section_pos: int):
        # id = self.structure["Course"]["Sections"][section_pos]["id"]
        id = self.course.sections[section_pos].id

        api_url = f"https://stepik.org/api/sections/{id}"
        r = requests.delete(api_url, headers=self.session.headers())

        if mk.is_success(r, 204):
            # self.structure["Course"]["Sections"][section_pos]["id"] = None
            self.course.sections[section_pos].id = None
            # for i in range( len( self.structure["Course"]["Sections"][section_pos]["Lessons"])):
            #     self.session["Course"]["Sections"][section_pos]["Lessons"][i]["Tied"] = False
            for i in range(len(self.course.sections[section_pos].lessons)):
                index = self.course.sections[section_pos].lessons[i].sect_ids.index(id)
                self.course.sections[section_pos].lessons[i].sect_ids.pop(index)
            self.save()
        return mk.request_status(r, 204)

    def __send_section__(self, position: int):

        # if self.structure["Course"]["Sections"][position]["id"] is not None:
        if self.course.sections[position].id is not None:
            return {"Success": True, "json": {"Status": "Already sent"}}

        # course = self.structure["Course"]
        # course_id = course["id"]
        # description = course["Sections"][position]["id"]
        # title = course["Sections"][position]["Title"]

        course_id = self.course.id
        title = self.course.sections[position].title

        api_url = "https://stepik.org/api/sections"
        payload = json.dumps( 
            {
                    "section": { **{
                        "position": position,
                        "required_percent": 100,
                        "title": title,
                        # "description": description,
                        "course": course_id
                    }, **self.course.sections[position].params }
                }
        )
        head = self.session.headers()
        head["Cookie"] = self.session.cookie

        r = requests.post(api_url, headers=head, data=payload)

        if mk.is_success(r, 201):
            # self.structure["Course"]["Sections"][position]["id"] = json.loads(r.text)["sections"][0]["id"]
            id = json.loads(r.text)["sections"][0]["id"]
            self.course.sections[position].id = id
        return mk.request_status(r, 201)
    
    def create_lesson(self, les: cl.Lesson, sect_pos: int, les_pos = -1):
        """ insert if position != -1 
            append if position = -1 """
        
        if les_pos != -1:
            # self.structure["Course"]["Sections"][sect_pos]["Lessons"].insert(les_pos, {"Title": les.title, "id": les.id, "Steps": [], "Tied": False})
            self.course.sections[sect_pos].lessons.insert( les_pos, les.dict_info())
        else:  # add creating steps ------------------------------------
            # self.structure["Course"]["Sections"][sect_pos]["Lessons"].append({"Title": les.title, "id": les.id, "Steps": [], "Tied": False})
            self.course.sections[sect_pos].lessons.append( les.dict_info())


    # def create_lesson(self, title: str, section_num:int, position = -1):
    #     """ insert if position != -1 
    #         append if position = -1 """
        
    #     if position != -1:
    #         self.structure["Course"]["Sections"][section_num]["Lessons"].insert(position, {"Title": title, "id": None, "Tied": False})
    #     else:
    #         self.structure["Course"]["Sections"][section_num]["Lessons"].append({"Title": title, "id": None, "Tied": False})

    def __tie_lesson__(self, lesson_id: int, section: int, lesson_pos: int):
        api_url = 'https://stepik.org/api/units'
        data = {
            "unit": {
                "position": lesson_pos,
                "lesson": lesson_id,
                "section": self.course.sections[section].id
                # "section": self.structure["Course"]["Sections"][section]["id"]
            }
        }

        r2 = requests.post(api_url, headers=self.session.headers(), json=data)
        return r2
    
    def __send_lesson__(self, section: int, lesson_pos: int):

        # p = self.structure["Course"]["Sections"][section]["Lessons"][lesson_pos]
        p = self.course.sections[section]
        les = p.lessons[lesson_pos]
        sect_id = p.id
        # if  p["id"] is not None:
        if les.id is not None:
            # if p["Tied"]:
            if sect_id in les.sect_ids:
                return {"Success": True, "json": {"Status": "Already sent"}}
            r = self.__tie_lesson__(les.id, section, lesson_pos)
            if mk.is_success(r, 0):
                # self.structure["Course"]["Sections"][section]["Lessons"][lesson_pos]["Tied"] = True
                self.course.sections[section].lessons[lesson_pos].sect_ids.append(sect_id)
            return mk.request_status(r, 0)
        
        # title = self.structure["Course"]["Sections"][section]["Lessons"][lesson_pos]["Title"]
        title = les.title

        api_url = 'https://stepik.org/api/lessons'
        data = {
            'lesson': { **{
                'title': title
            }, **les.params }
        }
        # Use POST to create new objects
        r = requests.post(api_url, headers=self.session.headers(), json=data)
        lesson_id = r.json()['lessons'][0]['id']

        r2 = self.__tie_lesson__(lesson_id, section, lesson_pos)

        if mk.is_success(r, 201, r2, 0):     # r.status_code() should be 201 (HTTP Created)
            # self.structure["Course"]["Sections"][section]["Lessons"][lesson_pos]["Tied"] = True
            # self.structure["Course"]["Sections"][section]["Lessons"][lesson_pos]["id"] = lesson_id
            self.course.sections[section].lessons[lesson_pos].sect_ids.append(sect_id)
            self.course.sections[section].lessons[lesson_pos].id = lesson_id
        return mk.request_status(r, 201, r2, 0)
    
    def delete_network_lesson(self, section: int, lesson_pos: int):
        # lesson_id = self.structure["Course"]["Sections"][section]["Lessons"][lesson_pos]["id"]
        lesson_id = self.course.sections[section].lessons[lesson_pos].id

        api_url = f"https://stepik.org/api/lessons/{lesson_id}"
        r = requests.delete(api_url, headers=self.session.headers())

        if mk.is_success(r, 204):
            # self.structure["Course"]["Sections"][section]["Lessons"][lesson_pos]["Tied"] = False
            # self.structure["Course"]["Sections"][section]["Lessons"][lesson_pos]["id"] = None
            sect_id = self.course.sections[section].id
            index = self.course.sections[section].lessons[lesson_pos].sect_ids.index(sect_id)
            self.course.sections[section].lessons[lesson_pos].sect_ids.pop(index)
            self.course.sections[section].lessons[lesson_pos].id = None
            self.save()
        return mk.request_status(r, 204)

    # def create_step(self, Step):

    def send_all(self):
        """ Save and send all elems without id to stepik.org
            Return logs """
        self.save()
        logs = []
        # content = self.structure["Course"]
        content = self.course
        logs.append(self.__send_course__())
        if not(logs[0]["Success"]): 
            self.save()
            return logs
        # for i in range(len(content["Sections"])):
        for i in range(len(content.sections)):
            logs.append(self.__send_section__(i))
            if not(logs[-1]["Success"]):
                self.save()
                return logs
            # for j in range(len(content["Sections"][i]["Lessons"])):
            for j in range(len(content.sections[i].lessons)):
                logs.append(self.__send_lesson__(i, j))
                if not(logs[-1]["Success"]):
                    self.save()
                    return logs
                # for k in range(content["Section"][i]["Lessons"][j]["Steps"].len()):
                #     self.__send_step__()
        self.save()

        return logs

    def delete_network_course(self):
        # id = self.structure["Course"]["id"]
        id = self.course.id
        url = f"https://stepik.org/api/courses/{id}"

        r = requests.delete(url, headers=self.session.headers())

        if mk.is_success(r, 204):
            # self.structure["Course"]["id"] = None
            self.course.id = None
            # for i in range( len( self.structure["Course"]["Sections"] )):
            for i in range( len( self.course.sections )):
                # self.structure["Course"]["Sections"][i]["id"] = None
                self.course.sections[i].id = None
                # for j in range( len( self.structure["Course"]["Sections"][i]["Lessons"])):
                #     self.structure["Course"]["Sections"][i]["Lessons"][j]["Tied"] = False
                for j in range(len(self.course.sections[i].lessons)):
                    index = self.course.sections[i].lessons[j].sect_ids.index( self.course.sections[i].id )
                    self.course.sections[i].lessons[j].sect_ids.pop(index)
                    self.save()
        return mk.request_status(r, 204)

            # def load_from_file(self, filename: str):
            #     file = open(filename, "r")
            #     structure = yaml.safe_load(file)

    # def load_from_network(self, course_id: int):
        
    #     api_url = f"https://stepik.org/api/courses/{course_id}"
    #     r = requests.get(api_url, headers=self.session.headers())

    #     data5 = json.loads(r.text)
    #     local = {"Course": {"Title": None, "Description": None, "id": course_id, "Sections": []} }
    #     section_ids = data["courses"]["sections"]
    #     for i in range(len(section_ids)):
    #         local["Course"]["Sections"][i]["id"] = section_ids[i]
        
