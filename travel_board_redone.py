from flask import Blueprint, jsonify, request
from config_redone import RunState, AirportChoice, COLOR_VISITED, COLOR_CONDUIT_CLOSED, COLOR_OPEN_CONDUIT
from services_redone import can_revisit, travel_cost
from FetchDB_RD import coords, distance_km

travel_board_redone = Blueprint('travel_board_redone', __name__)

W_IDX=3; W_NAME=36; W_IATA=6; W_ICAO=6; W_COUNTRY=8; W_DIST=6; W_COST=7

def fmt_cell(text: str, width: int) -> str:
    if text is None: text = ""
    return text[:width] if len(text) > width else f"{text:<{width}}"

def styled_name(a: AirportChoice) -> str:
    base = fmt_cell(a.name or "", W_NAME)
    if a.conduit and a.conduit_closed:
        return f"{COLOR_CONDUIT_CLOSED}{base}\033[0m"
    if a.visited and not can_revisit(a):
        return f"{COLOR_VISITED}{base}\033[0m"
    return base


@travel_board_redone.route("/fmt_cell")
def Fmt_cells():
    text = request.args.get("text", "")
    width = int(request.args.get("width", W_NAME))
    return jsonify(fmt_cell(text, width))

@travel_board_redone.route("/styled_name")
def Styled_names():
    # expects JSON dict of AirportChoice
    data = request.get_json()
    a = AirportChoice(**data)
    return jsonify(styled_name(a))
