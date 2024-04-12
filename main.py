import src.API.Classes as cl
import src.API.OAuthSession as auth
from src.API.Step import StepChoice as SC
""" Для корректной работы моих функций вам нужно создать свое Степик API приложение
    по следующей ссылке: https://stepik.org/oauth2/applications/ (client type = confidential, authorization grant type = client credentials)
    Далее запускайте pytest с аргументом -s для первого раза
    pytest -m local  -  запустит тесты функций не требующих подключение к интернету
    pytest -m network  -  запустит тесты требующие подключение к интернету
"""