from src.API.Classes import Course, Lesson
from src.API.Step import StepCode
from src.API.OAuthSession import OAuthSession
""" Для корректной работы моих функций вам нужно создать свое Степик API приложение
    по следующей ссылке: https://stepik.org/oauth2/applications/ (client type = confidential, authorization grant type = client credentials)
    Далее запускайте pytest с аргументом -s для первого раза
    pytest -m local  -  запустит тесты функций не требующих подключение к интернету
    pytest -m network  -  запустит тесты требующие подключение к интернету
"""

a = Course()
# a.load_from_net(202361, source=True, session=OAuthSession())
a.load_from_file("Py Course.yaml")
# p = Lesson("Wowa Lesson", None, [StepCode("Code Wowa", None, {}, StepCode.Unique("print('Wowa wowa')", 12, 124, "#enter your code", [ ["!", "Wowa wowa"], ["?", "Wowa wowa!!!!" ]], 1))])
# a.create_lesson(p, 1)
# a.save()
a.send_all(session=OAuthSession())