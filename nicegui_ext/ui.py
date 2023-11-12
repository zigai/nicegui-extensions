import datetime
import typing as T

from nicegui import ui
from nicegui.element import Element

from nicegui_ext.helpers import is_date_valid

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
