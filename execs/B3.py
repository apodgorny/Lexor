from lexor.Executor import Executor
class B3(Executor):
    def p_thing(self, t):
        print('thing', t)
        return t

    def p_list(self, *args):
        print('p_list', args)
        return args

    def p_trt(self, tl, r, tr):
        print('p_trt', tl, r, tr)
        return 1

    def p_q_3(self, tl, r):
        print('p_q_3', tl, r)
        return 1
