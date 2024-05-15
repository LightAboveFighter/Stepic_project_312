from src.API.Step import Step, StepChoice, StepCode, StepText, StepNumber, StepString

from src.markdown.steps.data_step_til import DataStepTaskinline
from src.markdown.steps.data_step_choice import DataStepChoice
from src.markdown.steps.data_step_number import DataStepNumber
from src.markdown.steps.data_step_string import DataStepString
from src.markdown.steps.data_step_quiz import DataStepQuiz
from src.markdown.steps.data_step_text import DataStepText
from src.markdown.steps.data_step import DataStep

import pyparsing as pp


class DataStepCreationSchema():
    @staticmethod
    def create_step(type: str,
                    name: str,
                    lesson_id: str = None,
                    lang: str = 'python3'
    ) -> DataStep:   # 
        if type == pp.Empty():
            type = 'TEXT'
        match type:
            case 'TEXT':
                return DataStepText(name, lesson_id)
            case 'QUIZ':
                return DataStepQuiz(name, lesson_id)
            case 'CHOICE':
                return DataStepChoice(name, lesson_id)
            case 'STRING':
                return DataStepString(name, lesson_id)
            case 'NUMBER':
                return DataStepNumber(name, lesson_id)
            case 'TASKINLINE':
                return DataStepTaskinline(name, lesson_id, lang)
            case _:
                raise Exception('Unexpected step type.')

    @staticmethod
    def convert_step(step: DataStep) -> Step:   # should add STRING and NUMBER DataSteps
        match step:
            case DataStepText():
                return StepText(title = step.step_name,
                                lesson_id = None,
                                body = {"text": step.text})

            case DataStepQuiz():
                unique = {
                    'preserve_order': str.lower(step.step_addons['SHUFFLE']).strip() == 'false',
                    'options' : [{'text': var.text,
                                  'is_correct': var.is_correct,
                                  'feedback': var.feedback} for var in step.variants]
                }
                return StepChoice(title = step.step_name,
                                  lesson_id = None,
                                  body = {"text": step.text, "source": {"is_multiple_choice": step._correct_variants > 1}},
                                  unique = StepChoice.Unique(**unique))

            case DataStepChoice():
                unique = {
                    'preserve_order': str.lower(step.step_addons['SHUFFLE']).strip() == 'false',
                    'options' : [{'text': var.text,
                                  'is_correct': var.is_correct,
                                  'feedback': var.feedback} for var in step.variants]
                }
                return StepChoice(title = step.step_name,
                                  lesson_id = None,
                                  body = {"text": step.text, "source": {"is_multiple_choice": step._correct_variants > 1}},
                                  unique = StepChoice.Unique(**unique))

            case DataStepString():
                unique = {
                    'pattern': step.step_addons['ANSWER']
                }
                return StepString(title = step.step_name,
                                  lesson_id = None,
                                  body = {'text': step.text},
                                  unique = StepString.Unique(**unique))
            
            case DataStepNumber():
                unique = {
                    'options': [{'answer': answer[0],
                                 'max_error': answer[1]} for answer in step.step_addons['ANSWER']]
                }
                return StepNumber(title = step.step_name,
                                  lesson_id = None,
                                  body = {'text': step.text},
                                  unique = StepNumber.Unique(**unique))

            case DataStepTaskinline():
                lang = '::' + step.lang
                header = '::header\n' + step.header
                code = '::code\n'+ step.code
                footer = '::footer\n' + step.footer
                unique = {
                    'templates_data': '\n'.join([lang, header, code, footer]),
                    'test_cases': [[input, output] for input,output in zip(step.inputs, step.outputs)]
                }
                return StepCode(title = step.step_name,
                                lesson_id = None,
                                body = {"text": step.text},
                                unique = StepCode.Unique(**unique))

            case _:
                raise Exception('Unexpected step type.')