import requests
import json
import yaml 
import os

class OAuthSession:

    def __init__(self, client_id="", client_secret=""):

        if os.path.exists("Client_information.yaml") and (client_id == "" or client_secret == ""): 
            with open("Client_information.yaml", "r") as file:
                data = yaml.safe_load(file)
                client_id = data["client_id"]
                client_secret = data["client_secret"]
        else:
            with open("Client_information.yaml", "x") as file:
                yaml.dump({"client_id": client_id, "client_secret": client_secret}, file)

        auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
        resp = requests.post('https://stepik.org/oauth2/token/', data={'grant_type': 'client_credentials'}, auth=auth)
        self.__token = json.loads(resp.text)['access_token']

        next_api = "https://stepik.org/teach/courses"
        r = requests.get(next_api)
        self.__cookie = f'csrftoken={r.cookies["csrftoken"]}; sessionid={r.cookies["sessionid"]}'


    @property
    def token(self):
        return self.__token
    
    @property
    def cookie(self):
        return self.__cookie
    
    # @token.setter
    # def set_token(self):
    #     file = open("Client_information.yaml", "r")
    #     data = yaml.safe_load(file)
    #     client_id = data["client_id"]
    #     client_secret = data["client_data"]

    #     auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
    #     resp = requests.post('https://stepik.org/oauth2/token/', data={'grant_type': 'client_credentials', 'x-csrf-token': 'Fetch'}, auth=auth)
    #     self.__token = json.loads(resp.text)['access_token']

    def headers(self):
        return {'Content-Type': 'application/json', 'Authorization': 'Bearer '+ self.token}