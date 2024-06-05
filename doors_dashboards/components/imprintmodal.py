# components/imprint_modal.py

import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import os

from doors_dashboards.components.constant import ASSETS_PATH


# Function to read the imprint.md file content
def read_imprint_content(file_path):
    with open(file_path, 'r', encoding="utf-8") as file:
        return file.read()


# Path to the imprint.md file
IMPRINT_MD_PATH = os.path.join(os.path.dirname(__file__), ASSETS_PATH, 'imprint.md')

# Read the content of the imprint.md file
imprint_content = read_imprint_content(IMPRINT_MD_PATH)


# Define the imprint modal component
def ImprintModal():
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Imprint")),
            dbc.ModalBody(dcc.Markdown(imprint_content)),
            dbc.ModalFooter(
                dbc.Button("Close", id="close-imprint", className="ml-auto")
            ),
        ],
        id="modal-imprint",
        is_open=False,
        size="lg",
        style={"font-size": "x-small",
               "fontFamily": "Roboto, Helvetica, Arial, sans-serif;"}
    )
