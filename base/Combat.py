import pygame, random, time, math
from Ai import Enchanter, Madman, Monarch
from pygame.locals import *
import os

def cap_inkblots(inkblots, max_length=500):
    if len(inkblots) > max_length:
        del inkblots[0:len(inkblots) - max_length]

def render_wrapped_text(surface, text, font, color, alpha, rect, line_spacing=5):
    """
    Render text that wraps within a given rectangle.\n
    :param surface: The Pygame surface to render the text on.
    :param text: The text to render.
    :param font: The Pygame font object.
    :param color: The color of the text.
    :param rect: A pygame.Rect defining the area to wrap the text in.
    :param line_spacing: Spacing between lines of text.
    """
    words = text.split(' ')
    lines = []
    current_line = []

    for word in words:
        # Check if adding the word exceeds the width of the rect
        test_line = ' '.join(current_line + [word])
        if font.size(test_line)[0] <= rect.width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]

    # Add the last line
    if current_line:
        lines.append(' '.join(current_line))

    # Render each line
    y_offset = rect.top
    # print("rendering text")
    for line in lines:
        line_surface = font.render(line, True, color)
        line_surface.set_alpha(alpha)
        # (f"rendering line: {line}")
        pygame.draw.rect(surface, (0, 0, 0), line_surface.get_rect(topleft=(rect.left, y_offset)))  # Draw a Black rectangle around the text
        surface.blit(line_surface, (rect.left, y_offset))
        y_offset += font.size(line)[1] + line_spacing


def BatStart(Ai: str, display: pygame.Surface, RPC_on: bool, RPC: object, pid, Units: object, SaveUpdater: object, Scalars: list, Screensize: list, wrap_func: callable) -> bool:

    if len(Scalars) != 2:
        raise ValueError("Scalars Argument must contain two elements.")
    if len(Screensize) != 2:
        raise ValueError("Screensize Argument must contain two elements.")
    
    # Get screen dimensions dynamically
    screen_width, screen_height = Screensize[0], Screensize[1]
    scale_x, scale_y = Scalars[0], Scalars[1]
    #print()


    # For loading from config json file
    gamedefaults = {
        'player_mana': 5,
        'Enchanter_mana': 5,
        'player_HP': 20,
        'Enchanter_HP': 20,
        'Won': False,
        'Enemy_ai': Enchanter,
        'score': 0,
        'max_time': 1200,
    }
    player_mana = gamedefaults['player_mana']
    Enchanter_mana = gamedefaults['Enchanter_mana']
    player_HP = gamedefaults['player_HP']
    Enchanter_HP = gamedefaults['Enchanter_HP']
    Won = gamedefaults['Won']
    Enemy_ai = gamedefaults['Enemy_ai']
    score = gamedefaults['score']
    max_time = gamedefaults['max_time']
    

    #global defaults
    start_time = time.time()
    gameDisplay = display
    BattleGround = pygame.image.load(os.path.join("Assets", "Sprites", "pixil-frame-0.png"))
    inkblot = pygame.image.load(os.path.join("Assets", "Sprites", "InkBlot.png")).convert_alpha()
    clock = pygame.time.Clock()
    gameDisplay.fill((0, 0, 0))
    pygame.mixer.music.load(os.path.join("Assets", "Music", "DungeonSynth2Hr.mp3"))
    pygame.mixer.music.play(loops=-1)
    pygame.mixer.music.set_volume(1) if SaveUpdater.decode_save_file()['music'] else pygame.mixer.music.set_volume(0)

    # Scale assets dynamically


    BattleGround = pygame.transform.smoothscale(
        BattleGround,   #1000x1000 Asset
        # Height should be scaled to max y of screen, which is the same scalar as width
        (int(BattleGround.get_width() * (screen_height / 1000)), int(BattleGround.get_height() * (screen_height / 1000)))
    )
    inkblot = pygame.transform.smoothscale(
        inkblot,
        (int(inkblot.get_width() * scale_y), int(inkblot.get_height() * scale_y))
    )

    # Scale fonts dynamically
    HPFont = pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), int(screen_height * 0.1))
    SpeechFont = pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), int(screen_height * 0.05))
    pause = SpeechFont.render('Paused', True, (255, 255, 255))

    # Scale UI elements dynamically
    summon_UI = pygame.image.load(os.path.join("Assets", "Sprites", "Selecetion grid.png"))
    summon_UI = pygame.transform.smoothscale(
        summon_UI,
        (int(summon_UI.get_width() * scale_y), int(summon_UI.get_height() * scale_y))
    )

    manaCounter = pygame.image.load(os.path.join("Assets", "Sprites", "Mana_counter", "5.png"))
    manaCounter = pygame.transform.smoothscale(
        manaCounter,
        [int(manaCounter.get_width() * scale_y), int(manaCounter.get_height() * scale_y)]
    )

    # Adjust cursor size dynamically
    cursor_img = pygame.image.load(os.path.join("Assets", "Sprites", "Mouse.png"))
    cursor_img = pygame.transform.smoothscale(
        cursor_img,
        [int(cursor_img.get_width() * scale_y), int(cursor_img.get_height() * scale_y)]
    )

    # Dynamic positioning
    BattleGround_pos_rect = BattleGround.get_rect(center=(screen_width // 2, screen_height // 2))
    BattleGround_pos = BattleGround_pos_rect.topleft
    summon_UI_pos_rect = summon_UI.get_rect(center=(screen_width - (summon_UI.get_width() // 2), screen_height // 2))
    summon_UI_pos = summon_UI_pos_rect.topleft
    manaCounter_pos_rect = manaCounter.get_rect(center=((manaCounter.get_width() // 2), screen_height - (manaCounter.get_height() // 2)))
    manaCounter_pos = manaCounter_pos_rect.topleft
    HP_pos = (screen_width * 0, screen_height * 0)

    # Adjust tutorial text positions dynamically
    tutorial_positions = [
    pygame.Rect(
        screen_width // 2 - 200,  # Centered horizontally
        (screen_height * 0.8) - 50,  # Centered vertically
        400,  # Width of the text box
        100    # Height of the text box
    ),
    pygame.Rect(
        (screen_width * 0.2) - 200,  # Centered horizontally
        (screen_height * 0.8) - 50,  # Centered vertically
        400,  # Width of the text box
        100    # Height of the text box
    ),
    pygame.Rect(
        (screen_width * 0.75) - 200,  # Centered horizontally
        (screen_height * 0.2) - 50,  # Centered vertically
        400,  # Width of the text box
        100    # Height of the text box
    ),
    pygame.Rect(
        min(max(int(screen_width * 0.1), 0), screen_width - 400),
        min(max(int(screen_height * 0.2), 0), screen_height - 100),
        400,
        100
    ),
    pygame.Rect(
        min(max(int(screen_width * 0.5), 0), screen_width - 400),
        min(max(int(screen_height * 0.5), 0), screen_height - 100),
        400,
        100
    ),
    pygame.Rect(
        min(max(int(screen_width * 0.5), 0), screen_width - 400),
        min(max(int(screen_height * 0.4), 0), screen_height - 100),
        400,
        100
    ),
    pygame.Rect(
        min(max(int(screen_width * 0.5), 0), screen_width - 400),
        min(max(int(screen_height * 0.4), 0), screen_height - 100),
        400,
        100
    ),
    pygame.Rect(
        screen_width // 2 - 200,  # Centered horizontally
        (screen_height * 0.8) - 50,  # Centered vertically
        400,  # Width of the text box
        100    # Height of the text box
    )
]

    # Adjust other hardcoded positions dynamically
    Rloc = (screen_width * 0.4, screen_height * 0.9)
    Bloc = (screen_width * 0.45, screen_height * 0.9)

    # Adjust costs dynamically
    # 123px distance between each cost * scale

    Footman_cost_pos = (summon_UI_pos_rect.centerx, summon_UI_pos_rect.topleft[1] + (1* ((123 * scale_y)//2)))
    Horse_cost_pos = (summon_UI_pos_rect.centerx, summon_UI_pos_rect.topleft[1] + (3* ((123 * scale_y)//2)))
    Soldier_cost_pos = (summon_UI_pos_rect.centerx, summon_UI_pos_rect.topleft[1] + (5* ((123 * scale_y)//2)))
    Summoner_cost_pos = (summon_UI_pos_rect.centerx, summon_UI_pos_rect.topleft[1] + (7* ((123 * scale_y)//2)))
    Runner_cost_pos = (summon_UI_pos_rect.centerx, summon_UI_pos_rect.topleft[1] + (9* ((123 * scale_y)//2)))
    Tank_cost_pos = (summon_UI_pos_rect.centerx, summon_UI_pos_rect.topleft[1] + (11* ((123 * scale_y)//2)))

    # Adjust endgame message positions dynamically
    endgame_message_pos = (screen_width * 0.4, screen_height * 0.9)
    
    X_MIN = int(BattleGround_pos[0] + (BattleGround.get_width() * 0.124))
    X_MAX = int(BattleGround_pos[0] + (BattleGround.get_width() * 0.865))
    Y_MIN = int(BattleGround_pos[1] + (BattleGround.get_height() * 0.19))
    Y_MAX = int(BattleGround_pos[1] + (BattleGround.get_height() * 0.89))

    
    BattleGround_width = X_MAX - X_MIN
    BattleGround_height = Y_MAX - Y_MIN

    BattleGround_debug_rect = pygame.Rect(X_MIN, Y_MIN, BattleGround_width, BattleGround_height)
    player_base = (int(X_MIN + (BattleGround_width // 2)), int(Y_MAX - (BattleGround_height * 0.1)))
    enemy_base = (int(X_MIN + (BattleGround_width // 2)),int(Y_MIN + (BattleGround_height * 0.1)))
    # Adjust pump positions dynamically to be centered and evenly spaced
    Pumps = [
        Units.Generator((X_MIN + (BattleGround_width * 0.20), Y_MIN + (BattleGround_height * 0.20)), Scalars),
        Units.Generator((X_MIN + (BattleGround_width * 0.70), Y_MIN + (BattleGround_height * 0.20)), Scalars),
        Units.Generator((X_MIN + (BattleGround_width * 0.20), Y_MIN + (BattleGround_height * 0.70)), Scalars),
        Units.Generator((X_MIN + (BattleGround_width * 0.70), Y_MIN + (BattleGround_height * 0.70)), Scalars)
    ]

    # Adjust selection bounds dynamically
    boundaries = {
        'left': X_MIN,
        'right': X_MAX,
        'top': Y_MIN,
        'bottom': Y_MAX
    }
    epoch = int(time.time())
    
    if RPC_on:
        RPC.update(
            pid=pid,
            state="Inking and Incanting",
            details=f"{player_HP}:{Enchanter_HP}",
            start=epoch,
            large_image="icon",
            large_text="The Enchanters Book awaits...."
        )
    if Ai == 'enchanter':
        Ready = SpeechFont.render('Are you Ready, Mage?', True, (255, 150, 255))
        Begin = SpeechFont.render('Let us begin.', True, (255, 150, 255))
        Rloc = (Ready.get_rect(center=(screen_width // 2, screen_height * 0.9)))
        Bloc = (Begin.get_rect(center=(screen_width // 2, screen_height * 0.9)))
        Enemy_ai = Enchanter
    elif Ai == 'monarch':
        Ready = SpeechFont.render('You know why I summoned you to my court?', True, (80, 200, 120))
        Begin = SpeechFont.render('To entertain me.', True, (80, 200, 120))
        Rloc = (Ready.get_rect(center=(screen_width // 2, screen_height * 0.9)))
        Bloc = (Begin.get_rect(center=(screen_width // 2, screen_height * 0.9)))
        Enemy_ai = Monarch
    elif Ai == 'madman':
        TitleFont = pygame.font.Font(os.path.join("Assets", "Fonts", "Books-Vhasenti.ttf"), 50)
        Ready = SpeechFont.render('The walls, I hear them in the walls. Those Ticks.', True, (255, 0, 0))
        Begin = TitleFont.render('Do you hear them too?', True, (255, 0, 0))
        Rloc = (Ready.get_rect(center=(screen_width // 2, screen_height * 0.9)))
        Bloc = (Begin.get_rect(center=(screen_width // 2, screen_height // 2)))
        Enemy_ai = Madman
    else:
        Ready = SpeechFont.render('Error', True, (255, 150, 255))
        Begin = SpeechFont.render('Error: No AI selected', True, (255, 150, 255))
        Rloc = (Ready.get_rect(center=(screen_width // 2, screen_height * 0.9)))
        Bloc = (Begin.get_rect(center=(screen_width // 2, screen_height * 0.9)))
        Enemy_ai = Enchanter

    # Enchanters speech
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

    # Fade in the background
    a = 0
    for i in range(255):
        gameDisplay.fill((0, 0, 0))
        a += 1
        BattleGround.set_alpha(a)
        gameDisplay.blit(BattleGround, BattleGround_pos)
        pygame.display.flip()




    # Fade in the UI + pumps
    pygame.time.delay(1)
    running = True
    Hp = HPFont.render(str(player_HP) + ":" + str(Enchanter_HP), False, (255, 150, 255))
    Footman_cost = SpeechFont.render(str(Units.Footman.cost), True, (255, 0, 0))
    Horse_cost = SpeechFont.render(str(Units.Horse.cost), True, (255, 0, 0))
    Soldier_cost = SpeechFont.render(str(Units.Soldier.cost), True, (255, 0, 0))
    Summoner_cost = SpeechFont.render(str(Units.Summoner.cost), True, (255, 0, 0))
    Runner_cost = SpeechFont.render(str(Units.Runner.cost), True, (255, 0, 0))
    Tank_cost = SpeechFont.render(str(Units.Tank.cost), True, (255, 0, 0))
    a = 0
    for i in range(255):
        gameDisplay.fill((0, 0, 0))
        gameDisplay.blit(BattleGround, BattleGround_pos)
        a += 1
        for p in Pumps:
            p.Asset.set_alpha(a)
            gameDisplay.blit(p.Asset, (p.x, p.y))
        manaCounter.set_alpha(a)
        summon_UI.set_alpha(a)
        gameDisplay.blit(summon_UI, summon_UI_pos)
        gameDisplay.blit(manaCounter, manaCounter_pos)
        Footman_cost.set_alpha(a)
        gameDisplay.blit(Footman_cost, Footman_cost_pos)
        Horse_cost.set_alpha(a)
        gameDisplay.blit(Horse_cost, Horse_cost_pos)
        Soldier_cost.set_alpha(a)
        gameDisplay.blit(Soldier_cost, Soldier_cost_pos)
        Summoner_cost.set_alpha(a)
        gameDisplay.blit(Summoner_cost,Summoner_cost_pos)
        Runner_cost.set_alpha(a)
        gameDisplay.blit(Runner_cost, Runner_cost_pos)
        Tank_cost.set_alpha(a)
        gameDisplay.blit(Tank_cost, Tank_cost_pos)
        Hp.set_alpha(a)
        gameDisplay.blit(Hp, HP_pos)
        pygame.display.flip()

    # Loading Vars
    selection_icon = pygame.image.load(os.path.join("Assets", "Sprites", "unit_sprites", "Selected.png")) 
    cursor_img = pygame.image.load(os.path.join("Assets", "Sprites", "Mouse.png"))
    pygame.mouse.set_visible(False)
    Selecting = False
    selected = []
    friendly = []
    enemy = []
    inkblots = []
    hp_cache = (player_HP, Enchanter_HP)
    hp_text = HPFont.render(f"{player_HP}:{Enchanter_HP}", True, (255, 150, 255))
    mouseinkblots = []

    t_x = player_base[0]
    t_y = player_base[1] - (BattleGround_height * 0.2)


    move_rate = BattleGround_width // 400

    pygame.event.clear()

    if not SaveUpdater.decode_save_file()['tutorial']:
        tutorial_steps = [
            ("Welcome to the battlefield, Mage.", tutorial_positions[0]),
            ("<--- This is your mana counter. You need mana to summon units.", tutorial_positions[1]),
            ("These are your summoning options. Each unit costs a different amount of mana. --->", tutorial_positions[2]),
            ("<--- This is your health. If it reaches zero, you lose.", tutorial_positions[3]),
            ("These are your pumps. Control them to gain more mana.", tutorial_positions[4]),
            ("Click and drag to select your units.", tutorial_positions[5]),
            ("Right-click to move your selected units.", tutorial_positions[6]),
            ("Defeat the enemy by reducing their health to zero.", tutorial_positions[7])
        ]
        i = 0
        for step, turect in tutorial_steps:
            i += 1
            frame = 0
            gameDisplay.fill((0, 0, 0))
            gameDisplay.blit(BattleGround, BattleGround_pos)
            for p in Pumps:
                gameDisplay.blit(p.Asset, (p.x, p.y))
            gameDisplay.blit(manaCounter, manaCounter_pos)
            gameDisplay.blit(summon_UI, summon_UI_pos)
            gameDisplay.blit(Hp, HP_pos)
            render_wrapped_text(gameDisplay, step, SpeechFont, (255, 150, 255), 255, turect)    #surface, text, font, color, alpha, rect, line_spacing=5
            pygame.display.flip()
            pygame.time.delay(500)
            skip = False
            if i == 6 or i == 7:
                friendly.append(Units.Footman((player_base[0], player_base[1]), Scalars))
                friendly[-1].target = (player_base[0], player_base[1])

            while not skip:
                frame += 1
                clock.tick(60)  # Limit the frame rate to 60 FPS
                gameDisplay.fill((0, 0, 0))  # Clear the screen
                gameDisplay.blit(BattleGround, BattleGround_pos)  # Redraw the background

                # Redraw all static elements
                for p in Pumps:
                    gameDisplay.blit(p.Asset, (p.x, p.y))
                gameDisplay.blit(manaCounter, manaCounter_pos)
                gameDisplay.blit(summon_UI, summon_UI_pos)
                gameDisplay.blit(Hp, HP_pos)

                # Handle animations for step 6
                if i == 6:
                    if frame < 360:
                        gameDisplay.blit(friendly[-1].Asset, (friendly[-1].x, friendly[-1].y))
                        x = friendly[-1].x + (friendly[-1].Asset.get_width() // 2) - (inkblot.get_width() // 2) + (cursor_img.get_width() // 2)
                        y = friendly[-1].y + (friendly[-1].Asset.get_height() // 2) - (inkblot.get_height() // 2) + (cursor_img.get_height() // 2)
                        angle = frame * (2 * math.pi / 360)  # Convert frame to angle in radians
                        inkblot_x = x + (math.cos(angle) * 50)
                        inkblot_y = y + (math.sin(angle) * 50)
                        inkblot_pos = (inkblot_x, inkblot_y)
                        inkblots.append(inkblot_pos)

                    # Draw inkblots
                    for ink in inkblots:
                        gameDisplay.blit(inkblot, ink)

                    if frame == 361:
                        inkblots.clear()
                        gameDisplay.blit(friendly[-1].Asset, (friendly[-1].x, friendly[-1].y))
                        gameDisplay.blit(selection_icon, (friendly[-1].x, friendly[-1].y))

                    if 361 < frame < 461:
                        gameDisplay.blit(friendly[-1].Asset, (friendly[-1].x, friendly[-1].y))
                        gameDisplay.blit(selection_icon, (friendly[-1].x, friendly[-1].y))

                    if frame == 461:
                        inkblots.clear()
                        frame = 0  # Reset frame counter
                    
                    gameDisplay.blit(cursor_img, inkblot_pos)

                # Handle animations for step 7
                if i == 7:
                    if frame < 100:
                        gameDisplay.blit(friendly[-1].Asset, (friendly[-1].x, friendly[-1].y))
                        gameDisplay.blit(selection_icon, (friendly[-1].x, friendly[-1].y))
                    elif 100 <= frame < 500:
                        cursor_pos = (
                            (friendly[-1].x + ((t_x - friendly[-1].x) * (frame - 100) / 400)+(cursor_img.get_width() // 2)),
                            (friendly[-1].y + ((t_y - friendly[-1].y) * (frame - 100) / 400)+(cursor_img.get_height() // 2))
                        )
                        gameDisplay.blit(cursor_img, cursor_pos)
                        
                        gameDisplay.blit(friendly[-1].Asset, (friendly[-1].x, friendly[-1].y))
                        gameDisplay.blit(selection_icon, (friendly[-1].x, friendly[-1].y))
                    elif frame == 500:
                        friendly[-1].target = (t_x, t_y)
                    elif 500 < frame < 1000:
                        friendly[-1].move(0.1, [], boundaries, Scalars)
                        gameDisplay.blit(friendly[-1].Asset, (friendly[-1].x, friendly[-1].y))
                        gameDisplay.blit(selection_icon, (friendly[-1].x, friendly[-1].y))
                        gameDisplay.blit(cursor_img, cursor_pos)
                    elif frame == 1000:
                        friendly[-1].target = (player_base)
                        friendly[-1].x, friendly[-1].y = player_base[0], player_base[1]
                        frame = 0
                # Update the display
                render_wrapped_text(gameDisplay, step, SpeechFont, (255, 150, 255), 255, turect)
                pygame.display.flip()

                # Event handling
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                        pygame.quit()
                        return False
                    if event.type == MOUSEBUTTONDOWN or event.type == KEYDOWN:
                        skip = True

        friendly.clear()
        inkblots.clear()
        save = SaveUpdater.decode_save_file()
        save['tutorial'] = True
        SaveUpdater.encode_save_file(save)

    pygame.event.clear()

    # Initialize variables for delta time
    last_time = time.time()
    player_mana_timer = 0
    enchanter_mana_timer = 0
    summon_timer = 0
    targeting_timer = 0
    show_fps_debug = False
    show_mana_debug = False
    show_battle_debug = False

    mana_images = []
    for i in range(10):
        mana_images.append(pygame.image.load(os.path.join("Assets", "Sprites", "Mana_counter", str(i) + ".png")))
        mana_images[i] = pygame.transform.smoothscale(
            mana_images[i],
            [int(mana_images[i].get_width() * scale_y), int(mana_images[i].get_height() * scale_y)]
        )
    # Main game loop
    running = True
    while running:
        # Calculate delta time
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                running = False
                pygame.quit()
                return False
            if event.type == KEYDOWN and event.key == K_F1:
                if not show_fps_debug:
                    show_fps_debug = True
                    show_mana_debug = False
                else:
                    show_fps_debug = False
                    show_mana_debug = False
            if event.type == KEYDOWN and event.key == K_F2:
                if show_mana_debug:
                    show_mana_debug = False
                    show_fps_debug = False
                else:
                    show_mana_debug = True
                    show_fps_debug = True
            if event.type == KEYDOWN and event.key == K_F3:
                show_battle_debug = not show_battle_debug
            if event.type == KEYDOWN and event.key == K_p:
                paused = True
                while paused:
                    gameDisplay.blit(pause, (800, 450))
                    pygame.display.flip()
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                            running = False
                            paused = False
                        if event.type == KEYDOWN and event.key == K_p:
                            paused = False 
            # start of selection
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
    # Check if the click is within the battlefield bounds
                if X_MIN < event.pos[0] < X_MAX and not Selecting and Y_MIN < event.pos[1] < Y_MAX:
                    Selecting = True
                # Check if the click is within the summoning UI bounds
                elif summon_UI_pos[0] < event.pos[0] < (summon_UI_pos[0] + summon_UI.get_width()) and summon_UI_pos[1] < event.pos[1] < (summon_UI_pos[1] + summon_UI.get_height()):
                    # Determine which unit to summon based on the Y position of the click
                    if player_mana >= Units.Footman.cost and summon_UI_pos[1] <= event.pos[1] < (summon_UI_pos[1] + (123 * scale_y)):
                        friendly.append(Units.Footman((player_base[0], player_base[1]), Scalars))
                        friendly[-1].target = (player_base[0], player_base[1])
                        player_mana -= Units.Footman.cost
                    elif player_mana >= Units.Horse.cost and (summon_UI_pos[1] + (123 * scale_y)) <= event.pos[1] < (summon_UI_pos[1] + 2 * (123 * scale_y)):
                        friendly.append(Units.Horse((player_base[0], player_base[1]), Scalars))
                        friendly[-1].target = (player_base[0], player_base[1])
                        player_mana -= Units.Horse.cost
                    elif player_mana >= Units.Soldier.cost and (summon_UI_pos[1] + 2 * (123 * scale_y)) <= event.pos[1] < (summon_UI_pos[1] + 3 * (123 * scale_y)):
                        friendly.append(Units.Soldier((player_base[0], player_base[1]), Scalars))
                        friendly[-1].target = (player_base[0], player_base[1])
                        player_mana -= Units.Soldier.cost
                    elif player_mana >= Units.Summoner.cost and (summon_UI_pos[1] + 3 * (123 * scale_y)) <= event.pos[1] < (summon_UI_pos[1] + 4 * (123 * scale_y)):
                        friendly.append(Units.Summoner((player_base[0], player_base[1]), Scalars))
                        friendly[-1].target = (player_base[0], player_base[1])
                        player_mana -= Units.Summoner.cost
                    elif player_mana >= Units.Runner.cost and (summon_UI_pos[1] + 4 * (123 * scale_y)) <= event.pos[1] < (summon_UI_pos[1] + 5 * (123 * scale_y)):
                        friendly.append(Units.Runner((player_base[0], player_base[1]), Scalars))
                        friendly[-1].target = (player_base[0], player_base[1])
                        player_mana -= Units.Runner.cost
                    elif player_mana >= Units.Tank.cost and (summon_UI_pos[1] + 5 * (123 * scale_y)) <= event.pos[1] < (summon_UI_pos[1] + 6 * (123 * scale_y)):
                        friendly.append(Units.Tank((player_base[0], player_base[1]), Scalars))
                        friendly[-1].target = (player_base[0], player_base[1])
                        player_mana -= Units.Tank.cost
           # end of selection
            if event.type == MOUSEBUTTONUP and event.button == 1:
                # checking if in bounds of the field
                if Selecting:
                    Selecting = False
                    if mouseinkblots:
                        blotx=[]
                        bloty=[]
                        for ink in mouseinkblots:
                            blotx.append(ink[0][0])
                            bloty.append(ink[0][1])
                        blotx.sort()
                        bloty.sort()
                        startselect = (blotx[0], bloty[0])
                        endselect = (blotx[-1], bloty[-1])
                        selected = []
                        for f in friendly:
                            if startselect[0] <= f.x <= endselect[0] and startselect[1] <= f.y <= endselect[1]:
                                    selected.append(f)
                            # #print(f"Selection from {startselect} to {endselect}")
                            # #print(f"Selected units: {selected}")
            if event.type == MOUSEBUTTONDOWN and event.button == 3:
                for s in selected:
                    s.target = event.pos
            if event.type == MOUSEBUTTONDOWN and event.button == 2:
                #middle mouse button
                #print(event.pos)
                pass
            # Adjust the boundary conditions in the MOUSEMOTION event handler
            if Selecting and event.type == MOUSEMOTION:
                pos = event.pos
                # Clamp the position within the battlefield bounds
                clamped_x = max(X_MIN, min(pos[0], X_MAX))
                clamped_y = max(Y_MIN, min(pos[1], Y_MAX))
                pos = (clamped_x, clamped_y)
                mouseinkblots.append([pos, 255, 100, random.choice(range(0, 360, 45))])

        gameDisplay.blit(BattleGround, BattleGround_pos)
        # putting the inkblots on the field
        for blot in inkblots:
            blot[2] -= 1
            if blot[2] <= 0:
                blot[2] = 0
                blot[1] -= 1
            if blot[1] < 0:
                    blot[1] = 0
            rotated = pygame.transform.rotate(inkblot, blot[3])
            rotated.convert_alpha()
            rotated = rotated.set_alpha(blot[1])
            #print(rotated.get_alpha())
            if rotated:
                gameDisplay.blit(rotated, blot[0])

        for blot in mouseinkblots:
            if not Selecting:
                blot[2] -= 1
                if blot[2] <= 0:
                    blot[2] = 0
                    blot[1] -= 1
                if blot[1] < 0:
                    blot[1] = 0
            rotated = pygame.transform.rotate(inkblot, blot[3])
            rotated.convert_alpha()
            rotated = rotated.set_alpha(blot[1])
            #print(rotated.get_alpha())
            if rotated:
                gameDisplay.blit(rotated, blot[0])


        inkblots = [b for b in inkblots if b[1] > 0]
        mouseinkblots = [b for b in mouseinkblots if b[1] > 0]


        # putting the pumps on the field
        for p in Pumps:
            gameDisplay.blit(p.Asset, (p.x, p.y))
            if p.hp <= 0:
                for f in friendly:
                    if p.x - 10 <= f.x <= p.x + 42 and p.y - 10 <= f.y <= p.y + 42:
                        # #print("Friendly Pump gained")
                        score += 100
                        try:
                            Pumps.remove(p)
                        except Exception as e:
                            print(e)
                        friendly.append(Units.Generator([p.x, p.y], Scalars))
                        break
                for e in enemy:
                    if p.x - 42 <= e.x <= p.x + 42 and p.y - 42 <= e.y <= p.y + 42:
                        # #print("Enemy Pump gained")
                        enemy.append(Units.Generator([p.x, p.y], Scalars))
                        try:
                            Pumps.remove(p)
                        except Exception as e:
                            print(e)
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
                if abs(f.x - e.x) < 12 and abs(f.y - e.y) < 12:
                    # combat
                    f.hp -= e.attack
                    e.hp -= f.attack
            # checking for enchanter damage
            if f.x in range(enemy_base[0]-5, enemy_base[0]+5) and f.y in range(enemy_base[1]-5, enemy_base[1]+5):
                Enchanter_HP -= f.attack
                f.hp = 0
            # unit death
            if f.hp <= 0:
                score -= 10
                if f.__class__.__name__ == "Generator":
                    # #print("Friendly Pump destroyed")
                    enemy.append(Units.Generator([f.x, f.y], Scalars))
                else:
                    inkblots.append([(f.x, f.y), 255, 1000, random.choice(range(0, 360, 45))])
                try:
                    friendly.remove(f)
                except Exception as e:
                    print(e)
                continue
            # movement
            else:
                f.move(dt, friendly, boundaries, Scalars)
                gameDisplay.blit(f.Asset, (f.x, f.y))
            # counting the number of controlled pumps
            if f.__class__.__name__ == "Generator":
                p_controled += 1
            if f.__class__.__name__ == "Summoner":
                if not hasattr(f, "spawn_timer"):
                    f.spawn_timer = 0  # Initialize spawn timer if not already set
                f.spawn_timer += dt  # Increment spawn timer by delta time
                if f.spawn_timer >= 1:  # Check if 1 second has passed
                    friendly.append(Units.Minion([f.x, f.y], Scalars, f))
                    friendly[-1].target = f.target
                    if f in selected:
                        selected.append(friendly[-1])
                    f.spawn_timer = 0  # Reset the spawn timer
            if f.__class__.__name__ == "Minion":
                f.lifetime += dt
                if f.master:
                    f.target = f.master.target
                if f.lifetime >= 10:
                    inkblots.append([(f.x, f.y), 255, 1000, random.choice(range(0, 360, 45))])
                    try:
                        friendly.remove(f)
                    except Exception as e:
                        print(e)
                    continue

        # similar to player controlled units, but for enchanter units
        p_e_controled = 0
        for e in enemy:
            # checking for player Damage
            if e.x in range(player_base[0]-5, player_base[0]+5) and e.y in range(player_base[1]-5, player_base[1]+5):
                player_HP -= e.attack
                e.hp = 0

            if e.hp <= 0:
                score += 10
                if e.__class__.__name__ == "Generator":
                    #print("Enemy Pump destroyed")
                    friendly.append(Units.Generator([e.x, e.y], Scalars))
                else:
                    inkblots.append([(e.x, e.y), 255, 1000, random.choice(range(0, 360, 45))])
                try:
                    enemy.remove(e)
                except Exception as e:
                    print(e)
                continue
            else:
                e.move(dt, enemy, boundaries, Scalars)
                gameDisplay.blit(e.Asset, (e.x, e.y))
            if e.__class__.__name__ == "Generator":
                p_e_controled += 1
            if e.__class__.__name__ == "Summoner":
                if not hasattr(e, "spawn_timer"):
                    e.spawn_timer = 0  # Initialize spawn timer if not already set
                e.spawn_timer += dt  # Increment spawn timer by delta time
                if e.spawn_timer >= 1:  # Check if 1 second has passed
                    enemy.append(Units.Minion([e.x, e.y], Scalars, e))
                    enemy[-1].target = e.target
                    e.spawn_timer = 0  # Reset the spawn timer
            if e.__class__.__name__ == "Minion":
                e.lifetime += dt
                if e.lifetime >= 10:
                    inkblots.append([(e.x, e.y), 255, 1000, random.choice(range(0, 360, 45))])
                    try:
                        enemy.remove(e)
                    except Exception as e:
                        print(e)
                    continue

        # Mana Regen, for both player and Enchanter
        P_ratio = {0: 1, 1: 3, 2: 4, 3: 4, 4: 6}
        
        divisor = P_ratio[p_controled]
        player_mana_timer += dt
        if player_mana_timer >= (5/divisor):
            player_mana = min(player_mana + 1, 9)
            player_mana_timer = 0
        enchanter_mana_timer += dt
        divisor_text = SpeechFont.render(f"Divisor: {str(divisor)}", True, (255, 255, 255))
        divisor = P_ratio[p_e_controled]
        if enchanter_mana_timer >= (5/divisor):
            Enchanter_mana = min(Enchanter_mana + 1, 9)
            enchanter_mana_timer = 0

        if Ai == 'madman':
            #Yes, the madman Cheats, Hes mad, he doesnt care about the rules
            Enchanter_mana = 9
        # Summoning enemy units
        summon_timer += dt
        if summon_timer >= 5:
            summon = Enemy_ai.summon(Enchanter_mana, p_e_controled, enemy)
            #print(summon)
            spawn_position = enemy_base  # Dynamic spawn position for enemy units
            if summon == 0:
                enemy.append(Units.Footman(spawn_position, Scalars))
                Enchanter_mana -= 1
                last = [enemy[-1]]
                Enemy_ai.target(last, friendly, Pumps, player_HP, Enchanter_HP, player_base, enemy_base)
            elif summon == 1:
                enemy.append(Units.Horse(spawn_position, Scalars))
                Enchanter_mana -= 3
                last = [enemy[-1]]
                Enemy_ai.target(last, friendly, Pumps, player_HP, Enchanter_HP, player_base, enemy_base)
            elif summon == 2:
                enemy.append(Units.Soldier(spawn_position, Scalars))
                Enchanter_mana -= 3
                last = [enemy[-1]]
                Enemy_ai.target(last, friendly, Pumps, player_HP, Enchanter_HP, player_base, enemy_base)
            elif summon == 3:
                enemy.append(Units.Summoner(spawn_position, Scalars))
                Enchanter_mana -= 6
                last = [enemy[-1]]
                Enemy_ai.target(last, friendly, Pumps, player_HP, Enchanter_HP, player_base, enemy_base)
            elif summon == 4:
                enemy.append(Units.Runner(spawn_position, Scalars))
                Enchanter_mana -= 8
                last = [enemy[-1]]
                Enemy_ai.target(last, friendly, Pumps, player_HP, Enchanter_HP, player_base, enemy_base)
            elif summon == 5:
                enemy.append(Units.Tank(spawn_position, Scalars))
                Enchanter_mana -= 8
                last = [enemy[-1]]
                Enemy_ai.target(last, friendly, Pumps, player_HP, Enchanter_HP, player_base, enemy_base)
            else:
                #print("Summon failed")
                pass

        # Enchanter targeting
        targeting_timer += dt
        if targeting_timer >= 10:  # Update targeting every 10 seconds
            Enemy_ai.target(enemy, friendly, Pumps, player_HP, Enchanter_HP, player_base, enemy_base)
            targeting_timer = 0

        if player_HP <= 0:
            running = False
            
        if Enchanter_HP <= 0:
            running = False
            Won = True


        for s in selected:
            gameDisplay.blit(selection_icon, (s.x, s.y))

        # player mana display
        manaCounter = mana_images[player_mana]
        gameDisplay.blit(manaCounter, manaCounter_pos)

        # Hp display
        if hp_cache != (player_HP, Enchanter_HP):
            hp_text = HPFont.render(f"{player_HP}:{Enchanter_HP}", True, (255, 150, 255))
            hp_cache = (player_HP, Enchanter_HP)
            if RPC_on:
                RPC.update(
                pid=pid,
                state="Inking and Incanting",
                details=f"{player_HP}:{Enchanter_HP}",
                start=epoch, 
                large_image="icon",
                large_text="The Enchanters Book awaits....")
        gameDisplay.blit(hp_text, HP_pos)

        gameDisplay.blit(summon_UI, summon_UI_pos)
        gameDisplay.blit(Footman_cost, Footman_cost_pos)
        gameDisplay.blit(Horse_cost, Horse_cost_pos)
        gameDisplay.blit(Soldier_cost, Soldier_cost_pos)
        gameDisplay.blit(Summoner_cost, Summoner_cost_pos)
        gameDisplay.blit(Runner_cost, Runner_cost_pos)
        gameDisplay.blit(Tank_cost, Tank_cost_pos)
        
        # cursor display
        gameDisplay.blit(cursor_img, pygame.mouse.get_pos())
        
        
        
        # Display FPS counter
        fps = int(clock.get_fps())
        if show_fps_debug:
            fps_text = SpeechFont.render(f"FPS: {fps}", True, (255, 255, 255))
            gameDisplay.blit(fps_text, (int(screen_width * 0), int(screen_height * 0.3)))  # Dynamic position for FPS
            dt_text = SpeechFont.render(f"dt: {round(dt * 1000, 3)}ms", True, (255, 255, 255))
            gameDisplay.blit(dt_text, (int(screen_width * 0), int(screen_height * 0.35)))  # Dynamic position for delta time
        if show_mana_debug:
            mana_text = SpeechFont.render(f"Mana Timer: {round(player_mana_timer, 3)}", True, (255, 255, 255))
            gameDisplay.blit(mana_text, (int(screen_width * 0), int(screen_height * 0.4)))  # Dynamic position for mana timer
            gameDisplay.blit(divisor_text, (int(screen_width * 0), int(screen_height * 0.45)))  # Dynamic position for divisor
            mana_text = SpeechFont.render(f"Enchanter Mana Timer: {round(enchanter_mana_timer, 3)}", True, (255, 255, 255))
            gameDisplay.blit(mana_text, (int(screen_width * 0), int(screen_height * 0.5)))  # Dynamic position for enchanter mana timer
            Enchanter_mana_text = SpeechFont.render(f"Enchanter Mana: {Enchanter_mana}", True, (255, 255, 255))
            gameDisplay.blit(Enchanter_mana_text, (int(screen_width * 0), int(screen_height * 0.55)))  # Dynamic position for enchanter mana
        if show_battle_debug:
            pygame.draw.rect(gameDisplay, (255, 0, 0), BattleGround_debug_rect, 2)  # Red rectangle with a thickness of 2\
        

        # Debug rect!!!
        # Drect = pygame.Rect(0, 0, screen_width, screen_height)
        # pygame.draw.rect(gameDisplay, (255, 0, 0), Drect, 1)


        pygame.display.flip()
        clock.tick(100)
        gameDisplay.fill((0, 0, 0))

    
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
                Second1Loc = Second_1.get_rect(center=(screen_width // 2, screen_height * 0.5))
                Second2Loc = Second_2.get_rect(center=(screen_width // 2, screen_height * 0.6))
                save = SaveUpdater.decode_save_file()
                save['enchanter'] = True
                SaveUpdater.encode_save_file(save)
                messages = [(Second_1, Second1Loc), (Second_2, Second2Loc)]
            else:
                First_Win = SpeechFont.render('You never learn', True, (255, 150, 255))
                FirstWLoc = First_Win.get_rect(center=(screen_width // 2, screen_height * 0.4))
                Enchanter_HP = 100
                player_HP = 1
                messages = [(First_Win, FirstWLoc)]
        elif Ai == 'monarch':
            M_win = SpeechFont.render('Oh quite a game, Shall we play again', True, (80, 200, 120))
            mWLoc = M_win.get_rect(center=(screen_width // 2, screen_height * 0.5))
            save = SaveUpdater.decode_save_file()
            save['monarch'] = True
            SaveUpdater.encode_save_file(save)
            messages = [(M_win, mWLoc)]
        elif Ai == 'madman':
            mad_1 = SpeechFont.render('This isnt a Prison, this is a Machine.', True, (255, 0, 0))
            mad_2 = SpeechFont.render('ISNT THAT RIGHT ' + Madman.scare(), True, (255, 0, 0))
            mad1loc = mad_1.get_rect(center=(screen_width // 2, screen_height * 0.4))
            mad2loc = mad_2.get_rect(center=(screen_width // 2, screen_height * 0.5))
            save = SaveUpdater.decode_save_file()
            save['madman'] = True
            SaveUpdater.encode_save_file(save)
            messages = [(mad_1, mad1loc), (mad_2, mad2loc)]
        else:
            No_win = SpeechFont.render('Error: No AI selected', True, (255, 150, 255))
            No_wLoc = No_win.get_rect(center=(screen_width // 2, screen_height * 0.5))
            messages = [(No_win, No_wLoc)]
    else:
        if Ai == 'enchanter':
            Loss_1 = SpeechFont.render('All you need to do is learn', True, (255, 150, 255))
            Loss_2 = SpeechFont.render('Again', True, (255, 150, 255))
            l1Loc = Loss_1.get_rect(center=(screen_width // 2, screen_height * 0.5))
            l2Loc = Loss_2.get_rect(center=(screen_width // 2, screen_height * 0.6))
            messages = [(Loss_1, l1Loc), (Loss_2, l2Loc)]
        elif Ai == 'monarch':
            messages = []
        elif Ai == 'madman':
            mad_1 = SpeechFont.render('This isnt a Prison, this is a Machine', True, (255, 0, 0))
            mad_2 = SpeechFont.render('ISNT THAT RIGHT ' + Madman.scare(), True, (255, 0, 0))
            mad1loc = mad_1.get_rect(center=(screen_width // 2, screen_height * 0.4))
            mad2loc = mad_2.get_rect(center=(screen_width // 2, screen_height * 0.5))
            messages = [(mad_1, mad1loc), (mad_2, mad2loc)]
        else:
            No_loss = SpeechFont.render('Error: No AI selected', True, (255, 150, 255))
            no_lLoc = No_loss.get_rect(center=(screen_width // 2, screen_height * 0.5))
            messages = [(No_loss, no_lLoc)]

    # Display end game messages
    

    if Ai == 'enchanter' and not SaveUpdater.decode_save_file()["beat_enchanter_first_time"] and not Won:
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
        friendly = []
        # Spawn a bunch of enemy troops around the player spawn
        for _ in range(10):
            enemy.append(Units.Footman([
                random.randint((player_base[0] - int(screen_width * 0.02)), (player_base[0] + int(screen_width * 0.02))),
                random.randint((player_base[1] - int(screen_height * 0.1)), (player_base[1] - int(screen_height * 0.15))),
                Scalars
            ]))
            enemy.append(Units.Horse([
                random.randint((player_base[0] - int(screen_width * 0.02)), (player_base[0] + int(screen_width * 0.02))),
                random.randint((player_base[1] - int(screen_height * 0.1)), (player_base[1] - int(screen_height * 0.15))),
                Scalars
            ]))
            enemy.append(Units.Soldier([
                random.randint((player_base[0] - int(screen_width * 0.02)), (player_base[0] + int(screen_width * 0.02))),
                random.randint((player_base[1] - int(screen_height * 0.1)), (player_base[1] - int(screen_height * 0.15))),
                Scalars
            ]))
            enemy.append(Units.Runner([
                random.randint((player_base[0] - int(screen_width * 0.02)), (player_base[0] + int(screen_width * 0.02))),
                random.randint((player_base[1] - int(screen_height * 0.1)), (player_base[1] - int(screen_height * 0.15))),
                Scalars
            ]))
            for e in enemy:
                e.target = player_base

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    print("Game exiting")
                    running = False
                    pygame.quit()
                    return False

            gameDisplay.fill((0, 0, 0))
            gameDisplay.blit(BattleGround, BattleGround_pos)

            for e in enemy:
                e.move(dt, enemy, boundaries, Scalars)
                gameDisplay.blit(e.Asset, (e.x, e.y))
                if (
                    player_base[0] - int(screen_width * 0.005) <= e.x <= player_base[0] + int(screen_width * 0.005)
                    and player_base[1] - int(screen_height * 0.005) <= e.y <= player_base[1] + int(screen_height * 0.005)
                ):
                    player_HP -= e.attack
                    e.hp = 0
                if e.hp <= 0:
                    try:
                        enemy.remove(e)
                    except Exception as e:
                        print(e)
                    continue

            if player_HP <= 0:
                running = False

            # Display player and enchanter HP
            # Hp display
            if hp_cache != (player_HP, Enchanter_HP):
                hp_text = HPFont.render(f"{player_HP}:{Enchanter_HP}", True, (255, 150, 255))
                hp_cache = (player_HP, Enchanter_HP)
                if RPC_on:
                    RPC.update(
                    pid=pid,
                    state="Losing to the Enchanter",
                    details=f"They never learn",
                    start=epoch, 
                    large_image="icon",
                    large_text="The Enchanters Book awaits....")
            gameDisplay.blit(hp_text, HP_pos)
            # Display cursor
            gameDisplay.blit(cursor_img, pygame.mouse.get_pos())

            pygame.display.flip()
            clock.tick(100)

        Loss_1 = SpeechFont.render('All you need to do is learn…', True, (255, 150, 255))
        Loss_2 = SpeechFont.render('Again.', True, (255, 150, 255))
        l1Loc = Loss_1.get_rect(center=(screen_width // 2, screen_height * 0.4))
        l2Loc = Loss_2.get_rect(center=(screen_width // 2, screen_height * 0.5))
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

    elif Ai == 'monarch' and not Won:
        # Monarch crashes the game
        Crash_1 = SpeechFont.render('You bore me, Guards!', True, (255, 150, 255))
        crash_loc = Crash_1.get_rect(center=(screen_width // 2, screen_height * 0.5))
        gameDisplay.fill((0, 0, 0))
        gameDisplay.blit(Crash_1, crash_loc)
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
    play_again_font = pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), int(screen_height * 0.05))  # Dynamic font size
    play_again_text = play_again_font.render('Do you want to play again? (Y/N)', True, (255, 255, 255))
    score_text = play_again_font.render(str(round(score)), True, (255, 255, 255))

    # Center the text dynamically
    play_again_text_rect = play_again_text.get_rect(center=(screen_width // 2, screen_height * 0.6))
    score_text_rect = score_text.get_rect(center=(screen_width // 2, screen_height * 0.5))

    gameDisplay.fill((0, 0, 0))
    gameDisplay.blit(play_again_text, play_again_text_rect)
    gameDisplay.blit(score_text, score_text_rect)
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

