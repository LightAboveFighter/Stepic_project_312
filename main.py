import src.API.Classes as cl
import src.API.OAuthSession as auth
from src.API.Step import StepChoice as SC
""" Для корректной работы моих функций вам нужно создать свое Степик API приложение
    по следующей ссылке: https://stepik.org/oauth2/applications/ (client type = confidential, authorization grant type = client credentials)
    Далее запускайте pytest с аргументом -s для первого раза
    pytest -m local  -  запустит тесты функций не требующих подключение к интернету
    pytest -m network  -  запустит тесты требующие подключение к интернету
"""

# a = cl.Lesson("2_7_global.md")
# a.save()
# a.send(auth.OAuthSession(), send_all=True)
# a.save()

# a = SC("Choice title", 1243955, {"text": "Choose one of this variants:"}, True, [SC.Option(True, "Text 1 tutu"), SC.Option(False, "Text 2 fls", ":("), SC.Option(False, "dgdrg", "srgsgsdf")], cost=19)
# print(a.send(1, auth.OAuthSession()))
# # a.save()

a = cl.Course()
a.load_from_net(198266, False, auth.OAuthSession())
a.save()