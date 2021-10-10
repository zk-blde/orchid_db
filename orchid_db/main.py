from internal.KVTable import KVTableOperator
from mapEngine.factory import EngineType, MapEngineFactory

if __name__=="__main__":
	binarySearchMap_engine = MapEngineFactory.create(engine=EngineType.binarySearchMap.value)

	kv_table_obj = KVTableOperator("./data/test.db",engine=binarySearchMap_engine)
	# kv_table_obj.set("key1", "value1")
	print(kv_table_obj.get("key1"))
	print(kv_table_obj)