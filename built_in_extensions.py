from collections import OrderedDict


class OrderedDictInsert(OrderedDict):
    """
    OrderedDict c вставкой в произвольную позицию
    """
    def insert(self, index, key, value):
        self[key] = value
        for ii, k in enumerate(list(self.keys())):
            if ii >= index and k != key:
                self.move_to_end(k)