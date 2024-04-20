import yaml
from information_for_table import Class
import src.API.OAuthSession as auth

your_class_id = 0
t = Class(your_class_id, auth.OAuthSession())   #enter your_class_id and, if you need, args to OAuthSession
#t.update_info_lessons()
t.get_table()
print(t.class_id, t.course_id)

with open(f'klass_{t.class_id}.yaml', mode='r', encoding='utf-8') as fh:
    info_klass = yaml.load(fh, Loader=yaml.FullLoader)  #klass grades

with open(f'src/data/course_{t.course_id}.yaml', mode='r', encoding='utf-8') as fh:
    info_course = yaml.load(fh, Loader=yaml.FullLoader) #course structure

""" This part creates an html file, describing a table """
file_html = open("table1.html", "w", encoding="utf-8")
file_html.write("<!DOCTYPE html>\n<html>\n<head>\n<meta charset='UTF-8'>\n<style>\ntable {\n  font-family: arial, sans-serif;\n  border-collapse: collapse;\n  width: 100%;\n}\n\ntd, th {\n  border: 1px solid #dddddd;\n  text-align: left;\n  padding: 8px;\n}\n\ntr:nth-child(even) {\n  background-color: #dddddd;\n}\n</style>\n</head>\n<body>\n\n")
file_html.write(f"<h2>Класс id:{t.class_id}</h2>\n  <h3>Курс id:{t.course_id}  Название курса:{t.course_name}</h3>\n\n  <table>\n  <tr>\n    <th>Id</th>\n    <th>Имя</th>\n    <th>Всего</th>\n")

section_structure = []
for section in info_course["Course"]["sections"]:
    file_html.write(f"    <th><button type='button'>{section['title']}</button></th>\n")
    steps_of_section = []
    for lesson in section["lessons"]:
            lesson_id = lesson["id"]
            for step in range(len(lesson["steps"])):
                try:
                    name_step = str(lesson_id)+"-"+str(step+1)
                    if info_klass[0][name_step]:
                        steps_of_section.append(name_step)
                except:
                    pass
    section_structure.append(steps_of_section)
file_html.write(f"  </tr>\n  <tr>\n")

for student in range(len(info_klass)):
    course_result = 0
    file_html.write(f"  <tr>\n    <td>{info_klass[student].get('id')}</td>\n    <td>{info_klass[student].get('name')}</td>\n")
    results_one_student = ""
    for section in range(len(info_course["Course"]["sections"])):
        section_result = 0
        for step in section_structure[section]:
            try:
                section_result += info_klass[student][str(step)]["score"]
            except:
                pass
        course_result += section_result        
        results_one_student += f"    <td>{int(section_result)}</td>\n"
    file_html.write(f"    <td>{int(course_result)}</td>\n" + results_one_student)
    file_html.write(f"</tr>\n")


file_html.write("</table>\n\n</body>\n</html>")
file_html.close()