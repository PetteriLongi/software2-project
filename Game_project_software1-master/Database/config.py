import mysql.connector
from dataclasses import dataclass, field
from typing import List, Optional

# ---------- Gameplay tunables ONLY FILE ----------
RATE_PER_KM = 0.5              # Markka per km
REWARD_MARKKA = 100            # Reward for closing a conduit
#SANITY_LOSS = 5                # Sanity penalty when closing a conduit
START_MARKKA = 5_000_000       # Starting money
START_SANITY = 100             # Starting sanity
START_HP = 100                 # Starting HP for [3] Rest

# Doom clock travel tuning (ticks per kilometre travelled)
DOOM_PER_KM = 0.002            # Roughly 1 doom tick per 500 km
MIN_DOOM_TRAVEL_TICK = 1       # Minimum doom tick per flight

NUM_AIRPORT_CHOICES = 10       # How many airports to show (excl. HEL)
NUM_CONDUITS = 5               # How many conduits hidden in those airports

# ---------- DB settings ----------
DB_USER = "gameuser"
DB_PASSWORD = "yourpassword"   # change me
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "flight_game"        # your SQL script created this

# ---------- UI / Colors ----------
USE_ANSI = True  # turn off if terminal is weird

# You can swap these if we want different colors:
COLOR_VISITED = "\033[92m"             # green
COLOR_CONDUIT_CLOSED = "\033[91m"      # red
COLOR_OPEN_CONDUIT = "\033[93m"        # yellow
COLOR_RESET = "\033[0m"


# ---------- Get the connection ----------
def get_connection():
    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT
    )
    return connection

# ---------- AirportChoice and RunState classes ----------
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
    # current position (starts at HEL)
    current_id: int
    current_name: str
    current_iata: str
    current_icao: str
    current_country: str
    current_lat: Optional[float]
    current_lon: Optional[float]

    # travel options
    airports: List[AirportChoice]

    # stats
    markka: int

    # inventory
    inventory: List[str] = None

    # progression
    conduits_found: int = 0
    conduits_closed: int = 0

    def __post_init__(self):
        if self.inventory is None:
            self.inventory = []
