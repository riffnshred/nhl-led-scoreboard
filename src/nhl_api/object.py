"""Module that is used for holding basic objects"""
import json

class Object(object):
    def __init__(self, d):
        if type(d) is str:
            d = json.loads(d)
        self.convert_json(d)

    def convert_json(self, d):
        self.__dict__ = {}
        if d.items() is not None:
            for key, value in d.items():
                if type(value) is dict:
                    value = Object(value)
                self.__dict__[key] = value

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]

class MultiLevelObject(object):
    """
        Turn multi dimensional dictionary into an object of objects.
        Used to turn raw API data into an object.
    """
    def __init__(self, data):
        # loop through data
        for x in data:
            # set information as correct data type
            try:
                setattr(self, x, int(data[x]))
            except ValueError:
                try:
                    setattr(self, x, float(data[x]))
                except ValueError:
                    # string if not number
                    setattr(self, x, str(data[x]))
            except TypeError:
                if isinstance(data[x], list):
                    list_data = data[x]
                    obj_list = []
                    for index in range(len(list_data)):
                        obj_list.append(MultiLevelObject(list_data[index]))
                    setattr(self, x, obj_list)
                else:
                    obj = Object(data[x])
                    setattr(self, x, obj)