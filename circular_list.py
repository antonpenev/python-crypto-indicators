import os


class CircularList(object):
    def __init__(self, size):
        self.size = size
        self.start = 0
        self.current_size = 0
        self._arr = [None]*size

    def add(self, element):
        idx = self.start
        self.start = (self.start + 1) % self.size
        self._arr[idx] = element
        if self.current_size < self.size:
            self.current_size += 1

    def get_last_elemet(self):
        if self.current_size == 0:
            raise Exception("Array is empty")

        return self._arr[(self.start - 1 + self.size) % self.size]

    # If None is passed, then it returns list of all elements
    def get_ordered_elements(self):
        if self.current_size == self.size:
            return self._arr[self.start: self.current_size] + self._arr[0: self.start]
        return self._arr[0: self.start]

    def get_last_n_elements(self, n):
        if n > self.current_size:
            raise("N={} is greater than the size of the array!".format(n))
        if n == 0:
            return []
        return self.get_ordered_elements()[-n:]

    def length(self):
        return self.current_size
