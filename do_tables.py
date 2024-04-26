from information_for_table import Class
import src.API.OAuthSession as auth
import os
import yaml
import jinja2

def do_a_site_with_tables(your_class_id: int, update: bool)->None:
    """Creates an html file, which shows score tables of your class divided into sections
    If you need to update information about course or scores, use update=True"""

    """Here i prepare everything needed"""
    t = Class(your_class_id, auth.OAuthSession())   #enter args to OAuthSession, if you need
    if update:
        t.update_info_lessons()
    t.get_table()
    print(t.class_id, t.course_id)

    with open(f'klass_{t.class_id}.yaml', mode='r', encoding='utf-8') as fh:
        info_klass = yaml.load(fh, Loader=yaml.FullLoader)  #klass grades

    with open(f'src/data/course_{t.course_id}.yaml', mode='r', encoding='utf-8') as fh:
        info_course = yaml.load(fh, Loader=yaml.FullLoader) #course structure

    course_structure = get_course_structure(info_course, info_klass)

    html_name = f"table_{t.class_id}.html"
    open_flag = "w" if os.path.exists(html_name) else "x"
    with open(html_name, open_flag, encoding="utf-8") as file_html:
        file_html.write(do_course_table(t, info_course, info_klass, course_structure))
        for section in range(len(info_course['Course']['sections'])):
            file_html.write(do_section_table(section, t, info_course, info_klass, course_structure))


def get_course_structure(info_course: dict, info_klass: list)->list:
    """Mentions only functional step of the course to evaluate them"""
    course_structure = []
    for section in info_course['Course']['sections']:
        steps_of_section = []
        for lesson in section['lessons']:
                lesson_id = lesson['id']
                for step in range(len(lesson['steps'])):
                    name_step = str(lesson_id)+"-"+str(step+1)
                    if info_klass[0].get(name_step):
                        steps_of_section.append(name_step)
        course_structure.append(steps_of_section)
    return course_structure


def do_course_table(t: Class, info_course: dict, info_klass: list, course_structure: list)->str:
    """Does the main table with section scores in order of highest score"""

    template = jinja2.Template("""<!DOCTYPE html>
<html>
<head>
<meta charset='UTF-8'>
    <style>
    table {
      font-family: arial, sans-serif;
      border-collapse: collapse;
      width: 100%;
    }
    td, th {
      border: 1px solid #dddddd;
      text-align: left;
      padding: 8px;
    }
    tr:nth-child(even) {
      background-color: #dddddd;
    }
    </style>
</head>
<body>
  <h1>Курс:{{course_name}}</h1>
  <h2>Курс id:{{course_id}}</h2>
  <h2>Класс id:{{class_id}}</h2>
  <table>
    <tr>
      <th>Id</th>
      <th>Имя</th>
      <th>Всего</th>
{{section_names}}
    </tr>
{{students_with_section_scores}}
  </table>
""")
    section_names = ""
    for section in info_course['Course']['sections']:
        section_names += f"      <th>{section['title']}</th>\n"
    student_section_scores = ""
    for student in range(len(info_klass)):  #forming one string of main table
        course_result = 0
        student_section_scores += f"    <tr>\n      <td>{info_klass[student].get('id')}</td>\n      <td>{info_klass[student].get('name')}</td>\n"
        results_one_student = ""
        for section in range(len(info_course['Course']['sections'])):
            section_result = 0
            for step in course_structure[section]:
                if info_klass[student].get(str(step)):
                    section_result += info_klass[student][str(step)]['score']
            course_result += section_result        
            results_one_student += f"      <td>{int(section_result)}</td>\n"  #student's total course score
        student_section_scores += f"      <td>{int(course_result)}</td>\n" + results_one_student + "    </tr>\n"    #section results
    return template.render(
        course_name=info_course['Course']['title'],
        course_id=t.course_id,
        class_id=t.class_id,
        section_names=section_names[:-1],   #removes extra line break
        students_with_section_scores=student_section_scores)


def do_section_table(section: int, t: Class, info_course: dict, info_klass: list, course_structure: list)->str:
    """Does a table with step scores of one section in order of highest course score"""

    template = jinja2.Template("""
<details>
  <summary><big><big>{{section_name}}</big></big></summary>
  <table>
    <tr>
      <th rowspan='2'>Id</th>
      <th rowspan='2'>Имя</th>
      <th rowspan='2'>Всего</th>
{{lesson_names}}
    </tr>
    <tr>
{{title_steps}}
    </tr>
    {{students_with_step_scores}}
  </table>
</details>""")
    title_steps_info = "" 
    title_lessons_info = ""
    steps_info = ""
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
            lesson_name = jinja2.Template("      <th colspan={{amount_steps}} text-align='center'>{{lesson_name}}</th>")
            title_lessons_info += lesson_name.render(amount_steps=amount_steps_in_lesson, lesson_name=info_course['Course']['sections'][section]['lessons'][lesson]['title']) + "\n"        
    for step in course_structure[section]:
        steps_info += f"  <th>{step}</th>\n"
    table_info = ""
    for student in range(len(info_klass)):  #score part of the table
        section_score = 0
        student_score_info = ""
        for step in course_structure[section]:
            step_score = 0
            if info_klass[student].get(str(step)):
                step_score = int(info_klass[student][step].get('score'))
            section_score += step_score
            student_score_info += f"      <td>{step_score}</td>\n"
        student_info = jinja2.Template("""<tr>
      <td>{{student_id}}</td>
      <td>{{student_name}}</td>
      <td>{{section_score}}</td>
{{student_score_info}}
    </tr>
    """)
        table_info += student_info.render(student_id=info_klass[student].get('id'),
        student_name=info_klass[student].get('name'),
        section_score=section_score,
        student_score_info=student_score_info[:-1])   #removes extra line break

    return template.render(
        section_name=info_course['Course']['sections'][section]['title'],
        lesson_names=title_lessons_info[:-1],   #removes extra line break
        title_steps=title_steps_info[:-1],   #removes extra line break
        students_with_step_scores=table_info)
