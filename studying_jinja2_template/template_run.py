
import jinja2

def first():
    template = templateEnv.get_template("template_test1.html")
    return template.render() 

def second():
    cap_title_list = ["Красная кепка", "Чёрная кепка", "Ещё одна чёрная кепка"] 
    cap_text_list = ["$ 100.00", "$ 120.00", "$ 90.00",]
    template = templateEnv.get_template("template_test2.html")
    return template.render(
        cap_title_list=cap_title_list,
        cap_text_list=cap_text_list)


templateLoader = jinja2.FileSystemLoader(searchpath="./")
templateEnv = jinja2.Environment(loader=templateLoader)
outputText = first() + second()
with open(f'test_site.html', mode='w', encoding='utf-8') as fh:
    fh.write(outputText)