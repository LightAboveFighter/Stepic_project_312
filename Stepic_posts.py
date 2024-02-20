import json
import requests
import yaml

token = ""


def set_user_variables(client_id, client_secret):

    with open("Client_information.yaml", "w") as file:
        yaml.dump({"client_id": client_id, "client_secret": client_secret}, file)

def get_token():
    global token
    client_id = ""
    client_secret = ""
    with open("Client_information.yaml", "r") as file:
        data = yaml.safe_load(file)
        client_id = data["client_id"]
        client_secret = data["client_secret"]
    auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
    resp = requests.post('https://stepik.org/oauth2/token/', data={'grant_type': 'client_credentials'}, auth=auth)
    token = json.loads(resp.text)['access_token']
    

def send_status(*r):
    """ r - (requests.post object, strict requirment, ...)
    If strict requirment = 0 - every success code will be enough """
    for i in range(1, len(r)+1, 2):
        if r[i] == 0:
            if not(r[i-1]):
                print("Failed")
                return
            print("Success")
            return
        if r[i-1].status_code != r[i]:
            print("Failed") 
            return
    print("Success")

# # 2. Get a token
# auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
# resp = requests.post('https://stepik.org/oauth2/token/', data={'grant_type': 'client_credentials'}, auth=auth)
# token = json.loads(resp.text)['access_token']

def __update_session_inf__():
    global token

    if token != "":
        return
    get_token() 
    

def create_step(lesson_id: int, position: int, text:str, check=False, get_json=False):
    """(Position inside your lesson, Name of your step, Text inside your step)
    check = true - print "success" or "Failed" of creation step
    get_json = true - return json with this operation"""
    __update_session_inf__()
    global token

    api_url = 'https://stepik.org/api/step-sources'

    data = {
	    "stepSource": {
		"block": {
			"name": "text",
			"text": f"<p>{text}</p>"
		    },
		"lesson": lesson_id,
		"position": position
	    }
    }
    # Use POST to create new objects
    r = requests.post(api_url, headers={'Authorization': 'Bearer '+ token}, json=data)

    if check:
        send_status(r, 201)
    if get_json: return r.text # – should print the lesson's json (with lots of properties)
    return None

def create_lesson(section_id: int, position: int, title: str, check=False, get_json=False):
    """ Returns created lesson's id """
    __update_session_inf__()
    global token

    api_url = 'https://stepik.org/api/lessons'
    data = {
        'lesson': {
            'title': title
        }
    }
    # Use POST to create new objects
    r = requests.post(api_url, headers={'Authorization': 'Bearer '+ token}, json=data)
    lesson_id = r.json()['lessons'][0]['id']

    api_url = 'https://stepik.org/api/units'
    data = {
        "unit": {
            "position": position,
            "lesson": lesson_id,
            "section": section_id
        }
    }

    r2 = requests.post(api_url, headers={'Authorization': 'Bearer '+ token}, json=data)
    if check: send_status(r, 201, r2, 0)     # r.status_code() should be 201 (HTTP Created)
    if get_json: return r.text + r2.text
    return lesson_id

set_user_variables("", "")
get_token()
# create_step(1226398, 1, "text", "Это был Алекс2 из Питона", check=True)

# create_lesson(389525, 4, "Python lesson", check=True, get_json=True)
print(create_step(1237002, 1, "Yaml check", check=True, get_json=True))