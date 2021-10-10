import collections

__all__ = ['Hashmap']

import threading

from mapEngine.base import BaseMapWrapper

MINSIZE = 8
PERTURB_SHIFT = 5

KeyValue = collections.namedtuple('KeyValue', ('key', 'value'))


class Hashmap:
    """An implementation of dictobj in pure Python

    This code simply demonstrates how to write a dictionary structure 
    in Python without the dict() primitive.

    Hashmap is an open addressing dictionary implementation with 
    amortized constant time lookup implementation that supports the 
    following interface:

        x[key] => value or Hashmap.absent
        x[key] <= value
        key in x => boolean
        iter(x) => Generator
        len(x) => Integer
        del x[key] 

    Open address probing is most effective when its load < 2/3. This 
    implementation resizes the backing structure when the load exceeds
    this value. 

    Hashmap uses the hash() primitive to generate hash keys. The open
    address indexing as that of dictobj. For additional references,
    see the following:

    http://svn.python.org/view/python/trunk/Objects/dictobject.c?view=markup
    http://svn.python.org/view/python/trunk/Objects/dictnotes.txt?view=markup
    http://www.laurentluce.com/posts/python-dictionary-implementation/
    
    """

    absent = object()

    def __init__(self, minsize=MINSIZE, perturb_shift=PERTURB_SHIFT):
        self._minsize = minsize
        self._perturb_shift = perturb_shift
        self._build(self._minsize)

    def __getitem__(self, key):
        """x[key] => value or Hashmap.absent

        Returns the value of the Hashmap at the key, or Hashmap.absent 

        """
        _, kv_pair = self._lookup(key, self._backing)
        if kv_pair:
            return kv_pair.value
        else:
            return Hashmap.absent

    def __setitem__(self, key, value):
        """x[key] = value

        Sets the value of the Hashmap at the key. It resizes the backing
        structure if the utilization of the Hashmap is > ~ 2/3

        """
        i, kv_pair = self._lookup(key, self._backing)
        self._backing[i] = KeyValue(key, value)
        if kv_pair is None:
            self._used += 1

        size = len(self._backing)
        utilization = self._used / size
        if utilization > 0.67:
            self._resize(self._incr_size(size))

    def __contains__(self, key):
        """key in x => boolean

        Returns true if key is contained in the Hashmap.

        """
        _, kv_pair = self._lookup(key, self._backing)
        return kv_pair and not kv_pair.value is Hashmap.absent

    def __iter__(self):
        """iter(x) => Generator

        Returns a generator that iterates over the key value tuples in
        the Hashmap.

        """
        for kv_pair in self._backing:
            if kv_pair and not kv_pair.value is Hashmap.absent:
                yield kv_pair

    def __len__(self):
        """len(x) => Integer

        Returns the number of key value tuples stored in the Hashmap.

        """
        return self._used - self._deleted

    def __delitem__(self, key):
        """del(x[key])

        Sets the key in the Hashmap to absent, releasing the original
        item. It resizes the backing structure if the utilization of 
        the Hashmap is < ~ 1/6

        """
        i, kv_pair = self._lookup(key, self._backing)
        if kv_pair and not kv_pair.value is Hashmap.absent:
            self._backing[i] = KeyValue(key, Hashmap.absent)
            self._deleted += 1

            size = len(self._backing)
            utilization = (self._used - self._deleted) / size
            if utilization < 0.16:
                self._resize(self._decr_size(size))
        else:
            raise KeyError('no such item!')

    def _lookup(self, key, backing):
        # Performs a lookup to find the index and value of the key 
        # in the backing structure
        for i in self._indices(key, len(backing)):
            value = backing[i]
            if value is None or value.key == key:
                return i, value
        assert False, 'should not reach this!'

    def _indices(self, key, size):
        # Produces the list of indices that the Hashmap uses in 
        # open addressing
        #
        # Based on:
        # http://svn.python.org/view/python/trunk/Objects/dictobject.c?view=markup
        j = perturb = hash(key)
        for _ in range(size):
            j %= size
            yield j
            j = 5 * j + 1 + perturb
            perturb >>= self._perturb_shift

    def _resize(self, new_size):
        # Resizes the backing structure if new size is different
        if new_size != len(self._backing):
            old_backing = self._backing[:]
            self._build(new_size, old_backing)

    def _build(self, size, init=None):
        # Build a new backing structure given a old list of (possibly None)
        # key value tuples
        if not init:
            init = []
        self._backing = [None] * size
        self._used = 0
        self._deleted = 0
        for kv_pair in init:
            if kv_pair and not kv_pair.value is Hashmap.absent:
                self[kv_pair.key] = kv_pair.value

    def _incr_size(self, size):
        return size * 2

    def _decr_size(self, size):
        return max(self._minsize, size // 2)


class HashMapWrapper(BaseMapWrapper):
    ###########################################################################
    # 这是一个单例模式的标准写法，线程安全
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            with HashMapWrapper._instance_lock:
                if not hasattr(cls, '_instance'):
                    HashMapWrapper._instance = super().__new__(cls)

            return HashMapWrapper._instance

    ############################################################################
    def __init__(self):
        self.hash_map_core = Hashmap()

    def __setitem__(self, key, value):
        assert type(key) == str
        self.hash_map_core["key"] = value

    def __getitem__(self, key):
        value = self.get(key)
        if not value:
            raise KeyError
        return self.hash_map_core[key]

    def get(self, key):
        assert type(key) == str
        value = self.hash_map_core[key]

        if type(value) == object:

            return None
        else:
            return value

    def _del(self, key):
        assert type(key) == str
        del self.hash_map_core[key]

    def __delitem__(self, key):
        assert type(key) == str
        return self._del(key)

    def pop(self, key):
        assert type(key) == str
        return self._del(key)
