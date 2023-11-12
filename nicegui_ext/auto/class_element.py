import typing as T

from nicegui import ui
from nicegui.element import Element
from objinspect import Class, Parameter

from nicegui_ext.auto.auto_element import SINGLE_ROW, AutoElement
from nicegui_ext.auto.parser import DEFAULT_VALUES, STR_PARSER, element_for_type
from nicegui_ext.helpers import element_takes_label, err_message_missing_param, is_type
from nicegui_ext.ui import notification, tooltip


class ClassElement(AutoElement):
    def __init__(
        self,
        cls: T.Type,
        ignored_fields: list[str] | None = None,
        title: str | bool = True,  #
        description: bool = False,
        icon: str | None = None,
        icon_size: str = "32px",
        elements_per_row: list[int] | None = SINGLE_ROW,
        draggable: bool = False,
        expandable: bool = False,
        extras: list[Element] | None = None,
        add_delete_button: bool = False,
        add_default_button: bool = False,
        add_clear_button: bool = False,
        add_button_tooltips: bool = True,
        width_class: str = "w-fit-content",
    ) -> None:
        self.cls = cls
        self.obj = Class(self.cls)
        self._title_value = title
        self.ignored_fields = ignored_fields or []
        self.n_params = self.get_n_params()
        elements_per_row = elements_per_row or [1] * (self.n_params + len(extras or []))

        super().__init__(
            elements_per_row=elements_per_row,
            title=self.get_title(),
            description=self.obj.description or None if description else None,
            icon=icon,
            icon_size=icon_size,
            draggable=draggable,
            add_delete_button=add_delete_button,
            add_default_button=add_default_button,
            add_clear_button=add_clear_button,
            add_button_tooltips=add_button_tooltips,
            width_class=width_class,
            expandable=expandable,
        )
        self._fill_elements_per_row()

    def get_title(self) -> str | None:
        if isinstance(self._title_value, str):
            return self.format_title(self._title_value)
        if isinstance(self._title_value, bool):
            if self._title_value:
                return self.format_title(self.obj.name)
            return None
        raise TypeError(f"Invalid type for title: {type(self._title_value)}")

    def get_instance(self) -> T.Any:
        if self.obj.is_initialized:
            return self.cls.__class__(**self.get_args())
        return self.cls(**self.get_args())

    def get_init_params(self) -> dict[str, Parameter]:
        if not self.obj.init_method:
            return {}
        return self.obj.init_method._parameters

    def get_n_params(self) -> int:
        params = self.get_init_params()
        if not params:
            return 0
        return sum(1 for i in params.keys() if i not in self.ignored_fields)

    def get_args(self) -> dict[str, T.Any]:
        init_params = self.get_init_params()
        args = {}
        missing_args = {}
        for k, v in self.field_elements.items():
            value = v.value  # type: ignore
            param = init_params[k]

            if value is None and param.is_required:
                missing_args[k] = err_message_missing_param(param)
                continue

            if not param.is_typed:
                args[k] = value
                continue

            type_hint = init_params[k].type
            if is_type(value, type_hint):
                args[k] = value
            else:
                args[k] = STR_PARSER.parse(value, type_hint)

        if missing_args:
            for i in missing_args.values():
                notification(i, type="warning")
            missing_names = ", ".join(f"'{i}'" for i in missing_args.keys())
            raise ValueError(f"Missing required arguments: {missing_names}")
        return args

    def format_title(self, title: str) -> str:
        title = super().format_title(title)
        if title.endswith(" instance") and self.obj.is_initialized:
            title = title[: -len(" instance")]
        return title

    def add_input_element_for_param(self, param: Parameter) -> None:
        elem = element_for_type(param.type)
        kwargs = {}
        if element_takes_label(elem):
            kwargs["label"] = self.format_label(param.name)

        # Experimental
        if self.obj.is_initialized:
            kwargs["value"] = getattr(self.obj.instance, param.name)
        elif not param.is_required:
            kwargs["value"] = param.default

        if param.type is bool:
            kwargs["text"] = param.name.capitalize()

        e: Element = elem(**kwargs)  # type: ignore

        if param.description:
            with e:
                tooltip(param.description)

        self.field_elements[param.name] = e

    def _fill_elements_per_row(self) -> None:
        """
        Populate elements_per_row with default value in case the user provided too short list
        """
        total = sum(self._elements_per_row)
        if total < self.n_params:
            n_missing = self.n_params - total
            self._elements_per_row += [1] * n_missing

    def reset_to_defaults(self) -> None:
        init_params = self.get_init_params()
        if not init_params:
            return

        for element_field_name, element in self.field_elements.items():
            param = init_params[element_field_name]
            if not param.is_required:
                element.value = param.default  # type:ignore
            else:
                default_val = DEFAULT_VALUES.get(type(element), None)  # type:ignore
                if default_val is not None:
                    element.value = default_val  # type:ignore

    def create_reset_to_defaults_button(self) -> ui.button:
        button = ui.button(icon="refresh", on_click=self.reset_to_defaults)
        if self._add_button_tooltips:
            with button:
                tooltip("Reset")
        return button

    def _build_extra_buttons(self) -> None:
        super()._build_extra_buttons()
        with self:
            if self._add_default_button:
                with self.get_current_row():
                    self.reset_to_defaults_button = self.create_reset_to_defaults_button()

    def build(self) -> None:
        init_method = self.obj.init_method
        if not init_method:
            return

        self.build_title_row()

        for param in init_method.params:
            if param.name in self.ignored_fields:
                continue
            with self.get_current_row():
                self.add_input_element_for_param(param)


__all__ = ["ClassElement"]
