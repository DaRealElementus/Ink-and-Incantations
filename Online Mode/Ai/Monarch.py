"""Monarch Action Handler Class"""

import random
import pygame


def target(controlled: list, targets: list, gens: list, player_hp: int, monarch_hp: int, player_base: list, monarch_base: list) -> None:
    """
    Updates every enemy troop with a target based on the game state
    Includes proximity-based defensive reactions
    """
    DANGER_RADIUS = 150  # Distance to trigger defensive response
    p_e_controlled = 0
    controlled_gens = []
    under_threat = False

    # Check for nearby threats
    for unit in controlled:
        if unit.__class__.__name__ != "Generator":
            for enemy in targets:
                distance = ((enemy.x - unit.x)**2 + (enemy.y - unit.y)**2)**0.5
                if distance <= DANGER_RADIUS:
                    under_threat = True
                    break
            if under_threat:
                break

    for e in controlled:
        if e.__class__.__name__ == "Generator":
            p_e_controlled += 1
            controlled_gens.append(e)

    # Adjust defense based on threat level
    if under_threat:
        # 60% defense when threatened
        num_defenders = max(2, int(len(controlled) * 0.6))
        num_responders = len(controlled) - \
            num_defenders    # 40% counter-attack
    else:
        num_defenders = max(1, int(len(controlled) * 0.75)
                            )  # Normal 75% defense
        num_responders = len(controlled) - num_defenders     # 25% patrol

    defenders_assigned = 0
    responders_assigned = 0

    for unit in controlled:
        if unit.__class__.__name__ == "Minion":
            unit.target = unit.master.target
            continue

        if unit.__class__.__name__ == "Generator":
            continue

        # Priority 1: React to nearby threats
        if under_threat:
            nearby_enemies = []
            for enemy in targets:
                distance = ((enemy.x - unit.x)**2 + (enemy.y - unit.y)**2)**0.5
                if distance <= DANGER_RADIUS:
                    nearby_enemies.append((enemy, distance))

            if nearby_enemies and responders_assigned < num_responders:
                # Target closest threatening unit
                closest_enemy = min(nearby_enemies, key=lambda x: x[1])[0]
                unit.target = closest_enemy
                responders_assigned += 1
                continue

        # Priority 2: Capture/defend generators
        if p_e_controlled < len(gens):
            if unit.__class__.__name__ != "Generator":
                uncaptured = [g for g in gens if g not in controlled_gens]
                if uncaptured:
                    closest_gen = min(uncaptured,
                                      key=lambda g: ((g.x - unit.x)**2 + (g.y - unit.y)**2)**0.5)
                    unit.target = [closest_gen.x, closest_gen.y]
                continue

        # Priority 3: Maintain defensive positions
        if defenders_assigned < num_defenders:
            if controlled_gens and random.random() < 0.7:  # 70% chance to defend generators
                Targeted = random.choice(controlled_gens)
                unit.target = [Targeted.x, Targeted.y]
            else:  # 30% chance to defend base
                unit.target = [
                    random.randint(monarch_base[0] - 50, monarch_base[0] + 50),
                    random.randint(monarch_base[1] - 50, monarch_base[1] + 50)
                ]
            defenders_assigned += 1
            continue

        # Default: Return to defensive position
        unit.target = monarch_base


def summon(mana: int, p_e_controlled: int, controlled: list) -> int:
    """
    Returns the id of the troop the AI wants to summon
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
    affordable_units = [unit for unit in units if unit['cost']
                        <= mana and unit_counts[unit['id']] < 5]

    if not affordable_units:
        # print("Insufficient mana to summon any unit")
        return None

    # Choose a unit to summon based on the adjusted weights
    total_weight = sum(unit['weight'] for unit in affordable_units)
    choice = random.uniform(0, total_weight)
    cumulative_weight = 0
    for unit in affordable_units:
        cumulative_weight += unit['weight']
        if choice <= cumulative_weight:
            return unit['id']

    # print("Choice failed")
    return None
