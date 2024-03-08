import OAuthSession as auth
import logs.project_logger as log
import Classes as cl

""" Для корректной работы моих функций вам нужно создать свое Степик API приложение
    по следующей ссылке: https://stepik.org/oauth2/applications/ (client type = confidential, authorization grant type = client credentials)
    Далее запускайте pytest с аргументом -s для первого раза
    pytest -m local  -  запустит тесты функций не требующих подключение к интернету
    pytest -m network  -  запустит тесты требующие подключение к интернету
"""

# c = cl.Course("Class usage 22")
# course = co.Course_manager(c)
# wre = cl.Lesson("1 Lesson class")
# l1 = [wre, cl.Lesson("2 lessons class")]
# a = cl.Section("First section", lessons=l1)
# course.create_section(a)
# course.save()
# # s = auth.OAuthSession()
# # course.auth(s)
# # course.send_all()

c = cl.Course("Classes classes")
l = [cl.Lesson("Fafa"), cl.Lesson("Oiao")]
d = cl.Section("SectiIONNN", lessons=l)
c.create_section(d)
c.save()
c.auth(auth.OAuthSession())
c.send_all()