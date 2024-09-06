from dash import dcc
import dash_bootstrap_components as dbc
import os

from doors_dashboards.components.modal import create_modal

ASSETS_PATH = "../assets"


# Function to read the imprint.md file content
def read_imprint_content(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


# Path to the imprint.md file
IMPRINT_MD_PATH = os.path.join(os.path.dirname(__file__), ASSETS_PATH, "imprint.md")

# Read the content of the imprint.md file
imprint_content = read_imprint_content(IMPRINT_MD_PATH)


# Define the imprint modal component
def create_imprint_modal():
    imprint_modal = create_modal(
        modal_id="imprint",
        title="Imprint",
        content=imprint_content
    )
    return imprint_modal
