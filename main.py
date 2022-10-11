from lexor import Lexor

with open('data/code.calculator') as file:
    code = file.read()

lexor = Lexor('data/calculator.json')
lexor.run(code)


