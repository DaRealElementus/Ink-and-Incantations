"""Madman Action Handler Class"""
import random, pygame, os, platform, difflib, Units
from Ai.names import names
def target(controlled:list, targets:list, gens:list, player_hp:int, enchanter_hp:int) -> None:
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

            #this section is done weirdly in order to prevent SubScriptable Errors from happening, Before it was using everything like a dic
            #Now everything is being treated like a unit
            Random = Units.Unit()
            Random.x = random.randint(598, 1322)
            Random.y = random.randint(154, 876)


            choices.append(Random)  # Random position on the map
            Targeted = random.choice(choices)
            unit.target = [Targeted.x, Targeted.y]
        else:
            # Randomly move to a random position on the map
            unit.target = [random.randint(0, 1920), random.randint(0, 1080)]

def summon(mana:int, p_e_controlled:int, controlled:list) -> None:
    """
    Returns the id of the troop the Ai wants to summon
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
        print("Insufficient mana to summon any unit")
        return None

    chosen_unit = random.choice(affordable_units)
    return chosen_unit['id']


def scare():
    """Madmans moment of self awareness, Returns the Players name if ran"""
    s = os.getlogin()
    res = []
    for l in s:
        if l.isupper() and not res:
            res.append(l)
        elif l.isupper():
            pass
        else:
            res.append(l)
    res[0].upper()
    if platform.system() == 'Windows':
        res = difflib.get_close_matches(''.join(res), names, 1)
        return res[0].upper()
    else:
        return "YOU LAIR"
