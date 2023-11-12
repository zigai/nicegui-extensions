import re
import sys

from nicegui import ui
from nicegui.element import Element

from nicegui_ext import md
from nicegui_ext.draggable import Draggable
from nicegui_ext.ui import tooltip

SINGLE_ROW = [sys.maxsize]  # all elements in one row
ONE_PER_ROW = [1]  # one element per row, will auto-expand


class AutoElement(Draggable):
    def __init__(
        self,
        elements_per_row: list[int] = SINGLE_ROW,
        title: str | None = None,
        description: str | None = None,
        icon: str | None = None,
        icon_size: str = "32px",
        draggable: bool = False,
        expandable: bool = False,
        add_delete_button: bool = False,
        add_default_button: bool = False,
        add_clear_button: bool = False,
        add_button_tooltips: bool = True,
        width_class: str = "w-fit-content",
    ) -> None:
        self._title_text = title
        self._icon_name = icon
        self._icon_size = icon_size
        self._description_text = self.get_description(description)

        self._add_delete_button = add_delete_button
        self._add_default_button = add_default_button
        self._add_clear_button = add_clear_button
        self._add_button_tooltips = add_button_tooltips

        self._elements_per_row: list[int] = elements_per_row
        self._row_index = 0
        self.is_expandable = expandable
        self.rows: list[ui.row] = []
        self.field_elements: dict[str, Element] = {}

        super().__init__(enable_dragging=draggable, width_class=width_class)
        self._build_extras()
        self._build_extra_buttons()

    def get_description(self, description: str | None) -> str | None:
        return description

    def get_container(self) -> ui.expansion | ui.row:
        return self.container

    def new_row(self) -> ui.row:
        if not self.is_expandable:
            return ui.row().classes("items-center")

        with self.container:
            return ui.row().classes("items-center")

    def add_extra_element(self, element: Element) -> None:
        with self:
            element.move(self.get_current_row())

    def get_current_row(self) -> ui.row:
        try:
            space_left = self._elements_per_row[self._row_index]
        except IndexError:
            self._elements_per_row.append(1)
            space_left = 1

        if space_left == 0:
            self._row_index += 1
            try:
                space_left = self._elements_per_row[self._row_index]
            except IndexError:
                self._elements_per_row.append(1)
                space_left = 1

        self._elements_per_row[self._row_index] -= 1
        if len(self.rows) <= self._row_index:
            self.rows.append(self.new_row())
        return self.rows[self._row_index]

    def format_label(self, label: str) -> str:
        return label.replace("_", " ").capitalize()

    def format_title(self, title: str) -> str:
        matches = re.finditer(".+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)", title)
        words = [m.group(0).capitalize() for m in matches]
        return " ".join(words)

    def build_title_row(self) -> None:
        if self.is_expandable:
            self.container = ui.expansion(
                self._title_text,
                icon=self._icon_name,
                value=True,
            ).classes(self.width_class)

            if self._description_text:
                with self.container:
                    tooltip(self._description_text)
            return

        with ui.row().classes("items-center") as self.container:
            if not self._icon_name and not self._title_text:
                return

            with self.get_current_row():
                if self._icon_name:
                    self.icon = ui.icon(self._icon_name, size=self._icon_size)
                if self._title_text:
                    self.title = md.heading(
                        self._title_text, level=4, tooltip=self._description_text
                    )
                else:
                    if self._icon_name and self._description_text:
                        with self.icon:
                            tooltip(self._description_text)

    def _build_extra_buttons(self):
        if self._add_clear_button:
            with self.get_current_row():
                self.clear_fields_button = self.create_clear_fields_button()

        if self._add_delete_button:
            with self.get_current_row():
                self.delete_button = self.create_delete_button()

    def create_delete_button(self):
        button_delete = ui.button(icon="delete", on_click=self.delete_from_parent)
        if self._add_button_tooltips:
            with button_delete:
                tooltip("Delete")
        return button_delete

    def create_clear_fields_button(self):
        button_clear = ui.button(icon="backspace", on_click=self.clear_fields)
        if self._add_button_tooltips:
            with button_clear:
                tooltip("Clear")
        return button_clear

    def _build_extras(self, extras: list[Element] | None = None):
        if not extras:
            return
        with self.get_current_row():
            for element in extras:
                element.move(self.get_current_row())

    def clear_fields(self):
        for k, v in self.field_elements.items():
            default_val = DEFAULT_VALUES.get(type(v), None)  # type: ignore
            if default_val is not None:
                v.value = default_val  # type: ignore

    def build(self):
        raise NotImplementedError


__all__ = ["AutoElement", "SINGLE_ROW", "ONE_PER_ROW"]
