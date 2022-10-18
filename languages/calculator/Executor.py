from library.BaseExecutor import BaseExecutor
from library.Postfix import Postfix
from library.ExpressionTree import ExpressionNode, ExpressionTree

class Executor(BaseExecutor):
    def p_main(self, *args):
        postfix = Postfix()
        for arg in args:
            postfix.insert(arg)
        postfix.insert('EOF')
        tokens = postfix.get()

        s = f'Postfix: [{postfix}]'
        print('=' * len(s))
        print(s)
        print('=' * len(s))
        tokens.reverse()
        tree = ExpressionTree(tokens)
        result = tree.calculate()
        print('RESULT:', result)