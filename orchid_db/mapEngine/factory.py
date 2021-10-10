from enum import Enum

from .bTree import BTreeWrapper
from .hashmap import HashMapWrapper

from .inderdb import inder_db


class EngineType(Enum):
    dict = "dict"
    hashMap = "hashMap"
    bTreeMap = "bTreeMap"
    binarySearchMap = "binarySearchMap"

class MapEngineFactory:
    @staticmethod
    def create(engine):
        if engine == "dict":
            return dict()
        elif engine == "hashMap":
            return HashMapWrapper()
        elif engine == "bTreeMap":
            return BTreeWrapper()
        elif engine == "binarySearchMap":
            return inder_db()



