import pyparsing as pp


class ParsingModuleSchema():
    __step_types = ['QUIZ', 'CHOICE', 'TEXT', 'TASKINLINE']
    __header_addons = ['lesson', 'lang']
    __body_addons = ['ANSWER', 'HINT', 'SHUFFLE']
    __choice_types = ['+', '-']
    __quiz_seperators = [')', '.']

    @staticmethod
    def lesson():
        '''Returns parsing module for title of the lesson.
        
        Example::

            line = "# Lesson_name and something else"
            print(ParsingModuleSchema.lesson().parseString(line))
        
        prints::
        
            ['Lesson_name and something else']'''
        lesson_title = pp.rest_of_line() ('title')
        lesson_module = pp.Suppress(pp.Keyword('#') + pp.White()[1, ...]) + pp.Optional(lesson_title)
        return lesson_module

    @staticmethod
    def step():
        '''Returns parsing module for title of the step.
        
        Example::

            line = "## QUIZ Step_name"
            print(ParsingModuleSchema.step().parseString(line))
        
        prints::
            
            ['QUIZ', 'Step_name']'''
        step_type = pp.one_of(ParsingModuleSchema.__step_types,
                              as_keyword=True) ('type')
        step_name = pp.rest_of_line() ('name')
        step_module = pp.Suppress('##' + pp.White()[1, ...]) + pp.Optional(step_type) \
                      + pp.Suppress(pp.White()[...]) + pp.Optional(step_name)
        return step_module
    
    @staticmethod
    def header_addon():
        '''Returns parsing module for lesson addons.
        
        Example::

            line1 = "lesson = 1234556"
            print(ParsingModuleSchema.header_addon().parseString(line1))
        
            line2 = "lang=python"
            print(ParsingModuleSchema.header_addon().parseString(line2))

        prints::
            
            ['lesson', '1234556']
            ['lang', 'python']'''
        addon = pp.one_of(ParsingModuleSchema.__header_addons,
                          as_keyword=True) ('type')
        addon_value = pp.rest_of_line() ('value')
        addon_module = addon + pp.Suppress('=' + pp.White()[...]) + addon_value
        return addon_module\


    @staticmethod
    def body_addon():
        '''Returns parsing module for lesson addons.
        
        Example::

            line1 = "SHUFFLE: false"
            print(ParsingModuleSchema.body_addon().parseString(line1))
        
            line2 = "HINT : Something"
            print(ParsingModuleSchema.body_addon().parseString(line2))

            line3 = "ANSWER:A, C"
            print(ParsingModuleSchema.body_addon().parseString(line3))

        prints::
            
            ['SHUFFLE', 'false']
            ['HINT', 'Something']
            ['ANSWER', 'A, C']'''
        addon = pp.one_of(ParsingModuleSchema.__body_addons,
                          as_keyword=True) ('type')
        addon_value = pp.rest_of_line() ('value')
        addon_module = addon + pp.Suppress(':' + pp.White()[...]) + addon_value
        return addon_module 

    @staticmethod
    def choice_variant():
        '''Returns parsing module for lesson addons.
        
        Example::

            line1 = "+)Mmm, nice answer"
            print(ParsingModuleSchema.choice_variant().parseString(line1))
        
            line2 = "-) You don't know a thing"
            print(ParsingModuleSchema.choice_variant().parseString(line2))

        prints::
            
            ['+', 'Mmm, nice answer']
            ['-', "You don't know a thing"]'''
        choicevar_type = pp.one_of(ParsingModuleSchema.__choice_types) ('type')
        choicevar_value = pp.rest_of_line() ('value')
        choicevar_module = choicevar_type + pp.Suppress(')' + pp.White()[...]) + choicevar_value
        return choicevar_module
    
    @staticmethod
    def quiz_variant():
        '''Returns parsing module for lesson addons.
        
        Example::

            line1 = "A.Mmm, nice answer"
            print(ParsingModuleSchema.quiz_variant().parseString(line1))
        
            line2 = "B) You don't know a thing"
            print(ParsingModuleSchema.quiz_variant().parseString(line2))

        prints::
            
            ['A', 'Mmm, nice answer']
            ['B', "You don't know a thing"]'''
        quizvar_label = pp.Word(pp.srange("[A-Z]"), exact=1) ('label')
        quizvar_seperator = pp.Or(ParsingModuleSchema.__quiz_seperators)
        quizvar_value = pp.rest_of_line() ('value')
        quizvar_module = quizvar_label + pp.Suppress(quizvar_seperator + pp.White()[...]) + quizvar_value
        return quizvar_module