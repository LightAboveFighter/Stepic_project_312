from src.markdown.schemas import ParsingModuleSchema
from src.markdown.steps.data_step import DataStep
import pyparsing as pp

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