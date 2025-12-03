import mysql.connector
from dataclasses import dataclass, field
from typing import List, Optional
from flask import Blueprint, jsonify, request


config = Blueprint('config', __name__)


RATE_PER_KM = 0.5
REWARD_MARKKA = 100
SANITY_LOSS = 5
START_MARKKA = 5_000_000
START_SANITY = 100
START_HP = 100
DOOM_PER_KM = 0.002
MIN_DOOM_TRAVEL_TICK = 1
NUM_AIRPORT_CHOICES = 10
NUM_CONDUITS = 5


DB_USER = "gameuser"
DB_PASSWORD = "yourpassword"
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "flight_game"


USE_ANSI = True
COLOR_VISITED = "\033[92m"
COLOR_CONDUIT_CLOSED = "\033[91m"
COLOR_OPEN_CONDUIT = "\033[93m"
COLOR_RESET = "\033[0m"

# ---------- DB connection ----------
def get_connection():
    return mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
        database=DB_NAME, port=DB_PORT
    )


@dataclass
class AirportChoice:
    id: int
    name: str
    iata: str
    icao: str
    country: str
    lat: Optional[float]
    lon: Optional[float]
    conduit: bool = False
    visited: bool = False
    conduit_closed: bool = False
    entered_terminal: bool = False

    def __str__(self):
        return f"{self.name} ({self.iata})"

@dataclass
class RunState:
    current_id: int
    current_name: str
    current_iata: str
    current_icao: str
    current_country: str
    current_lat: Optional[float]
    current_lon: Optional[float]
    airports: List[AirportChoice]
    markka: int
    inventory: List[str] = None
    conduits_found: int = 0
    conduits_closed: int = 0

    def __post_init__(self):
        if self.inventory is None:
            self.inventory = []

# ---------- Test route ----------
@config.route("/check")
def Check():
    return {"status": "ok"}
