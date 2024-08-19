from dash import dcc
import dash_bootstrap_components as dbc
import os


def read_help_content(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


ASSETS_PATH = "../assets"

# Path to the help.md file
HELP_MD_PATH = os.path.join(os.path.dirname(__file__), ASSETS_PATH, "help.md")

# Read the content of the help.md file
help_content = read_help_content(HELP_MD_PATH)


def create_help_modal():
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Help")),
            dbc.ModalBody(
                dcc.Markdown(help_content,dangerously_allow_html=True),
                style={
                    "font-size": "small",
                    "fontFamily": "Roboto, Helvetica, Arial, sans-serif;",
                },
            ),
            dbc.ModalFooter(
                dbc.Button("Close", id="close-help", className="ml-auto")
            ),
        ],
        id="modal-help",
        is_open=False,
        size="lg",
        #style={
        #   "font-size": "x-small",
        #    "fontFamily": "Roboto, Helvetica, Arial, sans-serif;",
        #},
    )
