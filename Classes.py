from abc import ABC, abstractclassmethod

class Step(ABC):
    """
    lesson_id: int
    position: int
    (abstract) type_info: Any or tuple(Any)
    """
    def __init__(self, ls_id: int, pos: int):
        self.lesson_id = ls_id
        self.position = pos
        self.type_info = None

    @abstractclassmethod
    def set_type_information():
        pass

class Step_text(Step):

    def set_type_information(self, text):
        self.type_info = text