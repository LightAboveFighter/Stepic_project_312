import pyparsing as pp


class ParsingModuleSchema():
    __step_types = ['QUIZ', 'CHOICE', 'TEXT']    # Стоит добавить функция для изменения этого списка (или нет)
    __header_addons = ['lesson', 'lang']
    __body_addons = ['ANSWER', 'HINT', 'SHUFFLE']
    __choice_types = ['+', '-']
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

    @staticmethod
    def choice_variant():
        choicevar_type = pp.one_of(ParsingModuleSchema.__choice_types) ('type')
        choicevar_value = pp.rest_of_line() ('value')
        choicevar_module = choicevar_type + pp.Suppress(')' \
                           + pp.ZeroOrMore(pp.White())) + choicevar_value
        return choicevar_module