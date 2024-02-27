import requests
import json

auth = requests.auth.HTTPBasicAuth(input(), input())
resp = requests.post('https://stepik.org/oauth2/token/', data={'grant_type': 'client_credentials'}, auth=auth)
token = json.loads(resp.text)['access_token']

next_api = "https://stepik.org/teach/courses"
r = requests.get(next_api)
cookie = f'csrftoken={r.cookies["csrftoken"]}; sessionid={r.cookies["sessionid"]}'
print(cookie)

url = "https://stepik.org/api/sections"

payload = json.dumps(
    {
    "section": {
        "position": 7,
        "title": "DAS",
        "description": "AQW",
        "course": "198026"
        }
    }
)
headers = {
  'Content-Type': 'application/json',
  'Authorization': f'Bearer {token}',
  "Cookie": cookie
}
print(headers)

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
print(response.status_code)

# headers = {
#   'Content-Type': 'application/json',
#   'Authorization': f'Bearer {token}'
#   }

# url = "https://stepik.org/api/courses/198271"

# r = requests.delete(url, headers=headers)
# print(r.status_code)
# print(r.text)
