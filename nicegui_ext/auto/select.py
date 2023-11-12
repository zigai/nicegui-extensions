import typing as T

from nicegui import ui
from objinspect.util import get_enum_choices, get_literal_choices, is_enum, is_literal

from nicegui_ext.helpers import clean_variable_name


def typehint_select(
    hint: T.Type | T.Any,
    *,
    label: str | None = None,
    value: T.Any = None,
    on_change: T.Callable | None = None,
    with_input: bool = False,
    multiple: bool = False,
    clearable: bool = False,
    width_class="w-40",
) -> ui.select:
    """Creates a select element from a enum or Literal type hint."""
    if is_enum(hint):
        choices = get_enum_choices(hint)
    elif is_literal(hint):
        choices = get_literal_choices(hint)
    else:
        raise ValueError(f"Type {type(hint)} not supported. Must be enum.Enum or typing.Literal")

    options = {i: clean_variable_name(i) for i in choices}
    if value:
        if value not in options.keys():
            raise ValueError(f"Value '{value}' not in options")

    select = ui.select(
        options,
        label=label,
        value=value,
        on_change=on_change,
        with_input=with_input,
        multiple=multiple,
        clearable=clearable,
    )
    select.classes(width_class)
    return select
