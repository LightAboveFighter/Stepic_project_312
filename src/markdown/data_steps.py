from dataclasses import dataclass
from abc import ABC, abstractmethod
from src.markdown.schemas import *
from src.API.Step import Step, StepChoice, StepCode, StepText

class DataStep(ABC):
    '''step_name: str
    lesson_id: int'''
    def __init__(
            self,
            nam: str = None,
            id : int = None
    ) -> None:
        self.step_name = nam
        self.lesson_id = None      # добавить сюда id от урока, в котором находится
    
    @abstractmethod
    def add_info(self, lines: list[str]):
        pass


class DataStepText(DataStep):
    '''step_name: str
    lesson_id: int
    text: str'''
    def add_info(self, lines: list[str]):
        self.text = ''.join(lines)
    
    def as_dict(self):
        data_dict = {
            "step_name": self.step_name,
            "id": self.lesson_id,
            "text": self.text
        }
        return data_dict        


class DataStepNumber(DataStep):
    '''step_name: str
    lesson_id: int
    text: str
    step_addons: dict'''

    def add_info(self, lines: list[str]):
        self.text = []
        self.step_addons = {}

        BEGIN = 'TEXTBEGIN'
        END = 'TEXTEND'
        state = 'TEXT'
        only_text = False

        
        for line in lines:
            if line.strip() == BEGIN:
                only_text = True
                continue
            elif line.strip() == END:
                only_text = False
                continue

            if only_text:
                self.text.append(line)
                continue

            try:
                answer = ParsingModuleSchema.body_addon().parseString(line)
                if answer.type == 'ANSWER':
                    self.step_addons[str(answer.type)] = answer.value
                    self.text = ''.join(self.text) 
                else:
                    raise ValueError("Expected only ANSWER in addons.") 
                continue
            except pp.ParseException:
                self.text.append(line)
                continue
        
        if self.step_addons:
            if "+-" in self.step_addons["ANSWER"]:
                self.step_addons["ANSWER"] = self.step_addons["ANSWER"].split("+-")
                try:
                    self.step_addons["ANSWER"][0] = float(self.step_addons["ANSWER"][0])
                    self.step_addons["ANSWER"][1] = float(self.step_addons["ANSWER"][1])
                except:
                    raise Exception("Answer value can not be converted into float.")
            else:
                try:
                    self.step_addons["ANSWER"] = list(float(self.step_addons["ANSWER"]))
                except:
                    raise Exception("Answer value can not be converted into float.")
        else:
            raise pp.ParseException("ANSWER must be in addons.")

    def as_dict(self):
        data_dict = {
            "step_name": self.step_name,
            "id": self.lesson_id,
            "text": self.text,
            "step_addons": self.step_addons
        }
        return data_dict  

class DataStepString(DataStep):
    '''step_name: str
    lesson_id: int
    text: str
    step_addons: dict'''

    def add_info(self, lines: list[str]):
        self.text = []
        self.step_addons = {}

        BEGIN = 'TEXTBEGIN'
        END = 'TEXTEND'
        state = 'TEXT'
        only_text = False

        
        for line in lines:
            if line.strip() == BEGIN:
                only_text = True
                continue
            elif line.strip() == END:
                only_text = False
                continue

            if only_text:
                self.text.append(line)
                continue

            try:
                answer = ParsingModuleSchema.body_addon().parseString(line)
                if answer.type == 'ANSWER':
                    self.step_addons[str(answer.type)] = answer.value
                    self.text = ''.join(self.text) 
                else:
                    raise ValueError("Expected only ANSWER in addons.") 
                continue
            except pp.ParseException:
                self.text.append(line)
                continue
        
        if not self.step_addons:
            raise pp.ParseException("ANSWER must be in addons.")

    def as_dict(self):
        data_dict = {
            "step_name": self.step_name,
            "id": self.lesson_id,
            "text": self.text,
            "step_addons": self.step_addons
        }
        return data_dict


class DataStepChoice(DataStep):
    # Text before answer variants
    '''text: str
    variants: list[Variant]
    step_addons: dict'''

    class Variant:
        def __init__(self, text: str, is_correct: str, feedback: str = ''):
            self.text = text
            if is_correct == '+':
                self.is_correct = True
            elif is_correct == '-':
                self.is_correct = False
            else:
                raise Exception('Undefined type of variant_data.')
            self.feedback = feedback
        
        def __eq__(self, other):
            if self.text == other.text and self.is_correct == other.is_correct and \
                self.feedback == other.feedback:
                return True
            return False
    
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
                        continue
                    elif line.strip() == END:
                        only_text = False
                        continue

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
    
    def as_dict(self):
        data_dict = {
            "step_name": self.step_name,
            "id": self.lesson_id,
            "text": self.text,
            "variants": self.variants,
            "step_addons": self.step_addons
        }
        return data_dict


class DataStepQuiz(DataStep):
    # text before answer variants
    '''text: str
    variants: list[Variant]
    step_addons: dict'''

    class Variant:
        def __init__(self, text: str, label: str, is_correct: bool=False, feedback: str=''):
            self.text = text
            self.is_correct = is_correct
            self.label = label
            self.feedback = feedback
        
        def __eq__(self, other):
            if self.text == other.text and self.is_correct == other.is_correct and \
                self.label == other.label and self.feedback == other.feedback:
                return True
            return False

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
                        variant_data = ParsingModuleSchema.quiz_variant().parseString(line)
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
        if self.step_addons["ANSWER"]:
            self.step_addons["ANSWER"] = self.step_addons["ANSWER"].replace(" ", "")
            answer_letters = self.step_addons["ANSWER"].split(",")
            for var in self.variants:
                if var.label in answer_letters:
                    var.is_correct = True
        else:
            raise Exception("Expected ANSWER obligatory addon.")

    def as_dict(self):
        data_dict = {
            "step_name": self.step_name,
            "id": self.lesson_id,
            "text": self.text,
            "variants": self.variants,
            "step_addons": self.step_addons
        }
        return data_dict


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
                case 'TEST':    ## some problems with outputs, need to fix ASAP
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

    def as_dict(self):
        data_dict = {
            "step_name": self.step_name,
            "id": self.lesson_id,
            "text": self.text,
            "code": self.code,
            "inputs": self.inputs,
            "outputs": self.outputs
        }
        return data_dict


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