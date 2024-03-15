import json
import pytest

from src.gift_processing import get_gift_dicts_from_text


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
    q = questions[0]
    assert q == json.loads(expected_json)


@pytest.mark.gift
def test_single_choice_feedback():
    text = '''
    // multiple choice with specified feedback for right and wrong answers
    ::Q2:: What's between orange and green in the spectrum? 
    { =yellow # right; good! ~red # wrong, it's yellow ~blue # wrong, it's yellow }
    '''
    questions = get_gift_dicts_from_text(text)
    q = questions[0]
    assert q['source']['options'][0]['feedback'] == 'right; good!'
    assert q['source']['options'][1]['feedback'] == "wrong, it\'s yellow"
    assert q['source']['options'][2]['feedback'] == "wrong, it\'s yellow"

    
