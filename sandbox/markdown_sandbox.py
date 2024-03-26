import pyparsing as pp

line1 = input()
step_type = pp.Word(pp.alphas) ("step_type")
# step_name = pp.ZeroOrMore(pp.Word(pp.alphas))
step_name = pp.rest_of_line()
parse_module = '##' + pp.Suppress(pp.White()) + step_type + pp.Suppress(pp.White()) + step_name
module = parse_module.parseString(line1)
print(parse_module.parseString(line1))
print(module.step_type)

line2 = input()
question_text = pp.rest_of_line()
parse_question = question_text
print(parse_question.parseString(line2))

if module.step_type == 'QUIZ':
    okay = True
    while okay:
        try:
            next_line = input()
            answer_letter = pp.Word(pp.alphas) ("letter")
            answer_text = pp.rest_of_line()
            parse_answer = answer_letter + pp.Suppress(".") + pp.Suppress(pp.White()) + answer_text
            answer = parse_answer.parseString(next_line)
            print(answer)
        except:
            print("End of answers.")
            okay = False
    
    while True:
        param = pp.Word("SHUFFLE", "ANSWER") ("parameter")
        vals = pp.rest_of_line() ("values")
        parse_parameters = param + pp.Suppress(": ") + vals
        parameters = parse_parameters.parseString(next_line)
        if parameters.parameter == "SHUFFLE":
            parse_bool_line = pp.Word("true", "false")
            bool_line = parse_bool_line.parseString(parameters.values)

        next_line = input()
        if next_line == '':
            break
    

    # while answer.letter in "QWERTYUIOPASDFGHJKLZXCVBNM":
    #     next_line = input()
    #     answer_letter = pp.Word(pp.alphas) ("letter")
    #     answer_text = pp.rest_of_line()
    #     parse_answer = answer_letter + pp.Suppress(".") + pp.Suppress(pp.White()) + answer_text
    #     answer = parse_answer.parseString(next_line)
    #     print(answer)

## QUIZ Сравнение указателей
# Как проверить, что `s` и `p` указывают на одну и ту же область памяти?
# A. `s == p`
# B. `*s == *p`
# C. `s[0] == p[0]`
# D. `strcmp(s, p)`
# E. `strcmp(s, p) == 0`
# SHUFFLE: false
# ANSWER: A, D