from typing import Type
from r2logparse.models.log import BaseLog


def get_subclasses(cls: Type):
    for subclass in cls.__subclasses__():
        yield from get_subclasses(subclass)
        yield subclass


def parse_msg(logmsg: str):
    for subclass in get_subclasses(BaseLog):
        result = subclass.from_logmsg(logmsg)
        if result:
            return result


def call_hooks(hooks, *args, **kwargs):
    for hook in hooks:
        try:
            hook(*args, **kwargs)
        except Exception as e:
            print(e)
