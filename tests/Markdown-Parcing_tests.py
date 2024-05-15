from src.markdown.data_lesson import DataLesson
from src.markdown.steps.data_step_til import DataStepTaskinline
from src.markdown.steps.data_step_choice import DataStepChoice
from src.markdown.steps.data_step_quiz import DataStepQuiz
from src.markdown.steps.data_step_text import DataStepText
from src.markdown.schemas import ParsingModuleSchema
from src.markdown.data_step_creation import DataStepCreationSchema
import pyparsing as pp
import pytest

@pytest.mark.markdown
def test_Text1():
    input_text =\
"""## TEXT sdhgosdrhofslkdf
jdhrgiohdrkfrjsdf
fdgrgerdgfgdg"""
    expected = {
        "step_name": "sdhgosdrhofslkdf",
        "id": None,
        "text": "jdhrgiohdrkfrjsdffdgrgerdgfgdg"
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
        "step_name": "sdhgosdrhofslkdf",
        "id": None,
        "text": "jdhrg iohdrkfrjsdffdgrgerdg fgdg"
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
        "step_name": "sdhgosdrhofslkdf",
        "id": None,
        "text": "jdhrgiohdrkfrjsdffdgrgerdgfgdg"
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
        "step_name": "sdhgosdrhofslkdf",
        "id": None,
        "text": "Question text?",
        "variants": [DataStepChoice.Variant("`s == p`", "+"), DataStepChoice.Variant("`*s == *p`", "-"), DataStepChoice.Variant("`s[0] == p[0]`", "-")],
        "step_addons": {"SHUFFLE": "true"}
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
        "step_name": "sdhgosdrhofslkdf",
        "id": None,
        "text": "?",
        "variants": [DataStepChoice.Variant("`s == p`", "+"), DataStepChoice.Variant("`*s == *p`", "-"), DataStepChoice.Variant("`s[0] == p[0]`", "-")],
        "step_addons": {"SHUFFLE": "true"}
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
        "step_name": "sdhgosdrhofslkdf",
        "id": None,
        "text": "Question text?",
        "variants": [DataStepChoice.Variant("`s == p`", "+"), DataStepChoice.Variant("`*s == *p`", "-"), DataStepChoice.Variant("`s[0] == p[0]`", "-", "подсказка")],
        "step_addons": {"SHUFFLE": "true"}
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
        "step_name": "sdhgosdrhofslkdf",
        "id": None,
        "text": "Question text?",
        "variants": [DataStepChoice.Variant("`s == p`", "+", "частная подсказка"), DataStepChoice.Variant("`*s == *p`", "-"), DataStepChoice.Variant("`s[0] == p[0]`", "-")],
        "step_addons": {"SHUFFLE": "true"}
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
        "step_name": "sdhgosdrhofslkdf",
        "id": None,
        "text": "Question text?",
        "variants": [DataStepChoice.Variant("`s == p`", "+"), DataStepChoice.Variant("`*s == *p`", "-"), DataStepChoice.Variant("`s[0] == p[0]`", "-")],
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
"""## QUIZ sdhgosdrhofslkdf
Do you have giraffe?
A. `НУ Yes`
HINT: подсказка

B. `А ху asking`

C. `Thank you for your question`

ANSWER: A"""
    expected = {
        "step_name": "sdhgosdrhofslkdf",
        "id": None,
        "text": "Do you have giraffe?",
        "variants": [DataStepQuiz.Variant("`НУ Yes`", "A", True, "подсказка"), \
                     DataStepQuiz.Variant("`А ху asking`", "B", False), \
                     DataStepQuiz.Variant("`Thank you for your question`", "C", False)],
        "step_addons": {"SHUFFLE": "true", "ANSWER": "A"}
    }
    input_text = input_text.split('\n')
    dst_inf = ParsingModuleSchema.step().parseString(input_text[0])
    input_text = input_text[1:]
    dst = DataStepCreationSchema.create_step(dst_inf.type, dst_inf.name)
    dst.add_info(input_text)
    assert isinstance(dst, DataStepQuiz)
    assert dst.as_dict() == expected


@pytest.mark.markdown
def test_Quiz2():
    input_text =\
"""## QUIZ sdhgosdrhofslkdf
Do you have giraffe?
A. `НУ Yes`
HINT: подсказка

B. `А ху asking`

C. `Thank you for your question`

ANSWER: A, B"""
    expected = {
        "step_name": "sdhgosdrhofslkdf",
        "id": None,
        "text": "Do you have giraffe?",
        "variants": [DataStepQuiz.Variant("`НУ Yes`", "A", True, "подсказка"), \
                     DataStepQuiz.Variant("`А ху asking`", "B", True), \
                     DataStepQuiz.Variant("`Thank you for your question`", "C", False)],
        "step_addons": {"SHUFFLE": "true", "ANSWER": "A,B"}
    }
    input_text = input_text.split('\n')
    dst_inf = ParsingModuleSchema.step().parseString(input_text[0])
    input_text = input_text[1:]
    dst = DataStepCreationSchema.create_step(dst_inf.type, dst_inf.name)
    dst.add_info(input_text)
    assert isinstance(dst, DataStepQuiz)
    assert dst.as_dict() == expected


@pytest.mark.markdown
def test_Quiz3():
    input_text =\
"""## QUIZ sdhgosdrhofslkdf
Question text?
A. `s == p`
HINT: подсказка

B. `*s == *p`

C. `s[0] == p[0]`

SHUFFLE: false
ANSWER: A, C
HINT: подсказка"""
    expected = {
        "step_name": "sdhgosdrhofslkdf",
        "id": None,
        "text": "Question text?",
        "variants": [DataStepQuiz.Variant("`s == p`", "A", True, "подсказка"), \
                     DataStepQuiz.Variant("`*s == *p`", "B", False), \
                     DataStepQuiz.Variant("`s[0] == p[0]`", "C", True)],
        "step_addons": {"SHUFFLE": "false", "ANSWER": "A,C", "HINT": "подсказка"}
    }
    input_text = input_text.split('\n')
    dst_inf = ParsingModuleSchema.step().parseString(input_text[0])
    input_text = input_text[1:]
    dst = DataStepCreationSchema.create_step(dst_inf.type, dst_inf.name)
    dst.add_info(input_text)
    assert isinstance(dst, DataStepQuiz)
    assert dst.as_dict() == expected


@pytest.mark.markdown
def test_Taskinline1():
    input_text =\
"""## QUIZ sdhgosdrhofslkdf
Question text?
A. `s == p`
HINT: подсказка

B. `*s == *p`

C. `s[0] == p[0]`

SHUFFLE: false
ANSWER: A, C
HINT: подсказка"""
    expected = {
        "step_name": "sdhgosdrhofslkdf",
        "id": None,
        "text": "Question text?",
        "variants": [DataStepQuiz.Variant("`s == p`", "A", True, "подсказка"), \
                     DataStepQuiz.Variant("`*s == *p`", "B", False), \
                     DataStepQuiz.Variant("`s[0] == p[0]`", "C", True)],
        "step_addons": {"SHUFFLE": "false", "ANSWER": "A,C", "HINT": "подсказка"}
    }
    input_text = input_text.split('\n')
    dst_inf = ParsingModuleSchema.step().parseString(input_text[0])
    input_text = input_text[1:]
    dst = DataStepCreationSchema.create_step(dst_inf.type, dst_inf.name)
    dst.add_info(input_text)
    assert isinstance(dst, DataStepQuiz)
    assert dst.as_dict() == expected