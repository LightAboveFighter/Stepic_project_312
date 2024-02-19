import json
import requests

client_id = ""
client_secret = ""
token = ""

def set_user_variables(cl_id, cl_secret):
    # 2. Get a token
    global client_id
    global client_secret
    global token
    client_id = cl_id
    client_secret = cl_secret

    auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
    resp = requests.post('https://stepik.org/oauth2/token/', data={'grant_type': 'client_credentials'}, auth=auth)
    token = json.loads(resp.text)['access_token']
    Session_inf = open("Session_information.txt", "w")
    Session_inf.write(f"{client_id=}\n{client_secret=}\n{token=}")
    Session_inf.close()

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
    global client_id
    global client_secret
    global token
    if client_id != "" and client_secret != "" and token != "":
        return
    Session_inf = open("Session_information.txt", "r").read()

    def find_new():
        nonlocal Session_inf
        index_0 = Session_inf.find("'")
        Session_inf = Session_inf[:index_0] + Session_inf[index_0+1:]
        index_1 = Session_inf.find("'")
        Session_inf = Session_inf[:index_1] + Session_inf[index_1+1:]

        ans = Session_inf[index_0:index_1]
        Session_inf = Session_inf[index_1:]
        return ans
    
    client_id = find_new()
    client_secret = find_new()
    token = find_new()    

def create_step(lesson_id: int, position: int, text:str, check=False, get_json=False):
    """(Position inside your lesson, Name of your step, Text inside your step)
    check = true - print "Success" or "Failed" of creation step
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
#set_user_variables("", "")

# create_step(1226398, 1, "text", "Это был Алекс2 из Питона", check=True)

# create_lesson(389525, 4, "Python lesson", check=True, get_json=True)
print(create_step(1236965, 3, "Мяу, у меня лапки", check=True, get_json=True))
