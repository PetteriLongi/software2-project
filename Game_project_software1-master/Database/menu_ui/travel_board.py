# conduit_game/ui/travel_board.py
from Database.config import RunState, AirportChoice
from Database.services import travel_cost, can_revisit
from Database.FetchDB import coords, distance_km
from game.ui import colorize, ui_print
from Database.config import (
    COLOR_VISITED, COLOR_CONDUIT_CLOSED
)

# column widths
W_IDX=3; W_NAME=36; W_IATA=6; W_ICAO=6; W_COUNTRY=8; W_DIST=6; W_COST=7

def fmt_cell(text: str, width: int) -> str:
    if text is None:
        text = ""
    if len(text) > width:
        return text[:width]
    return f"{text:<{width}}"

def styled_name(a: AirportChoice) -> str:
    # choose color & strike
    base = fmt_cell(a.name or "", W_NAME)

    if a.conduit and a.conduit_closed:
        return colorize(base, COLOR_CONDUIT_CLOSED, strike=True)

    # visited but NOT revisitable => green strike
    if a.visited and not can_revisit(a):
        return colorize(base, COLOR_VISITED, strike=True)

    """"# revisitable because conduit is open (hint in yellow)
    if a.conduit and not a.conduit_closed:
        return colorize(base, COLOR_OPEN_CONDUIT, strike=False)"""

    return base

def show_travel_options(state: RunState):
    # header
    line = "+" + "-"* (W_IDX+1) + "+" + "-"*(W_NAME+2) + "+" + "-"*(W_IATA+2) + "+" + "-"*(W_ICAO+2) + "+" + "-"*(W_COUNTRY+2) + "+" + "-"*(W_DIST+2) + "+" + "-"*(W_COST+2) + "+"
    print("\n" + " " * 6 + "TERMINAL • DEPARTURES")
    print(line)
    print(f"| {'#':<{W_IDX}} | {fmt_cell('Airport',W_NAME)} | {fmt_cell('IATA',W_IATA)} | {fmt_cell('ICAO',W_ICAO)} | {fmt_cell('Country',W_COUNTRY)} | {fmt_cell('Distkm',W_DIST)} | {fmt_cell('Cost (M)',W_COST)} |")
    print(line)

    cur = coords(state.current_lat, state.current_lon)

    for i, a in enumerate(state.airports, start=1):
        km = distance_km(cur, coords(a.lat, a.lon))
        cost = travel_cost(state, a)
        km_txt = f"{int(km):d}" if km is not None else "-"
        cost_txt = f"{cost:d}" if cost is not None else "-"

        # no strike if can revisit due to open conduit
        name_cell = styled_name(a)

        row = (
            f"| {i:<{W_IDX}} | {name_cell} "
            f"| {fmt_cell(a.iata or '-', W_IATA)} "
            f"| {fmt_cell(a.icao or '-', W_ICAO)} "
            f"| {fmt_cell(a.country or '-', W_COUNTRY)} "
            f"| {fmt_cell(km_txt, W_DIST)} "
            f"| {fmt_cell(cost_txt, W_COST)} |"
        )
        print(row)
    print(line)
    ui_print("(Enter 1–10 to travel. You cannot travel to VISITED entries, except airports with an open conduit.)", "bold cyan")
