from src.API.Step import Step, StepChoice, StepCode, StepText
from src.markdown.steps.data_step_til import DataStepTaskinline
from src.markdown.steps.data_step_choice import DataStepChoice
from src.markdown.steps.data_step_quiz import DataStepQuiz
from src.markdown.steps.data_step_text import DataStepText
from src.markdown.steps.data_step import DataStep
from src.markdown.schemas import ParsingModuleSchema
import pyparsing as pp


class DataStepCreationSchema():
    @staticmethod
    def create_step(type: str,
                    name: str,
                    lesson_id: str = None
    ) -> DataStep:   # пока что не знаю что мне делать с id
        if type == pp.Empty():
            type = 'TEXT'
        match type:
            case 'TEXT':
                return DataStepText(name, lesson_id)
            case 'QUIZ':
                return DataStepQuiz(name, lesson_id)
            case 'CHOICE':
                return DataStepChoice(name, lesson_id)
            case 'TASKINLINE':
                return DataStepTaskinline(name, lesson_id)
            case _:
                raise Exception('Unexpected step type.')

    @staticmethod
    def convert_step(step: DataStep) -> Step:
        match step:
            case DataStepText():
                return StepText(title = step.step_name,
                                lesson_id = None,
                                body = {"text": step.text})

            case DataStepChoice():
                unique = {
                    'preserve_order': str.lower(step.step_addons['SHUFFLE']).strip() == 'false',
                    'options' : [{'text': var.text,
                                  'is_correct': var.is_correct,
                                  'feedback': var.feedback} for var in step.variants]
                }
                return StepChoice(title = step.step_name,
                                  lesson_id = None,
                                  body = {"text": step.text, "source": {"is_multiple_choice": False} },
                                  unique = StepChoice.Unique(**unique))

            case DataStepQuiz():
                unique = {
                    'preserve_order': str.lower(step.step_addons['SHUFFLE']).strip() == 'false',
                    'options' : [{'text': var.text,
                                  'is_correct': var.is_correct,
                                  'feedback': var.feedback} for var in step.variants]
                }
                return StepChoice(title = step.step_name,
                                  lesson_id = None,
                                  body = {"text": step.text, "source": {"is_multiple_choice": False}},
                                  unique = StepChoice.Unique(**unique))

            case DataStepTaskinline():
                unique = {
                    'templates_data': step.code,
                    'test_cases': [[input, output] for input,output in zip(step.inputs, step.outputs)]
                }
                return StepCode(title = step.step_name,
                                lesson_id = None,
                                body = {"text": step.text},
                                unique = StepCode.Unique(**unique))

            case _:
                raise Exception('Unexpected step type.')