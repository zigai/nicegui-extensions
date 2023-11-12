import os
import typing as T
from dataclasses import dataclass
from functools import partial

from nicegui import ui
from nicegui.element import Element
from stdl import fs

from nicegui_ext import icons, md
from nicegui_ext.native_file_picker import NativeFileDialog
from nicegui_ext.ui import Textarea, notification, tooltip


class TextareaDialog(Element):
    def __init__(
        self,
        title: str | None = None,
        rows: int = 30,
        cols: int | None = None,
        placeholder: str | None = None,
        autogrow: bool = True,
    ) -> None:
        self.data: str | None = None
        self.rows = rows
        self.cols = cols
        self.title = title
        self.placeholder = placeholder
        self.autogrow = autogrow
        super().__init__()

    async def open(self):
        file_dialog = NativeFileDialog()
        with ui.dialog().classes("w-screen") as dialog, ui.card().classes("w-screen"):
            if self.title:
                with ui.row().classes("items-center"):
                    md.heading(self.title, level=3)

            textarea = Textarea(
                rows=self.rows,
                cols=self.cols,
                placeholder=self.placeholder,
                clearable=True,
                autogrow=self.autogrow,
            ).classes("w-full")

            def submit():
                dialog.submit(textarea.value)
                self.data = textarea.value

            def import_file():
                path = file_dialog.open()
                if not path:
                    notification("No file selected", type="warning")
                    return
                if os.path.isfile(path):
                    textarea.value = fs.File(path).read()
                else:
                    notification(f"Invalid file '{path}'", type="warning")

            with ui.row().classes("items-start"):
                ui.button("Done", icon="done", on_click=submit)
                ui.button("From file", icon=icons.UPLOAD_FILE, on_click=import_file)
                ui.button(icon=icons.CLOSE, on_click=dialog.close)

        selected = await dialog
        self.data = selected


@dataclass()
class SelectOption:
    name: str
    value: str
    tooltip: str | None = None


async def selection_dialog(
    options: list[SelectOption],
    title: str | None = None,
    one_per_row: bool = False,
    width_class="w-screen",
):
    if not options:
        raise ValueError("Selection data must not be empty")

    with ui.dialog().classes("items-center").classes(width_class) as dialog, ui.card().classes(
        "items-center"
    ).classes(width_class):
        if title:
            md.heading(title, level=4)

        def submit(value):
            dialog.submit(value)

        def make_button():
            button = ui.button(opt.name, on_click=partial(submit, value=opt.value))
            if opt.tooltip:
                with button:
                    tooltip(opt.tooltip)

        with ui.row().classes("items-center"):
            for opt in options:
                if one_per_row:
                    with ui.column().classes("items-center"):
                        make_button()
                else:
                    make_button()

    selected = await dialog
    return selected


def list_display_dialog(
    items: list[T.Any],
    item_display_fn: T.Callable | None = None,
    title: str | None = None,
    width_class="w-screen",
):
    if not item_display_fn:
        item_display_fn = lambda item: ui.markdown(f"- {item}")

    with ui.dialog().classes(width_class) as dialog, ui.card().classes(width_class):
        if title:
            md.heading(title, level=4)
        for item in items:
            with ui.row().classes("items-center"):
                item_display_fn(item)

    return dialog
