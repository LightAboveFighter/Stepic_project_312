# import src.API.Classes as sac
from data_steps import *
from schemas import *
import pyparsing as pp
from abc import ABC
import io

class DataLesson:
    '''title: str
    steps: list[DataSteps]
    params: dict'''

    def __init__(self, lesson_path: str, file_ecoding: str = 'utf-8'):
        with io.open(lesson_path, 'r', encoding=file_ecoding) as f:
            # All optional header parametrs will be added in 'param'
            self.params = {}

            # Writting down name of the lesson
            self.title = (ParsingModuleSchema.lesson().parseString(f.readline())).title
            
            # Adding all the optional header parametrs
            for addon_line in f:
                try:
                    new_step = ParsingModuleSchema.step().parseString(addon_line)
                    break
                except pp.ParseException:
                    if addon_line != pp.Empty():
                        addon = ParsingModuleSchema.header_addon().parseString(addon_line)
                        self.params[str(addon.type)] = addon.value
                        
            
            # Writting down steps of the lesson
            self.steps = []
            step_lines = []

            self.steps.append(DataStepCreationSchema.create_step(new_step.type, new_step.name))
            for line in f:
                try:
                    new_step = ParsingModuleSchema.step().parseString(line)

                    self.steps[-1].add_info(step_lines)
                    step_lines = []

                    self.steps.append(DataStepCreationSchema.create_step(new_step.type, new_step.name))
                except pp.ParseException:
                    step_lines.append(line)
            self.steps[-1].add_info(step_lines)