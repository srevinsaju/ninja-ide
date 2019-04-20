"""
from ninja_ide.core.conf import settings

# Read global settings
# From ini to object
settings.load()

# settings.on_changed('my-setting', callback, **kwargs)

"""
import os
import json

from ninja_ide import resources

DEFAULTS_SETTINGS_FILE = os.path.join(
    resources.PRJ_PATH, 'core', 'conf', 'defaults.json')


class Node:

    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.callback = None

    def __repr__(self):
        return '<Node: {}={}>'.format(self.name, self.value)


class _Settings:

    def __init__(self, kwargs):
        for key, value in kwargs.items():
            if isinstance(value, dict):
                value = _Settings(value)
            else:
                key = key.upper()
            if isinstance(value, _Settings):
                self.__dict__[key] = value
            else:
                self.__dict__[key] = Node(key, value)

    def __repr__(self):
        return '<Settings %s' % self.__dict__

    def __getattribute__(self, attr):
        if not attr.isupper():
            return object.__getattribute__(self, attr)
        return self.__dict__[attr].value

    def register_callback(self, key, callback):
        keys = key.split('.')[1:]
        import pprint
        pprint.pprint(self.__dict__)
        # def get_nested(data, *args):
        #     if args and data:
        #         element = args[0]
        #         if element:
        #             value = data.get(element)
        #             return value if len(args) == 1 else get_nested(value, *args[1:])
        # v = get_nested(self.__dict__, *keys)
        # print(v)


def foo():
    print('LALALALLA')


settings = _Settings(json.loads(open(DEFAULTS_SETTINGS_FILE).read()))
settings.register_callback('settings.editor.display.SHOW_TABS_AND_SPACES', foo)
