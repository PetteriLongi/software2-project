"""
travel_service.py - Travel system logic

Handles game initialization, travel actions, rest mechanics, and conduit closure.
Migrated from Game_project_software1-master/Database/services.py
"""
import random
from typing import Optional
from config import Config
from game_logic.database import (
    AirportChoice, RunState, fetch_hel, fetch_random_airports_excl_hel,
    coords, distance_km
)


def start_new_run() -> RunState:
    """
    Initialize a new game run.
    
    Creates the initial RunState with:
    - Current location set to Helsinki (HEL)
    - 10 random airport destinations
    - 5 random conduits hidden among the airports
    - Starting money (markka)
    
    Returns:
        RunState: Initial game state
    """
    hel = fetch_hel()
    airports = fetch_random_airports_excl_hel(Config.NUM_AIRPORT_CHOICES)

    # Randomly assign conduits to NUM_CONDUITS airports
    conduit_indices = random.sample(range(len(airports)), Config.NUM_CONDUITS)
    for i in conduit_indices:
        airports[i].conduit = True

    run_state = RunState(
        current_id=hel.id,
        current_name=hel.name,
        current_iata=hel.iata,
        current_icao=hel.icao,
        current_country=hel.country,
        current_lat=hel.lat,
        current_lon=hel.lon,
        airports=airports,
        markka=Config.START_MARKKA,
        inventory=[],
        conduits_found=0,
        conduits_closed=0
    )

    return run_state


def travel_cost(distance_km: Optional[float]) -> int:
    """
    Calculate the markka cost to travel a given distance.
    
    Args:
        distance_km: Distance in kilometers
    
    Returns:
        int: Cost in markka
    """
    if distance_km is None:
        return 0
    return int(distance_km * Config.RATE_PER_KM)


def doom_ticks_for_distance(distance_km: Optional[float]) -> int:
    """
    Calculate how many doom clock ticks occur for traveling this distance.
    
    Args:
        distance_km: Distance in kilometers
    
    Returns:
        int: Number of doom ticks (minimum 1)
    """
    if distance_km is None:
        return Config.MIN_DOOM_TRAVEL_TICK
    
    raw_ticks = distance_km * Config.DOOM_PER_KM
    return max(int(raw_ticks), Config.MIN_DOOM_TRAVEL_TICK)


def travel_to_index(run_state: RunState, airport_index: int) -> dict:
    """
    Travel to a chosen airport by index.
    
    Updates the RunState:
    - Deducts markka for travel cost
    - Marks airport as visited
    - Updates current location
    - Discovers conduits if present
    - Calculates doom ticks for distance traveled
    
    Args:
        run_state: Current game state
        airport_index: Index of chosen airport in run_state.airports list
    
    Returns:
        dict: Travel result containing:
            - success: bool
            - message: str
            - cost: int
            - distance: float
            - doom_ticks: int
            - conduit_found: bool
            - airport: dict (AirportChoice data)
    """
    if airport_index < 0 or airport_index >= len(run_state.airports):
        return {
            'success': False,
            'message': 'Invalid airport index',
            'cost': 0,
            'distance': 0,
            'doom_ticks': 0,
            'conduit_found': False
        }

    chosen = run_state.airports[airport_index]
    
    # Calculate distance and cost
    from_coord = coords(run_state.current_lat, run_state.current_lon)
    to_coord = coords(chosen.lat, chosen.lon)
    dist = distance_km(from_coord, to_coord)
    cost = travel_cost(dist)
    
    # Check if player can afford it
    if run_state.markka < cost:
        return {
            'success': False,
            'message': 'Not enough markka for this flight',
            'cost': cost,
            'distance': dist or 0,
            'doom_ticks': 0,
            'conduit_found': False
        }
    
    # Deduct cost
    run_state.markka -= cost
    
    # Mark as visited
    chosen.visited = True
    
    # Check for conduit discovery
    conduit_found = False
    if chosen.conduit and not chosen.entered_terminal:
        run_state.conduits_found += 1
        chosen.entered_terminal = True
        conduit_found = True
    
    # Update current location
    run_state.current_id = chosen.id
    run_state.current_name = chosen.name
    run_state.current_iata = chosen.iata
    run_state.current_icao = chosen.icao
    run_state.current_country = chosen.country
    run_state.current_lat = chosen.lat
    run_state.current_lon = chosen.lon
    
    # Calculate doom ticks
    doom_ticks = doom_ticks_for_distance(dist)
    
    return {
        'success': True,
        'message': f'Traveled to {chosen.name}',
        'cost': cost,
        'distance': dist or 0,
        'doom_ticks': doom_ticks,
        'conduit_found': conduit_found,
        'airport': chosen.to_dict()
    }


def rest(run_state: RunState, player) -> dict:
    """
    Rest at current location to restore HP and sanity.
    
    Costs 1 doom tick but restores player stats.
    
    Args:
        run_state: Current game state
        player: Player object to restore
    
    Returns:
        dict: Rest result containing:
            - success: bool
            - message: str
            - hp_restored: int
            - sanity_restored: int
            - doom_ticks: int
    """
    hp_before = player.hp
    sanity_before = player.sanity
    
    # Restore to max (capped at player's actual maximum stats)
    player.hp = min(Config.START_HP, player.max_hp)
    player.sanity = min(Config.START_SANITY, player.max_sanity)
    
    hp_restored = player.hp - hp_before
    sanity_restored = player.sanity - sanity_before
    
    return {
        'success': True,
        'message': 'You rest and regain your strength',
        'hp_restored': hp_restored,
        'sanity_restored': sanity_restored,
        'doom_ticks': 1  # Resting costs 1 doom tick
    }


def close_conduit(run_state: RunState, airport_index: int) -> dict:
    """
    Close a conduit at the current airport.
    
    Awards markka for closing the conduit and marks it as closed.
    
    Args:
        run_state: Current game state
        airport_index: Index of airport in run_state.airports list
    
    Returns:
        dict: Closure result containing:
            - success: bool
            - message: str
            - reward: int
    """
    if airport_index < 0 or airport_index >= len(run_state.airports):
        return {
            'success': False,
            'message': 'Invalid airport index',
            'reward': 0
        }
    
    chosen = run_state.airports[airport_index]
    
    # Check if this is the current location
    if chosen.iata != run_state.current_iata:
        return {
            'success': False,
            'message': 'You must be at the airport to close its conduit',
            'reward': 0
        }
    
    # Check if there's a conduit
    if not chosen.conduit:
        return {
            'success': False,
            'message': 'There is no conduit at this location',
            'reward': 0
        }
    
    # Check if already closed
    if chosen.conduit_closed:
        return {
            'success': False,
            'message': 'This conduit has already been closed',
            'reward': 0
        }
    
    # Close the conduit
    chosen.conduit_closed = True
    run_state.conduits_closed += 1
    
    # Award markka
    reward = Config.REWARD_MARKKA
    run_state.markka += reward
    
    return {
        'success': True,
        'message': f'Conduit sealed! Earned {reward} markka.',
        'reward': reward
    }


def get_travel_options(run_state: RunState) -> list:
    """
    Get list of available travel destinations with calculated distances and costs.
    
    Args:
        run_state: Current game state
    
    Returns:
        list: List of dicts containing airport data, distance, and cost
    """
    current_coord = coords(run_state.current_lat, run_state.current_lon)
    
    options = []
    for i, airport in enumerate(run_state.airports):
        to_coord = coords(airport.lat, airport.lon)
        dist = distance_km(current_coord, to_coord)
        cost = travel_cost(dist)
        
        options.append({
            'index': i,
            'airport': airport.to_dict(),
            'distance': round(dist, 2) if dist else 0,
            'cost': cost
        })
    
    return options
