import typing as T
from functools import lru_cache

from nicegui.element import Element
from objinspect import Class, Parameter
from objinspect.util import get_literal_choices, is_pure_literal, type_to_str
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
    """
    Note: not fully implemented. Only supports basic types.
    """
    if is_pure_literal(t):
        return val in get_literal_choices(t)
    origin = T.get_origin(t)
    args = T.get_args(t)

    if origin is None:
        return isinstance(val, t)
    elif origin is T.Union:
        return any(is_type(val, arg) for arg in args)
    else:
        if not isinstance(val, origin):
            return False
        if args:
            return all(is_type(val, arg) for arg in args)
        return True


@lru_cache()
def element_init_takes_label(e: Element) -> bool:
    obj = Class(e)
    init_method = obj.init_method
    if not init_method:
        return False
    for i in init_method.params:
        if i.name == "label":
            return True
    return False
