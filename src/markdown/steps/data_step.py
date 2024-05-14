from abc import ABC, abstractmethod
import pyparsing as pp

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