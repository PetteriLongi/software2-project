import random
from dataclasses import dataclass
from typing import Optional
from flask import Blueprint, jsonify, request
from config_redone import (
    RATE_PER_KM, REWARD_MARKKA, START_MARKKA,
    NUM_AIRPORT_CHOICES, NUM_CONDUITS,
    DOOM_PER_KM, MIN_DOOM_TRAVEL_TICK,
    RunState, AirportChoice
)
from FetchDB_RD import fetch_hel, fetch_random_airports_excl_hel, coords, distance_km
from Doomclock.doomclock import doom_clock

services_redone = Blueprint('services_redone', __name__)

# ---- helpers ----
def can_revisit(a: AirportChoice) -> bool:
    return a.conduit and not a.conduit_closed

def is_locked(a: AirportChoice) -> bool:
    return a.visited and not can_revisit(a)

def travel_cost(state: RunState, a: AirportChoice) -> Optional[int]:
    km = distance_km(coords(state.current_lat, state.current_lon), coords(a.lat, a.lon))
    if km is None: return None
    return max(int(round(RATE_PER_KM * km)), 1)

# ---- core API ----
def start_new_run(seed: Optional[int] = None) -> RunState:
    hel = fetch_hel()
    airports = fetch_random_airports_excl_hel(NUM_AIRPORT_CHOICES)
    rng = random.Random(seed) if seed is not None else random
    chosen = rng.sample(range(len(airports)), NUM_CONDUITS)
    for i in chosen:
        airports[i].conduit = True
    return RunState(
        current_id=hel.id, current_name=hel.name,
        current_iata=hel.iata, current_icao=hel.icao,
        current_country=hel.country, current_lat=hel.lat,
        current_lon=hel.lon, airports=airports,
        markka=START_MARKKA, inventory=[]
    )

def doom_ticks_for_distance(km: float) -> int:
    ticks = int(round(DOOM_PER_KM * km))
    return max(ticks, MIN_DOOM_TRAVEL_TICK)

# ---------- AJAX routes ----------
@services_redone.route("/start_new_run")
def Starting():
    seed = request.args.get("seed")
    seed = int(seed) if seed is not None else None
    new_run = start_new_run(seed)
    return jsonify({
        **new_run.__dict__,
        "airports": [a.__dict__ for a in new_run.airports]
    })

@services_redone.route("/doom_ticks")
def Doom_ticking():
    km = float(request.args.get("km", 0))
    return jsonify({'ticks': doom_ticks_for_distance(km)})
