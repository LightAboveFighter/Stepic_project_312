from abc import ABC
import pyparsing as pp
import src.API.Classes as sac
import io


class Step(ABC):
    '''id: int
    step_name: str
    step_info: str
    params: dict'''

    def __init__(
        self,
        id: int,
        nam: str,
        inf: list
    ) -> None:
        self.id = id
        self.step_name = nam
        self.step_info = inf


class StepText(Step):
    def text_info(self):
        return ''.join(self.step_info)


class Lesson:
    '''title: str
    steps: list or []
    id: int
    sect_ids: list or []
    params: dict'''

    def _module_step(self):
            step_type = pp.one_of(['QUIZ', 'CHOICE', 'TEXT'], as_keyword=True) ('type')
            step_name = pp.rest_of_line() ('name')
            parse_module = pp.Suppress(pp.Keyword('##')) + pp.Optional(step_type) + pp.Suppress(pp.ZeroOrMore(pp.White())) + pp.Optional(step_name)
            return parse_module

    def __init__(self, lesson_path: str):
        name = pp.rest_of_line ('name')
        parse_name = pp.Suppress(pp.Keyword('#') + pp.ZeroOrMore(pp.White())) + pp.Optional(name)

        id = pp.Word(pp.nums) ('id')
        parse_id = pp.Suppress(pp.Keyword('lesson') + pp.ZeroOrMore(pp.White()) + '=' + pp.ZeroOrMore(pp.White())) + id

        parse_step = self._module_step()

        with io.open(lesson_path, 'r', encoding='utf-8') as f:
            # Writting down name of the lesson
            self.title = (parse_name.parseString(f.readline())).name
            
            # Writting down id of the lesson 
            for id_line in f:
                if id_line != pp.Empty():
                    self.id = (parse_id.parseString(id_line)).id
                    break
            
            # Writting down steps of the lesson
            self = []

            step_lines = []
            first_cycle = True

            for line in f:
                try:
                    new_step = parse_step.parseString(line)
                    if not first_cycle:
                        self.steps.append(StepText(self.id, previous_step.name, step_lines))  # for now -- only StepText
                    step_lines = []
                    first_cycle = False
                    previous_step = new_step
                except pp.ParseException:
                    step_lines.append(line)
            self.steps.append(StepText(self.id, previous_step.name, step_lines))
        # self.API = sac.Lesson(self.title, self.id, self.steps)     # here may be params, which are totally optional (^人^)