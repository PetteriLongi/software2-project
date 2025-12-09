"""
database.py - Database integration for airport travel system

Provides MySQL connection utilities and airport data fetching.
Migrated from Game_project_software1-master/Database/
"""
import mysql.connector
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from geopy.distance import geodesic
from config import Config


@dataclass
class AirportChoice:
    """Represents an airport with its metadata and game state."""
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
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'iata': self.iata,
            'icao': self.icao,
            'country': self.country,
            'lat': self.lat,
            'lon': self.lon,
            'conduit': self.conduit,
            'visited': self.visited,
            'conduit_closed': self.conduit_closed,
            'entered_terminal': self.entered_terminal
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create AirportChoice from dictionary."""
        return cls(**data)


@dataclass
class RunState:
    """Represents the current game state for travel system."""
    # Current position (starts at HEL)
    current_id: int
    current_name: str
    current_iata: str
    current_icao: str
    current_country: str
    current_lat: Optional[float]
    current_lon: Optional[float]

    # Travel options
    airports: List[AirportChoice]

    # Stats
    markka: int

    # Inventory
    inventory: List[str] = field(default_factory=list)

    # Progression
    conduits_found: int = 0
    conduits_closed: int = 0

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'current_id': self.current_id,
            'current_name': self.current_name,
            'current_iata': self.current_iata,
            'current_icao': self.current_icao,
            'current_country': self.current_country,
            'current_lat': self.current_lat,
            'current_lon': self.current_lon,
            'airports': [a.to_dict() for a in self.airports],
            'markka': self.markka,
            'inventory': self.inventory,
            'conduits_found': self.conduits_found,
            'conduits_closed': self.conduits_closed
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create RunState from dictionary."""
        airports = [AirportChoice.from_dict(a) for a in data.get('airports', [])]
        return cls(
            current_id=data['current_id'],
            current_name=data['current_name'],
            current_iata=data['current_iata'],
            current_icao=data['current_icao'],
            current_country=data['current_country'],
            current_lat=data.get('current_lat'),
            current_lon=data.get('current_lon'),
            airports=airports,
            markka=data.get('markka', Config.START_MARKKA),
            inventory=data.get('inventory', []),
            conduits_found=data.get('conduits_found', 0),
            conduits_closed=data.get('conduits_closed', 0)
        )


# Database connection utilities
def get_connection():
    """
    Create and return a MySQL database connection.
    
    Returns:
        mysql.connector.connection: Database connection
    """
    return mysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        port=Config.DB_PORT
    )


def fetch_hel() -> AirportChoice:
    """
    Return Helsinki Airport (HEL) as an AirportChoice.
    
    Returns:
        AirportChoice: Helsinki Airport data
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, name, iata_code, ident AS icao_code, iso_country, latitude_deg, longitude_deg
        FROM airport
        WHERE iata_code = 'HEL'
        LIMIT 1;
    """)
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row:
        return AirportChoice(
            id=row[0], name=row[1], iata=row[2], icao=row[3],
            country=row[4], lat=row[5], lon=row[6]
        )
    else:
        # Fallback so the game won't crash if HEL isn't found
        return AirportChoice(
            id=-1, name="Helsinki (HEL)", iata="HEL", icao="EFHK",
            country="FI", lat=60.3172, lon=24.9633
        )


def fetch_random_airports_excl_hel(n: int) -> List[AirportChoice]:
    """
    Return n random airports (excluding HEL) as AirportChoice objects.
    
    Args:
        n: Number of airports to fetch
    
    Returns:
        List[AirportChoice]: List of random airports
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"""
        SELECT id, name, iata_code, ident AS icao_code, iso_country, latitude_deg, longitude_deg
        FROM airport
        WHERE iata_code <> 'HEL'
          AND iata_code IS NOT NULL
          AND iata_code != ''
          AND latitude_deg IS NOT NULL
          AND longitude_deg IS NOT NULL
        ORDER BY RAND()
        LIMIT {int(n)};
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        AirportChoice(
            id=row[0], name=row[1], iata=row[2], icao=row[3],
            country=row[4], lat=row[5], lon=row[6]
        )
        for row in rows
    ]


# Geographic calculation utilities
Coord = Tuple[float, float]


def coords(lat: Optional[float], lon: Optional[float]) -> Optional[Coord]:
    """
    Convert lat/lon to coordinate tuple.
    
    Args:
        lat: Latitude
        lon: Longitude
    
    Returns:
        Optional[Coord]: Tuple of (lat, lon) or None if either is None
    """
    if lat is None or lon is None:
        return None
    return (lat, lon)


def distance_km(a: Optional[Coord], b: Optional[Coord]) -> Optional[float]:
    """
    Calculate distance between two coordinates in kilometers.
    
    Args:
        a: First coordinate tuple (lat, lon)
        b: Second coordinate tuple (lat, lon)
    
    Returns:
        Optional[float]: Distance in kilometers, or None if either coord is None
    """
    if a is None or b is None:
        return None
    return geodesic(a, b).km
