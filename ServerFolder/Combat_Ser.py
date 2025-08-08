
import random
import time
import math
import os


def BatLogic(Units: object, gamedefaults:dict={
        'Player1_mana': int(5),
        'Player2_mana': int(5),
        'Player1_HP': int(20),
        'Player2_HP': int(20),
        'Won': bool(False),
        'last_update': float(time.time()),
        'time_index': list([]),
        'max_time': int(1200),
        'total_time': float(0),
        'Player1_mana_timer': float(0),
        'Player2_mana_timer': float(0),
        'Player1_Units': list([]),
        'Player2_Units': list([]),
        'Player1_SpawnPos': list([370, 630]), # Basic player spawn point
        'Player2_SpawnPos': list([370, 70]), # enchanter spawn point
        'Pumps': list([]),
        'GameSeed': int(123456789)}) -> bool:

    # A Default game state would look like this
    Scalars = [1, 1]

    # global defaults
    now_time = time.time()

    X_MIN = int((1000 * 0.124))
    X_MAX = int((1000 * 0.865))
    Y_MIN = int((1000 * 0.19))
    Y_MAX = int((1000 * 0.89))


    BattleGround_width = X_MAX - X_MIN
    BattleGround_height = Y_MAX - Y_MIN

    gamedefaults['Player1_SpawnPos'] = (int(X_MIN + (BattleGround_width // 2)),
                   int(Y_MAX - (BattleGround_height * 0.1)))
    gamedefaults['Player2_SpawnPos'] = (int(X_MIN + (BattleGround_width // 2)),
                   int(Y_MIN + (BattleGround_height * 0.1)))
    player1_base = gamedefaults['Player1_SpawnPos']
    Player2_base = gamedefaults['Player2_SpawnPos']
                    # Relative Pos 595, 540
    #set pumps up if the dont exist, they can also exist in player units
    n = len(gamedefaults['Pumps'])
    for p in gamedefaults['Player1_Units']:
        if p.__class__.__name__ == "Generator":
            n += 1
    for p in gamedefaults['Player2_Units']:
        if p.__class__.__name__ == "Generator":
            n += 1 
    

    if n == 0:
        gamedefaults['Pumps'] = [
            Units.Generator((X_MIN + (BattleGround_width * 0.20),
                            Y_MIN + (BattleGround_height * 0.20)), Scalars),
            Units.Generator((X_MIN + (BattleGround_width * 0.70),
                            Y_MIN + (BattleGround_height * 0.20)), Scalars),
            Units.Generator((X_MIN + (BattleGround_width * 0.20),
                            Y_MIN + (BattleGround_height * 0.70)), Scalars),
            Units.Generator((X_MIN + (BattleGround_width * 0.70),
                            Y_MIN + (BattleGround_height * 0.70)), Scalars)
        ]
    Pumps = gamedefaults['Pumps']

    # Adjust selection bounds dynamically
    boundaries = {
        'left': X_MIN,
        'right': X_MAX,
        'top': Y_MIN,
        'bottom': Y_MAX
    }
    
    Player1_Units = gamedefaults['Player1_Units']
    Player2_Units = gamedefaults['Player2_Units']


        # create the correct unit for the player
    #     troop_data={
    # 'hp': 1,
    # 'attack': 1,
    # 'cost': 1, 
    # 'speed': 1, 
    # 'x': 100, 
    # 'y': 100,
    # 'true_x': 100, 
    # 'true_y': 100, 
    # 'target': [0, 0], 
    # 'lifetime': 0, 
    # 'Goal': 'None', 
    # 'achived': True, 
    # 'spawn_timer': 0, 
    # 'move_timer': 0, 
    # 'Name': 'Footman', 
    # 'Scale': [1, 1]},
    # old_data={'hp': 1,
    # 'attack': 1,
    # 'cost': 1, 
    # 'speed': 1, 
    # 'x': 100, 
    # 'y': 100,
    # 'true_x': 100, 
    # 'true_y': 100, 
    # 'target': [0, 0], 
    # 'lifetime': 0, 
    # 'Goal': 'None', 
    # 'achived': True, 
    # 'spawn_timer': 0, 
    # 'move_timer': 0, 
    # 'Name': 'Footman', 
    # 'Scale': [1, 1]}
        #Troop data example
        



    # Calculate delta time
    current_time = time.time()
    dt = current_time - gamedefaults['last_update']

    # putting the pumps on the field
    for p in Pumps:
        if p.hp <= 0:
            for f in Player1_Units:
                if p.x - 10 <= f.x <= p.x + p.Asset + 10 and p.y - 10 <= f.y <= p.y + p.Asset + 10:
                    # #print("Player1_Units Pump gained")
                    score += 100
                    try:
                        Pumps.remove(p)
                    except Exception as e:
                        print(e)
                    Player1_Units.append(Units.Generator([p.x, p.y], Scalars))
                    break
            for e in Player2_Units:
                if p.x - 10 <= e.x <= p.x + p.Asset + 10 and p.y - 10 <= e.y <= p.y + p.Asset + 10:
                    # #print("Player2_Units Pump gained")
                    Player2_Units.append(Units.Generator([p.x, p.y], Scalars))
                    try:
                        Pumps.remove(p)
                    except Exception as e:
                        print(e)
                    break
            # Remove the pump from the field if its HP is 0
        else:
            for f in Player1_Units:
                if p.x - 10 <= f.x <= p.x + p.Asset + 10 and p.y - 10 <= f.y <= p.y + p.Asset + 10:
                    p.hp -= 1
            for e in Player2_Units:
                if p.x - 10 <= e.x <= p.x + p.Asset + 10 and p.y - 10 <= e.y <= p.y + p.Asset + 10:
                    p.hp -= 1
    # putting the selected units on the field
    p_controled = 0
    for f in Player1_Units:
        # checking for collision
        for e in Player2_Units:
            if abs(f.x - e.x) < 12 and abs(f.y - e.y) < 12 and e.hp > 0 and f.hp > 0:
                # combat
                f.hp -= e.attack
                e.hp -= f.attack
        # checking for enchanter damage
        if Player2_base[0] < f.x <= Player2_base[0] and Player2_base[1] < f.y <= Player2_base[1]:
            gamedefaults['Player2_HP'] -= f.attack
            f.hp = 0
        # unit death
        if f.hp <= 0:
            score -= 10
            if f.__class__.__name__ == "Generator":
                # #print("Player1_Units Pump destroyed")
                Player2_Units.append(Units.Generator([f.x, f.y], Scalars))
            try:
                Player1_Units.remove(f)
            except Exception as e:
                print(e)
            continue
        # movement
        else:
            f.move(dt, Player1_Units, boundaries, Scalars)
        # counting the number of controlled pumps
        if f.__class__.__name__ == "Generator":
            p_controled += 1
        if f.__class__.__name__ == "Summoner":
            if not hasattr(f, "spawn_timer"):
                f.spawn_timer = 0  # Initialize spawn timer if not already set
            f.spawn_timer += dt  # Increment spawn timer by delta time
            if f.spawn_timer >= 1:  # Check if 1 second has passed
                Player1_Units.append(Units.Minion([f.x, f.y], Scalars, f))
                Player1_Units[-1].target = f.target
                f.spawn_timer = 0  # Reset the spawn timer
        if f.__class__.__name__ == "Minion":
            f.lifetime += dt
            if f.master:
                f.target = f.master.target
            if f.lifetime >= 5:
                try:
                    Player1_Units.remove(f)
                except Exception as e:
                    print(e)
                continue

    # similar to player controlled units, but for enchanter units
    p_e_controled = 0
    for e in Player2_Units:
        # checking for player Damage
        if player1_base[0] - 5 <= e.x <= player1_base[0] + 5 and player1_base[1] - 5 <= e.y <= player1_base[1] + 5:
            gamedefaults['Player1_HP'] -= e.attack
            e.hp = 0

        if e.hp <= 0:
            score += 10
            if e.__class__.__name__ == "Generator":
                # print("Player2_Units Pump destroyed")
                Player1_Units.append(Units.Generator([e.x, e.y], Scalars))
            try:
                Player2_Units.remove(e)
            except Exception as e:
                print(e)
            continue
        else:
            e.move(dt, Player2_Units, boundaries, Scalars)
        if e.__class__.__name__ == "Generator":
            p_e_controled += 1
        if e.__class__.__name__ == "Summoner":
            if not hasattr(e, "spawn_timer"):
                e.spawn_timer = 0  # Initialize spawn timer if not already set
            e.spawn_timer += dt  # Increment spawn timer by delta time
            if e.spawn_timer >= 1:  # Check if 1 second has passed
                Player2_Units.append(Units.Minion([e.x, e.y], Scalars, e))
                Player2_Units[-1].target = e.target
                e.spawn_timer = 0  # Reset the spawn timer
        if e.__class__.__name__ == "Minion":
            e.lifetime += dt
            if e.lifetime >= 5:
                try:
                    Player2_Units.remove(e)
                except Exception as e:
                    print(e)
                continue

    # Mana Regen, for both player and Enchanter
    P_ratio = {0: 1, 1: 3, 2: 4, 3: 4, 4: 6}

    divisor = P_ratio[p_controled]
    gamedefaults['Player1_mana_timer']+= dt
    if gamedefaults['Player1_mana_timer']>= (5/divisor):
        gamedefaults['Player1_mana']= min(gamedefaults['Player1_mana']+ 1, 9)
        gamedefaults['Player1_mana_timer']= 0
    gamedefaults['Player2_mana_timer'] += dt
    divisor = P_ratio[p_e_controled]
    if gamedefaults['Player2_mana_timer'] >= (5/divisor):
        gamedefaults['Player2_mana'] = min(gamedefaults['Player2_mana'] + 1, 9)
        gamedefaults['Player2_mana_timer'] = 0


    if gamedefaults['Player1_HP'] <= 0:
        Won = "Player2"
    elif gamedefaults['Player2_HP'] <= 0:
        Won = "Player1"
    else:
        Won = None

    gamedefaults['Won'] = Won
    return gamedefaults