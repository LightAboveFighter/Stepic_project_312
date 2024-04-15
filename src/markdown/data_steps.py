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
    def add_info(lines: list[str]):
        pass


class DataStepText(DataStep):
    '''text: list[str]'''
    def add_info(self, lines: list[str]):
        self.text = lines


class DataStepChoice(DataStep):
    # Text before answer variants
    '''text: list[str]
    variants: list[variant]
    step_addons: dict'''

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
                    self.variants[-1].feedback = feedback.value
                except pp.ParseException:
                    if l != pp.Empty():
                        variant_data = ParsingModuleSchema.choice_variant().parseString(l)
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
    # text before answer variants
    '''text: list[str]
    variants: list[variant]
    step_addons: dict'''

    class variant:
        def __init__(self, text: str, label: str, feedback: str = None):
            self.text = text
            self.label = label
            self.feedback = feedback

    def add_info(self, lines: list[str]):
        self.text = []
        self.variants = []
        self.step_addons = {'SHUFFLE' : 'true'}

        begin = 'TEXTBEGIN'
        end = 'TEXTEND'
        only_text = False
        getting_text = True
        getting_variants = False
        getting_end = False

        for l in lines:

            
            # Нужно добавить вариант, когда текст обрамляется в TEXTBEGIN и TEXTEND
            if getting_text:
                if (not only_text) and (begin in l):
                    if l.strip().index(begin) == 0:
                        l = l[l.index(begin) + len(begin):].strip()
                        only_text = True

                if (only_text) and (end in l):
                    self.text.append(l[:l.index(end)])
                    l = l[l.index(end) + len(end):].strip()
                    only_text = False                

                try:
                    if only_text:
                        raise pp.ParseException('only_text == True')
                    variant_data = ParsingModuleSchema.quiz_variant().parseString(l)  # проблемы с этим парсером
                    self.variants.append(DataStepQuiz.variant(variant_data.value, variant_data.label))
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
                    self.variants[-1].feedback = feedback.value
                except pp.ParseException:
                    if l != pp.Empty():
                        variant_data = ParsingModuleSchema.quiz_variant().parseString(l)
                        self.variants.append(DataStepQuiz.variant(variant_data.value, variant_data.label))
                    continue
                    
            if getting_end:
                try:
                    addon = ParsingModuleSchema.body_addon().parseString(l)
                    self.step_addons[str(addon.type)] = addon.value
                    continue
                except pp.ParseException:
                    continue


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