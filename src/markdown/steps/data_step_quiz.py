from src.markdown.schemas import ParsingModuleSchema
from src.markdown.steps.data_step import DataStep
import pyparsing as pp

class DataStepQuiz(DataStep):
    # text before answer variants
    '''text: str
    variants: list[Variant]
    step_addons: dict'''

    class Variant:
        def __init__(self, text: str, label: str, is_correct: bool=False, feedback: str=''):
            self.text = text
            self.is_correct = is_correct
            self.label = label
            self.feedback = feedback
        
        def __eq__(self, other):
            if self.text == other.text and self.is_correct == other.is_correct and \
                self.label == other.label and self.feedback == other.feedback:
                return True
            return False

    def add_info(self, lines: list[str]):
        self.text = []
        self.variants = []
        self.step_addons = {'SHUFFLE' : 'true'}
        self._correct_variants = 0

        BEGIN = 'TEXTBEGIN'
        END = 'TEXTEND'
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

                    try:
                        variant_data = ParsingModuleSchema.quiz_variant().parseString(line)
                        self.variants.append(DataStepQuiz.Variant(variant_data.value.strip(), variant_data.label))  ###
                        state = 'VARIANTS'
                        self.text = ''.join(self.text)
                        continue
                    except pp.ParseException:
                        self.text.append(line)
                        continue
                case 'VARIANTS':
                    try:
                        feedback = ParsingModuleSchema.body_addon().parseString(line)
                        if feedback.type != 'HINT':
                            self.step_addons[str(feedback.type)] = feedback.value
                            state = 'END'
                            continue
                        self.variants[-1].feedback = feedback.value
                    except pp.ParseException:
                        if line != pp.Empty():
                            variant_data = ParsingModuleSchema.quiz_variant().parseString(line)
                            self.variants.append(DataStepQuiz.Variant(variant_data.value.strip(), variant_data.label))    ###
                        continue
                case 'END':
                    try:
                        addon = ParsingModuleSchema.body_addon().parseString(line)
                        self.step_addons[str(addon.type)] = addon.value
                        continue
                    except pp.ParseException:
                        continue
                case _:
                    raise Exception("Undefined DataStepQuiz.add_info() state.")
        if self.step_addons["ANSWER"]:
            self.step_addons["ANSWER"] = self.step_addons["ANSWER"].replace(" ", "")
            self.step_addons["ANSWER"] = self.step_addons["ANSWER"].split(",")
            for var in self.variants:
                var.is_correct = var.label in self.step_addons["ANSWER"]
            self._correct_variants = len(self.step_addons["ANSWER"])
        else:
            raise Exception("Expected ANSWER obligatory addon.")

    def as_dict(self):
        data_dict = {
            "step_name": self.step_name,
            "id": self.lesson_id,
            "text": self.text,
            "variants": self.variants,
            "step_addons": self.step_addons
        }
        return data_dict