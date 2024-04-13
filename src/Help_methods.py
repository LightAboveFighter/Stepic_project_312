import yaml

def is_success(*r):
    """ r - (requests.post object, strict requirment, ...)
    If strict requirment = 0 - every success code will be enough """
    for i in range(1, len(r)+1, 2):
        if r[i] == 0:
            if not(r[i-1]):
                return False
            return True
        if r[i-1].status_code != r[i]:
            return False
    return True

def request_status(*r):
    """ r - (requests.post object, strict requirment, ...)
    If strict requirment = 0 - every success code will be enough 
    Return {"Success": , "json": }"""
    text = r[0].text
    for i in range(2, len(r), 2):
        text += r[i].text

    return {"Success": is_success(*r), "json": text} 

def success_status(success: bool, text: str):
    return {"Success": success, "json": text} 


def clean_yaml(name: str):
    data2 = {}
    with open(name, "r") as file:
        data = yaml.safe_load(file)
        data2 = data.copy()
    clean_dict(data2)
    with open(name, "w") as file:
        yaml.safe_dump(data2, file)


def clean_dict(data: dict):
    data2 = data.copy()
    # for i in data.keys():
    #     if isinstance(data[i], dict):
    #         data2[i] = clean_dict(data2[i])
    #     if not data[i]:
    #         del data2[i]
    #         continue
    return data2