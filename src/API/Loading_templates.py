from marshmallow import fields, Schema

class Base(Schema):
    id = fields.Integer(required=True)
    title = fields.String(required=True)


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


class Section_template(Base):

    course = fields.Int(required=True)
    lessons = fields.Nested("Lesson_template", many=True)
    description = fields.Str()


class Section_template_source(Base):

    course = fields.Int(required=True)
    lessons = fields.Nested("Lesson_template_source", many=True)
    description = fields.Str()


class Course_template(Base):

    description = fields.Str()
    sections = fields.Nested("Section_template", many=True)


class Course_template_source(Base):

    description = fields.Str()
    sections = fields.Nested("Section_template_source", many=True)