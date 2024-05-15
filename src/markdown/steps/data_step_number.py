from src.markdown.schemas import ParsingModuleSchema
from src.markdown.steps.data_step import DataStep
import pyparsing as pp

class DataStepNumber(DataStep):
    '''step_name: str
    lesson_id: int
    text: str
    step_addons: dict'''

    def add_info(self, lines: list[str]):
        self.text = []
        self.step_addons = {}

        BEGIN = 'TEXTBEGIN'
        END = 'TEXTEND'
        only_text = False
        for line in lines:
            if line.strip() == BEGIN:
                only_text = True
                continue
            elif line.strip() == END:
                only_text = False
                continue
            if only_text:
                self.text.append(line)
                continue

            try:
                answer = ParsingModuleSchema.body_addon().parseString(line)
                if answer.type == 'ANSWER':
                    self.step_addons[str(answer.type)] = answer.value
                    self.text = ''.join(self.text) 
                else:
                    raise ValueError("Expected only ANSWER in addons.") 
                continue
            except pp.ParseException:
                self.text.append(line)
                continue
        
        if self.step_addons["ANSWER"]:
            if "+-" in self.step_addons["ANSWER"]:
                self.step_addons["ANSWER"] = self.step_addons["ANSWER"].split("+-")
                try:
                    self.step_addons["ANSWER"][0] = float(self.step_addons["ANSWER"][0])
                    self.step_addons["ANSWER"][1] = float(self.step_addons["ANSWER"][1])
                except ValueError:
                    raise Exception("Answer value can not be converted into float.")
            else:
                try:
                    answer = self.step_addons["ANSWER"].replace(",", ".")
                    answer = float(answer)
                    self.step_addons["ANSWER"] = [answer]
                    print("ok")
                except ValueError:
                    raise Exception("Answer value can not be converted into float.")
        else:
            raise pp.ParseException("ANSWER must be in addons.")

    def as_dict(self):
        data_dict = {
            "step_name": self.step_name,
            "id": self.lesson_id,
            "text": self.text,
            "step_addons": self.step_addons
        }
        return data_dict
