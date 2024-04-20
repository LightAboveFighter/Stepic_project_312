from information_for_table import Class
import src.API.OAuthSession as auth
import os
import yaml

def do_a_site_with_tables(your_class_id: int, update: bool)->None:
    """Creates an html file, which shows score tables of your class divided into sections
    If you need to update information about course or scores, use update=True"""
    t = Class(your_class_id, auth.OAuthSession())   #enter your_class_id and, if you need, args to OAuthSession
    if update:
        t.update_info_lessons()
    t.get_table()
    print(t.class_id, t.course_id)

    with open(f'klass_{t.class_id}.yaml', mode='r', encoding='utf-8') as fh:
        info_klass = yaml.load(fh, Loader=yaml.FullLoader)  #klass grades

    with open(f'src/data/course_{t.course_id}.yaml', mode='r', encoding='utf-8') as fh:
        info_course = yaml.load(fh, Loader=yaml.FullLoader) #course structure

    """ This part creates an html file, describing a table """
    html_name = f"table_{t.class_id}.html"
    if os.path.exists(html_name):
        file_html = open(html_name, "w", encoding="utf-8")
    else:
        file_html = open(html_name, "x", encoding="utf-8")

    file_html.write("<!DOCTYPE html>\n<html>\n<head>\n<meta charset='UTF-8'>\n<style>\ntable {\n  font-family: arial, sans-serif;\n  border-collapse: collapse;\n  width: 100%;\n}\n\ntd, th {\n  border: 1px solid #dddddd;\n  text-align: left;\n  padding: 8px;\n}\n\ntr:nth-child(even) {\n  background-color: #dddddd;\n}\n</style>\n</head>\n<body>\n\n")
    file_html.write(f"<h1>\nКурс: {info_course['Course']['title']}</h1>\n<h2>Курс id:{t.course_id}</h2>\n<h2>Класс id:{t.class_id}</h2>\n<table>\n  <tr>\n    <th>Id</th>\n    <th>Имя</th>\n    <th>Всего</th>\n")
    course_structure = []
    for section in info_course['Course']['sections']:   #title part of the big course table
        file_html.write(f"    <th>{section['title']}</th>\n")
        steps_of_section = []
        for lesson in section['lessons']:
                lesson_id = lesson['id']
                for step in range(len(lesson['steps'])):
                    try:
                        name_step = str(lesson_id)+"-"+str(step+1)
                        if info_klass[0][name_step]:
                            steps_of_section.append(name_step)
                    except:
                        pass
        course_structure.append(steps_of_section)
    file_html.write(f"  </tr>\n")

    for student in range(len(info_klass)):  #students and scores of a big course table
        course_result = 0
        file_html.write(f"  <tr>\n    <td>{info_klass[student].get('id')}</td>\n    <td>{info_klass[student].get('name')}</td>\n")
        results_one_student = ""
        for section in range(len(info_course['Course']['sections'])):
            section_result = 0
            for step in course_structure[section]:
                try:
                    section_result += info_klass[student][str(step)]['score']
                except:
                    pass
            course_result += section_result        
            results_one_student += f"    <td>{int(section_result)}</td>\n"
        file_html.write(f"    <td>{int(course_result)}</td>\n" + results_one_student)
        file_html.write(f"  </tr>\n")
    file_html.write("</table>\n\n")

    for section in range(len(info_course['Course']['sections'])):   #hidden section tables
        file_html.write(f"<details>\n  <summary>{str(info_course['Course']['sections'][section]['title'])}</summary>\n  <table>\n")
        title_lessons_info = "  <tr>\n    <th rowspan='2'>Id</th>\n    <th rowspan='2'>Имя</th>\n    <th rowspan='2'>Всего</th>\n"
        title_steps_info = "  <tr>\n"

        for lesson in range(len(info_course['Course']['sections'][section]['lessons'])):    #title part of the table
            flag = 0
            amount_steps_in_lesson = 0
            for step in range(1, len(info_course['Course']['sections'][section]['lessons'][lesson]["steps"])+1):
                lesson_step = str(info_course['Course']['sections'][section]['lessons'][lesson]['id']) + "-" + str(step)
                if lesson_step in course_structure[section]:
                    amount_steps_in_lesson += 1
                    title_steps_info += f"    <th>Step {step}</th>\n"
                    flag = 1
            if flag == 1:
                title_lessons_info += f"    <th colspan={str(amount_steps_in_lesson)} text-align='center'>{info_course['Course']['sections'][section]['lessons'][lesson]['title']}</th>\n"
        title_lessons_info += "  </tr>\n"
        file_html.write(title_lessons_info + title_steps_info)

        steps_info = "  <tr>\n"
        for step in course_structure[section]:  #score part of the table
            steps_info += f"  <th>{step}</th>\n"
        steps_info = "  </tr>\n"
        table_info = ""
        for student in range(len(info_klass)):
            section_score = 0
            student_score_info = ""
            for step in course_structure[section]:
                step_score = 0
                try:
                    step_score = int(info_klass[student][step]['score'])
                except:
                    pass
                section_score += step_score
                student_score_info += f"    <td>{step_score}</td>\n"
            table_info += f"  <tr>\n    <td>{info_klass[student].get('id')}</td>\n    <td>{info_klass[student].get('name')}</td>\n    <td>{section_score}</td>\n" + student_score_info + "  </tr>\n"
        file_html.write(steps_info + table_info + " </table>\n</details>\n\n")



    file_html.write("</body>\n</html>")
    file_html.close()