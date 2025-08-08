import pygame
import random
import time
import math
from pygame.locals import *
import os
import requests


def screenshot(screen):
    """
    Take a screenshot of the current screen and save it to the Screenshots directory outside of the base directory.
    """
    # Ensure the Screenshots directory exists
    # Navigate one level up from the current directory
    base_dir = os.path.dirname(os.getcwd())
    screenshots_dir = os.path.join(base_dir, 'Screenshots')

    if not os.path.exists(screenshots_dir):
        # Create the directory if it doesn't exist
        os.makedirs(screenshots_dir)

    screenshot_path = os.path.join(
        screenshots_dir, f'screenshot_{int(time.time())}.png')
    pygame.image.save(screen, screenshot_path)
    print(f"Screenshot saved to {screenshot_path}")


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
        pygame.draw.rect(surface, (0, 0, 0), line_surface.get_rect(
            topleft=(rect.left, y_offset)))  # Draw a Black rectangle around the text
        surface.blit(line_surface, (rect.left, y_offset))
        y_offset += font.size(line)[1] + line_spacing


def BatStart(RoomID:int, PlayerID:int, display:pygame.Surface, RPC_on: bool, RPC: object, pid, Units: object, SaveUpdater: object, Scalars: list, Screensize: list, state:dict) -> bool:

    if len(Scalars) != 2:
        raise ValueError("Scalars Argument must contain two elements.")
    if len(Screensize) != 2:
        raise ValueError("Screensize Argument must contain two elements.")
    
    DEFAULT_ADDR = 'http://127.0.0.1'
    DEFAULT_PORT = '54321'

    # Get screen dimensions dynamically
    screen_width, screen_height = Screensize[0], Screensize[1]
    scale_x, scale_y = Scalars[0], Scalars[1]
    # print()
    Targ_blinky_timer = 0

    # global defaults
    start_time = time.time()
    gameDisplay = display
    BattleGround = pygame.image.load(os.path.join(
        "Assets", "Sprites", "pixil-frame-0.png"))
    inkblot = pygame.image.load(os.path.join(
        "Assets", "Sprites", "InkBlot.png")).convert_alpha()
    clock = pygame.time.Clock()
    gameDisplay.fill((0, 0, 0))
    pygame.mixer.music.load(os.path.join(
        "Assets", "Music", "DungeonSynth2Hr.mp3"))
    pygame.mixer.music.play(loops=-1)
    pygame.mixer.music.set_volume(1)

    # Scale assets dynamically

    BattleGround = pygame.transform.smoothscale(
        BattleGround,  # 1000x1000 Asset
        # Height should be scaled to max y of screen, which is the same scalar as width
        (int(BattleGround.get_width() * (screen_height / 1000)),
         int(BattleGround.get_height() * (screen_height / 1000)))
    )
    inkblot = pygame.transform.scale(
        inkblot,
        (int(inkblot.get_width() * scale_y), int(inkblot.get_height() * scale_y))
    )

    # Scale fonts dynamically
    HPFont = pygame.font.Font(os.path.join(
        "Assets", "Fonts", "Speech.ttf"), int(screen_height * 0.1))
    SpeechFont = pygame.font.Font(os.path.join(
        "Assets", "Fonts", "Speech.ttf"), int(scale_y * 40))
    pause = SpeechFont.render('Paused', True, (255, 255, 255))

    # Scale UI elements dynamically
    summon_UI = pygame.image.load(os.path.join(
        "Assets", "Sprites", "Selecetion grid.jpg"))
    summon_UI = pygame.transform.scale(
        summon_UI,
        (int(summon_UI.get_width() * scale_y),
         int(summon_UI.get_height() * scale_y))
    )

    manaCounter = pygame.image.load(os.path.join(
        "Assets", "Sprites", "Mana_counter", "5.png"))
    manaCounter = pygame.transform.scale(
        manaCounter,
        [int(manaCounter.get_width() * scale_y),
         int(manaCounter.get_height() * scale_y)]
    )

    # Adjust cursor size dynamically
    cursor_img = pygame.image.load(
        os.path.join("Assets", "Sprites", "Mouse.png"))
    cursor_img = pygame.transform.scale(
        cursor_img,
        [int(cursor_img.get_width() * scale_y),
         int(cursor_img.get_height() * scale_y)]
    )

    # Dynamic positioning
    BattleGround_pos_rect = BattleGround.get_rect(
        center=(screen_width // 2, screen_height // 2))
    BattleGround_pos = BattleGround_pos_rect.topleft
    summon_UI_pos_rect = summon_UI.get_rect(
        center=(screen_width - (summon_UI.get_width() // 2), screen_height // 2))
    summon_UI_pos = summon_UI_pos_rect.topleft
    manaCounter_pos_rect = manaCounter.get_rect(center=(
        (manaCounter.get_width() // 2), screen_height - (manaCounter.get_height() // 2)))
    manaCounter_pos = manaCounter_pos_rect.topleft
    HP_pos = (screen_width * 0, screen_height * 0)

    # Adjust tutorial text positions dynamically

    # Adjust other hardcoded positions dynamically
    Rloc = (screen_width * 0.4, screen_height * 0.9)
    Bloc = (screen_width * 0.45, screen_height * 0.9)

    Footman_cost = SpeechFont.render(
        str(Units.Footman.cost), True, (255, 150, 255))
    Horse_cost = SpeechFont.render(str(Units.Horse.cost), True, (255, 150, 255))
    Soldier_cost = SpeechFont.render(
        str(Units.Soldier.cost), True, (255, 150, 255))
    Summoner_cost = SpeechFont.render(
        str(Units.Summoner.cost), True, (255, 150, 255))
    Runner_cost = SpeechFont.render(str(Units.Runner.cost), True, (255, 150, 255))
    Tank_cost = SpeechFont.render(str(Units.Tank.cost), True, (255, 150, 255))
    player_HP = 20
    Enchanter_HP = 20

    # Adjust costs dynamically
    # 144px distance between each cost * scale

    Footman_cost_pos = (
        summon_UI_pos_rect.centerx - Footman_cost.get_width() // 2,
        summon_UI_pos_rect.topleft[1] + (1 * ((144 * scale_y)//2))
    )
    Horse_cost_pos = (
        summon_UI_pos_rect.centerx - Horse_cost.get_width() // 2,
        summon_UI_pos_rect.topleft[1] + (3 * ((144 * scale_y)//2))
    )
    Soldier_cost_pos = (
        summon_UI_pos_rect.centerx - Soldier_cost.get_width() // 2,
        summon_UI_pos_rect.topleft[1] + (5 * ((144 * scale_y)//2))
    )
    Summoner_cost_pos = (
        summon_UI_pos_rect.centerx - Summoner_cost.get_width() // 2,
        summon_UI_pos_rect.topleft[1] + (7 * ((144 * scale_y)//2))
    )
    Runner_cost_pos = (
        summon_UI_pos_rect.centerx - Runner_cost.get_width() // 2,
        summon_UI_pos_rect.topleft[1] + (9 * ((144 * scale_y)//2))
    )
    Tank_cost_pos = (
        summon_UI_pos_rect.centerx - Tank_cost.get_width() // 2,
        summon_UI_pos_rect.topleft[1] + (11 * ((144 * scale_y)//2))
    )

    # Adjust endgame message positions dynamically
    endgame_message_pos = (screen_width * 0.4, screen_height * 0.9)

    X_MIN = int(BattleGround_pos[0] + (BattleGround.get_width() * 0.124))
    X_MAX = int(BattleGround_pos[0] + (BattleGround.get_width() * 0.865))
    Y_MIN = int(BattleGround_pos[1] + (BattleGround.get_height() * 0.19))
    Y_MAX = int(BattleGround_pos[1] + (BattleGround.get_height() * 0.89))

    identifyer = pygame.image.load(os.path.join(
        "Assets", "Sprites", "Identifier.png"))
    Friendly_identifyer = pygame.transform.scale(
        identifyer, (identifyer.get_width() * scale_y, identifyer.get_height() * scale_y))
    
    Enemy_identifyer = Friendly_identifyer.copy()
    Friendly_identifyer.fill((100, 100, 255, 255),
                             special_flags=BLEND_RGBA_MIN)
    
    Enemy_identifyer.fill((255, 100, 100, 255),
                             special_flags=BLEND_RGBA_MIN)


    BattleGround_width = X_MAX - X_MIN
    BattleGround_height = Y_MAX - Y_MIN


    BattleGround_debug_rect = pygame.Rect(
        X_MIN, Y_MIN, BattleGround_width, BattleGround_height)
    player_base = (int(X_MIN + (BattleGround_width // 2)),
                   int(Y_MAX - (BattleGround_height * 0.1)))
    enemy_base = (int(X_MIN + (BattleGround_width // 2)),
                  int(Y_MIN + (BattleGround_height * 0.1)))
    # Adjust pump positions dynamically to be centered and evenly spaced
    Pumps = [
        Units.Generator((X_MIN + (BattleGround_width * 0.20),
                        Y_MIN + (BattleGround_height * 0.20)), Scalars),
        Units.Generator((X_MIN + (BattleGround_width * 0.70),
                        Y_MIN + (BattleGround_height * 0.20)), Scalars),
        Units.Generator((X_MIN + (BattleGround_width * 0.20),
                        Y_MIN + (BattleGround_height * 0.70)), Scalars),
        Units.Generator((X_MIN + (BattleGround_width * 0.70),
                        Y_MIN + (BattleGround_height * 0.70)), Scalars)
    ]

    # AI bases
    bases_dir = os.path.join("Assets", "AI_Bases", "Opponent")
    base_images = []
    count = 0
    for filename in os.listdir(bases_dir):
        if filename.lower().endswith(".png"):
            count += 1
    for i in range(count):
        base_images.append(pygame.image.load(os.path.join(
            bases_dir, "Opponent"+str(i) + ".png")))
        base_images[i] = pygame.transform.scale(
                base_images[i],
                [int(base_images[i].get_width() * scale_y),
                 int(base_images[i].get_height() * scale_y)])
    base_fps = 1

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
    Hp = HPFont.render(str(player_HP) + ":" +
                       str(Enchanter_HP), False, (255, 150, 255))
    
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
        Hp.set_alpha(a)
        gameDisplay.blit(Hp, HP_pos)
        pygame.display.flip()

    # Loading Vars
    selection_icon = pygame.image.load(os.path.join(
        "Assets", "Sprites", "unit_sprites", "Selected.png"))
    selection_icon = pygame.transform.scale(
        selection_icon,
        (int(selection_icon.get_width() * scale_y),
         int(selection_icon.get_height() * scale_y))
    )

    pygame.mouse.set_visible(False)
    Selecting = False
    selected = []
    inkblots = []
    hp_cache = (player_HP, Enchanter_HP)
    hp_text = HPFont.render(
        f"{player_HP}:{Enchanter_HP}", True, (255, 150, 255))
    mouseinkblots = []

    pygame.event.clear()

    player_mana = state['Player1_mana' if PlayerID == state['player1_ID'] else 'Player2_mana']
    Enchanter_mana = state['Player2_mana' if PlayerID == state['player1_ID'] else 'Player1_mana']
    player_HP = state['Player1_HP' if PlayerID == state['player1_ID'] else 'Player2_HP']
    Enchanter_HP = state['Player2_HP' if PlayerID == state['player1_ID'] else 'Player1_HP']
    last_time = state['last_update']
    player_mana_timer = state['Player1_mana_timer' if PlayerID == state['player1_ID'] else 'Player2_mana_timer']
    enchanter_mana_timer = state['Player2_mana_timer' if PlayerID == state['player1_ID'] else 'Player1_mana_timer']
    friendly = state['Player1_Units'] if PlayerID == state['player1_ID'] else state['Player2_Units']
    enemy = state['Player2_Units'] if PlayerID == state['player1_ID'] else state['Player1_Units']
    Pumps = state['Pumps']
    friendly = [Units.Footman([f['x'], f['y']], Scalars) if f['Name'] == 'Footman'
            else Units.Horse([f['x'], f['y']], Scalars) if f['Name'] == 'Horse'
            else Units.Soldier([f['x'], f['y']], Scalars) if f['Name'] == 'Soldier'
            else Units.Summoner([f['x'], f['y']], Scalars) if f['Name'] == 'Summoner'
            else Units.Runner([f['x'], f['y']], Scalars) if f['Name'] == 'Runner'
            else Units.Tank([f['x'], f['y']], Scalars) if f['Name'] == 'Tank'
            else Units.Generator([f['x'], f['y']], Scalars) if f['Name'] == 'Generator'
            else Units.Minion([f['x'], f['y']], Scalars) if f['Name'] == 'Minion'
            else None
            for f in friendly]
    enemy = [Units.Footman([e['x'], e['y']], Scalars) if e['Name'] == 'Footman'
                else Units.Horse([e['x'], e['y']], Scalars) if e['Name'] == 'Horse'
                else Units.Soldier([e['x'], e['y']], Scalars) if e['Name'] == 'Soldier'
                else Units.Summoner([e['x'], e['y']], Scalars) if e['Name'] == 'Summoner'
                else Units.Runner([e['x'], e['y']], Scalars) if e['Name'] == 'Runner'
                else Units.Tank([e['x'], e['y']], Scalars) if e['Name'] == 'Tank'
                else Units.Generator([e['x'], e['y']], Scalars) if e['Name'] == 'Generator'
                else Units.Minion([e['x'], e['y']], Scalars) if e['Name'] == 'Minion'
                else None
                for e in enemy]
    Pumps = [Units.Generator(
            (p['x'], p['y']), Scalars)
            for p in Pumps]
    SERVER_X_MIN = 124
    SERVER_Y_MIN = 190
    ServerBattlefield_size = 741, 700
    if PlayerID == state['player2_ID']:
        for f in friendly:
            f.Unpackage(state['Player2_Units'][friendly.index(f)])
            flipped_x = ServerBattlefield_size[0] - f.x
            flipped_y = ServerBattlefield_size[1] - f.y

            f.x = ((flipped_x - SERVER_Y_MIN) / ServerBattlefield_size[0]) * (X_MAX - X_MIN) + X_MIN
            f.y = ((flipped_y - SERVER_X_MIN) / ServerBattlefield_size[1]) * (Y_MAX - Y_MIN) + Y_MIN

            flipped_target_x = ServerBattlefield_size[0] - f.target[0]
            flipped_target_y = ServerBattlefield_size[1] - f.target[1]
            f.target = ((flipped_target_x - SERVER_X_MIN) / ServerBattlefield_size[0]) * (X_MAX - X_MIN) + X_MIN, ((flipped_target_y - SERVER_Y_MIN) / ServerBattlefield_size[1]) * (Y_MAX - Y_MIN) + Y_MIN


        for e in enemy:
            e.Unpackage(state['Player1_Units'][enemy.index(e)])
            flipped_x = ServerBattlefield_size[0] - e.x
            flipped_y = ServerBattlefield_size[1] - e.y

            e.x = ((flipped_x - SERVER_Y_MIN) / ServerBattlefield_size[0]) * (X_MAX - X_MIN) + X_MIN
            e.y = ((flipped_y - SERVER_X_MIN) / ServerBattlefield_size[1]) * (Y_MAX - Y_MIN) + Y_MIN

            flipped_target_x = ServerBattlefield_size[0] - e.target[0]
            flipped_target_y = ServerBattlefield_size[1] - e.target[1]

            e.target = ((flipped_target_x - SERVER_X_MIN) / ServerBattlefield_size[0]) * (X_MAX - X_MIN) + X_MIN, ((flipped_target_y - SERVER_Y_MIN) / ServerBattlefield_size[1]) * (Y_MAX - Y_MIN) + Y_MIN
        for p in Pumps:
            p.Unpackage(state['Pumps'][Pumps.index(p)])
            flipped_x = ServerBattlefield_size[0] - p.x
            flipped_y = ServerBattlefield_size[1] - p.y

            p.x = ((flipped_x - SERVER_X_MIN) / ServerBattlefield_size[0]) * (X_MAX - X_MIN) + X_MIN
            p.y = ((flipped_y - SERVER_Y_MIN)/ ServerBattlefield_size[1]) * (Y_MAX - Y_MIN) + Y_MIN
    else:
        for f in friendly:
            f.Unpackage(state['Player1_Units'][friendly.index(f)])
            f.x = ((f.x - SERVER_X_MIN) / ServerBattlefield_size[0]) * (X_MAX - X_MIN) + X_MIN
            f.y = ((f.y - SERVER_Y_MIN) / ServerBattlefield_size[1]) * (Y_MAX - Y_MIN) + Y_MIN
            f.target = ((f.target[0] - SERVER_X_MIN) / ServerBattlefield_size[0]) * (X_MAX - X_MIN) + X_MIN, ((f.target[1] - SERVER_Y_MIN) / ServerBattlefield_size[1]) * (Y_MAX - Y_MIN) + Y_MIN
        for e in enemy:
            e.Unpackage(state['Player2_Units'][enemy.index(e)])
            e.x = ((e.x - SERVER_X_MIN) / ServerBattlefield_size[0]) * (X_MAX - X_MIN) + X_MIN
            e.y = ((e.y - SERVER_Y_MIN) / ServerBattlefield_size[1]) * (Y_MAX - Y_MIN) + Y_MIN
            e.target = ((e.target[0] - SERVER_X_MIN) / ServerBattlefield_size[0]) * (X_MAX - X_MIN) + X_MIN, ((e.target[1] - SERVER_Y_MIN) / ServerBattlefield_size[1]) * (Y_MAX - Y_MIN) + Y_MIN
        for p in Pumps:
            p.Unpackage(state['Pumps'][Pumps.index(p)])
            p.x = ((p.x - SERVER_X_MIN) / ServerBattlefield_size[0]) * (X_MAX - X_MIN) + X_MIN
            p.y = ((p.y - SERVER_Y_MIN) / ServerBattlefield_size[1]) * (Y_MAX - Y_MIN) + Y_MIN
    hp_cache = (player_HP, Enchanter_HP)
    hp_text = HPFont.render(
        f"{player_HP}:{Enchanter_HP}", True, (255, 150, 255))
    
    # flip units if player is player 2


    # Initialize variables for delta time
    show_fps_debug = False
    show_mana_debug = False
    show_battle_debug = False
    Targ_obj_cache = None
    Targ_obj = None
    mana_images = []
    base_timer = 0
    base_img = 0
    for i in range(10):
        mana_images.append(pygame.image.load(os.path.join(
            "Assets", "Sprites", "Mana_counter", str(i) + ".png")))
        mana_images[i] = pygame.transform.scale(
            mana_images[i],
            [int(mana_images[i].get_width() * scale_y),
             int(mana_images[i].get_height() * scale_y)]
        )
    dt = 0
    # Main game loop
    running = True
    while running:
        for p  in Pumps:
            print(p.x, p.y)
            print(p)
       # update the game state
        if dt > 0.2:
            state = requests.post(f"{DEFAULT_ADDR}:{DEFAULT_PORT}/get-state", json={'RoomID':RoomID}).json()['State']
        player_mana = state['Player1_mana' if PlayerID == state['player1_ID'] else 'Player2_mana']
        Enchanter_mana = state['Player2_mana' if PlayerID == state['player1_ID'] else 'Player1_mana']
        player_HP = state['Player1_HP' if PlayerID == state['player1_ID'] else 'Player2_HP']
        Enchanter_HP = state['Player2_HP' if PlayerID == state['player1_ID'] else 'Player1_HP']
        last_time = state['last_update']
        player_mana_timer = state['Player1_mana_timer' if PlayerID == state['player1_ID'] else 'Player2_mana_timer']
        enchanter_mana_timer = state['Player2_mana_timer' if PlayerID == state['player1_ID'] else 'Player1_mana_timer']
        friendly = state['Player1_Units'] if PlayerID == state['player1_ID'] else state['Player2_Units']
        enemy = state['Player2_Units'] if PlayerID == state['player1_ID'] else state['Player1_Units']
        Pumps = state['Pumps']
        friendly = [Units.Footman([f['x'], f['y']], Scalars) if f['Name'] == 'Footman'
                    else Units.Horse([f['x'], f['y']], Scalars) if f['Name'] == 'Horse'
                    else Units.Soldier([f['x'], f['y']], Scalars) if f['Name'] == 'Soldier'
                    else Units.Summoner([f['x'], f['y']], Scalars) if f['Name'] == 'Summoner'
                    else Units.Runner([f['x'], f['y']], Scalars) if f['Name'] == 'Runner'
                    else Units.Tank([f['x'], f['y']], Scalars) if f['Name'] == 'Tank'
                    else Units.Generator([f['x'], f['y']], Scalars) if f['Name'] == 'Generator'
                    else Units.Minion([f['x'], f['y']], Scalars) if f['Name'] == 'Minion'
                    else None
                    for f in friendly]
        enemy = [Units.Footman([e['x'], e['y']], Scalars) if e['Name'] == 'Footman'
                    else Units.Horse([e['x'], e['y']], Scalars) if e['Name'] == 'Horse'
                    else Units.Soldier([e['x'], e['y']], Scalars) if e['Name'] == 'Soldier'
                    else Units.Summoner([e['x'], e['y']], Scalars) if e['Name'] == 'Summoner'
                    else Units.Runner([e['x'], e['y']], Scalars) if e['Name'] == 'Runner'
                    else Units.Tank([e['x'], e['y']], Scalars) if e['Name'] == 'Tank'
                    else Units.Generator([e['x'], e['y']], Scalars) if e['Name'] == 'Generator'
                    else Units.Minion([e['x'], e['y']], Scalars) if e['Name'] == 'Minion'
                    else None
                    for e in enemy]
        Pumps = [Units.Generator(
                (p['x'], p['y']), Scalars)
                for p in Pumps]
        SERVER_X_MIN = 124
        SERVER_Y_MIN = 190
        ServerBattlefield_size = 741, 700
        if PlayerID == state['player2_ID']:
            for f in friendly:
                f.Unpackage(state['Player2_Units'][friendly.index(f)])
                flipped_x = ServerBattlefield_size[0] - f.x
                flipped_y = ServerBattlefield_size[1] - f.y

                f.x = ((flipped_x - SERVER_Y_MIN) / ServerBattlefield_size[0]) * (X_MAX - X_MIN) + X_MIN
                f.y = ((flipped_y - SERVER_X_MIN) / ServerBattlefield_size[1]) * (Y_MAX - Y_MIN) + Y_MIN

                flipped_target_x = ServerBattlefield_size[0] - f.target[0]
                flipped_target_y = ServerBattlefield_size[1] - f.target[1]
                f.target = ((flipped_target_x - SERVER_X_MIN) / ServerBattlefield_size[0]) * (X_MAX - X_MIN) + X_MIN, ((flipped_target_y - SERVER_Y_MIN) / ServerBattlefield_size[1]) * (Y_MAX - Y_MIN) + Y_MIN


            for e in enemy:
                e.Unpackage(state['Player1_Units'][enemy.index(e)])
                flipped_x = ServerBattlefield_size[0] - e.x
                flipped_y = ServerBattlefield_size[1] - e.y

                e.x = ((flipped_x - SERVER_Y_MIN) / ServerBattlefield_size[0]) * (X_MAX - X_MIN) + X_MIN
                e.y = ((flipped_y - SERVER_X_MIN) / ServerBattlefield_size[1]) * (Y_MAX - Y_MIN) + Y_MIN

                flipped_target_x = ServerBattlefield_size[0] - e.target[0]
                flipped_target_y = ServerBattlefield_size[1] - e.target[1]

                e.target = ((flipped_target_x - SERVER_X_MIN) / ServerBattlefield_size[0]) * (X_MAX - X_MIN) + X_MIN, ((flipped_target_y - SERVER_Y_MIN) / ServerBattlefield_size[1]) * (Y_MAX - Y_MIN) + Y_MIN
            for p in Pumps:
                p.Unpackage(state['Pumps'][Pumps.index(p)])
                flipped_x = ServerBattlefield_size[0] - p.x
                flipped_y = ServerBattlefield_size[1] - p.y

                p.x = ((flipped_x - SERVER_X_MIN) / ServerBattlefield_size[0]) * (X_MAX - X_MIN) + X_MIN
                p.y = ((flipped_y - SERVER_Y_MIN)/ ServerBattlefield_size[1]) * (Y_MAX - Y_MIN) + Y_MIN
        else:
            for f in friendly:
                f.Unpackage(state['Player1_Units'][friendly.index(f)])
                f.x = ((f.x - SERVER_X_MIN) / ServerBattlefield_size[0]) * (X_MAX - X_MIN) + X_MIN
                f.y = ((f.y - SERVER_Y_MIN) / ServerBattlefield_size[1]) * (Y_MAX - Y_MIN) + Y_MIN
                f.target = ((f.target[0] - SERVER_X_MIN) / ServerBattlefield_size[0]) * (X_MAX - X_MIN) + X_MIN, ((f.target[1] - SERVER_Y_MIN) / ServerBattlefield_size[1]) * (Y_MAX - Y_MIN) + Y_MIN
            for e in enemy:
                e.Unpackage(state['Player2_Units'][enemy.index(e)])
                e.x = ((e.x - SERVER_X_MIN) / ServerBattlefield_size[0]) * (X_MAX - X_MIN) + X_MIN
                e.y = ((e.y - SERVER_Y_MIN) / ServerBattlefield_size[1]) * (Y_MAX - Y_MIN) + Y_MIN
                e.target = ((e.target[0] - SERVER_X_MIN) / ServerBattlefield_size[0]) * (X_MAX - X_MIN) + X_MIN, ((e.target[1] - SERVER_Y_MIN) / ServerBattlefield_size[1]) * (Y_MAX - Y_MIN) + Y_MIN
            for p in Pumps:
                p.Unpackage(state['Pumps'][Pumps.index(p)])
                p.x = ((p.x - SERVER_X_MIN) / ServerBattlefield_size[0]) * (X_MAX - X_MIN) + X_MIN
                p.y = ((p.y - SERVER_Y_MIN) / ServerBattlefield_size[1]) * (Y_MAX - Y_MIN) + Y_MIN
            # Calculate delta time
        current_time = time.time()
        dt = current_time - last_time

        # Event handling
        for event in pygame.event.get([QUIT, KEYDOWN, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION]):
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                print("Game exiting")
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
            if event.type == KEYDOWN and event.key == K_F12:
                screenshot(gameDisplay)
            # start of selection
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                # Check if the click is within the battlefield bounds
                if X_MIN < event.pos[0] < X_MAX and not Selecting and Y_MIN < event.pos[1] < Y_MAX:
                    Selecting = True
                # Check if the click is within the summoning UI bounds
                elif summon_UI_pos[0] < event.pos[0] < (summon_UI_pos[0] + summon_UI.get_width()) and summon_UI_pos[1] < event.pos[1] < (summon_UI_pos[1] + summon_UI.get_height()):
                    # Determine which unit to summon based on the Y position of the click
                    if player_mana >= Units.Footman.cost and summon_UI_pos[1] <= event.pos[1] < (summon_UI_pos[1] + (144 * scale_y)):
                        friendly.append(Units.Footman(
                            (player_base[0], player_base[1]), Scalars))
                        friendly[-1].target = (player_base[0], player_base[1])
                        player_mana -= Units.Footman.cost
                        requests.post(f"{DEFAULT_ADDR}:{DEFAULT_PORT}/summon", json={'RoomID': RoomID, 'PlayerID': PlayerID, 'SummonIndex': 0})
                    elif player_mana >= Units.Horse.cost and (summon_UI_pos[1] + (144 * scale_y)) <= event.pos[1] < (summon_UI_pos[1] + 2 * (144 * scale_y)):
                        friendly.append(Units.Horse(
                            (player_base[0], player_base[1]), Scalars))
                        friendly[-1].target = (player_base[0], player_base[1])
                        player_mana -= Units.Horse.cost
                        requests.post(f"{DEFAULT_ADDR}:{DEFAULT_PORT}/summon", json={'RoomID': RoomID, 'PlayerID': PlayerID, 'SummonIndex': 1})
                    elif player_mana >= Units.Soldier.cost and (summon_UI_pos[1] + 2 * (144 * scale_y)) <= event.pos[1] < (summon_UI_pos[1] + 3 * (144 * scale_y)):
                        friendly.append(Units.Soldier(
                            (player_base[0], player_base[1]), Scalars))
                        friendly[-1].target = (player_base[0], player_base[1])
                        player_mana -= Units.Soldier.cost
                        requests.post(f"{DEFAULT_ADDR}:{DEFAULT_PORT}/summon", json={'RoomID': RoomID, 'PlayerID': PlayerID, 'SummonIndex': 2})
                    elif player_mana >= Units.Summoner.cost and (summon_UI_pos[1] + 3 * (144 * scale_y)) <= event.pos[1] < (summon_UI_pos[1] + 4 * (144 * scale_y)):
                        friendly.append(Units.Summoner(
                            (player_base[0], player_base[1]), Scalars))
                        friendly[-1].target = (player_base[0], player_base[1])
                        player_mana -= Units.Summoner.cost
                        requests.post(f"{DEFAULT_ADDR}:{DEFAULT_PORT}/summon", json={'RoomID': RoomID, 'PlayerID': PlayerID, 'SummonIndex': 3})
                    elif player_mana >= Units.Runner.cost and (summon_UI_pos[1] + 4 * (144 * scale_y)) <= event.pos[1] < (summon_UI_pos[1] + 5 * (144 * scale_y)):
                        friendly.append(Units.Runner(
                            (player_base[0], player_base[1]), Scalars))
                        friendly[-1].target = (player_base[0], player_base[1])
                        player_mana -= Units.Runner.cost
                        requests.post(f"{DEFAULT_ADDR}:{DEFAULT_PORT}/summon", json={'RoomID': RoomID, 'PlayerID': PlayerID, 'SummonIndex': 4})
                    elif player_mana >= Units.Tank.cost and (summon_UI_pos[1] + 5 * (144 * scale_y)) <= event.pos[1] < (summon_UI_pos[1] + 6 * (144 * scale_y)):
                        friendly.append(Units.Tank(
                            (player_base[0], player_base[1]), Scalars))
                        friendly[-1].target = (player_base[0], player_base[1])
                        player_mana -= Units.Tank.cost
                        requests.post(f"{DEFAULT_ADDR}:{DEFAULT_PORT}/summon", json={'RoomID': RoomID, 'PlayerID': PlayerID, 'SummonIndex': 5})
           # end of selection
            if event.type == MOUSEBUTTONUP and event.button == 1:
                # checking if in bounds of the field
                if Selecting:
                    Selecting = False
                    if mouseinkblots:
                        blotx = []
                        bloty = []
                        for ink in mouseinkblots:
                            blotx.append(ink[0][0])
                            bloty.append(ink[0][1])
                        blotx.sort()
                        bloty.sort()
                        startselect = (blotx[0], bloty[0])
                        endselect = (blotx[-1], bloty[-1])
                        for blot in mouseinkblots:
                            inkblots.append(blot)
                        mouseinkblots.clear()
                        selected = []
                        for f in friendly:
                            if startselect[0] <= f.x <= endselect[0] and startselect[1] <= f.y <= endselect[1] and f.__class__.__name__ != 'Generator':
                                selected.append(f)
                            # #print(f"Selection from {startselect} to {endselect}")
                            # #print(f"Selected units: {selected}")
            if event.type == MOUSEBUTTONDOWN and event.button == 3:
                # check for enemy collision with the right click
                TarObj = None
                enemy_base_rect = base_images[base_img].get_rect(
                    center=(enemy_base[0], enemy_base[1]))
                if enemy_base_rect.collidepoint(event.pos):
                    TarObj = enemy_base
                for p in Pumps:
                    if p.x - 10 <= event.pos[0] <= p.x + p.Asset.get_width() + 10 and p.y - 10 <= event.pos[1] <= p.y + p.Asset.get_height() + 10:
                        TarObj = p
                for e in enemy:
                    if e.x - 10 <= event.pos[0] <= e.x + e.Asset.get_width() + 10 and e.y - 10 <= event.pos[1] <= e.y + e.Asset.get_height() + 10:
                        TarObj = e

                for s in selected:
                    mouse_x, mouse_y = event.pos
                    i = friendly.index(s)
                    if PlayerID == state['player1_ID']:
                        server_x = (mouse_x - X_MIN) / BattleGround_width * ServerBattlefield_size[0]
                        server_y = (mouse_y - Y_MIN) / BattleGround_height * ServerBattlefield_size[1]
                        requests.post(f"{DEFAULT_ADDR}:{DEFAULT_PORT}/retarget", json={'RoomID': RoomID, 'PlayerID': PlayerID, 'UnitIndex': i, 'target': [server_x, server_y]})
                    elif PlayerID == state['player2_ID']:
                        server_x = (mouse_x - X_MIN) / BattleGround_width * ServerBattlefield_size[0]
                        server_y = (mouse_y - Y_MIN) / BattleGround_height * ServerBattlefield_size[1]
                        # Flip the coordinates for Player 2
                        flipped_server_x = ServerBattlefield_size[0] - server_x
                        flipped_server_y = ServerBattlefield_size[1] - server_y
                        requests.post(f"{DEFAULT_ADDR}:{DEFAULT_PORT}/retarget", json={'RoomID': RoomID, 'PlayerID': PlayerID, 'UnitIndex': i, 'target': [flipped_server_x, flipped_server_y]})

                    if TarObj:
                        s.target = TarObj
                        Targ_obj = TarObj
                    else:
                        s.target = event.pos
                        Targ_obj = event.pos
            if event.type == MOUSEBUTTONDOWN and event.button == 2:
                # middle mouse button
                # print(event.pos)
                pass
            # Adjust the boundary conditions in the MOUSEMOTION event handler
            if event.type == MOUSEMOTION:
                if Selecting:
                    pos = event.pos
                    # Clamp the position within the battlefield bounds
                    clamped_x = max(X_MIN, min(pos[0], X_MAX))
                    clamped_y = max(Y_MIN, min(pos[1], Y_MAX))
                    pos = (clamped_x, clamped_y)
                    mouseinkblots.append(
                        [pos, 255, 100, random.choice(range(0, 360, 15))])
        # putting the inkblots on the field

        gameDisplay.fill((0, 0, 0))
        gameDisplay.blit(BattleGround, BattleGround_pos)

        for blot in inkblots:
            blot[2] -= 1
            if blot[2] <= 0:
                blot[2] = 0
                blot[1] -= 1
            if blot[1] < 0:
                blot[1] = 0
            rotated = pygame.transform.rotate(inkblot, blot[3]).convert_alpha()
            rotated.set_alpha(blot[1])
            # print(rotated.get_alpha())
            if rotated:
                gameDisplay.blit(rotated, blot[0])
            else:
                print(
                    f"Error: {rotated}{blot[0]} {blot[1]} {blot[2]} {blot[3]}")
        for blot in mouseinkblots:
            rotated = pygame.transform.rotate(inkblot, blot[3]).convert_alpha()
            rotated.set_alpha(blot[1])
            if rotated:
                gameDisplay.blit(rotated, blot[0])
            else:
                print(
                    f"Error: {rotated}{blot[0]} {blot[1]} {blot[2]} {blot[3]}")

        inkblots = [b for b in inkblots if b[1] > 0]
        mouseinkblots = [b for b in mouseinkblots if b[1] > 0]

        # putting the pumps on the field
        for p in Pumps:
            gameDisplay.blit(p.Asset, (p.x, p.y))
            if p.hp <= 0:
                for f in friendly:
                    if p.x - 10 <= f.x <= p.x + p.Asset.get_width() + 10 and p.y - 10 <= f.y <= p.y + p.Asset.get_height() + 10:
                        # #print("Friendly Pump gained")
                        score += 100
                        try:
                            Pumps.remove(p)
                        except Exception as e:
                            print(e)
                        friendly.append(Units.Generator([p.x, p.y], Scalars))
                        break
                for e in enemy:
                    if p.x - 10 <= e.x <= p.x + p.Asset.get_width() + 10 and p.y - 10 <= e.y <= p.y + p.Asset.get_height() + 10:
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
                    if p.x - 10 <= f.x <= p.x + p.Asset.get_width() + 10 and p.y - 10 <= f.y <= p.y + p.Asset.get_height() + 10:
                        p.hp -= 1
                for e in enemy:
                    if p.x - 10 <= e.x <= p.x + p.Asset.get_width() + 10 and p.y - 10 <= e.y <= p.y + p.Asset.get_height() + 10:
                        p.hp -= 1
        # putting the selected units on the field
        p_controled = 0
        for f in friendly:
            # checking for collision
            for e in enemy:
                if abs(f.x - e.x) < 12 and abs(f.y - e.y) < 12 and e.hp > 0 and f.hp > 0:
                    # combat
                    f.hp -= e.attack
                    e.hp -= f.attack
            # checking for enchanter damage
            if enemy_base[0]-(base_images[base_img].get_height()//2) < f.x <= enemy_base[0]+(base_images[base_img].get_width()//2) and enemy_base[1]-(base_images[base_img].get_height()//2) < f.y <= enemy_base[1]+(base_images[base_img].get_height()//2):
                Enchanter_HP -= f.attack
                f.hp = 0
            # unit death
            if f.hp <= 0:
                score -= 10
                if f.__class__.__name__ == "Generator":
                    # #print("Friendly Pump destroyed")
                    enemy.append(Units.Generator([f.x, f.y], Scalars))
                else:
                    inkblots.append(
                        [(f.x, f.y), 255, 1000, random.choice(range(0, 360, 45))])
                try:
                    friendly.remove(f)
                except Exception as e:
                    print(e)
                continue
            # movement
            else:
                f.move(dt, friendly, boundaries, Scalars)
                gameDisplay.blit(f.Asset, (f.x, f.y))
                gameDisplay.blit(Friendly_identifyer, (f.x + f.Asset.get_width() // 2 - Friendly_identifyer.get_width(
                ) // 2, f.y - f.Asset.get_height() // 2 - Friendly_identifyer.get_height() // 2))
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
                if f.lifetime >= 5:
                    inkblots.append(
                        [(f.x, f.y), 255, 1000, random.choice(range(0, 360, 45))])
                    try:
                        friendly.remove(f)
                    except Exception as e:
                        print(e)
                    continue

        # similar to player controlled units, but for enchanter units
        p_e_controled = 0
        for e in enemy:
            # checking for player Damage
            if player_base[0] - 5 <= e.x <= player_base[0] + 5 and player_base[1] - 5 <= e.y <= player_base[1] + 5:
                player_HP -= e.attack
                e.hp = 0

            if e.hp <= 0:
                score += 10
                if e.__class__.__name__ == "Generator":
                    # print("Enemy Pump destroyed")
                    friendly.append(Units.Generator([e.x, e.y], Scalars))
                else:
                    inkblots.append(
                        [(e.x, e.y), 255, 1000, random.choice(range(0, 360, 45))])
                try:
                    enemy.remove(e)
                except Exception as e:
                    print(e)
                continue
            else:
                e.move(dt, enemy, boundaries, Scalars)
                gameDisplay.blit(e.Asset, (e.x, e.y))
                gameDisplay.blit(Enemy_identifyer, (e.x + e.Asset.get_width() // 2 - Enemy_identifyer.get_width(
                ) // 2, e.y - e.Asset.get_height() // 2 - Enemy_identifyer.get_height() // 2))
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
                if e.lifetime >= 5:
                    inkblots.append(
                        [(e.x, e.y), 255, 1000, random.choice(range(0, 360, 45))])
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
        divisor_text = SpeechFont.render(
            f"Divisor: {str(divisor)}", True, (255, 255, 255))
        divisor = P_ratio[p_e_controled]
        if enchanter_mana_timer >= (5/divisor):
            Enchanter_mana = min(Enchanter_mana + 1, 9)
            enchanter_mana_timer = 0


        # Enchanter targeting

        if player_HP <= 0:
            running = False

        if Enchanter_HP <= 0:
            running = False
            Won = True

        for s in selected:
            if s in friendly:
                gameDisplay.blit(selection_icon, (s.x, s.y))
            else:
                try:
                    selected.remove(s)
                except Exception as e:
                    print(e)
        # player mana display
        manaCounter = mana_images[player_mana]
        gameDisplay.blit(manaCounter, manaCounter_pos)

        # blit bases of enemy
        base_timer += dt
        if base_timer >= 1/base_fps:
            base_timer = 0
            base_img += 1
            if base_img >= len(base_images):
                base_img = 0
        gameDisplay.blit(base_images[base_img], base_images[base_img].get_rect(
            center=(enemy_base[0], enemy_base[1])))

        # Hp display
        if hp_cache != (player_HP, Enchanter_HP):
            hp_text = HPFont.render(
                f"{player_HP}:{Enchanter_HP}", True, (255, 150, 255))
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

        mouse_x, mouse_y = pygame.mouse.get_pos()
        # Only show cost if mouse is hovering over the troop's area
        if summon_UI_pos[0] <= mouse_x:
            if summon_UI_pos[1] <= mouse_y < (summon_UI_pos[1] + (144 * scale_y)):
                gameDisplay.blit(Footman_cost, Footman_cost_pos)
            elif (summon_UI_pos[1] + (144 * scale_y)) <= mouse_y < (summon_UI_pos[1] + 2 * (144 * scale_y)):
                gameDisplay.blit(Horse_cost, Horse_cost_pos)
            elif (summon_UI_pos[1] + 2 * (144 * scale_y)) <= mouse_y < (summon_UI_pos[1] + 3 * (144 * scale_y)):
                gameDisplay.blit(Soldier_cost, Soldier_cost_pos)
            elif (summon_UI_pos[1] + 3 * (144 * scale_y)) <= mouse_y < (summon_UI_pos[1] + 4 * (144 * scale_y)):
                gameDisplay.blit(Summoner_cost, Summoner_cost_pos)
            elif (summon_UI_pos[1] + 4 * (144 * scale_y)) <= mouse_y < (summon_UI_pos[1] + 5 * (144 * scale_y)):
                gameDisplay.blit(Runner_cost, Runner_cost_pos)
            elif (summon_UI_pos[1] + 5 * (144 * scale_y)) <= mouse_y < (summon_UI_pos[1] + 6 * (144 * scale_y)):
                gameDisplay.blit(Tank_cost, Tank_cost_pos)

        # cursor display
        gameDisplay.blit(cursor_img, pygame.mouse.get_pos())

        # Display FPS counter
        fps = int(clock.get_fps())
        if show_fps_debug:
            fps_text = SpeechFont.render(f"FPS: {fps}", True, (255, 255, 255))
            # Dynamic position for FPS
            gameDisplay.blit(
                fps_text, (int(screen_width * 0), int(screen_height * 0.3)))
            dt_text = SpeechFont.render(
                f"dt: {round(dt * 1000, 3)}ms", True, (255, 255, 255))
            # Dynamic position for delta time
            gameDisplay.blit(dt_text, (int(screen_width * 0),
                             int(screen_height * 0.35)))
        if show_mana_debug:
            mana_text = SpeechFont.render(
                f"Mana Timer: {round(player_mana_timer, 3)}", True, (255, 255, 255))
            # Dynamic position for mana timer
            gameDisplay.blit(
                mana_text, (int(screen_width * 0), int(screen_height * 0.4)))
            # Dynamic position for divisor
            gameDisplay.blit(
                divisor_text, (int(screen_width * 0), int(screen_height * 0.45)))
            mana_text = SpeechFont.render(
                f"Enchanter Mana Timer: {round(enchanter_mana_timer, 3)}", True, (255, 255, 255))
            # Dynamic position for enchanter mana timer
            gameDisplay.blit(
                mana_text, (int(screen_width * 0), int(screen_height * 0.5)))
            Enchanter_mana_text = SpeechFont.render(
                f"Enchanter Mana: {Enchanter_mana}", True, (255, 255, 255))
            # Dynamic position for enchanter mana
            gameDisplay.blit(Enchanter_mana_text, (int(
                screen_width * 0), int(screen_height * 0.55)))
        if show_battle_debug:
            pygame.draw.rect(gameDisplay, (255, 0, 0), BattleGround_debug_rect,
                             2)  # Red rectangle with a thickness of 2\

        if Targ_obj_cache != Targ_obj:
            Targ_obj_cache = Targ_obj
            Targ_blinky_timer = 3

        if Targ_blinky_timer > 0:
            Targ_blinky_timer -= dt
            if Targ_blinky_timer <= 0:
                Targ_blinky_timer = 0
            if Targ_obj:
                if isinstance(Targ_obj, Units.Unit):
                    pygame.draw.rect(gameDisplay, (255, 0, 0), Targ_obj.Asset.get_rect(
                        topleft=[Targ_obj.x, Targ_obj.y]), 1)
                else:
                    pygame.draw.circle(
                        gameDisplay, (255, 0, 0), Targ_obj, 5, 1)

        # Debug rect!!!
        # Drect = pygame.Rect(0, 0, screen_width, screen_height)
        # pygame.draw.rect(gameDisplay, (255, 0, 0), Drect, 1)

        pygame.display.flip()
        clock.tick()

    # Ask if the player wants to play again
    play_again_font = pygame.font.Font(os.path.join(
        "Assets", "Fonts", "Speech.ttf"), int(screen_height * 0.05))  # Dynamic font size
    play_again_text = play_again_font.render(
        'Do you want to play again? (Y/N)', True, (255, 255, 255))

    # Center the text dynamically
    play_again_text_rect = play_again_text.get_rect(
        center=(screen_width // 2, screen_height * 0.6))

    gameDisplay.fill((0, 0, 0))
    gameDisplay.blit(play_again_text, play_again_text_rect)
    pygame.display.flip()

    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                print("Game exiting")
                pygame.quit()
                return False
            if event.type == KEYDOWN:
                if event.key == K_y:
                    return True
                elif event.key == K_n:
                    return False
                elif event.type == KEYDOWN and event.key == K_F12:
                    screenshot(gameDisplay)
    # Show Score and ask if they wanna play again, if they player wants to return to menu, return False, Else return True (Doesnt apply to monarch as game is crashed)
