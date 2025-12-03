from typing import List, Optional, Tuple
from flask import Blueprint, jsonify, request
from geopy.distance import geodesic
from config_redone import get_connection, AirportChoice

FetchDB = Blueprint('FetchDB', __name__)

def fetch_hel() -> AirportChoice:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, name, iata_code, ident AS icao_code, iso_country, latitude_deg, longitude_deg
        FROM airport WHERE iata_code = 'HEL' LIMIT 1;
    """)
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return AirportChoice(id=row[0], name=row[1], iata=row[2], icao=row[3],
                             country=row[4], lat=row[5], lon=row[6])
    return AirportChoice(id=-1, name="Helsinki (HEL)", iata="HEL", icao="EFHK", country="FI", lat=None, lon=None)

def fetch_random_airports_excl_hel(n: int) -> List[AirportChoice]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"""
        SELECT id, name, iata_code, ident AS icao_code, iso_country, latitude_deg, longitude_deg
        FROM airport WHERE iata_code <> 'HEL' ORDER BY RAND() LIMIT {int(n)};
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [AirportChoice(id=r[0], name=r[1], iata=r[2], icao=r[3],
                          country=r[4], lat=r[5], lon=r[6]) for r in rows]

Coord = Tuple[float, float]
def coords(lat: Optional[float], lon: Optional[float]) -> Optional[Coord]:
    if lat is None or lon is None:
        return None
    return (lat, lon)

def distance_km(a: Optional[Coord], b: Optional[Coord]) -> Optional[float]:
    if a is None or b is None:
        return None
    return geodesic(a, b).km


@FetchDB.route("/fetch_hel")
def Fetch_HEL():
    hel = fetch_hel()
    return jsonify(hel.__dict__)

@FetchDB.route("/fetch_random_airports")
def Fetch_random_airports():
    n = int(request.args.get("n", 10))
    airports = fetch_random_airports_excl_hel(n)
    return jsonify([a.__dict__ for a in airports])
