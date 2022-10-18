import pytest
from library.RecursionDetector import RecursionDetector

class Test_RecursionDetector:
    def test_suspicion_arise(self):
        rd = RecursionDetector()
        assert rd.suspect == False
        rd.detect([1, 2, 3, 4], 1)
        assert rd.suspect == True

    def test_max_depth_reached(self):
        max_depth = 4
        rd = RecursionDetector(max_depth)
        assert rd.suspect == False
        a = [1, 2, 3, 4]
        for i in range(max_depth):
            for n in [1, 2, 3, 4]:
                rd.detect(a, n)
                a.append(n)
        detected = rd.detect(a, 1)

        if detected:
            print(rd.fragment)

        assert detected == True

    def test_recursion_with_real_data(self):
        lines = tuple(open('tests/repeating_tokens.txt', 'r'))
        max_depth = 4
        rd = RecursionDetector(max_depth)
        tokens = []
        for token in lines:
            detected = rd.detect(tokens, token)
            tokens.append(token)
            if detected:
                break

        if detected:
            for token in rd.fragment:
                print(token.rstrip())

        assert detected == True