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

    Steps = fields.Nested("Step_template", many=True)
    courses = fields.List(fields.Int())
    steps = fields.List(fields.Int())


class Section_template(Base):

    Lessons = fields.Nested("Lesson_template", many=True)


class Course_template(Base):

    description = fields.Str()
    Sections = fields.Nested("Section_template", many=True)

# print( Lesson_template().dump( {'id': 1200, 'Fafa': 3453453, 'Title': 'Lessonsss', 'Steps': [ { 'id': 1000, 'title': 'Steppp', "rgsrg": 3453, "block": {'name': 'text', "gdg": 0}} ] } ))

# print( Base().load( "{'id': 130, 'Title': 'Lessonsss'}" ) )