from marshmallow import fields, Schema

class Base(Schema):
    id = fields.Integer(required=True)
    title = fields.String(required=True)
    __del_status__ = fields.Str()

class ChoiceUnique(Schema):

    class Options(Schema):
        text = fields.Str()
        is_correct = fields.Bool()
        feedback = fields.Str()

    preserve_order = fields.Bool()
    options = fields.Nested("Options", many=True)

class CodeUnique(Schema):

    code = fields.Str(required=True)
    execution_time_limit = fields.Int()
    execution_memory_limit = fields.Int()
    templates_data = fields.Str()
    is_time_limit_scaled = fields.Bool(required=True)
    samples_count = fields.Int()
    test_cases = fields.List(fields.List(fields.Str()), required=True)

class StringUnique(Schema):

    pattern = fields.Str(required=True)
    use_re = fields.Bool()
    match_substring = fields.Bool()
    case_sensitive = fields.Bool()
    code = fields.Str()
    is_text_disabled = fields.Bool()
    is_file_disabled = fields.Bool()

class FreeAnswerUnique(Schema):

    is_html_enabled = fields.Bool()

class NumberUniqueOption(Schema):

    answer = fields.Str(required=True)
    max_error = fields.Str(required=True)

class NumberUnique(Schema):

    options = fields.Nested("NumberUniqueOption", many=True)

class Step_block_template(Schema):

    text = fields.Str()
    name = fields.Str(required=True)
    options = fields.Dict()
    source = fields.Dict()

class Step_template(Schema):

    id = fields.Integer(required=True)
    cost = fields.Int()
    lesson = fields.Int()
    block = fields.Nested("Step_block_template")

class Lesson_template(Base):  

    courses = fields.List(fields.Int())
    steps = fields.List(fields.Int())


class Lesson_template_source(Base):  

    courses = fields.List(fields.Int())
    steps = fields.Nested("Step_template", many=True)


class Lesson_preview_section_template(Base):

    file = fields.Str(required=True)
    unit = fields.Int()


class Section_template(Base):

    course = fields.Int(required=True)
    lessons = fields.Nested("Lesson_preview_section_template", many=True)
    description = fields.Str()


class Course_template(Base):

    description = fields.Str()
    sections = fields.Nested("Section_template", many=True)