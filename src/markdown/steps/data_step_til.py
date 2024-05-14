from src.markdown.schemas import ParsingModuleSchema
from src.markdown.steps.data_step import DataStep
import pyparsing as pp

class DataStepTaskinline(DataStep):
    def add_info(self, lines: list[str]):
        self.text = []
        self.code = []
        self.inputs = []
        self.outputs = []

        data = []
        BEGIN = 'TEXTBEGIN'
        END = 'TEXTEND'
        CODE = 'CODE'
        TEST = 'TEST'
        state = 'TEXT'
        only_text = False
        for line in lines:
            match (state):
                case 'TEXT':
                    if line.strip() == BEGIN:
                        only_text = True
                        continue
                    elif line.strip() == END:
                        only_text = False
                        continue
                    if only_text:
                        self.text.append(line)
                        continue

                    elif line.strip() == CODE or line.strip() == TEST:
                        state = line.strip()
                        self.text = ''.join(self.text)
                        continue
                    self.text.append(line)
                    continue

                case 'CODE':
                    if line.strip() == CODE or line.strip() == TEST:
                        state = line.strip()
                        continue
                    self.code.append(line)
                    continue
                case 'TEST':    ## some problems with outputs, need to fix ASAP
                    if line.strip() == CODE or line.strip() == TEST:
                        state = line.strip()
                        continue
                    elif line.strip() == '----':
                        self.inputs.append(''.join(data))
                        data = []
                        continue
                    elif line.strip() == '====':
                        self.outputs.append(''.join(data))
                        data = []
                        continue
                    data.append(line)
                    continue
                case _:
                    raise Exception("Undefined DataStepTaskinline.add_info() state.")
        self.code = ''.join(self.code)
        

    def as_dict(self):
        data_dict = {
            "step_name": self.step_name,
            "id": self.lesson_id,
            "text": self.text,
            "code": self.code,
            "inputs": self.inputs,
            "outputs": self.outputs
        }
        return data_dict