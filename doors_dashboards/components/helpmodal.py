from dash import dcc
import dash_bootstrap_components as dbc
import os

from doors_dashboards.components.modal import create_modal


def read_help_content(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


ASSETS_PATH = "../assets"

# Path to the help.md file
HELP_MD_PATH = os.path.join(os.path.dirname(__file__), ASSETS_PATH, "help.md")

# Read the content of the help.md file
help_content = read_help_content(HELP_MD_PATH)


def create_help_modal():
    help_modal = create_modal(
        modal_id="help",
        title="Help",
        content=help_content,
        font_size="small"
    )
    return help_modal
