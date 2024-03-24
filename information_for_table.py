import requests
import json

def get_id(class_id, headers):
    api = f"https://stepik.org/api/students?klass={class_id}&page=1"
    r = requests.get(api, headers=headers)
    work = r.json()
    id_list = []
    i = 2
    while len(work) > 1:
        for i in range(len(work["students"])):
            id_list.append(work["students"][i]["user"])
        api = f"https://stepik.org/api/students?klass={class_id}&page=2"
        r = requests.get(api, headers=headers)
        work = r.json()
    return id_list

def get_names(id_list, headers):
    api = "https://stepik.org/api/users?"
    for i in id_list:
        api += f'ids%5B%5D={i}&'
    api = api[:-1]
    r = requests.get(api, headers=headers)
    work = r.json()
    names_list = []
    for user in work["users"]:
        names_list.append(user["full_name"])
    return names_list

