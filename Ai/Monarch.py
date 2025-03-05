"""Monarch Action Handler Class"""

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

    num_defenders = max(1, int(len(controlled) * 0.75))  # Assign 75% of the units to defense, at least one unit
    num_patrollers = len(controlled) - num_defenders  # Remaining 25% for patrol or core defense

    defenders_assigned = 0
    patrollers_assigned = 0

    for unit in controlled:
        # Prioritize capturing Generator points if not controlled
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

        # Patrol or defend core
        if patrollers_assigned < num_patrollers:
            if unit.__class__.__name__ != "Generator":
                # Randomly choose to patrol or defend core
                if random.choice([True, False]):
                    # Patrol around the base
                    unit.target = [random.randint(900, 1030), random.randint(150, 220)]
                else:
                    # Defend core
                    unit.target = [966, 185]
                patrollers_assigned += 1
            continue

        # Default behavior: defend own base
        unit.target = [966, 185]

def summon(mana:int, p_e_controlled:int, controlled:list) -> None:
    """
    Returns the id of the troop the Ai wants to summon
    """
    # Define the units and their mana costs
    units = [
        {'name': 'Footman', 'cost': 1, 'id': 0, 'weight': 1},
        {'name': 'Horse', 'cost': 3, 'id': 1, 'weight': 1},
        {'name': 'Soldier', 'cost': 3, 'id': 2, 'weight': 1},
        {'name': 'Tank', 'cost': 8, 'id': 5, 'weight': 1}
    ]

    # Count the number of each unit type currently controlled
    unit_counts = {unit['id']: 0 for unit in units}
    for unit in controlled:
        for u in units:
            if unit.__class__.__name__ == u['name']:
                unit_counts[u['id']] += 1

    # Adjust weights based on the number of controlled generators
    if p_e_controlled < 2:
        # Prioritize tankier units for defense
        for unit in units:
            if unit['id'] in [2, 5]:  # Soldier, Tank
                unit['weight'] += 2
    else:
        # Maintain balance between different unit types
        for unit in units:
            unit['weight'] += 1

    # Filter units that can be summoned with the available mana and are within the limit
    affordable_units = [unit for unit in units if unit['cost'] <= mana and unit_counts[unit['id']] < 10]

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