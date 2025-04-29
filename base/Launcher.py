# pip installed/default libs
import time, os, multiprocessing, ctypes
import Units, Combat

#pip install/imported libs
# auto pip install if missing
try: 
    import pygame
    from pygame.locals import *
    from pypresence import Presence, exceptions
    import SaveUpdater
    import requests
except ImportError:
    try:
        os.system("pip install -r requirements.txt") if os.name == "nt" else os.system("pip3 install -r requirements.txt")
    except Exception as e:
        pass
        #print(f"Failed to install dependencies: {e}")



def get_physical_screen_resolution():
    user32 = ctypes.windll.user32
    # Set process DPI awareness to get true resolution
    user32.SetProcessDPIAware()
    width = user32.GetSystemMetrics(0)
    height = user32.GetSystemMetrics(1)
    return width, height

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
    for line in lines:
        line_surface = font.render(line, True, color)
        line_surface.set_alpha(alpha)
        surface.blit(line_surface, (rect.left, y_offset))
        y_offset += font.size(line)[1] + line_spacing

# check for update
VERSION = "0.8.8"
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/DaRealElementus/Ink-and-Incantations/refs/heads/main/base/Version.txt"  # URL to the version file on GitHub
def check_for_update():
    try:
        response = requests.get(GITHUB_VERSION_URL, timeout=5)
        if response.status_code == 200:
            latest_version = response.text.strip()
            Maj,_min,Pat = latest_version.split('.')
            Maj2,min2,Pat2 = VERSION.split('.')
            Maj = int(Maj) - int(Maj2)
            _min = int(_min) - int(min2)
            Pat = int(Pat) - int(Pat2)
            if Maj > 0 or _min > 0 or Pat > 0:
                #print(f"[UPDATE] A new version ({latest_version}) is available! You have {VERSION}.")
                return "update"  # Indicate that an update is available
            else:
                #print(f"[INFO] You are using the latest version ({VERSION}).")
                return "good"
        else:
            #print("[WARN] Failed to fetch update info.")
            return "error"
    except Exception as e:
        #print(f"[ERROR] Could not check for updates: {e}")
        return "error"


def try_connect(client_id, success_flag):
    """
    Create the Presence object inside the child process and attempt to connect.
    """
    try:
        RPC = Presence(client_id)
        RPC.connect()
        success_flag.value = True
    except exceptions as e:  # Catches Discord-related issues
        #print(f"Failed to connect: {e}")
        pass
    except Exception as e:
        #print(f"Failed to connect: {e}")
        pass


def connect_rpc(client_id):
    """
    Use multiprocessing to attempt connecting to Discord RPC.
    """
    success_flag = multiprocessing.Value('b', False)  # Shared boolean value
    process = multiprocessing.Process(target=try_connect, args=(client_id, success_flag))
    process.start()
    process.join(timeout=5)  # Wait for max 5 seconds

    if not success_flag.value:
        #print("Connection timed out. Skipping...")
        return None
    else:
        #print("Connected to Discord RPC.")
        # Return a new Presence object for the main process
        RPC = Presence(client_id)
        RPC.connect()
        return RPC, success_flag.value


def incompat_save(save_data: dict):
    """
    checks when the save file is corrupted or incompatible with version or mods
    """
    try:
        error = False
        font = pygame.font.Font(os.path.join("Assets", "Fonts", "Books-Vhasenti.ttf"), 50)
        text = font.render("Save file is passed", True, (255, 0, 0))
        if save_data is None:
            text = font.render("Save file is corrupted", True, (255, 0, 0))
            error = True
        elif save_data['GameVersion'] != VERSION:
            text = font.render("Incompatible save file with this version, please delete it", True, (255, 0, 0))
            error = True
        elif save_data['modded']:
            text = font.render("This save file is modded, and thus invalid", True, (255, 0, 0))
            error = True
    except:
        text = font.render("Save file is corrupted", True, (255, 0, 0))
        error = True

    return error, text

    

flags = FULLSCREEN | DOUBLEBUF
Combat_loader = Combat  # Importing combat module
Unit_loader = Units  # Importing unit module



if __name__ == "__main__":
    check = check_for_update()  # Check for updates at the start
    #print(check)
    # Ensure multiprocessing works correctly on Windows
    multiprocessing.freeze_support()
    
    # Initialize Pygame
    pygame.init()
    pygame.font.init()
    pygame.mixer.init()

    # Get screen dimensions dynamically
    screen_width, screen_height = get_physical_screen_resolution() if os.name == 'nt' else (pygame.display.Info().current_w, pygame.display.Info().current_h)

    scale_x = screen_width / 1536
    scale_y = screen_height / 864
    #for all assets, use y scaling <- this is for ultrawide support

    #print(scale_x, scale_y)
    #print(screen_width, screen_height)
    # Initialize display
    gameDisplay = pygame.display.set_mode((screen_width, screen_height), flags)
    pygame.display.set_caption('Ink and Incantations')
    gameDisplay.fill((0, 0, 0))

    savecompat = incompat_save(SaveUpdater.decode_save_file())
    if savecompat[0]:
        gameDisplay.fill((0, 0, 0))
        gameDisplay.blit(savecompat[1], savecompat[1].get_rect(center=(screen_width // 2, screen_height // 2)))
        pygame.display.update()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    running = False
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    running = False
            pygame.time.delay(1)
        pygame.quit()
        os._exit(0)  # Exit the program
    title_font_size = int(scale_y * 60)
    speech_font_size = int(scale_y * 40)
    TitleFont = pygame.font.Font(os.path.join("Assets", "Fonts", "Books-Vhasenti.ttf"), title_font_size)
    SpeechFont = pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), speech_font_size)

    if check == "update":
        update = pygame.image.load(os.path.join("Assets", "Updates", "Update.png"))
        updateHover = SpeechFont.render("Update Avaliable", False, (255, 255, 255))
    elif check == "good":
        update = pygame.image.load(os.path.join("Assets", "Updates", "NoUpdate.png"))
        updateHover = SpeechFont.render("No Updates", False, (255, 255, 255))
    elif check == "error":
        update = pygame.image.load(os.path.join("Assets", "Updates", "Error.png"))
        updateHover = SpeechFont.render("Error getting update", False, (255, 255, 255))
    else:
        update = pygame.image.load(os.path.join("Assets", "Updates", "Error.png"))
    update_rect = update.get_rect(topleft=(screen_width * 0, screen_height * 0))  # Update message


    
    # Load assets

    icon = pygame.image.load(os.path.join("Assets", "Icon.png"))
    menu_background = pygame.image.load(os.path.join("Assets", "Openbook.png"))
    selector = pygame.image.load(os.path.join("Assets", "Selector.jpg"))  # 235x119 size
    pygame.display.set_icon(icon)


    # Load music
    music = pygame.mixer.Sound(os.path.join("Assets", "Music", "last-fight-dungeon-synth-music-281592.mp3"))
    music.set_volume(1 if SaveUpdater.decode_save_file()['music'] else 0)  # Set volume based on saved state
    music.play(-1)  # Loop the music indefinitely


    # Scale factor for all assets

    # Scale images dynamically
    menu_background = pygame.transform.scale(
        menu_background,
        (int(menu_background.get_width() * scale_y), int(menu_background.get_height() * scale_y))
    )
    selector = pygame.transform.scale(
        selector,
        (int(selector.get_width() * scale_y), int(selector.get_height() * scale_y))
    )

    update = pygame.transform.scale(
        update,
        (int(update.get_width() * scale_y), int(update.get_height() * scale_y))
    )

    # Scale fonts dynamically
    


    AudioMute = pygame.image.load(os.path.join("Assets", "Sprites", "Audio-Mute.png"))
    AudioUnmute = pygame.image.load(os.path.join("Assets","Sprites", "Audio-Unmute.png"))
    AudioMute = pygame.transform.scale(AudioMute, (int(AudioMute.get_width() * scale_y), int(AudioMute.get_height() * scale_y)))
    AudioUnmute = pygame.transform.scale(AudioUnmute, (int(AudioUnmute.get_width() * scale_y), int(AudioUnmute.get_height() * scale_y)))
    AudioMuteRect = AudioMute.get_rect(topleft=(screen_width - AudioMute.get_width(), 0))

    # Render scaled text
    title = TitleFont.render('Ink & Incantations', False, (255, 0, 255))
    play = SpeechFont.render('PLAY', False, (255, 255, 255))
    warning = "Warning: This game is work in progress, some features are incomplete"
    _quit = SpeechFont.render('QUIT', False, (255, 255, 255))

    selector_enchanter = SpeechFont.render('Mage', False, (255, 255, 255))
    selector_monarch = SpeechFont.render('Monarch', False, (255, 255, 255))
    selector_madman = SpeechFont.render('Madman', False, (255, 255, 255))

    AudioHoverUn = SpeechFont.render('Audio: Unmuted', False, (255, 255, 255))
    AudioHoverUnRect = AudioHoverUn.get_rect(topleft=(screen_width - AudioMute.get_width(), 0))
    AudioHoverMu = SpeechFont.render('Audio: Muted', False, (255, 255, 255))
    AudioHoverMuRect = AudioHoverMu.get_rect(topleft=(screen_width - AudioMute.get_width(), 0))

    

    # Center elements dynamically
    title_rect = title.get_rect(center=(screen_width // 2, screen_height * 0.3))
    play_rect = play.get_rect(center=(screen_width // 2, screen_height * 0.5))
    quit_rect = _quit.get_rect(center=(screen_width // 2, screen_height * 0.55))
    menu_background_rect = menu_background.get_rect(center=(screen_width // 2, screen_height // 2))
    selector_rect = selector.get_rect(center=(selector.get_width() // 2, (screen_height - (selector.get_height() // 2 ))))


    Audio = AudioUnmute if SaveUpdater.decode_save_file()['music'] else AudioMute



    # Discord RPC
    pid = os.getpid()
    client_id = "1336631328195481722"
    epoch = int(time.time())
    try:
        RPC, Connect = connect_rpc(client_id)
    except Exception as e:
        #print(f"Failed to connect to Discord RPC: {e}")
        Connect = False
        RPC = Presence(client_id)

    # Main menu and game logic
    running = True
    a = 0
    for i in range(255):
        gameDisplay.fill((0, 0, 0))
        a += 1
        render_wrapped_text(gameDisplay, warning, TitleFont, (255, 0, 0), a, pygame.Rect(screen_width * 0.025, screen_height * 0.4, screen_width * 0.95, screen_height * 0.2), line_spacing=5)
        pygame.display.update()

    gameDisplay.fill((0, 0, 0))
    render_wrapped_text(gameDisplay, warning, TitleFont, (255, 0, 0), a, pygame.Rect(screen_width * 0.025, screen_height * 0.4, screen_width * 0.95, screen_height * 0.2), line_spacing=5)
    pygame.display.update()
    skip = False
    for i in range(4000):
        if skip:
            break
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                skip = True
        pygame.time.delay(1)

    for i in range(255):
        gameDisplay.fill((0, 0, 0))
        a -= 1
        render_wrapped_text(gameDisplay, warning, TitleFont, (255, 0, 0), a, pygame.Rect(screen_width * 0.025, screen_height * 0.4, screen_width * 0.95, screen_height * 0.2), line_spacing=5)
  
        pygame.display.update()

    a = 0
    v = 0
    for i in range(255):
        gameDisplay.fill((0, 0, 0))
        a += 1
        v += 0.004
        pygame.mixer.music.set_volume(v)
        title.set_alpha(a)
        play.set_alpha(a)
        _quit.set_alpha(a)
        menu_background.set_alpha(a)
        Audio.set_alpha(a)
        update.set_alpha(a)
        selector.set_alpha(a)
        gameDisplay.blit(selector, selector_rect.topleft)
        gameDisplay.blit(menu_background, menu_background_rect.topleft)
        gameDisplay.blit(Audio, AudioMuteRect.topleft)
        gameDisplay.blit(update, update_rect.topleft)
        gameDisplay.blit(title, title_rect.topleft)
        gameDisplay.blit(play, play_rect.topleft)
        gameDisplay.blit(_quit, quit_rect.topleft)
        pygame.display.update()

    hover_enchanter = False
    hover_monarch = False
    hover_madman = False
    ai = 'enchanter'

    while running:
        if Connect:
            RPC.update(
                pid=pid,
                state="Preparing for battle",
                details=f"Current opponent: {ai.capitalize()}",
                start=epoch,
                large_image="icon",
                large_text="The Enchanters Book awaits....")
        gameDisplay.blit(selector, selector_rect.topleft)
        gameDisplay.blit(menu_background, menu_background_rect.topleft)
        gameDisplay.blit(Audio, AudioMuteRect.topleft)
        gameDisplay.blit(update, update_rect.topleft)  # Update message
        gameDisplay.blit(title, title_rect.topleft)
        gameDisplay.blit(play, play_rect.topleft)
        gameDisplay.blit(_quit, quit_rect.topleft)
        gameDisplay.blit(update, (screen_width * 0, screen_height * 0))  # Update message
        gameDisplay.blit(Audio, AudioMuteRect.topleft)
        music.set_volume(1) if SaveUpdater.decode_save_file()['music'] else music.set_volume(0)
        for event in pygame.event.get():

            if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                running = False

            if event.type == MOUSEBUTTONDOWN and event.button == 2:
                pass
                #print(event.pos)


            if event.type == MOUSEBUTTONDOWN and event.button == 1:
            # Select opponent
                if selector_rect.collidepoint(event.pos):
                    # Determine which villain is selected
                    third_width = selector_rect.width / 3
                    relative_x = event.pos[0] - selector_rect.left  # Calculate relative X position within the selector
                    if relative_x < third_width:
                        ai = 'enchanter'
                    elif relative_x < third_width * 2:
                        ai = 'monarch'
                    else:
                        ai = 'madman'
                # PLAY button
                if play_rect.collidepoint(event.pos):
                    a = 255
                    v = 1
                    for i in range(255):
                        gameDisplay.fill((0, 0, 0))
                        a -= 1
                        v -= 0.004
                        pygame.mixer.music.set_volume(v)
                        title.set_alpha(a)
                        play.set_alpha(a)
                        _quit.set_alpha(a)
                        menu_background.set_alpha(a)
                        selector.set_alpha(a)
                        gameDisplay.blit(menu_background, menu_background_rect.topleft)
                        gameDisplay.blit(selector, selector_rect.topleft)
                        gameDisplay.blit(title, title_rect.topleft)
                        gameDisplay.blit(play, play_rect.topleft)
                        gameDisplay.blit(_quit, quit_rect.topleft)
                        pygame.time.delay(1)
                        pygame.display.update()
                    pygame.time.delay(1000)
                    Again = True
                    while Again:
                        music.stop()
                        gameDisplay.fill((0, 0, 0))
                        Again = Combat_loader.BatStart(ai, gameDisplay, Connect, RPC, pid, Unit_loader, SaveUpdater, [scale_x, scale_y], [screen_width, screen_height], render_wrapped_text)
                    running = False

                # QUIT button
                elif quit_rect.collidepoint(event.pos):
                    running = False

                elif AudioMuteRect.collidepoint(event.pos):
                    save = SaveUpdater.decode_save_file()
                    save['music'] = False if save['music'] else True
                    SaveUpdater.encode_save_file(save)
                    Audio = AudioUnmute if save['music'] else AudioMute
        if event.type == MOUSEMOTION:
            # Selector: Show names of villains on hover, each villain occupies 1/3 of the selector's width
            if selector_rect.collidepoint(event.pos):
                # Determine which villain is being hovered over
                third_width = selector_rect.width / 3
                relative_x = event.pos[0] - selector_rect.left  # Calculate relative X position within the selector
                if relative_x < third_width:
                    hover_enchanter, hover_monarch, hover_madman = True, False, False
                elif relative_x < third_width * 2:
                    hover_enchanter, hover_monarch, hover_madman = False, True, False
                else:
                    hover_enchanter, hover_monarch, hover_madman = False, False, True
            else:
                # Reset hover states if the mouse is outside the selector bounds
                hover_enchanter, hover_monarch, hover_madman = False, False, False
            if AudioMuteRect.collidepoint(event.pos):
                pygame.draw.rect(gameDisplay, (0, 0, 0), AudioHoverUn.get_rect(topright=event.pos)) if SaveUpdater.decode_save_file()['music'] else pygame.draw.rect(gameDisplay, (0, 0, 0), AudioHoverMu.get_rect(topright=event.pos))
                gameDisplay.blit(AudioHoverUn, AudioHoverUn.get_rect(topright=event.pos)) if SaveUpdater.decode_save_file()['music'] else gameDisplay.blit(AudioHoverMu, AudioHoverMu.get_rect(topright=event.pos))
                
            if update_rect.collidepoint(event.pos):
                pygame.draw.rect(gameDisplay, (0, 0, 0), updateHover.get_rect(topleft=event.pos)) 
                gameDisplay.blit(updateHover, updateHover.get_rect(topleft=event.pos))
                   

        mouseloc = pygame.mouse.get_pos()
        if hover_enchanter:
            text_rect = selector_enchanter.get_rect(bottomleft=mouseloc)
            pygame.draw.rect(gameDisplay, (0, 0, 0), text_rect)
            gameDisplay.blit(selector_enchanter, text_rect.topleft)
        elif hover_monarch:
            text_rect = selector_monarch.get_rect(bottomleft=mouseloc)
            pygame.draw.rect(gameDisplay, (0, 0, 0), text_rect)
            gameDisplay.blit(selector_monarch, text_rect.topleft)
        elif hover_madman:
            text_rect = selector_madman.get_rect(bottomleft=mouseloc)
            pygame.draw.rect(gameDisplay, (0, 0, 0), text_rect)
            gameDisplay.blit(selector_madman, text_rect.topleft)
        
        #Debug rect!!!
        # Drect = pygame.Rect(0, 0, screen_width, screen_height)
        # pygame.draw.rect(gameDisplay, (255, 0, 0), Drect, 1)


        
        pygame.display.flip()
        gameDisplay.fill((0, 0, 0))

