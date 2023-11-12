from nicegui import ui

from nicegui_ext import ui as ext_ui


def heading(
    value: str,
    level: int = 1,
    center: bool = False,
    *,
    background: str | None = None,
    margin: int = 0,
    border_radius: int = 0,
    unit: str = "px",
    tooltip: str | None = None,
):
    """
    Create a markdown title.

    Args:
        value (str): The title text.
        size (int, optional): The title size. Defaults to 1. Must be between 1 and 6. See https://www.markdownguide.org/basic-syntax/#headings.
        center (bool, optional): Whether to center the title. Defaults to False.
        background (str, optional): The background color. Defaults to None.
        margin (int, optional): The margin. Defaults to 0.
        border_radius (int, optional): The border radius. Defaults to 0.
        unit (str, optional): The unit for margin and border_radius. Defaults to "px".
        tooltip (str, optional): The tooltip text. Defaults to None.


    """
    if level not in range(1, 7):
        raise ValueError("Size must be between 1 and 6")

    level = "#" * level  # type: ignore
    mdtitle = ui.markdown(f"{level} {value}")

    if center:
        mdtitle = mdtitle.classes("text-center")
    if background:
        mdtitle = mdtitle.style(f"background-color: {background};")

    mdtitle = mdtitle.style(f"margin: {margin}{unit};").style(
        f"border-radius: {border_radius}{unit};"
    )
    if tooltip:
        ext_ui.tooltip(tooltip)

    return mdtitle
