from lexor import Lexor

with open('data/code.b3') as file:
    code = file.read()

lexor = Lexor('data/synthax.b3.json')
lexor.run(code)


