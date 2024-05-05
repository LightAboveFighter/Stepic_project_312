from dataclasses import dataclass
from abc import ABC, abstractmethod
from src.markdown.schemas import *


class DataStep(ABC):
    '''id: int
    step_name: str'''
    def __init__(
            self,
            nam: str,
            id : int = None
    ) -> None:
        self.step_name = nam
        self.id = None      # пока не знаю как это заполнять
    
    @abstractmethod
    def add_info(self, lines: list[str]):
        pass


class DataStepText(DataStep):
    '''text: list[str]'''
    def add_info(self, lines: list[str]):
        self.text = ''.join(lines)


class DataStepChoice(DataStep):
    # Text before answer variants
    '''text: list[str]
    variants: list[Variant]
    step_addons: dict'''

    class Variant:
        def __init__(self, text: str, is_correct: str, feedback: str = None):
            self.text = text
            if is_correct == '+':
                self.is_correct = True
            elif is_correct == '-':
                self.is_correct = False
            else:
                raise Exception('Undefined type of variant_data.')
            self.feedback = feedback
    
    def add_variant(self, value, type):
        value_begin = value.find('`')
        value_end = value[value_begin+1:].find('`')
        self.variants.append(self.Variant(value[value_begin+1:value_end+1], type))

    def add_info(self, lines: list[str]):
        self.text = []
        self.variants = []
        self.step_addons = {'SHUFFLE' : 'true'}

        BEGIN = 'TEXTBEGIN'
        END = 'TEXTEND'
        state = 'TEXT'
        only_text = False
        for line in lines:
            match (state):
                case 'TEXT':
                    if line.strip() == BEGIN:
                        only_text = True
                    elif line.strip() == END:
                        only_text = False

                    if only_text:
                        self.text.append(line)
                        continue

                    try:
                        variant_data = ParsingModuleSchema.choice_variant().parseString(line)
                        self.add_variant(variant_data.value, variant_data.type)
                        state = 'VARIANTS'
                        self.text = ''.join(self.text)
                        continue
                    except pp.ParseException:
                        self.text.append(line)
                        continue
                case 'VARIANTS':
                    try:
                        feedback = ParsingModuleSchema.body_addon().parseString(line)
                        if feedback.type != 'HINT':
                            self.step_addons[str(feedback.type)] = feedback.value
                            state = 'END'
                            continue
                        self.variants[-1].feedback = feedback.value
                    except pp.ParseException:
                        if line != pp.Empty():
                            variant_data = ParsingModuleSchema.choice_variant().parseString(line)
                            self.add_variant(variant_data.value, variant_data.type)
                        continue
                case 'END':
                    try:
                        addon = ParsingModuleSchema.body_addon().parseString(line)
                        self.step_addons[str(addon.type)] = addon.value
                        continue
                    except pp.ParseException:
                        continue
                case _:
                    raise Exception("Undefined DataStepChoice.add_info() state.")


class DataStepQuiz(DataStep):
    # text before answer variants
    '''text: list[str]
    variants: list[Variant]
    step_addons: dict'''

    class Variant:
        def __init__(self, text: str, label: str, feedback: str = None):
            self.text = text
            self.label = label
            self.feedback = feedback

    def add_variant(self, value, label):
        value_begin = value.find('`')
        value_end = value[value_begin+1:].find('`')
        self.variants.append(DataStepQuiz.Variant(value[value_begin+1:value_end+1], label))

    def add_info(self, lines: list[str]):
        self.text = []
        self.variants = []
        self.step_addons = {'SHUFFLE' : 'true'}

        BEGIN = 'TEXTBEGIN'
        END = 'TEXTEND'
        state = 'TEXT'
        only_text = False

        for line in lines:
            match (state):
                case 'TEXT':
                    if line.strip() == BEGIN:
                        only_text = True
                    elif line.strip() == END:
                        only_text = False

                    if only_text:
                        self.text.append(line)
                        continue

                    try:
                        variant_data = ParsingModuleSchema.quiz_variant().parseString(line)  # проблемы с этим парсером
                        self.add_variant(variant_data.value, variant_data.label)
                        state = 'VARIANTS'
                        self.text = ''.join(self.text)
                        continue
                    except pp.ParseException:
                        self.text.append(line)
                        continue
                case 'VARIANTS':
                    try:
                        feedback = ParsingModuleSchema.body_addon().parseString(line)
                        if feedback.type != 'HINT':
                            self.step_addons[str(feedback.type)] = feedback.value
                            state = 'END'
                            continue
                        self.variants[-1].feedback = feedback.value
                    except pp.ParseException:
                        if line != pp.Empty():
                            variant_data = ParsingModuleSchema.quiz_variant().parseString(line)
                            self.add_variant(variant_data.value, variant_data.label)
                        continue    
                case 'END':
                    try:
                        addon = ParsingModuleSchema.body_addon().parseString(line)
                        self.step_addons[str(addon.type)] = addon.value
                        continue
                    except pp.ParseException:
                        continue
                case _:
                    raise Exception("Undefined DataStepQuiz.add_info() state.")


class DataStepTaskinline(DataStep):
    def add_info(self, lines: list[str]):
        self.text = []
        self.code = []
        self.inputs = []
        self.outputs = []
        data = []

        BEGIN = 'TEXTBEGIN'
        END = 'TEXTEND'
        state = 'TEXT'
        only_text = False
        for line in lines:
            match (state):
                case 'TEXT':
                    if line.strip() == BEGIN:
                        only_text = True
                    elif line.strip() == END:
                        only_text = False
                    if only_text:
                        self.text.append(line)
                        continue

                    elif line.strip() == 'CODE':
                        state = 'CODE'
                        self.text = ''.join(self.text)
                        continue
                    self.text.append(line)
                    continue
                case 'CODE':
                    if line.strip() == 'TEST':
                        state = 'TEST'
                        self.code = ''.join(self.code)
                        continue
                    self.code.append(line)
                    continue
                case 'TEST':
                    if line.strip() == '----':
                        self.inputs.append(''.join(data))
                        data = []
                        continue
                    elif line.strip() == '====':
                        self.outputs.append(''.join(data))
                        data = []
                        continue
                    data.append(line)
                    continue
                case _:
                    raise Exception("Undefined DataStepTaskinline.add_info() state.")


class DataStepCreationSchema():
    @staticmethod
    def create_step(type,
                    name,
                    id = None
    ):   # пока что не знаю что мне делать с id
        if type == pp.Empty():
            type = 'TEXT'
        match type:
            case 'TEXT':
                return DataStepText(name, id)
            case 'QUIZ':
                return DataStepQuiz(name, id)
            case 'CHOICE':
                return DataStepChoice(name, id)
            case 'TASKINLINE':
                return DataStepTaskinline(name, id)
            case _:
                raise Exception('Unexpected step type.')