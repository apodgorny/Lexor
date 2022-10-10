class CycleDetector:
    def __init__(self):
        self.suspect = False
        self.start = None
        self.end   = None
        self.next  = None

    def _get_index(self, l, v):
        for i in range(len(l)):
            if l[i] == v:
                return i
        return None

    def detect(self, l, v):
        if self.suspect:
            if l[self.next] == v:
                if self.next == self.end:
                    return True
                else:
                    self.next += 1
        else:
            index = self._get_index(l, v)
            if index is not None:
                self.suspect = True
                self.start = index
                self.next = index + 1
                self.end = len(l)

        return False
