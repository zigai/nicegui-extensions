try:
    import tkinter as tk
    from tkinter import filedialog
except ImportError:
    raise ImportError("'nicegui_ext.native_file_picker' module requires tkinter to be installed. ")
import os
import typing as T

from nicegui import ui
from nicegui.element import Element
from stdl import fs

from nicegui_ext import icons

_TKINTER_ROOT = tk.Tk()  # For file dialogs
_TKINTER_ROOT.withdraw()

# Filetypes for tkinter.filedialog
ALL_FILES = ("All files", "*.*")
TEXT_FILES = ("Text files", "*.txt")
PYTHON_FILES = ("Python files", "*.py")


class NativeFileDialog:
    """
    A wrapper around tkinter.filedialog
    """

    def __init__(
        self,
        select: T.Literal["file", "dir"] = "file",
        mode: T.Literal["open", "save"] = "open",
        multiple: bool = False,
        title_open: str | None = None,
        title_save: str | None = None,
        filetypes: list[tuple[str, str]] = [("All files", "*.*")],
        initial_directory: str | None = None,
        open_at_last_dir: bool = True,
    ):
        self.select = select
        if self.select not in ["file", "dir"]:
            raise ValueError("Invalid selection type. Choose 'file' or 'dir'.")
        self.mode = mode

        self.multiple = multiple
        self.title_open = (
            title_open or f"Select file{'s' if multiple else ''}"
            if select == "file"
            else "Select a directory"
        )
        self.title_save = title_save or "Save file"
        self.filetypes = filetypes
        self.open_at_last_dir = open_at_last_dir

        self.last_dir = ""
        self.chosen = None
        self.initial_dir = initial_directory or os.getcwd()

    def _get_dir(self) -> str:
        if not self.open_at_last_dir:
            return self.initial_dir
        return self.last_dir or self.initial_dir

    def open(self):
        _TKINTER_ROOT.lift()  # Bring the root window to the front
        _TKINTER_ROOT.attributes("-topmost", True)  # Make the root window always appear on top

        fn = self._save_dialog_hidden if self.mode == "save" else self._open_dialog_hidden
        filepath = fn()

        if filepath:
            self.last_dir = os.path.dirname(
                filepath[0] if self.multiple and self.mode == "open" else filepath
            )
            self.chosen = filepath
        _TKINTER_ROOT.update()  # Make the dialog close completely

        _TKINTER_ROOT.attributes("-topmost", False)  # Reset the topmost attribute
        return filepath

    def _save_dialog_hidden(self):
        options = {
            "initialdir": self._get_dir(),
            "title": self.title_save,
            "filetypes": self.filetypes,
        }
        filename = filedialog.asksaveasfilename(**options)
        return filename

    def _open_dialog_hidden(self):
        options = {
            "initialdir": self._get_dir(),
            "title": self.title_open,
        }
        if self.select == "file":
            options["filetypes"] = self.filetypes  # type: ignore
            if self.multiple:
                options["multiple"] = True  # type: ignore
            filename = filedialog.askopenfilename(**options)  # type: ignore
        elif self.select == "dir":
            filename = filedialog.askdirectory(**options)  # type: ignore
        else:
            raise ValueError("Invalid selection type. Choose 'file' or 'dir'.")
        return filename

    @property
    def chosen_contents(self):
        if self.chosen is None:
            return None
        if self.select == "file":
            return fs.File(self.chosen).read()
        elif self.select == "dir":
            raise NotImplementedError("Not implemented for directories")


class NativeFilePickerElement(Element):
    def __init__(
        self,
        select: T.Literal["file", "dir"] = "file",
        title: str | None = None,
        filetypes=[ALL_FILES],
        initial_directory: str | None = None,
        open_at_last_dir: bool = True,
        add_file_exists_indicator: bool = True,
        width_class="w-80",
    ) -> None:
        super().__init__()
        self.file_dialog = NativeFileDialog(
            select=select,
            multiple=False,
            title_open=title,
            filetypes=filetypes,
            initial_directory=initial_directory,
            open_at_last_dir=open_at_last_dir,
        )

        self._add_file_exists_indicator = add_file_exists_indicator
        self.auto_complete = []
        self.filepath: str | None = None
        with ui.row().classes("items-center") as self.container:
            self.path_input = (
                ui.input(
                    placeholder="No file selected",
                    autocomplete=self.auto_complete,
                    on_change=self.on_input_change,
                )
                .classes(width_class)
                .classes("font-mono")
            )
            if self._add_file_exists_indicator:
                self.label_file_exists = ui.label("  ")
            self.button_open_file_dialog = ui.button(
                icon=icons.FOLDER_OPEN, on_click=self.open_dialog
            )

    def open_dialog(self):
        filename = self.file_dialog.open()
        if filename:
            self.filepath = filename
            self.path_input.value = filename
            self.auto_complete.append(filename)
            self.path_input.set_autocomplete(self.auto_complete)
        return filename

    def on_input_change(self):
        value = self.path_input.value
        if not value:
            if self._add_file_exists_indicator:
                self.label_file_exists.text = "  "
            return
        if fs.exists(value):
            if self._add_file_exists_indicator:
                self.label_file_exists.text = "🟢"
            self.auto_complete.append(value)
            self.path_input.set_autocomplete(self.auto_complete)
        else:
            if self._add_file_exists_indicator:
                self.label_file_exists.text = "🔴"

    @property
    def value(self):
        return self.path_input.value


__all__ = ["NativeFilePickerElement", "NativeFileDialog"]
