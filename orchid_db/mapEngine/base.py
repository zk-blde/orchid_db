class BaseMapWrapper:
    def __setitem__(self, key, value):
        raise Exception("please implementation")

    def __getitem__(self, key):
        assert type(key) == str
        value = self.get(key)
        if not value:
            raise KeyError
        else:
            return value

    def get(self, key):
        raise Exception("please implementation")

    def _del(self, key):
        raise Exception("please implementation")

    def __delitem__(self, key):
        assert type(key) == str
        return self._del(key)

    def pop(self, key):
        assert type(key) == str
        return self._del(key)



