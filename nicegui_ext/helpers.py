import typing as T
from functools import lru_cache

from nicegui.element import Element
from objinspect import Class, Parameter
from objinspect.util import type_to_str
from stdl import dt, st


def is_date_valid(string: str) -> bool:
    try:
        dt.parse_datetime_str(string)
        return True
    except ValueError:
        return False


def err_message_missing_param(param: Parameter) -> str:
    return f"Missing required argument '{param.name}' with type '{type_to_str(param.type)}'"


def clean_variable_name(name: str) -> str:
    return st.snake_case(name).replace("_", " ").title()


def is_type(val: T.Any, t: T.Type) -> bool:
    if T.get_origin(t) is None:
        return type(val) is t
    else:
        origin = T.get_origin(t)
        args = T.get_args(t)
        return isinstance(val, origin) and all(isinstance(arg, type) for arg in args)


@lru_cache()
def element_takes_label(e: Element) -> bool:
    obj = Class(e)
    init_method = obj.init_method
    if not init_method:
        return False
    for i in init_method.params:
        if i.name == "label":
            return True
    return False
