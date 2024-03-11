from abc import ABC, abstractclassmethod
import pyparsing as pp

def module_step():
    _step_type = pp.Word(pp.alphas) ('type')
    _step_name = pp.rest_of_line() ('name')
    _parse_module = pp.Suppress('##') + pp.Suppress(pp.White()) + _step_type + pp.Suppress(pp.White()) + _step_name
    return _parse_module


class Step(ABC):
    _lesson_id: int
    _position: int
    _step_type: str
    _step_name: str
    
    def __init__(
        self,
        les_id: int,
        pos: int,
        typ: str,
        nam: str
    ) -> None:
        self._lesson_id = les_id
        self._position = pos
        self._step_type = typ
        self._step_name = nam
    
    @property
    def lesson_id(self) -> int:
        return self._lesson_id

    @property
    def position(self) -> int:
        return self._position

    @property
    def step_type(self) -> str:
        return self._step_type

    @property
    def step_name(self) -> str:
        return self._step_name


class StepText(Step):
    _step_name: str
    _text_lines: list
    
    def __init__(self,
                 les_id: int,
                 t_lines: list
    ) -> None:
        self._lesson_id = les_id
        self._text_lines = t_lines


class Lesson:
    _lesson_name: str
    _lesson_id: int
    _step_list: list

    def __init__(self, lesson_path: str):
        name = pp.rest_of_line ('name')
        parse_name = pp.Suppress('#' + pp.White()) + name

        les_id = pp.Word(pp.nums) ('id')
        parse_id = pp.Suppress('lesson' + pp.White() + '=' + pp.White()) + les_id
        
        parse_step = module_step()

        with open(lesson_path, 'r') as f:
            # Writting down name of the lesson
            self._lesson_name = (parse_name.parseString(f.readline())).name
            
            # Writting down id of the lesson 
            for id_line in f:
                if id_line != pp.Empty():
                    self._lesson_id = (parse_id.parseString(id_line)).id
                    break
            
            # Writting down steps of the lesson
            self._step_list = []

            step_lines = []
            first_cycle = True

            for line in f:
                try:
                    parse_step.parseString(line)
                    if not first_cycle:
                        self._step_list.append(StepText(self._lesson_id, step_lines))  # for now -- only StepText
                    step_lines = []
                    first_cycle = False
                except:
                    step_lines.append(line)
            self._step_list.append(StepText(self.lesson_id, step_lines))

    @property
    def lesson_name(self) -> str:
        return self._lesson_name

    @property
    def lesson_id(self) -> int:
        return self._lesson_id
    

test = Lesson('test2.md')
print(test.lesson_name)
print(test._step_list[1]._lesson_id)
# l = []
# m = StepText(1212, 'Happy Thoughts')
# l.append(m)
# print(l[0]._text_lines)