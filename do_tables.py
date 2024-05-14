from information_for_table import Class
import src.API.OAuthSession as auth
import os
import yaml
import jinja2

def do_a_site_with_tables(your_class_id: int, update: bool, client_id="", client_secret="")->None:
    """Creates an html file, which shows score tables of your class divided into sections
    If you need to update information about course or scores, use update=True"""

    if client_id and client_secret:   #enters args to OAuthSession, if needed
        t = Class(your_class_id, auth.OAuthSession(client_id, client_secret))
    else:
        t = Class(your_class_id, auth.OAuthSession())
        
    if update:
        t.update_info_lessons()
    t.get_table()
    print("class id:", t.class_id, ", course_id:", t.course_id)

    with open(f'klass_{t.class_id}.yaml', mode='r', encoding='utf-8') as fh:
        info_klass = yaml.load(fh, Loader=yaml.FullLoader)  #klass grades

    with open(f'src/data/course_{t.course_id}.yaml', mode='r', encoding='utf-8') as fh:
        info_course = yaml.load(fh, Loader=yaml.FullLoader) #default course structure

    course_structure = get_course_structure(info_course, info_klass)    #more cofortable course structure

    templateLoader = jinja2.FileSystemLoader(searchpath="templates/")
    templateEnv = jinja2.Environment(loader=templateLoader)
    html_name = f"table_{t.class_id}.html"  #main file with the site
    open_flag = "w" if os.path.exists(html_name) else "x"
    with open(html_name, open_flag, encoding='utf-8') as fh:
        outputText = do_course_table(t, info_course, info_klass, course_structure, templateEnv) + do_section_tables(t, info_course, info_klass, course_structure, templateEnv)
        fh.write(outputText)


def get_course_structure(info_course: dict, info_klass: list)->list:
    """Mentions only functional steps of the course to evaluate them"""
    course_structure = []
    for section in info_course['Course']['sections']:
        steps_of_section = []
        for lesson in section['lessons']:
                lesson_id = lesson['id']
                for step in range(len(lesson['steps'])):    #don’t need a global step number, but a serial number in the lesson
                    name_step = str(lesson_id)+"-"+str(step+1)  #it is how they writen in received course_grades files
                    flag = 0
                    for student in info_klass:
                        if student.get(name_step):
                            flag = 1
                            break
                    if flag == 1:
                        steps_of_section.append(name_step)

        course_structure.append(steps_of_section)
    return course_structure


def do_course_table(t: Class, info_course: dict, info_klass: list, course_structure: list, templateEnv)->str:
    """Does the main table with section scores in order of highest score"""

    section_names = []
    for section in info_course['Course']['sections']:
        section_names.append(section['title'])
    student_names = []
    course_results = []
    all_section_results = []
    for student in range(len(info_klass)):  #score part of main table
        course_result = 0
        student_names.append(info_klass[student].get('name'))
        results_one_student = []
        for section in range(len(info_course['Course']['sections'])):
            section_result = 0
            for step in course_structure[section]:
                if info_klass[student].get(str(step)):
                    section_result += info_klass[student][str(step)]['score']
            course_result += section_result
            results_one_student.append(int(section_result))
        course_results.append(int(course_result))
        all_section_results.append(results_one_student)

    template = templateEnv.get_template("main_template.html")
    return template.render(
        title=t.class_id,
        course_name=info_course['Course']['title'],
        course_id=t.course_id,
        class_id=t.class_id,
        section_names=section_names,
        student_ids=t.student_ids,
        student_names=student_names,
        course_results=course_results,
        all_section_results=all_section_results)


def do_section_tables(t: Class, info_course: dict, info_klass: list, course_structure: list, templateEnv)->str:
    """Does a table with step scores of one section in order of highest course score"""

    section_tables = ''
    for section in range(len(info_course['Course']['sections'])):
        title_steps = []
        steps_in_section = []
        lesson_names = []
        for lesson in range(len(info_course['Course']['sections'][section]['lessons'])):    #title part of the table
            flag = 0
            amount_steps_in_lesson = 0
            for step in range(1, len(info_course['Course']['sections'][section]['lessons'][lesson]["steps"])+1):
                lesson_step = str(info_course['Course']['sections'][section]['lessons'][lesson]['id']) + "-" + str(step)
                if lesson_step in course_structure[section]:    #to know if this lesson containes some functional steps
                    amount_steps_in_lesson += 1
                    flag = 1
            if flag == 1:
                lesson_names.append(info_course['Course']['sections'][section]['lessons'][lesson]['title'])
                steps_in_section.append(amount_steps_in_lesson)  #to know width of lesson_name cell     
        for step in course_structure[section]:
            title_steps.append(step[step.index("-")+1:]) #only step numbers, without mentioning lessons

        student_names = []
        section_scores = []
        section_steps_scores = []
        for student in range(len(info_klass)):  #score part of the table
            section_score = 0
            student_score_info = []
            for step in course_structure[section]:
                if info_klass[student].get(str(step)):
                    step_score = info_klass[student][step].get('score')
                    if str(step_score) == str(int(step_score)):
                        student_score_info.append("-")  #if student hasn't tryed to complete the step
                    else:
                        student_score_info.append(int(step_score))  #if he/she/they has some score, even 0
                else:
                    student_score_info.append("-")
                section_score += step_score
            student_names.append(info_klass[student].get('name'))
            section_scores.append(int(section_score))
            section_steps_scores.append(student_score_info)

        section_template = templateEnv.get_template("section_template.html")
        section_tables += section_template.render(
            section_name=info_course['Course']['sections'][section]['title'],
            lesson_names=lesson_names,
            amount_steps=steps_in_section,
            section_steps=title_steps,
            student_ids=t.student_ids,
            student_names=student_names,
            section_scores=section_scores,
            section_steps_scores=section_steps_scores) + "\n"

    template = templateEnv.get_template("dop_template.html")
    return template.render(
        section_tables=section_tables)

