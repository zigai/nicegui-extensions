import datetime
import os
import typing as T
from dataclasses import dataclass
from functools import partial

from nicegui import ui
from nicegui.element import Element
from stdl import fs

from nicegui_ext import icons, md
from nicegui_ext.helpers import is_date_valid
from nicegui_ext.native_file_picker import NativeFileDialog

# For multi-line notifications
ui.html("<style>.multi-line-notification { white-space: pre-line; }</style>")

Position = T.Literal[
    "top-left",
    "top-right",
    "bottom-left",
    "bottom-right",
    "top",
    "bottom",
    "left",
    "right",
    "center",
]

NotificationType = T.Literal["positive", "negative", "warning", "info", "ongoing"]
FontFamily = T.Literal["font-mono", "font-sans", "font-serif"]


def notification(
    message: str,
    type: NotificationType = "info",
    position: Position = "bottom-left",
    *,
    multiline: bool = False,
    close_button: str | None = "✖",
    progress: bool = True,
    **kwargs,
) -> None:
    extra = {}
    if multiline:
        extra["classes"] = "multi-line-notification"
    ui.notify(
        message=message,
        type=type,
        position=position,
        close_button=close_button if close_button is not None else False,  # type: ignore
        progress=progress,
        **extra,
        **kwargs,
    )


def tooltip(
    message: str,
    size="text-base",
    dark: bool = True,
    font_family: FontFamily = "font-mono",
    border: str = "border border-solid",
):
    element = ui.tooltip(message).classes(font_family).classes(border).classes(size)

    if dark:
        element.classes("bg-grey-2 text-black border-black")
    else:
        element.classes("bg-grey-10 text-white border-white")

    return element


class Textarea(ui.textarea):
    def __init__(
        self,
        label: str | None = None,
        *,
        placeholder: str | None = None,
        value: str = "",
        rows: int | None = None,
        cols: int | None = None,
        clearable: bool = True,
        autogrow: bool = False,
        filled: bool = False,
        on_change: T.Callable | None = None,
        validation: dict[str, T.Callable[..., bool]] = {},
    ) -> None:
        super().__init__(
            label,
            placeholder=placeholder,
            value=value,
            on_change=on_change,
            validation=validation,
        )
        if autogrow:
            self.props(add="autogrow")
        if clearable:
            self.props(add="clearable")
        if filled:
            self.props(add="filled")
        if rows is not None:
            self.props(f"rows={rows}")
        if cols is not None:
            self.props(f"cols={cols}")


class DatePicker(Element):
    def __init__(
        self,
        label: str = "Date",
        value: datetime.date | str | None = None,
        placeholder: str | None = "YYYY//MM//DD",
        tag: str | None = None,
    ):
        super().__init__(tag=tag)
        if isinstance(value, datetime.date):
            value = value.strftime("%Y-%m-%d")

        validation = {"Invalid date!": is_date_valid}

        with ui.input(
            label,
            value=value or "",
            validation=validation,
            placeholder=placeholder,
        ) as self.text_input_element:
            with self.text_input_element.add_slot("append"):
                ui.icon("edit_calendar").on("click", lambda: self.menu_element.open()).classes(
                    "cursor-pointer"
                )
            with ui.menu() as self.menu_element:
                self.date_element = ui.date(value=value).bind_value(self.text_input_element)


DialogPosition = T.Literal["standard", "top", "bottom", "left", "right"]


class Dialog(ui.dialog):
    def __init__(
        self,
        *,
        value: bool = False,
        position: DialogPosition = "standard",
        seamless: bool = False,
        maximized: bool = False,
        full_width: bool = False,
        full_height: bool = False,
    ) -> None:
        """Dialog

        Creates a dialog based on Quasar's `QDialog <https://quasar.dev/vue-components/dialog>`_ component.
        By default it is dismissible by clicking or pressing ESC.
        To make it persistent, set `.props('persistent')` on the dialog element.

        :param value: whether the dialog should be opened on creation (default: `False`)
        """
        super().__init__(value=value)
        if maximized:
            self.props("maximized")
        self.props(f"position={position}")
        if full_width:
            self.classes("full-width")
        if full_height:
            self.classes("full-height")
        if seamless:
            self.props("seamless")


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
        with Dialog(maximized=True).classes("w-screen") as dialog, ui.card().classes("w-screen"):
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
