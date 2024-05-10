# import src.API.Classes as sac
# from data_steps import *
from src.markdown.data_steps import *
from src.markdown.schemas import *
import pyparsing as pp
import io

class DataLesson:
    '''title: str
    steps: list[DataSteps]
    params: dict'''

    def __init__(self):
        self.title = None
        # All optional header parametrs will be added in 'param'
        self.params = {}
        # List of lesson's steps
        self.steps = []

    def add_info(self, lesson_path: str, file_ecoding: str = 'utf-8'):
        with io.open(lesson_path, 'r', encoding=file_ecoding) as f:
            # Writting down name of the lesson    
            self.title = ((ParsingModuleSchema.lesson().parseString(f.readline())).title).strip()
            # Adding all the optional header parametrs
            for addon_line in f:
                try:
                    new_step = ParsingModuleSchema.step().parseString(addon_line)
                    break
                except pp.ParseException:
                    if addon_line != pp.Empty():
                        addon = ParsingModuleSchema.header_addon().parseString(addon_line)
                        self.params[str(addon.type)] = (addon.value).strip()
                        
            # Writting down steps of the lesson
            step_lines = []
            self.steps.append(DataStepCreationSchema.create_step(new_step.type, (new_step.name).strip()))
            for line in f:

                try:
                    new_step = ParsingModuleSchema.step().parseString(line)
                    self.steps[-1].add_info(step_lines)
                    step_lines = []

                    self.steps.append(DataStepCreationSchema.create_step(new_step.type, (new_step.name).strip()))
                except pp.ParseException:

                    step_lines.append(line)
            self.steps[-1].add_info(step_lines)