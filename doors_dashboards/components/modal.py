from dash import dcc
import dash_bootstrap_components as dbc


def create_modal(modal_id, title, content, size="lg", font_size="x-small"):
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle(title)),
            dbc.ModalBody(dcc.Markdown(content, dangerously_allow_html=True)),
            dbc.ModalFooter(
                dbc.Button("Close", id=f"close-{modal_id}", className="ml-auto")
            ),
        ],
        id=f"modal-{modal_id}",
        is_open=False,
        size=size,
        style={
            "font-size": font_size,
            "fontFamily": "Roboto, Helvetica, Arial, sans-serif;",
        },
    )
