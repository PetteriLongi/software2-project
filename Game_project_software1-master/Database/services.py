# conduit_game/services.py
import random
from dataclasses import dataclass
from typing import Optional
from Database.config import (
    RATE_PER_KM, REWARD_MARKKA, #SANITY_LOSS,
    START_MARKKA,
    NUM_AIRPORT_CHOICES, NUM_CONDUITS,
    DOOM_PER_KM, MIN_DOOM_TRAVEL_TICK,
    RunState, AirportChoice
)
from Database.FetchDB import fetch_hel, fetch_random_airports_excl_hel
from Database.FetchDB import coords, distance_km
from Doomclock.doomclock import doom_clock
from game.items import Weapon
from game.combat_actions import reload_gun

# ---- helpers ----
def can_revisit(a: AirportChoice) -> bool:
    # allow revisiting only if conduit exists and not closed
    if a.conduit and not a.conduit_closed:
        return True
    return False

def is_locked(a: AirportChoice) -> bool:
    # visited but NOT an open conduit => locked
    if a.visited and not can_revisit(a):
        return True
    return False

def travel_cost(state: RunState, a: AirportChoice) -> Optional[int]:
    cur = coords(state.current_lat, state.current_lon)
    tgt = coords(a.lat, a.lon)
    km = distance_km(cur, tgt)
    if km is None:
        return None
    # int math + min cost of 1
    cost = int(round(RATE_PER_KM * km))
    if cost < 1:
        cost = 1
    return cost

#def extract_bloody_note(state: RunState) -> str | None:
#    if not state.inventory:
#        return None
#    return state.inventory.pop(0)
    
# ---- core API ----
def start_new_run(seed: int | None = None) -> RunState:
    hel = fetch_hel()
    hel_id = hel.id
    hel_name = hel.name
    hel_iata = hel.iata
    hel_icao = hel.icao
    hel_country = hel.country
    hel_lat = hel.lat
    hel_lon = hel.lon

    rows = fetch_random_airports_excl_hel(NUM_AIRPORT_CHOICES)

    airports: list[AirportChoice] = []
    for r in rows:
        a = AirportChoice(
            id=r.id, name=r.name, iata=r.iata or "", icao=r.icao or "",
            country=r.country or "", lat=r.lat, lon=r.lon,
            conduit=r.conduit, visited=r.visited, conduit_closed=r.conduit_closed
        )
        airports.append(a)

    # pick conduits
    rng = random.Random(seed) if seed is not None else random
    indexes = list(range(len(airports)))
    if len(indexes) >= NUM_CONDUITS:
        chosen = rng.sample(indexes, NUM_CONDUITS)
        for i in chosen:
            airports[i].conduit = True


    #bloody_note = create_bloody_note(airports)

    state = RunState(
        current_id=hel_id, current_name=hel_name,
        current_iata=hel_iata, current_icao=hel_icao,
        current_country=hel_country, current_lat=hel_lat, current_lon=hel_lon,
        airports=airports,
        markka=START_MARKKA, inventory=[]
    )
    return state

def rest(state: RunState, player=None) -> str:

    doom_clock.countdown(1, log=None, reason="Resting costs precious time.")
    if player is not None:
        player.hp = getattr(player, "max_hp", player.hp)
        player.sanity = getattr(player, "max_sanity", player.sanity)

    reload_msgs: list[str] = []
    if player is not None:
        weapons_to_reload: list[Weapon] = []
        if isinstance(getattr(player, "weapon", None), Weapon):
            weapons_to_reload.append(player.weapon)
        for item in getattr(player, "inventory", []) or []:
            if isinstance(item, Weapon):
                weapons_to_reload.append(item)

        seen = set()
        for weapon in weapons_to_reload:
            if not isinstance(weapon, Weapon):
                continue
            if getattr(weapon, "weapon_type", "melee") != "gun":
                continue
            key = id(weapon)
            if key in seen:
                continue
            seen.add(key)
            _, msgs = reload_gun(player, weapon=weapon, consume_turn=False)
            for msg in msgs:
                if msg:
                    reload_msgs.append(msg)

    hp_total = player.max_hp if player is not None and hasattr(player, "max_hp") else None
    sanity_total = player.max_sanity if player is not None and hasattr(player, "max_sanity") else None
    hp_current = player.hp if player is not None and hasattr(player, "hp") else None
    sanity_current = player.sanity if player is not None and hasattr(player, "sanity") else None

    separator = "\033[95m" + "═" * 60 + "\033[0m"
    lines = [
        "",
        separator,
        "\033[96m☽ Respite Taken ☾\033[0m",
        (f"\033[92m✧ HP restored to {hp_current}/{hp_total}.\033[0m" if hp_current is not None and hp_total is not None else "\033[92m✧ HP restored.\033[0m"),
        (f"\033[95m✧ Sanity steadied at {sanity_current}/{sanity_total}.\033[0m" if sanity_current is not None and sanity_total is not None else "\033[95m✧ Sanity steadied.\033[0m"),
        f"\033[91m⏳ Doom Clock -1 → {doom_clock.ticks}\033[0m",
    ]
    if reload_msgs:
        lines.append("\033[96m☍ Arsenal Refitted:\033[0m")
        lines.extend(reload_msgs)
    lines.append(separator)
    return "\n".join(lines)

@dataclass
class TravelResult:
    message: str
    conduit_found: bool = False
    conduit_closed: bool = False
    airport: Optional[AirportChoice] = None
    doom_spent: int = 0


def doom_ticks_for_distance(km: float) -> int:
    ticks = int(round(DOOM_PER_KM * km))
    if ticks < MIN_DOOM_TRAVEL_TICK:
        return MIN_DOOM_TRAVEL_TICK
    return ticks

def travel_to_index(state: RunState, idx: int) -> TravelResult:
    n = len(state.airports)
    if idx < 1 or idx > n:
        return TravelResult(message=f"Choose between 1 and {n}.")

    a = state.airports[idx - 1]

    if is_locked(a):
        return TravelResult(message="You cannot return there (already visited).")

    cost = travel_cost(state, a)

    if cost is None:
        return TravelResult(message="Cannot compute distance/cost for that route.")

    if state.markka < cost:
        return TravelResult(message=f"Not enough Markka (need {cost}, have {state.markka}).")


    origin_coords = coords(state.current_lat, state.current_lon)
    target_coords = coords(a.lat, a.lon)
    km = distance_km(origin_coords, target_coords)

    state.markka -= cost
    state.current_id = a.id
    state.current_name = a.name
    state.current_iata = a.iata
    state.current_icao = a.icao
    state.current_country = a.country
    state.current_lat = a.lat
    state.current_lon = a.lon
    first_visit = not a.visited
    a.visited = True

    separator = "\033[95m" + "═" * 60 + "\033[0m"
    msg_lines: list[str] = ["", separator]
    msg_lines.append(f"\033[95m✈ Arrival: {a.name} ({a.iata or '—'}/{a.icao or '—'}, {a.country})\033[0m")
    msg_lines.append(f"\033[94m✧ Markka Spent: {cost} → Remaining {state.markka}\033[0m")
    conduit_found = False
    conduit_closed = False

    doom_spent = 0

    if km is not None:
        doom_spent = doom_ticks_for_distance(km)
        doom_clock.countdown(doom_spent, log=None, reason=f"Flight to {a.name} (~{int(round(km))} km)")
        msg_lines.append(
            f"\033[91m⏳ Doom Clock -{doom_spent} → {doom_clock.ticks}\033[0m" if doom_spent > 0
            else f"\033[92m⏳ Doom Clock steady at {doom_clock.ticks}\033[0m"
        )
    else:
        msg_lines.append(f"\033[92m⏳ Doom Clock steady at {doom_clock.ticks}\033[0m")

    if a.conduit and not a.conduit_closed:
        msg_lines.append("\033[93mA strange presence hums in the air…\033[0m")
        choice = input("Venture into the terminal? (Y/N): ").strip().lower()
        if choice == "y":
            if not a.entered_terminal:
                state.conduits_found += 1
            conduit_found = True
            a.entered_terminal = True
            a.conduit_closed = True
            state.markka += REWARD_MARKKA
            #state.sanity = max(0, state.sanity - SANITY_LOSS)
            state.conduits_closed += 1
            conduit_closed = True
            msg_lines.append(f"\033[92mConduit CLOSED (+{REWARD_MARKKA} Markka)\033[0m")
            msg_lines.append("\033[95m✶ The terminal sighs as reality knits closed.✶\033[0m")
        else:
            msg_lines.append("\033[90m✧ You withdraw, leaving the resonance untouched.\033[0m")

    msg_lines.append(separator)

    msg = "\n".join(msg_lines)

    return TravelResult(
        message=msg,
        conduit_found=conduit_found,
        conduit_closed=conduit_closed,
        airport=a,
        doom_spent=doom_spent
    )
