"""Enchanter Action Handler Class"""


import random, pygame

def target(controlled:list, targets:list, gens:list, player_hp:int, enchanter_hp:int) -> None:
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
        if p_e_controlled <= len(gens):
            if unit.__class__.__name__ != "Generator":
                if gens:
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
        base_x, base_y = 966, 185
        if enchanter_hp < 10:
            if unit.__class__.__name__ != "Generator":
                unit.target = [random.randint(base_x - 50, base_x + 50), random.randint(base_y - 50, base_y + 50)]
            continue

        # Default behavior: attack player or target random enemy units
        player_base_x, player_base_y = 966, 860
        if len(targets) > 0:
            Targeted = random.choice(targets)
            unit.target = [Targeted.x, Targeted.y]
        else:
            # If no targets, attack player's base
            unit.target = [player_base_x, player_base_y]

def summon(mana:int, p_e_controlled:int, controlled:list) -> None:
    """
    Returns the id of the troop the Ai wants to summon
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
        #this is the strategy for this game, capture then generators first and hold them
        for unit in units:
            if unit['id'] in [0, 1, 4]:  # Footman, Horse, Runner
                unit['weight'] += 3
    else:
        # Prioritize tankier units
        #this is for when we have the generators, we now want to be on the offensive
        for unit in units:
            if unit['id'] in [2, 3, 5]:  # Soldier, Summoner, Tank
                unit['weight'] += 3

    # Filter units that can be summoned with the available mana
    affordable_units = [unit for unit in units if unit['cost'] <= mana and unit_counts[unit['id']] < 5]


    #enchanter was silly and didnt save mana
    if not affordable_units:
        print("Insufficient mana to summon any unit")
        return None

    # Choose a unit to summon based on the adjusted weights
    total_weight = sum(unit['weight'] for unit in affordable_units)
    choice = random.uniform(0, total_weight)
    cumulative_weight = 0
    for unit in affordable_units:
        cumulative_weight += unit['weight']
        if choice <= cumulative_weight:
            return unit['id']

    print("Choice failed")
    return None