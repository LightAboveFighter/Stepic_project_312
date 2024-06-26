import json
import pytest
import types

from src.gift.gift_processing import get_gift_dicts_from_text, __function_short_generator__


@pytest.mark.gift
def test_single_choice():
    text = '''
    ::Q2:: What's between orange and green in the spectrum?
    { =yellow  ~red  ~blue }
    '''
    expected_json = '''
    {
        "name": "choice",
        "text": "What's between orange and green in the spectrum?",
        "source": {
            "options": [
                {
                    "is_correct": true,
                    "text": "yellow",
                    "feedback": ""
                },
                {
                    "is_correct": false,
                    "text": "red",
                    "feedback": ""
                },
                {
                    "is_correct": false,
                    "text": "blue",
                    "feedback": ""
                }
            ],
            "is_always_correct": false,
            "sample_size": 3,
            "is_multiple_choice": false
        }
    }
    '''
    questions = get_gift_dicts_from_text(text)
    q = questions[0].dict_info()["block"]
    #assert all(item in dict(json.loads(expected_json.items())) for item in q.items())
    expected =  dict(json.loads(expected_json))
    assert (expected | q) == q


@pytest.mark.gift
def test_single_choice_feedback():
    text = '''
    // multiple choice with specified feedback for right and wrong answers
    ::Q2:: What's between orange and green in the spectrum? 
    { =yellow # right; good! ~red # wrong, it's yellow ~blue # wrong, it's yellow }
    '''
    questions = get_gift_dicts_from_text(text)
    q = questions[0].dict_info()["block"]
    assert q['source']['options'][0]['feedback'] == 'right; good!'
    assert q['source']['options'][1]['feedback'] == "wrong, it\'s yellow"
    assert q['source']['options'][2]['feedback'] == "wrong, it\'s yellow"



@pytest.mark.gift
def test_is_multiple_choise_value():
    text_single = '''
    ::Q2:: What's between orange and green in the spectrum? 
    { =yellow # right; good! ~red # wrong, it's yellow ~blue # wrong, it's yellow }
    '''
    text_multiple = '''
    ::Q2:: What's between orange and green in the spectrum? 
    { ~%50%yellow # right; good! ~%-100%red # wrong, it's yellow ~%50%yellow2 # it's yellow }
    '''
    questions = [get_gift_dicts_from_text(text_single)[0].dict_info()["block"], get_gift_dicts_from_text(text_multiple)[0].dict_info()["block"]]
    assert questions[0]['source']['is_multiple_choice'] == False
    assert questions[1]['source']['is_multiple_choice'] == True


@pytest.mark.gift
def test_true_false_generation():
    text = '''
    ::Q1:: 1+1=2 {T}
    '''
    question = get_gift_dicts_from_text(text)[0].dict_info()["block"]
    expected_json = '''
    {
        "name": "choice",
        "text": "1+1=2",
        "source": {
            "options": [
                {
                    "is_correct": true,
                    "text": "True",
                    "feedback": ""
                },
                {
                    "text": "False",
                    "is_correct": false,
                    "feedback": ""
                }
            ],
            "is_always_correct": false,
            "sample_size": 2,
            "is_multiple_choice": false
        }
    }
    '''
    expected =  dict(json.loads(expected_json))
    assert (expected | question) == question


''' Тест не работет, нет нужного степа
@pytest.mark.gift
def test_function_short_generator():
   text1 = 'Two plus two equals {=four =4 =\"четыре\"}' 
   text2 = 'Two plus two equals {=four =4 =\'четыре\'}' 
   text3 = 'Two plus two equals {=four =4 ="четыре"}' 
   question = [get_gift_dicts_from_text(text1)[0].dict_info()["block"],
               get_gift_dicts_from_text(text2)[0].dict_info()["block"],
               get_gift_dicts_from_text(text3)[0].dict_info()["block"]]
   for block in question:
        namspace = types.SimpleNamespace()
        exec(block["source"]["code"],namspace.__dict__)
        assert namspace.check(namspace.solve())
        assert namspace.check('4')
        assert not namspace.check("чотыре")
'''

