import pytest
from markdown_parsing import Lesson, lesson_module, step_module

@pytest.mark.markdown
def test_TitleOneSpace():
    input_text = """# Lesson with nothing (To be honest, I'm not sure what should I do)"""
    parse_lesson = lesson_module()
    result_lesson = parse_lesson.parseString(input_text)
    assert result_lesson.name == "Lesson with nothing (To be honest, I'm not sure what should I do)"


@pytest.mark.markdown
def test_TitleMoreThanOneSpace():
    input_text = """#         Lesson with nothing (To be honest, I'm not sure what should I do)"""
    parse_lesson = lesson_module()
    result_lesson = parse_lesson.parseString(input_text)
    assert result_lesson.name == "Lesson with nothing (To be honest, I'm not sure what should I do)"


@pytest.mark.markdown
def test_StepOneSpace():
    input_text = """
# Lesson with nothing (To be honest, I'm not sure what should I do)
## QUIZ title
    """
    parse_lesson = lesson_module()
    result_lesson = parse_lesson.parseString(input_text)
    parse_step = step_module()
    result_step = parse_step.parseString(input_text)
    assert result_lesson.name == "Lesson with nothing (To be honest, I'm not sure what should I do)"
    assert result_step.type == "QUIZ"
    assert result_step.name == "title"


@pytest.mark.markdown
def test_StepMoreThanOneSpace():
    input_text = """
#     Lesson with nothing (To be honest, I'm not sure what should I do)
##     QUIZ title
    """
    parse_lesson = lesson_module()
    result_lesson = parse_lesson.parseString(input_text)
    parse_step = step_module()
    result_step = parse_step.parseString(input_text)
    assert result_lesson.name == "Lesson with nothing (To be honest, I'm not sure what should I do)"
    assert result_step.type == "QUIZ"
    assert result_step.name == "title"


@pytest.mark.markdown
def test_StepWithoutType():
    input_text = """
# Lesson with nothing (To be honest, I'm not sure what should I do)
## title
    """
    parse_lesson = lesson_module()
    result_lesson = parse_lesson.parseString(input_text)
    parse_step = step_module()
    result_step = parse_step.parseString(input_text)
    assert result_lesson.name == "Lesson with nothing (To be honest, I'm not sure what should I do)"
    assert result_step.type == "" # ПОМЕНЯТЬ ПОТОМ НА TEXT
    assert result_step.name == "title"