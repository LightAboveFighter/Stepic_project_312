from marshmallow import fields, Schema

class Base(Schema):
    id = fields.Integer(required=True)
    Title = fields.String(required=True)

class Step_template(Base):
    type = fields.Str(required=True)
    cost = fields.Int()
    options = fields.Dict()
    source = fields.Dict()
    text = fields.Str()

class Lesson_template(Base):  
    Steps = fields.Nested("Step_template", many=True)

class Section_template(Base):
    Lessons = fields.Nested("Lesson_template", many=True)

class Course_template(Base):
    description = fields.Str()
    Sections = fields.Nested("Section_template", many=True)

# print( Lesson_template().dump( {'id': 1200, 'Fafa': 3453453, 'Title': 'Lessonsss', 'Steps': [ { 'id': 1000, 'title': 'Steppp', "rgsrg": 3453, 'type': 'text'} ] } ))

# print( Base().load( "{'id': 130, 'Title': 'Lessonsss'}" ) )