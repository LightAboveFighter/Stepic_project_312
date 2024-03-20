import yaml

with open('klass.yaml') as fh:
    klass = yaml.load(fh, Loader=yaml.FullLoader)

with open('lesson.yaml') as fh:
    lessons = yaml.load(fh, Loader=yaml.FullLoader)

print(klass[0])
print(lessons[0])

file_html = open("table1.html", "w")
file_html.write("<!DOCTYPE html>\n<html>\n<head>\n<style>\ntable {\n  font-family: arial, sans-serif;\n  border-collapse: collapse;\n  width: 100%;\n}\n\ntd, th {\n  border: 1px solid #dddddd;\n  text-align: left;\n  padding: 8px;\n}\n\ntr:nth-child(even) {\n  background-color: #dddddd;\n}\n</style>\n</head>\n<body>\n\n")
file_html.write("<h3>Course name</h3>\n\n<table>\n  <tr>\n    <th>Users</th>\n")
for i in range(len(lessons)):
    file_html.write(f"    <th>{lessons[i].get('lesson_id')}</th>\n")
file_html.write(f"  </tr>\n  <tr>\n")
for i in range(len(klass)):
    file_html.write(f"  <tr>\n    <td>{klass[i].get('name')}</td>\n    <td>{klass[i].get('Result_lesson1')}</td>\n    <td>{klass[i].get('Result_lesson2')}</td>\n    <td>{klass[i].get('Result_lesson3')}</td>\n  </tr>\n")


file_html.write("</table>\n\n</body>\n</html>")
file_html.close()