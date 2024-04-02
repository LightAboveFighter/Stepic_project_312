import pyparsing as pp
from data_steps import *

class ParsingModuleSchema():
    __step_types = ['QUIZ', 'CHOICE', 'TEXT']    # Стоит добавить функция для изменения этого списка (или нет)
    __header_addons = ['lesson', 'lang']
    __body_addons = ['ANSWER', 'HINT', 'SHUFFLE']
    @staticmethod
    def lesson():
        lesson_title = pp.rest_of_line() ('title')
        lesson_module = pp.Suppress(pp.Keyword('#') + pp.OneOrMore(pp.White())) \
                        + pp.Optional(lesson_title)
        return lesson_module

    @staticmethod
    def step():
        step_type = pp.one_of(ParsingModuleSchema.__step_types,
                              as_keyword=True) ('type')
        step_name = pp.rest_of_line() ('name')
        step_module = pp.Suppress('##' + pp.OneOrMore(pp.White())) + pp.Optional(step_type) \
                      + pp.Suppress(pp.ZeroOrMore(pp.White())) + pp.Optional(step_name)
        return step_module
    
    @staticmethod
    def header_addon():
        addon = pp.one_of(ParsingModuleSchema.__header_addons,
                          as_keyword=True) ('type')  # Проверить: работает ли "=" перед keyword
        addon_value = pp.rest_of_line() ('value')
        addon_module = addon + pp.Suppress(pp.ZeroOrMore(pp.White()) \
                       + '=' + pp.ZeroOrMore(pp.White())) + addon_value
        return addon_module

    @staticmethod
    def body_addon():
        addon = pp.one_of(ParsingModuleSchema.__body_addons,
                          as_keyword=True) ('type')
        addon_value = pp.rest_of_line() ('value')
        addon_module = addon + pp.Suppress(pp.ZeroOrMore(pp.White()) \
                       + ':' + pp.ZeroOrMore(pp.White())) + addon_value
        return addon_module 

# Not fully implemented
class DataStepCreationSchema():
    @staticmethod
    def create_step(type,
                    name,
                    id = None
    ) -> DataStep:   # пока что не знаю что мне делать с id
        if type == pp.Empty():
            type = 'TEXT'
        match type:
            case 'TEXT':
                return DataStepText(name)
            case 'QUIZ':
                return DataStepQuiz(name)
            case 'CHOICE':
                return DataStepChoice(name)
            case _:
                raise Exception('Unexpected step type.')

    @staticmethod
    def text():
        pass

    @staticmethod
    def choice():
        pass

    @staticmethod
    def quiz():
        pass
