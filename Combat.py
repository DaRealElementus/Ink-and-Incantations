import Units, pygame, random, SaveUpdater, time
from Ai import Enchanter, Madman, Monarch
from pygame.locals import *


def BatStart(Ai:str, display:pygame.Surface):
    player_mana = 5
    Enchanter_mana = 5
    player_HP = 20
    Enchanter_HP=20
    Won = False
    Enemy_ai = Enchanter
    score = 0
    max_time = 1200000
    start_time = time.time()
    gameDisplay = display
    BattleGround = pygame.image.load("Assets\Sprites\pixil-frame-0.png")
    inkblot = pygame.image.load("Assets\Sprites\InkBlot.png")

    clock = pygame.time.Clock()
    gameDisplay.fill((0,0,0))
    pygame.mixer.music.load("Assets\Music\last-fight-dungeon-synth-music-281592.mp3")
    pygame.mixer.music.play(loops=-1)
    pygame.mixer.music.set_volume(1)
    HPFont = pygame.font.Font("""Assets\Fonts\Speech.ttf""", 60)
    SpeechFont = pygame.font.Font("""Assets\Fonts\Speech.ttf""", 30)
    if Ai == 'enchanter':
        Ready = SpeechFont.render('Are you Ready, Mage?', True, (255, 150, 255))
        Begin = SpeechFont.render('Let us begin.', True, (255, 150, 255))
        Rloc = (800, 900)
        Bloc = (870, 900)
        Enemy_ai = Enchanter
    elif Ai == 'monarch':
        Ready = SpeechFont.render('You know why I summoned you to my court?', True, (80, 200, 120))
        Begin = SpeechFont.render('To entertain me.', True, (80, 200, 120))
        Rloc = (800, 900)
        Bloc = (870, 900)
        Enemy_ai = Monarch
    elif Ai == 'madman':
        TitleFont = pygame.font.Font("""Assets\Fonts\Books-Vhasenti.ttf""", 50)
        Ready = SpeechFont.render('The walls, I hear them in the walls. Those Ticks.', True, (255, 0, 0))
        Begin = TitleFont.render('Do you hear them too?', True, (255, 0, 0))
        Rloc = (725, 900)
        Bloc = (770, 400)
        Enemy_ai = Madman
    else:
        Ready = SpeechFont.render('Error', True, (255, 150, 255))
        Begin = SpeechFont.render('Error: No AI selected', True, (255, 150, 255))
        Rloc = (800, 900)
        Bloc = (870, 900)
        Enemy_ai = Enchanter

    # enchanters speech
    for i in range(0, 5):
        gameDisplay.fill((0, 0, 0))
        if i == 1:
            gameDisplay.blit(Ready, Rloc)
        if i == 3:
            gameDisplay.blit(Begin, Bloc)
        pygame.display.flip()
        
        clock.tick(100)
        skip = False
        if i != 2 or i != 0:
            for i in range(4000):
                if skip:
                    break
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                        quit()
                    if event.type == MOUSEBUTTONDOWN and event.button == 1:
                        skip = True
                pygame.time.delay(1)
                    
        else:
            for i in range(2000):
                if skip:
                    break
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                        quit()
                    if event.type == MOUSEBUTTONDOWN and event.button == 1:
                        skip = True
                pygame.time.delay(1)
                    
        
    # fade in the background
    a = 0
    for i in range(255):
        gameDisplay.fill((0, 0, 0))
        a += 1
        BattleGround.set_alpha(a)
        gameDisplay.blit(BattleGround, (460, 0))
        pygame.display.flip()

    # fade in the UI + pumps    
    pygame.time.delay(1)
    running = True
    Pumps = [Units.Generator((760, 315)), Units.Generator((1120, 315)), Units.Generator((760, 650)), Units.Generator((1120, 650))]
    Hp = HPFont.render(str(player_HP) + ":" + str(Enchanter_HP), False, (255, 150, 255))
    Footman_cost = SpeechFont.render('1', True, (0, 0, 0))
    Horse_cost = SpeechFont.render('3', True, (0, 0, 0))
    Soldier_cost = SpeechFont.render('3', True, (0, 0, 0))
    Summoner_cost = SpeechFont.render('6', True, (0, 0, 0))
    Runner_cost = SpeechFont.render('8', True, (0, 0, 0))
    Tank_cost = SpeechFont.render('8', True, (0, 0, 0))
    summon_UI = pygame.image.load("Assets\Sprites\Selecetion grid.png")
    a = 0
    manaCounter = pygame.image.load("Assets\Sprites\Mana_counter\\5.png")
    for i in range(255):
        gameDisplay.fill((0, 0, 0))
        gameDisplay.blit(BattleGround, (460, 0))
        a += 1
        for p in Pumps:
            p.Asset.set_alpha(a)
            gameDisplay.blit(p.Asset, (p.x, p.y))
        manaCounter.set_alpha(a)
        summon_UI.set_alpha(a)
        gameDisplay.blit(summon_UI, (1600, 200))
        gameDisplay.blit(manaCounter, (200, 862))
        Footman_cost.set_alpha(a)
        gameDisplay.blit(Footman_cost, (1688, 287))
        Horse_cost.set_alpha(a)
        gameDisplay.blit(Horse_cost, (1612, 412))
        Soldier_cost.set_alpha(a)
        gameDisplay.blit(Soldier_cost, (1700, 537))
        Summoner_cost.set_alpha(a)
        gameDisplay.blit(Summoner_cost, (1700, 667))
        Runner_cost.set_alpha(a)
        gameDisplay.blit(Runner_cost, (1700, 782))
        Tank_cost.set_alpha(a)
        gameDisplay.blit(Tank_cost, (1700, 907))
        Hp.set_alpha(a)
        gameDisplay.blit(Hp, (200, 200))
        pygame.display.flip()

    # loading Vars
    cursor_img = pygame.image.load("Assets\Sprites\Mouse.png")
    pygame.mouse.set_visible(False)
    startselect = (960, 540)
    endselect = (0, 0)
    frame = 0
    counter = 0
    Selecting = False
    selected = []
    friendly = []
    enemy = []
    inkblots = []
    if not SaveUpdater.decode_save_file()['tutorial']:
        tutorial_steps = [
            ("Welcome to the battlefield, Mage.", (700, 800)),
            ("This is your mana counter. You need mana to summon units.", (300, 800)),
            ("These are your summoning options. Each unit costs a different amount of mana.", (800, 300)),
            ("This is your health. If it reaches zero, you lose.", (300, 300)),
            ("These are your pumps. Control them to gain more mana.", (800, 400)),
            ("Click and drag to select your units.", (900, 600)),
            ("Right-click to move your selected units.", (900, 600)),
            ("Defeat the enemy by reducing their health to zero.", (700, 800))
        ]
        for step, loc in tutorial_steps:
            gameDisplay.fill((0, 0, 0))
            gameDisplay.blit(BattleGround, (460, 0))
            for p in Pumps:
                gameDisplay.blit(p.Asset, (p.x, p.y))
            gameDisplay.blit(manaCounter, (200, 862))
            gameDisplay.blit(summon_UI, (1600, 200))
            gameDisplay.blit(Hp, (200, 200))
            tutorial_text = SpeechFont.render(step, True, (255, 150, 255))
            text_rect = tutorial_text.get_rect(topleft=loc)
            pygame.draw.rect(gameDisplay, (0, 0, 0), text_rect)
            gameDisplay.blit(tutorial_text, loc)
            pygame.display.flip()
            pygame.time.delay(500)
            skip = False
            while not skip:
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                            pygame.quit()
                            return False
                if event.type == MOUSEBUTTONDOWN or event.type == KEYDOWN:
                        pygame.time.delay(100)
                        skip = True


        save = SaveUpdater.decode_save_file()
        save['tutorial'] = True
        SaveUpdater.encode_save_file(save)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                running = False
                pygame.quit()
            # start of selection
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                print(event.pos)
                if 598 < event.pos[0] < 1322 and not Selecting and 154 < event.pos[1] < 876:
                    startselect = event.pos
                    Selecting = True
                elif 1600 < event.pos[0] < 1920 and 200 < event.pos[1] < 940:
                    if player_mana >= 1 and event.pos[1] in range(200, 323, 1):
                        friendly.append(Units.Footman([966, 860]))
                        friendly[-1].target = [966, 860]
                        player_mana -= 1
                    elif player_mana >= 3 and event.pos[1] in range(323, 446, 1):
                        friendly.append(Units.Horse([966, 860]))
                        friendly[-1].target = [966, 860]
                        player_mana -= 3
                    elif player_mana >= 3 and event.pos[1] in range(446, 569, 1):
                        friendly.append(Units.Soldier([966, 860]))
                        friendly[-1].target = [966, 860]
                        player_mana -= 3
                    elif player_mana >= 6 and event.pos[1] in range(569, 692, 1):
                        friendly.append(Units.Summoner([966, 860]))
                        friendly[-1].target = [966, 860]
                        player_mana -= 6
                    elif player_mana >= 8 and event.pos[1] in range(692, 815, 1):
                        friendly.append(Units.Runner([966, 860]))
                        friendly[-1].target = [966, 860]
                        player_mana -= 8
                    elif player_mana >= 8 and event.pos[1] in range(815, 940, 1):
                        friendly.append(Units.Tank([966, 860]))
                        friendly[-1].target = [966, 860]
                        player_mana -= 8
                        
           # end of selection
            if event.type == MOUSEBUTTONUP and event.button == 1:
                # checking if in bounds of the field
                if 598 < event.pos[0] < 1322 and Selecting and 154 < event.pos[1] < 876:
                    endselect = event.pos
                    Selecting = False
                    start_x, end_x = sorted([startselect[0], endselect[0]])
                    start_y, end_y = sorted([startselect[1], endselect[1]])
                    startselect = (start_x, start_y)
                    endselect = (end_x, end_y)
                    selected = []
                    for f in friendly:
                        if startselect[0] <= f.x <= endselect[0] and startselect[1] <= f.y <= endselect[1]:
                            selected.append(f)
                    # print(f"Selection from {startselect} to {endselect}")
                    # print(f"Selected units: {selected}")
                elif Selecting:
                    # if not in bounds, find which co-ords are in bounds, if none, find the closest
                    xrange = [598, 1322]
                    yrange = [154, 876]
                    if 598 < event.pos[0] < 1322:
                        endselect = (event.pos[0], min(yrange, key=lambda y: abs(y - event.pos[1])))
                    elif 154 < event.pos[1] < 876:
                        endselect = (min(xrange, key=lambda x: abs(x - event.pos[0])), event.pos[1])
                    else:
                        endselect = (min(xrange, key=lambda x: abs(x - event.pos[0])), min(yrange, key=lambda y: abs(y - event.pos[1])))
                    selected = []
                    Selecting = False
                    start_x, end_x = sorted([startselect[0], endselect[0]])
                    start_y, end_y = sorted([startselect[1], endselect[1]])
                    startselect = (start_x, start_y)
                    endselect = (end_x, end_y)
                    for f in friendly:
                        if startselect[0] <= f.x <= endselect[0] and startselect[1] <= f.y <= endselect[1]:
                            selected.append(f)
                    # print(f"Selection from {startselect} to {endselect}")
                    # print(f"Selected units: {selected}")
            if event.type == MOUSEBUTTONDOWN and event.button == 3:
                for s in selected:
                    s.target = event.pos
            if Selecting and event.type == MOUSEMOTION:
                inkblots.append([event.pos, 255, 100, random.randint(0, 360)])


        gameDisplay.blit(BattleGround, (460, 0))
        # putting the inkblots on the field
        for blot in inkblots:
            blot[2] -= 1
            if blot[2] <= 0:
                blot[2] = 0
                blot[1] -= 1
                if blot[1] <=0:
                    inkblots.remove(blot)
            inkblot.set_alpha(blot[1])
            pygame.transform.rotate(inkblot, blot[3])
            gameDisplay.blit(inkblot, blot[0])

            # putting the pumps on the field
        for p in Pumps:
            gameDisplay.blit(p.Asset, (p.x, p.y))
            if p.hp <= 0:
                for f in friendly:
                    if p.x - 10 <= f.x <= p.x + 42 and p.y - 10 <= f.y <= p.y + 42:
                        # print("Friendly Pump gained")
                        score += 100
                        Pumps.remove(p)
                        friendly.append(Units.Generator([p.x, p.y]))
                        break
                for e in enemy:
                    if p.x - 42 <= e.x <= p.x + 42 and p.y - 42 <= e.y <= p.y + 42:
                        # print("Enemy Pump gained")
                        enemy.append(Units.Generator([p.x, p.y]))
                        Pumps.remove(p)
                        break
                # Remove the pump from the field if its HP is 0
            else:
                for f in friendly:
                    if p.x - 10 <= f.x <= p.x + 42 and p.y - 10 <= f.y <= p.y + 42:
                        p.hp -= 1
                for e in enemy:
                    if p.x - 10 <= e.x <= p.x + 42 and p.y - 10 <= e.y <= p.y + 42:
                        p.hp -= 1
        # putting the selected units on the field
        p_controled = 0
        for f in friendly:
            # checking for collision
            for e in enemy:
                if f.x in range(e.x, e.x + 12, 1) and f.y in range(e.y, e.y + 12, 1):
                    # combat
                    f.hp -= e.attack
                    e.hp -= f.attack
            # checking for enchanter damage
            if f.x in range(961, 971) and f.y in range(180, 190):
                Enchanter_HP -= f.attack
                f.hp = 0
            # unit death
            if f.hp <= 0:
                score -= 10
                if f.__class__.__name__ == "Generator":
                    # print("Friendly Pump destroyed")
                    enemy.append(Units.Generator([f.x, f.y]))
                else:
                    inkblots.append([(f.x, f.y), 255, 1000, random.randint(0, 360)])
                friendly.remove(f)
            # movement
            else:
                f.move(frame, friendly)
                gameDisplay.blit(f.Asset, (f.x, f.y))
            # counting the number of controlled pumps
            if f.__class__.__name__ == "Generator":
                p_controled += 1
            if f.__class__.__name__ == "Summoner" and frame in range(0, 500, 100):
                friendly.append(Units.Minion([f.x+3, f.y+3]))
                friendly[-1].target = f.target
            if f.__class__.__name__ == "Minion":
                f.lifetime += 1
                if f.lifetime >= 1000:
                    inkblots.append([(f.x, f.y), 255, 1000, random.randint(0, 360)])
                    friendly.remove(f)

        # similar to player controlled units, but for enchanter units
        p_e_controled = 0
        for e in enemy:
            # checking for player Damage
            if e.x in range(961, 971) and e.y in range(855, 865):
                player_HP -= e.attack
                e.hp = 0

            if e.hp <= 0:
                score += 10
                if e.__class__.__name__ == "Generator":
                    print("Enemy Pump destroyed")
                    friendly.append(Units.Generator([e.x, e.y]))
                else:
                    inkblots.append([(e.x, e.y), 255, 1000, random.randint(0, 360)])
                enemy.remove(e)
            else:
                e.move(frame, enemy)
                gameDisplay.blit(e.Asset, (e.x, e.y))
            if e.__class__.__name__ == "Generator":
                p_e_controled += 1
            if e.__class__.__name__ == "Summoner" and frame in range(0, 500, 100):
                enemy.append(Units.Minion([e.x+3, e.y+3]))
                enemy[-1].target = e.target
            if e.__class__.__name__ == "Minion":
                e.lifetime += 1
                if e.lifetime >= 1000:
                    inkblots.append([(e.x, e.y), 255, 1000, random.randint(0, 360)])
                    enemy.remove(e)

        # Mana Regen, for both player and Enchanter
        P_ratio = {0: 1, 1: 3, 2: 4, 3: 4, 4: 6}

        divisor = P_ratio[p_controled]
        if frame in range(0, 500,int(500/divisor)):
            player_mana += 1
            score += 5
            if player_mana > 9:
                player_mana = 9
        
        divisor = P_ratio[p_e_controled]
        if frame in range(0, 500,int(500/divisor)):
            Enchanter_mana += 1
            if Enchanter_mana > 9:
                Enchanter_mana = 9
        
        if Ai == 'madman':
            #Yes, the madman Cheats, Hes mad, he doesnt care about the rules
            Enchanter_mana = 9

        # Summoning enchanter units
        if frame in (100, 200, 300, 400, 500):
            summon = Enemy_ai.summon(Enchanter_mana, p_e_controled, enemy)
            print(summon)
            if summon == 0:
                enemy.append(Units.Footman([966, 185]))
                Enchanter_mana -= 1
                last = [enemy[-1]]
                Enemy_ai.target(last, friendly, Pumps, player_HP, Enchanter_HP)
            elif summon == 1:
                enemy.append(Units.Horse([966, 185]))
                Enchanter_mana -= 3
                last = [enemy[-1]]
                Enemy_ai.target(last, friendly, Pumps, player_HP, Enchanter_HP)
            elif summon == 2:
                enemy.append(Units.Soldier([966, 185]))
                Enchanter_mana -= 3
                last = [enemy[-1]]
                Enemy_ai.target(last, friendly, Pumps, player_HP, Enchanter_HP)
            elif summon == 3:
                enemy.append(Units.Summoner([966, 185]))
                Enchanter_mana -= 6
                last = [enemy[-1]]
                Enemy_ai.target(last, friendly, Pumps, player_HP, Enchanter_HP)
            elif summon == 4:
                enemy.append(Units.Runner([966, 185]))
                Enchanter_mana -= 8
                last = [enemy[-1]]
                Enemy_ai.target(last, friendly, Pumps, player_HP, Enchanter_HP)
            elif summon == 5:
                enemy.append(Units.Tank([966, 185]))
                Enchanter_mana -= 8
                last = [enemy[-1]]
                Enemy_ai.target(last, friendly, Pumps, player_HP, Enchanter_HP)
            else:
                print("summon failed")
                
            # enchanter targeting
        if player_HP <= 0:
            running = False
            
        if Enchanter_HP <= 0:
            running = False
            Won = True

        if frame >= 500:
            frame = 0
            counter += 1
            if counter == 3:
                Enemy_ai.target(enemy, friendly, Pumps, player_HP, Enchanter_HP)
                counter = 0
        # player mana display
        manaPath = "Assets\Sprites\Mana_counter\\" + str(player_mana) + ".png"
        manaCounter = pygame.image.load(manaPath)
        gameDisplay.blit(manaCounter, (200, 850))

        # Hp display
        hp = HPFont.render(str(player_HP) + ":" + str(Enchanter_HP), True, (255, 150, 255))
        gameDisplay.blit(hp, (200, 200))

        gameDisplay.blit(summon_UI, (1600, 200))
        gameDisplay.blit(Footman_cost, (1688, 287))
        gameDisplay.blit(Horse_cost, (1612, 416))
        gameDisplay.blit(Soldier_cost, (1692, 535))
        gameDisplay.blit(Summoner_cost, (1700, 662))
        gameDisplay.blit(Runner_cost, (1700, 785))
        gameDisplay.blit(Tank_cost, (1700, 912))
        
        # cursor display
        gameDisplay.blit(cursor_img, pygame.mouse.get_pos())

        # display update, counters, and FPS
        pygame.display.flip()
        clock.tick(100)
        gameDisplay.fill((0, 0, 0))
        frame += 1
    
    end_time = time.time()
    total_time = end_time - start_time
    time_score = max_time - total_time
    if time_score <= 0:
        time_score = 0
    score += time_score
    if Won:
        if Ai == 'enchanter':
            if SaveUpdater.decode_save_file()["beat_enchanter_first_time"]:
                Second_1 = SpeechFont.render('The game is the same', True, (255, 150, 255))
                Second_2 = SpeechFont.render('So you have learnt', True, (255, 150, 255))
                
                Second1Loc = (870, 900)
                Second2Loc = (870, 900)
                save = SaveUpdater.decode_save_file()
                save['enchanter'] = True
                SaveUpdater.encode_save_file(save)
                messages = [(Second_1, Second2Loc), (Second_2, Second1Loc)]
            else:
                First_Win = SpeechFont.render('You never learn', True, (255, 150, 255))
                FirstWLoc = (800, 900)
                Enchanter_HP = 100
                player_HP = 1
                messages = [(First_Win, FirstWLoc), (Loss_1, l1Loc), (Loss_2, l2Loc)]
                #Restart the battle with enchanter at 100 HP, and player with 0, the enchanter has a bunch of units about to kill the player, the battle then continues till the player loses, in which case, the enchanter has won
        elif Ai == 'monarch':
            M_win = SpeechFont.render('Oh quite a game, Shall we play again', True, (80, 200, 120))
            mWLoc= (800, 900)
            save = SaveUpdater.decode_save_file()
            save['monarch'] = True
            SaveUpdater.encode_save_file(save)
            messages = [(M_win, mWLoc)]

        elif Ai == 'madman':
            mad_1 = SpeechFont.render('This isnt a Prison, this is a Machine.', True, (255, 0, 0))
            mad_2 = SpeechFont.render('ISNT THAT RIGHT ' + Madman.scare() , True, (255, 0, 0))
            mad1loc = (725, 900)
            mad2loc = (770, 400)
            save = SaveUpdater.decode_save_file()
            save['madman'] = True
            SaveUpdater.encode_save_file(save)
            messages = [(mad_1, mad1loc), (mad_2, mad2loc)]

        else:
            No_win = SpeechFont.render('Error: No AI selected', True, (255, 150, 255))
            No_wLoc = (870, 900)
            messages = [(No_win, No_wLoc)]
    else:
        if Ai == 'enchanter':
            Loss_1 = SpeechFont.render(' All you need to do is learn', True, (255, 150, 255))
            Loss_2 = SpeechFont.render('Again', True, (255, 150, 255))
            l1Loc = (800, 900)
            l2Loc = (870, 900)
            messages = [(Loss_1, l1Loc), (Loss_2, l2Loc)]

        elif Ai == 'monarch':
            Crash_1 = SpeechFont.render('You bore me, Guards', True, (80, 200, 120))
            crash_loc = (800, 900)
            messages = [(Crash_1, crash_loc)]
            #Crash Game

        elif Ai == 'madman':
            mad_1 = SpeechFont.render('This isnt a Prison, this is a Machine', True, (255, 0, 0))
            mad_2 = SpeechFont.render('ISNT THAT RIGHT ' + Madman.scare() , True, (255, 0, 0))
            mad1loc = (725, 900)
            mad2loc = (770, 400)
            messages = [(mad_1, mad1loc), (mad_2, mad2loc)]

        else:
            No_loss = SpeechFont.render('Error: No AI selected', True, (255, 150, 255))
            no_lLoc = (870, 900)
            messages = [(No_loss, no_lLoc)]

    # Display end game messages

    if Ai == 'enchanter' and not SaveUpdater.decode_save_file()["beat_enchanter_first_time"]:
        for message, loc in messages:
            gameDisplay.fill((0, 0, 0))
            gameDisplay.blit(message, loc)
            pygame.display.flip()
            skip = False
            for i in range(4000):
                if skip:
                    break
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                        pygame.quit()
                        return False
                    if event.type == MOUSEBUTTONDOWN and event.button == 1:
                        skip = True
        save = SaveUpdater.decode_save_file()
        save["beat_enchanter_first_time"] = True
        SaveUpdater.encode_save_file(save)
        # Enchanter cheats
        Enchanter_HP = 100
        player_HP = 1
        running = True
        enemy = []
        # Spawn a bunch of enemy troops around the player spawn
        for _ in range(10):
            enemy.append(Units.Footman([random.randint(950, 980), random.randint(840, 880)]))
            enemy.append(Units.Horse([random.randint(950, 980), random.randint(840, 880)]))
            enemy.append(Units.Soldier([random.randint(950, 980), random.randint(840, 880)]))
            enemy.append(Units.Runner([random.randint(950, 980), random.randint(840, 880)]))

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    return False

            gameDisplay.fill((0, 0, 0))
            gameDisplay.blit(BattleGround, (460, 0))

            for e in enemy:
                e.move(frame, enemy)
                gameDisplay.blit(e.Asset, (e.x, e.y))
                if e.x in range(961, 971) and e.y in range(855, 865):
                    player_HP -= e.attack
                    e.hp = 0
                if e.hp <= 0:
                    enemy.remove(e)

            if player_HP <= 0:
                running = False

            # Display player and enchanter HP
            hp = HPFont.render(str(player_HP) + ":" + str(Enchanter_HP), True, (255, 150, 255))
            gameDisplay.blit(hp, (200, 200))

            # Display cursor
            gameDisplay.blit(cursor_img, pygame.mouse.get_pos())

            pygame.display.flip()
            clock.tick(100)
            frame += 1
        Loss_1 = SpeechFont.render(' All you need to do is learn…', True, (255, 150, 255))
        Loss_2 = SpeechFont.render('Again.', True, (255, 150, 255))
        l1Loc = (800, 900)
        l2Loc = (870, 900)
        messages = [(Loss_1, l1Loc), (Loss_2, l2Loc)]
        for message, loc in messages:
            gameDisplay.fill((0, 0, 0))
            gameDisplay.blit(message, loc)
            pygame.display.flip()
            skip = False
            for i in range(4000):
                if skip:
                    break
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                        pygame.quit()
                        return False
                    if event.type == MOUSEBUTTONDOWN and event.button == 1:
                        skip = True
                pygame.time.delay(1)

    elif Ai == 'monarch':
        # Monarch crashes the game
        Crash_1 = SpeechFont.render('You bore me, Guards!', True, (255, 150, 255))
        gameDisplay.fill((0, 0, 0))
        gameDisplay.blit(Crash_1, (800, 900))
        pygame.display.flip()
        pygame.time.delay(4000)
        pygame.quit()
        return False
    else:
        for message, loc in messages:
            gameDisplay.fill((0, 0, 0))
            gameDisplay.blit(message, loc)
            pygame.display.flip()
            skip = False
            for i in range(4000):
                if skip:
                    break
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                        pygame.quit()
                        return False
                    if event.type == MOUSEBUTTONDOWN and event.button == 1:
                        skip = True
        

    # Ask if the player wants to play again
    play_again_font = pygame.font.Font("Assets\Fonts\Speech.ttf", 40)
    play_again_text = play_again_font.render('Do you want to play again? (Y/N)', True, (255, 255, 255))
    play_again_text = play_again_font.render(str(score), True, (255, 255, 255))
    gameDisplay.fill((0, 0, 0))
    gameDisplay.blit(play_again_text, (800, 900))
    gameDisplay.blit(play_again_text, (800, 700))
    pygame.display.flip()

    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                return False
            if event.type == KEYDOWN:
                if event.key == K_y:
                    return True
                elif event.key == K_n:
                    return False
    #Show Score and ask if they wanna play again, if they player wants to return to menu, return False, Else return True (Doesnt apply to monarch as game is crashed)

