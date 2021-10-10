import json
import logging
import os
import sys


class KVTable:
    def __init__(self, source: str = ""):
        '''
        source 本地持久化文件路径
        '''
        if source == "":
            raise Exception("需要实现这个方法")
        self.source = source
        self.internal_db = {}
        self._load_source_file()

        raise Exception("需要实现这个方法")

    def _load_source_file(self):
        '''
        将source读入internal_db
        '''
        raise Exception("需要实现这个方法")

    def _update_source(self):
        '''
        更新source本地文件
        '''
        raise Exception("需要实现这个方法")

    def set(self, key: str, value: str) -> bool:
        '''
        将k-v写入字典并更新本地文件source
        return bool 成功就返回True，失败就返回False
        '''
        self._update_source()

        raise Exception("需要实现这个方法")

    def get(self, key: str) -> str:
        '''
        获取key
        return str 返回获取到的value，没有就抛出异常
        '''

        raise Exception("需要实现这个方法")

    def update(self, key: str, value: str) -> bool:
        '''
        更新key的value，并更新source文件
        return bool 成功就返回True，失败就返回False
        '''
        self._update_source()
        raise Exception("需要实现这个方法")

    def delete(self, key: str) -> bool:
        '''
        删除key
        return bool 成功就返回True，失败就返回False
        '''
        raise Exception("需要实现这个方法")


class KVTableOperator():
    '''
    用户提示:
    需要输入的格式如下 :
    methed   您的具体操作
    [key]    您要操作的键
    [value]  您要操作的值
    Available Commands: SET set a key to db GET get a key from db UPDATE update key DELETE delete key
    '''

    def __init__(self, source: str = "",engine=None):
        '''
        source 本地持久化文件路径
        '''
        if source == "":
            raise Exception("source can not empty")
        self.source = source
        if not os.path.exists(self.source):
            with open(self.source, "w"):
                pass
        if not engine:
            raise Exception("engine can not None")
        self.internal_db = engine
        self._load_source_file()

    def __call__(self,key):
        return self.get(key)

    def __str__(self):
        self._load_source_file()
        return str(self.internal_db)

    def help(self):
        return self.__doc__

    def _load_source_file(self):
        '''
        将source读入internal_db
        '''
        # try:
        with open(self.source, "r", encoding="utf-8") as e:
            for i in e:
                # 去掉两边空白符
                i = i.strip()
                # 用空格分隔读出来的字符串返回列表, 0索引为键,1索引为值

                # 方法一
                methed = i.split()[0]
                key = i.split()[1]
                value = i.split()[2]
                #-------------------------------------------
                #if methed == "set" or methed == "update":
                    #self.internal_db[key] = value
                #elif methed == "delete":
                    #self.internal_db.pop(key)
                # ------------------------------------------
                #todo
                # 方法二: 基于反射的写法
                getattr(self, methed)(key, value, False)

    # except Exception as e:
    # logging.error(str(e))

    def _update_source(self, key, value, count):
        '''
        更新source本地文件
        '''
        # try:
        with open(self.source, "a", encoding="utf-8") as e:
            #todo
            # 不用判断直接拼接就行
            data = count + " " + key + " " + value + "\n"
            e.write(data)

    # except Exception:
    # 	raise Exception("update error")

    def set(self, key: str, value: str,callback=True) -> bool:
        '''
        将k-v写入字典并更新本地文件source
        return bool 成功就返回True，失败就返回False
        '''

        # try:
        self.internal_db[key] = value
        #todo
        # 教你一个比较装逼的写法，避免代码hardcode
        # sys._getframe().f_code.co_name可以获取当前的方法名，也就是"set"
        if callback:
            self._update_source(key, value, sys._getframe().f_code.co_name)


    def get(self, key: str) -> str:
        '''
        获取key
        return str 返回获取到的value，没有就抛出异常
        '''
        return self.internal_db[key]

    def update(self, key: str, value: str,callback=True) -> bool:
        '''
        更新key的value，并更新source文件
        return bool 成功就返回True，失败就返回False
        '''

        try:
            self.internal_db[key] = value
            if callback:
                self._update_source(key, value, sys._getframe().f_code.co_name)
        except:
            return False
        return True

    def delete(self, key: str, placeholder=None,callback=True) -> bool:
        '''
        删除key
        return bool 成功就返回True，失败就返回False
        '''
        # try:

        value = self.internal_db[key]
        if value:
            self.internal_db.pop(key)
        if callback:
            self._update_source(key, value, sys._getframe().f_code.co_name)

    def valid_cammand(self, cammand: str):
        try:
            cmd = cammand.split(" ")
            if cmd[0] == "del":
                if len(cmd) != 2:
                    return "console: del key", False
                else:
                    return "ok", True
            if cmd[0] == "get" or cmd[0] == "set" or cmd[0] == "update":
                if len(cmd) != 3:
                    return "console: {} key value".format(cmd[0]), False
                else:
                    return "ok", True
            else:
                return "console: method [key] [value]", False
        except Exception as e:
            return str(e), False


    def console(self, methed, key , value):
        while True:
            try:
                cammand = input("console:")
                error, ok = self.valid_cammand(cammand)
                if ok:
                    methed = cammand.split()[0]
                    key = cammand.split()[1]
                    value = cammand.split()[2]
                    getattr(self, methed.lower())(key, value,False)
                else:
                    print(error)

            except Exception as e:
                print("input error:({})".format(str(e)))






# def test():
#     '''
#     测试用例，不可以修改
#     '''
#     kv_table_obj = KVTableOperator("test.db")
#     kv_table_obj.set("key1", "value1")
#     # kv_table_obj.set("key2", "value2")
#     # kv_table_obj.update("key", "value_new")
#     #v = kv_table_obj.get("key1")
#     #print(v)
#     # kv_table_obj.delete("key")
#     print(kv_table_obj("key1"))
#     print(kv_table_obj)
#     print(kv_table_obj.help())
#
# def main():
#     test()
#
#
# if __name__ == "__main__":
#     main()
