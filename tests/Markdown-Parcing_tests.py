import pytest
from src.markdown.data_lesson import DataLesson
from src.markdown.schemas import ParsingModuleSchema
from src.markdown import data_steps
from src.markdown.data_steps import *
# data_steps import DataStepCreationSchema, DataStepText, DataStepChoice, DataStepQuiz

# """
# #            Lesson Text Blabla    gukddthstfdg
# lesson = 763259629
# ##       TEXT      sdhgosdrhofslkdf
# jdhrg iohdrkfrjsdf
# fdgrgerdg fgdg
# """

# """
# #            Lesson Text Blabla    gukddthstfdg
# lang = Python
# lesson = 763259629
# ##       TEXT      sdhgosdrhofslkdf
# jdhrg iohdrkfrjsdf
# fdgrgerdg fgdg
# """

# Как отделить общую подсказку в конце и просто подсказку после последнего ответа а????

# voprosy s oformleniem pro хинт и шаффл

# А должно быть фичей што перезаписывается лейблы A, B, C??

@pytest.mark.markdown
def test_Text1():
    input_text =\
"""## TEXT sdhgosdrhofslkdf
jdhrgiohdrkfrjsdf
fdgrgerdgfgdg"""
    expected = {
        "step_name": sdhgosdrhofslkdf,
        "id": None,
        "text": "jdhrgiohdrkfrjsdf\nfdgrgerdgfgdg"
    }
    input_text = input_text.split('\n')
    dst_inf = ParsingModuleSchema.step().parseString(input_text[0])
    input_text = input_text[1:]
    dst = DataStepCreationSchema.create_step(dst_inf.type, dst_inf.name)
    dst.add_info(input_text)
    assert isinstance(dst, DataStepText)
    assert dst.as_dict() == expected


@pytest.mark.markdown
def test_Text2():
    input_text =\
"""##       TEXT      sdhgosdrhofslkdf
jdhrg iohdrkfrjsdf
fdgrgerdg fgdg"""
    expected = {
        "step_name": sdhgosdrhofslkdf,
        "id": None,
        "text": "jdhrg iohdrkfrjsdf\nfdgrgerdg fgdg"
    }
    input_text = input_text.split('\n')
    dst_inf = ParsingModuleSchema.step().parseString(input_text[0])
    input_text = input_text[1:]
    dst = DataStepCreationSchema.create_step(dst_inf.type, dst_inf.name)
    dst.add_info(input_text)
    assert isinstance(dst, DataStepText)
    assert dst.as_dict() == expected


@pytest.mark.markdown
def test_Text3():
    input_text =\
"""## sdhgosdrhofslkdf
jdhrgiohdrkfrjsdf
fdgrgerdgfgdg"""
    expected = {
        "step_name": sdhgosdrhofslkdf,
        "id": None,
        "text": "jdhrgiohdrkfrjsdf\nfdgrgerdgfgdg"
    }
    input_text = input_text.split('\n')
    dst_inf = ParsingModuleSchema.step().parseString(input_text[0])
    input_text = input_text[1:]
    dst = DataStepCreationSchema.create_step(dst_inf.type, dst_inf.name)
    dst.add_info(input_text)
    assert isinstance(dst, DataStepText)
    assert dst.as_dict() == expected


# Нужно будет менять
@pytest.mark.markdown
def test_Choice1():
    input_text =\
"""## CHOICE sdhgosdrhofslkdf
Question text?
+) `s == p`
-) `*s == *p`
-) `s[0] == p[0]`"""
    expected = {
        "step_name": sdhgosdrhofslkdf,
        "id": None,
        "text": "Question text?",
        "variants": [DataStepChoice.Variant("s == p", True), DataStepChoice.Variant("*s == *p", False), DataStepChoice.Variant("s[0] == p[0]", False)],
        "step_addons": {"SHUFFLE": "true", "HINT": None}
    }
    input_text = input_text.split('\n')
    dst_inf = ParsingModuleSchema.step().parseString(input_text[0])
    input_text = input_text[1:]
    dst = DataStepCreationSchema.create_step(dst_inf.type, dst_inf.name)
    dst.add_info(input_text)
    assert isinstance(dst, DataStepChoice)
    assert dst.as_dict() == expected


@pytest.mark.markdown
def test_Choice2():
    input_text =\
"""##        CHOICE sdhgosdrhofslkdf
?
+) `s == p`
-) `*s == *p`
-) `s[0] == p[0]`"""
    expected = {
        "step_name": sdhgosdrhofslkdf,
        "id": None,
        "text": "?",
        "variants": [DataStepChoice.Variant("s == p", True), DataStepChoice.Variant("*s == *p", False), DataStepChoice.Variant("s[0] == p[0]", False)],
        "step_addons": {"SHUFFLE": "true", "HINT": None}
    }
    input_text = input_text.split('\n')
    dst_inf = ParsingModuleSchema.step().parseString(input_text[0])
    input_text = input_text[1:]
    dst = DataStepCreationSchema.create_step(dst_inf.type, dst_inf.name)
    dst.add_info(input_text)
    assert isinstance(dst, DataStepChoice)
    assert dst.as_dict() == expected

@pytest.mark.markdown
def test_Choice3():
    input_text =\
"""## CHOICE sdhgosdrhofslkdf
Question text?
+) `s == p`
-) `*s == *p`
-) `s[0] == p[0]`

HINT: подсказка"""
    expected = {
        "step_name": sdhgosdrhofslkdf,
        "id": None,
        "text": "Question text?",
        "variants": [DataStepChoice.Variant("s == p", True), DataStepChoice.Variant("*s == *p", False), DataStepChoice.Variant("s[0] == p[0]", False, "подсказка")],
        "step_addons": {"SHUFFLE": "true", "HINT": None}
    }
    input_text = input_text.split('\n')
    dst_inf = ParsingModuleSchema.step().parseString(input_text[0])
    input_text = input_text[1:]
    dst = DataStepCreationSchema.create_step(dst_inf.type, dst_inf.name)
    dst.add_info(input_text)
    assert isinstance(dst, DataStepChoice)
    assert dst.as_dict() == expected

@pytest.mark.markdown
def test_Choice4():
    input_text =\
"""## CHOICE sdhgosdrhofslkdf
Question text?
+) `s == p`
HINT: частная подсказка
-) `*s == *p`
-) `s[0] == p[0]`"""
    expected = {
        "step_name": sdhgosdrhofslkdf,
        "id": None,
        "text": "Question text?",
        "variants": [DataStepChoice.Variant("s == p", True, "частная подсказка"), DataStepChoice.Variant("*s == *p", False), DataStepChoice.Variant("s[0] == p[0]", False)],
        "step_addons": {"SHUFFLE": "true", "HINT": None}
    }
    input_text = input_text.split('\n')
    dst_inf = ParsingModuleSchema.step().parseString(input_text[0])
    input_text = input_text[1:]
    dst = DataStepCreationSchema.create_step(dst_inf.type, dst_inf.name)
    dst.add_info(input_text)
    assert isinstance(dst, DataStepChoice)
    assert dst.as_dict() == expected


@pytest.mark.markdown
def test_Choice5():
    input_text =\
"""## CHOICE sdhgosdrhofslkdf
Question text?
+) `s == p`
-) `*s == *p`
-) `s[0] == p[0]`

SHUFFLE: false
HINT: общая подсказка"""
    expected = {
        "step_name": sdhgosdrhofslkdf,
        "id": None,
        "text": "Question text?",
        "variants": [DataStepChoice.Variant("s == p", True), DataStepChoice.Variant("*s == *p", False), DataStepChoice.Variant("s[0] == p[0]", False)],
        "step_addons": {"SHUFFLE": "false", "HINT": "общая подсказка"}
    }
    input_text = input_text.split('\n')
    dst_inf = ParsingModuleSchema.step().parseString(input_text[0])
    input_text = input_text[1:]
    dst = DataStepCreationSchema.create_step(dst_inf.type, dst_inf.name)
    dst.add_info(input_text)
    assert isinstance(dst, DataStepChoice)
    assert dst.as_dict() == expected


@pytest.mark.markdown
def test_Quiz1():
    input_text =\
"""## QUIZ Сравнение указателей
Do you have giraffe?
A. `НУ Yes`
HINT: подсказка

B. `А ху asking`

C. `Thank you for your question`

ANSWER: A"""
    input_text = input_text.split('\n')
    dst_inf = ParsingModuleSchema.step().parseString(input_text[0])
    input_text = input_text[1:]
    dst = DataStepCreationSchema.create_step(dst_inf.type, dst_inf.name)
    dst.add_info(input_text)
    assert isinstance(dst, DataStepQuiz) == True
    assert dst.step_name == "Сравнение указателей"
    assert dst.text == "Do you have giraffe?"
    assert dst.variants[0].text == "НУ Yes"
    assert dst.variants[0].label == "A"
    assert dst.variants[0].feedback == "подсказка"
    assert dst.variants[1].text == "`А ху asking`"
    assert dst.variants[1].label == "B"
    assert dst.variants[1].feedback == None
    assert dst.variants[2].text == "`Thank you for your question`"
    assert dst.variants[2].label == "C"
    assert dst.variants[2].feedback == None
    assert dst.step_addons["SHUFFLE"] == "true"
    assert dst.step_addons["ANSWER"] == "A"


@pytest.mark.markdown
def test_Quiz2():
    input_text =\
"""## QUIZ Сравнение указателей
Question text?
A. `s == p`
HINT: подсказка

B. `*s == *p`

C. `s[0] == p[0]`

SHUFFLE: false
ANSWER: A, C
HINT: подсказка"""
    input_text = input_text.split('\n')
    dst_inf = ParsingModuleSchema.step().parseString(input_text[0])
    input_text = input_text[1:]
    dst = DataStepCreationSchema.create_step(dst_inf.type, dst_inf.name)
    dst.add_info(input_text)
    assert isinstance(dst, DataStepQuiz) == True
    assert dst.step_name == "Сравнение указателей"
    assert dst.text == ["Question text?"]
    assert dst.variants[0].text == "`s == p`"
    assert dst.variants[0].label == "A"
    assert dst.variants[0].feedback == "подсказка"
    assert dst.variants[1].text == "`*s == *p`"
    assert dst.variants[1].label == "B"
    assert dst.variants[1].feedback == None
    assert dst.variants[2].text == "`s[0] == p[0]`"
    assert dst.variants[2].label == "C"
    assert dst.variants[2].feedback == None
    assert dst.step_addons["SHUFFLE"] == "false"
    assert dst.step_addons["ANSWER"] == "A, C"
    assert dst.step_addons["HINT"] == "подсказка"