"""Enchanter Action Handler Class"""


import random, pygame

def target(controlled: list, targets: list, gens: list, player_hp: int, enchanter_hp: int, player_base: list, enchanter_base: list) -> None:
    """
    Updates every enemy troop with a target based on the game state
    """
    p_e_controlled = 0
    controlled_gens = []
    for e in controlled:
        if e.__class__.__name__ == "Generator":
            p_e_controlled += 1
            controlled_gens.append(e)

    num_defenders = max(1, len(controlled) // 3)  # Assign one-third of the units to defense, at least one unit
    defenders_assigned = 0

    for unit in controlled:
        # Prioritize capturing Generator points if not controlled
        if unit.__class__.__name__ == "Minion":
            unit.target = unit.master.target
            continue
        if p_e_controlled < len(gens):
            if unit.__class__.__name__ != "Generator":
                Targeted = random.choice(gens)
                unit.target = [Targeted.x, Targeted.y]
            continue
        # Defend captured Generator points
        if p_e_controlled > 0 and defenders_assigned < num_defenders:
            if unit.__class__.__name__ != "Generator":
                if controlled_gens:
                    Targeted = random.choice(controlled_gens)
                    unit.target = [Targeted.x, Targeted.y]
                    defenders_assigned += 1
            continue

        # Defend own base if under threat
        if enchanter_hp < 10:
            unit.target = [
                random.randint(enchanter_base[0] - 50, enchanter_base[0] + 50),
                random.randint(enchanter_base[1] - 50, enchanter_base[1] + 50)
            ]
            continue

        # Default behavior: attack player or target random enemy units
        if len(targets) > 0:
            Targeted = random.choice(targets)
            unit.target = [Targeted.x, Targeted.y]
        else:
            # If no targets, attack player's base
            unit.target = player_base

def summon(mana: int, p_e_controlled: int, controlled: list) -> int:
    """
    Returns the id of the troop the AI wants to summon
    """
    # Define the units and their mana costs
    units = [
        {'name': 'Footman', 'cost': 1, 'id': 0, 'weight': 0.5},
        {'name': 'Horse', 'cost': 3, 'id': 1, 'weight': 1},
        {'name': 'Soldier', 'cost': 3, 'id': 2, 'weight': 1},
        {'name': 'Summoner', 'cost': 6, 'id': 3, 'weight': 2},
        {'name': 'Runner', 'cost': 8, 'id': 4, 'weight': 3},
        {'name': 'Tank', 'cost': 8, 'id': 5, 'weight': 3}
    ]
    unit_counts = {unit['id']: 0 for unit in units}
    for unit in controlled:
        for u in units:
            if unit.__class__.__name__ == u['name']:
                unit_counts[u['id']] += 1

    # Adjust weights based on the number of controlled generators
    if p_e_controlled < 2:
        # Prioritize faster units
        for unit in units:
            if unit['id'] in [0, 1, 4]:  # Footman, Horse, Runner
                unit['weight'] += 3
    else:
        # Prioritize tankier units
        for unit in units:
            if unit['id'] in [2, 3, 5]:  # Soldier, Summoner, Tank
                unit['weight'] += 3

    # Filter units that can be summoned with the available mana
    affordable_units = [unit for unit in units if unit['cost'] <= mana and unit_counts[unit['id']] < 5]

    if not affordable_units:
        #print("Insufficient mana to summon any unit")
        return None

    # Choose a unit to summon based on the adjusted weights
    total_weight = sum(unit['weight'] for unit in affordable_units)
    choice = random.uniform(0, total_weight)
    cumulative_weight = 0
    for unit in affordable_units:
        cumulative_weight += unit['weight']
        if choice <= cumulative_weight:
            return unit['id']

    #print("Choice failed")
    return None