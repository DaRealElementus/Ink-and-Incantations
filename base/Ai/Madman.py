"""Madman Action Handler Class"""
import random, pygame, os, platform, difflib, Units
from Ai.names import names

def target(controlled: list, targets: list, gens: list, player_hp: int, madman_hp: int, player_base: list, madman_base: list) -> None:
    """
    Updates every enemy troop with a target based on the game state
    """
    for unit in controlled:
        # Randomly decide whether to move or stay
        if random.choice([True, False]):
            # Randomly choose a target from generators, enemy units, or player's base
            choices = []
            if gens:
                choices.extend(gens)
            if targets:
                choices.extend(targets)

            # Add player's base as a potential target
            choices.append({'x': player_base[0], 'y': player_base[1]})

            Targeted = random.choice(choices)
            unit.target = [Targeted['x'], Targeted['y']]
        else:
            # Randomly move to a random position near the madman base
            unit.target = [
                random.randint(madman_base[0] - 100, madman_base[0] + 100),
                random.randint(madman_base[1] - 100, madman_base[1] + 100)
            ]

def summon(mana: int, p_e_controlled: int, controlled: list) -> int:
    """
    Returns the id of the troop the AI wants to summon
    """
    # Define the units and their mana costs
    units = [
        {'name': 'Footman', 'cost': 1, 'id': 0},
        {'name': 'Horse', 'cost': 3, 'id': 1},
        {'name': 'Soldier', 'cost': 3, 'id': 2},
        {'name': 'Summoner', 'cost': 6, 'id': 3},
        {'name': 'Runner', 'cost': 8, 'id': 4},
        {'name': 'Tank', 'cost': 8, 'id': 5}
    ]

    # Randomly choose a unit to summon without any constraints
    affordable_units = [unit for unit in units if unit['cost'] <= mana]

    if not affordable_units:
        #print("Insufficient mana to summon any unit")
        return None

    chosen_unit = random.choice(affordable_units)
    return chosen_unit['id']

def scare() -> str:
    """
    Madman's moment of self-awareness. Returns the player's name if run.
    """
    try:
        s = os.getlogin()
        return s.capitalize()
    except Exception:
        return "Player"
