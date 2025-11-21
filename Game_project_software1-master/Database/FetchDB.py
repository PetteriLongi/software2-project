from typing import List
from Database.config import get_connection
from Database.config import AirportChoice
from typing import Optional, Tuple
from geopy.distance import geodesic


def fetch_hel() -> AirportChoice:
    """
    Return Helsinki Airport (HEL) as an AirportChoice.
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
        # Simple fallback so the game won't crash if HEL isn't found
        return AirportChoice(id=-1, name="Helsinki (HEL)", iata="HEL", icao="EFHK",
                             country="FI", lat=None, lon=None)


def fetch_random_airports_excl_hel(n: int) -> List[AirportChoice]:
    """
    Return n random airports (excluding HEL) as AirportChoice objects.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"""
        SELECT id, name, iata_code, ident AS icao_code, iso_country, latitude_deg, longitude_deg
        FROM airport
        WHERE iata_code <> 'HEL'
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

Coord = Tuple[float, float]

def coords(lat: Optional[float], lon: Optional[float]) -> Optional[Coord]:
    if lat is None or lon is None:
        return None
    return (lat, lon)

def distance_km(a: Optional[Coord], b: Optional[Coord]) -> Optional[float]:
    if a is None or b is None:
        return None
    return geodesic(a, b).km


#def create_bloody_note(airports: List[AirportChoice]):
#    # Define maximum length for the name and the spacing
#    max_name_length = max(len(airport.name) for airport in airports)
#    line_width = 43  # Width of the line in the ASCII art

    # This is the function to format each airport name within a fixed-width space
#    def format_airport_line(airport_name: str, line_position: str) -> str:
        # Center the airport name in a field with a specific width
#        name_field = f"{airport_name}".center(max_name_length + 3 )
#        return f"{line_position}{name_field}{' ' * (line_width - len(name_field) - len(line_position))}"


#    bloody_note = f"""
#[red]      @@#@@                                                                               @*@@      
#[red]      %%%@@                                                                               @%%@      
#[red]       %@@                                                                                @@%           
#[red]        @@                                                                                @@@       
#[red]      @@@%@                                                                              @%@@@      
#[red]   %@@@%%@@@@@                                                                        @@@@@@%%%%%   
#[red] @@@@@%%#@@@@@@                                                                      @@@@@%@@#%@@%@ 
#[red]@@@@@@%%%%%%###%@                                                                  %###%%@%%@%%@@@@@
#[red]  @@@%%%%@@@@@@                                                                      @@@@%%%@%@@@@@ 
#[red]  @@@%@@%#%%@@%%%%%%###%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@@@@@@@%%%@%%%@@@  
#[red]  @@@@@@%#%%@@%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@@%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@@@@%%#@@@%@@@  
#[red]   @@@@@%#%@@@%%%%%%%%%%%%%%%{format_airport_line(airports[0].name, "")} %%%%%%%%%@@@@@@%%#%@@%@@   
#[red]   @@@@%%%%@@@%%%%%%%%%%%%%%%%%%%%%%#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@@@@@@@%%%@@@@@   
#[red]   @@@@%%%%@@@%%%%%%%%%%%%%%%{format_airport_line(airports[1].name, "")} %%%%%%%%%@@@@@%%%%@@@@@   
#[red]   @@%@%%%%@@@%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@@@@@@@%%%@%@@@@   
#[red]   @%#@%%%%@@@%%%%%%%%%%%%%##{format_airport_line(airports[2].name, "")} %%%%%%@%@@@@@@@%@%%%@@@   
#[red]   @##@%%%%@@@%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@@@@@@%##%@@@   
#[red]   @@%@%%%%@@@%%%%%%%%%%%%%%%{format_airport_line(airports[3].name, "")} %%%%%%%%@@@@@@@@%%%%%@@  
#[red]   @@@@%%%%@@@@%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@@@@@@@@@%%%%%@@@   
#[red]   @@@%%%%%@@@%%%%%%%%%%%%%%%{format_airport_line(airports[4].name, "")} %%%%%%@@@@@@@@@%%%%%@@@  
#[red]   @@@%%%%%@@@@%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@@@@@@@@@@@%%%%%@@@   
#[red]   @@@%%%%%@@@%%%%%%%%%%%%%%%{format_airport_line(airports[5].name, "")} %%%%%@%%%@@@@@@%%%%%@@@   
#[red]   @@@%%%%%@@@%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@%@@@@@@%%%%%@@@   
#[red]   @@@%%%%%@@@%%%%%%%%%%%%%%%{format_airport_line(airports[6].name, "")}%%%%%%%%@%%%%%@@@%%%%@@@   
#[red]   @@@%%%%%@@@%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@@@@@@%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@@@%%%%%@@@   
#[red]   @@@%%%%%@@@%%%%%%%%%%%%%%%{format_airport_line(airports[7].name, "")}%%%%%%%%%%%%%%@@%%%%%@@@   
#[red]   @@@%%%%%@@@%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@%@@%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@@@@%%%%%@@@   
#[red]   @@@%%%%%@@@@%%%%%%%%%%%%%%{format_airport_line(airports[8].name, "")}%%%%%%%%%%%%%@@@@%%#%%%@@   
#[red]   @@%%##%@@@@%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@@@%#%#%@@@   
#[red]   @@%%#%%@@@@%%%%%%%%%%%%%%%{format_airport_line(airports[9].name, "")}%%%%%%%%%%%%%@@@@%%%%%@@   
#[red]   @@@%##%%@@@%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@@@%%###%@@@       
#[red]  @@@%%%%%%@@@@@@@@@@@@@%%%%%@@@@@@@@@@@@%%%%%%%@@@@@%%%%%%%%%%%%%%%%%%%%%%%%%%%@@%%%%@@%%%%%%@@@@  
#[red]  @@@@@%%@@@@@@@                                                                    @@@@@%%%%@@@@@  
#[red]@@@%%@@@@@@@@@@@@                                                                  @@@@@@@@@@@@@@%@@
#[red] @@@@%%#%%%%%%@@                                                                    %%%%%@@%%%@@@@@ 
#[red]   @@@@%%@@%#%                                                                         #%@@@@@@@@   
#[red]      @@@@@                                                                              @@@@@      
#[red]        %                                                                                  %@       
#[red]       @%+                                                                                +%@            
#[red]      @@#*+                                                                               *#@@      
#[red]      @@###                                                                               ###@@
#    """
#    return bloody_note