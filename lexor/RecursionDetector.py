class RecursionDetector:
    def __init__(self, max_depth=10):
        self.suspect = False
        self.depth = 0
        self.max_depth = max_depth
        self.fragment = []

        self.start_index = None
        self.end_index   = None
        self.next_index  = None

    def _get_last_index(self, l, v):
        for n in range(len(l)-1, -1, -1):
            if l[n] == v:
                return n
        return None

    def detect(self, path_list, next_value):
        if self.suspect:
            '''
            [..., A, b, c] + A => [..., A, b, c]
            suspect, that next is "b", then "c"
            then, if "A" => cycle complete, recursion detected.
            '''
            if path_list[self.next_index] == next_value: # suspicion continues to prove
                if self.next_index == self.end_index:    # suspicion turns into fact
                    self.depth += 1
                    self.start_index = self.end_index
                    self.end_index = len(path_list)
                    if self.depth >= self.max_depth:     # facts turn into pattern
                        for n in range(self.start_index, self.end_index):
                            self.fragment.append(path_list[n])
                        return True
                self.next_index += 1
            else:                                        # relax
                self.suspect = False
                self.depth = 0
        else:
            index = self._get_last_index(path_list, next_value)
            if index is not None:
                self.suspect = True
                self.depth = 0
                self.start_index = index            # first occurance of suspect
                self.next_index = index + 1         # next index to check
                self.end_index = len(path_list)     # second occurence of suspect

        return False
