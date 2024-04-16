from dataclasses import dataclass
from abc import ABC, abstractmethod
from schemas import *


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
    def add_info(lines: list[str]):
        pass


class DataStepText(DataStep):
    '''text: list[str]'''
    def add_info(self, lines: list[str]):
        self.text = lines


class DataStepChoice(DataStep):
    # Text before answer variants
    '''text: list[str]
    variants: list[variant_data]
    step_addons: dict'''
    # option 
    # {
    #   text 
    #   is_correct
    # feedback
    # }

    class variant:
        def __init__(self, text: str, is_correct: str, feedback: str = None):
            self.text = text
            if is_correct == '+':
                self.is_correct = True
            elif is_correct == '-':
                self.is_correct = False
            else:
                raise Exception('Undefined type of variant_data.')
            self.feedback = feedback

    def add_variant(self, variant_data):
        match (variant_data.type):
            case '+':
                self.correct[variant_data.value] = None
            case '-':
                self.incorrect[variant_data.value] = None
            case _:
                raise Exception('Undefined type of choice variant_data.')

    def add_feedback(self, variant_data, feedback):
        if feedback.type != 'HINT':
            raise Exception('Wrong feedback type.')

        match (variant_data.type):
            case '+':
                self.correct[variant_data.value] = feedback.value
            case '-':
                self.incorrect[variant_data.value] = feedback.value
            case _:
                raise Exception('Undefined type of choice variant_data.')

    def add_info(self, lines: list[str]):
        self.text = []
        self.variants = []
        self.step_addons = {'SHUFFLE' : 'true'}

        getting_text = True
        getting_variants = False
        getting_end = False

        for l in lines:
            if getting_text:
                try:
                    variant_data = ParsingModuleSchema.choice_variant().parseString(l)
                    # add_variant
                    self.variants.append(DataStepChoice.variant(variant_data.value, variant_data.type))
                    getting_text = False
                    getting_variants = True
                    continue
                except pp.ParseException:
                    self.text.append(l)
                    continue
                    
            if getting_variants:
                try:
                    feedback = ParsingModuleSchema.body_addon().parseString(l)
                    if feedback.type != 'HINT':
                        self.step_addons[str(feedback.type)] = feedback.value
                        getting_variants = False
                        getting_end = True
                        continue
                    # self.add_feedback(variant_data, feedback)
                    self.variants[-1].feedback = feedback.value
                except pp.ParseException:
                    if l != pp.Empty():
                        variant_data = ParsingModuleSchema.choice_variant().parseString(l)
                        # self.add_variant(variant_data)
                        self.variants.append(DataStepChoice.variant(variant_data.value, variant_data.type))
                    continue
                    
            if getting_end:
                try:
                    addon = ParsingModuleSchema.body_addon().parseString(l)
                    self.step_addons[str(addon.type)] = addon.value
                    continue
                except pp.ParseException:
                    continue


class DataStepQuiz(DataStep):
    '''text: list[str]
    variants: dict
    step_addons: dict'''
    def add_info(self, lines: list[str]):
        # Нужно будет отпарсить все строчки находящиеся в lines
        pass


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
            case _:
                raise Exception('Unexpected step type.')