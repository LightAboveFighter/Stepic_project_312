# from dataclasses import dataclass
from abc import ABC, abstractclassmethod

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
    
    @abstractclassmethod
    def add_info(lines: list[str]):
        pass

class DataStepText(DataStep):
    # text: list[str] = []
    def add_info(self, lines: list[str]):
        self.text = lines

# @dataclass
class DataStepChoice(DataStep):
    # Text before answer variants
    # text: list[str] = []
    def add_info(self, lines: list[str]):
        # Нужно будет отпарсить все строчки находящиеся в lines
        pass

# @dataclass
class DataStepQuiz(DataStep):
    # Text before answer variants
    # tex: list[str] = []
    def add_info(self, lines: list[str]):
        # Нужно будет отпарсить все строчки находящиеся в lines
        pass