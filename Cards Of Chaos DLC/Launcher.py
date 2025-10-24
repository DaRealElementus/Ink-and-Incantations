# pip installed/default libs
import time
import os
import multiprocessing
import ctypes
import random



import ModSave
import Units
import Combat
import SaveUpdater
import Storymanv2 as StoryManager


# pip install/imported libs
# auto pip install if missing
try:
    import pygame
    from pygame.locals import *
    from pypresence import Presence
    from pypresence.exceptions import DiscordNotFound, InvalidID, InvalidPipe, DiscordError
    import requests
except ImportError:
    try:
        (os.system("pip install -r requirements.txt") if os.name == "nt" else os.system("pip3 install -r requirements.txt --break-system-packages")
         ) if input("Missing Libaries, force install them? (this will use --b-s-p on linux): (Y/N) ").upper() == "Y" else quit()
    except Exception as e:
        pass
        # print(f"Failed to install dependencies: {e}")


def get_physical_screen_resolution():
    user32 = ctypes.windll.user32
    # Set process DPI awareness to get true resolution
    user32.SetProcessDPIAware()
    width = user32.GetSystemMetrics(0)
    height = user32.GetSystemMetrics(1)
    return width, height


# check for update
with open("Version.txt", 'r' )as f:
    VERSION = f.read().strip()  # Read the current version from the file
# URL to the version file on GitHub
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/DaRealElementus/Ink-and-Incantations/refs/heads/main/base/Version.txt"


def check_for_update():
    try:
        response = requests.get(GITHUB_VERSION_URL, timeout=5)
        if response.status_code == 200:
            latest_version = response.text.strip()
            Maj, _min, Pat = latest_version.split('.')
            Maj2, min2, Pat2 = VERSION.split('.')
            Maj = int(Maj) - int(Maj2)
            _min = int(_min) - int(min2)
            Pat = int(Pat) - int(Pat2)
            if Maj > 0 or _min > 0 or Pat > 0:
                # print(f"[UPDATE] A new version ({latest_version}) is available! You have {VERSION}.")
                return "update"  # Indicate that an update is available
            else:
                # print(f"[INFO] You are using the latest version ({VERSION}).")
                return "good"
        else:
            # print("[WARN] Failed to fetch update info.")
            return "error"
    except Exception as e:
        # print(f"[ERROR] Could not check for updates: {e}")
        return "error"


def try_connect(client_id, success_flag):
    """
    Create the Presence object inside the child process and attempt to connect.
    """
    try:
        RPC = Presence(client_id)
        RPC.connect()
        success_flag.value = True
    except (DiscordNotFound, InvalidID, InvalidPipe, DiscordError) as e:  # Catches Discord-related issues
        print(f"Failed to connect: {e}")
    except Exception as e:
        print(f"Failed to connect: {e}")


def connect_rpc(client_id):
    """
    Use multiprocessing to attempt connecting to Discord RPC.
    """
    success_flag = multiprocessing.Value('b', False)  # Shared boolean value
    process = multiprocessing.Process(
        target=try_connect, args=(client_id, success_flag))
    process.start()
    process.join(timeout=1)  # Wait for max 5 seconds

    if not success_flag.value:
        # print("Connection timed out. Skipping...")
        return None
    else:
        # print("Connected to Discord RPC.")
        # Return a new Presence object for the main process
        RPC = Presence(client_id)
        RPC.connect()
        return RPC, success_flag.value


def incompat_save(save_data: dict, scale_y: float = 1.0) -> tuple:
    """
    checks when the save file is corrupted or incompatible with version or mods
    """
    title_font_size = int(scale_y * 60)
    try:
        error = False
        font = pygame.font.Font(os.path.join(
            "Assets", "Fonts", "Books-Vhasenti.ttf"), title_font_size)
        text = font.render("Save file is passed", True, (255, 0, 0))
        if save_data is None:
            text = font.render("Save file is corrupted", True, (255, 0, 0))
            error = True
        elif save_data['GameVersion'] != VERSION:
            text = font.render(
                "Incompatible save file with this version, please delete it", True, (255, 0, 0))
            error = True
        elif not save_data['modded']:
            text = font.render(
                "This save file is unmodded, and thus invalid", True, (255, 0, 0))
            error = True
    except:
        text = font.render("Save file is corrupted", True, (255, 0, 0))
        error = True

    return error, text


flags = FULLSCREEN | SCALED
Combat_loader = Combat  # Importing combat module
Unit_loader = Units  # Importing unit module


if __name__ == "__main__":
    check = check_for_update()  # Check for updates at the start
    # print(check)
    # Ensure multiprocessing works correctly on Windows
    multiprocessing.freeze_support()

    # Initialize Pygame
    pygame.init()
    pygame.font.init()
    pygame.mixer.init()

    # Get screen dimensions dynamically
    screen_width, screen_height = get_physical_screen_resolution() if os.name == 'nt' else (
        pygame.display.Info().current_w, pygame.display.Info().current_h)
    # Use a fixed window resolution for testing / fallback (width, height)
    screen_width, screen_height = 1280, 720
    scale_x = screen_width / 1536
    scale_y = screen_height / 864

    StoryManager.scale_x, StoryManager.scale_y = scale_x, scale_y
    # StoryManager expects (screen_x, screen_y)
    StoryManager.screen_x, StoryManager.screen_y = screen_width, screen_height
    # for all assets, use y scaling <- this is for ultrawide support

    # print(scale_x, scale_y)
    # print(screen_width, screen_height)
    # Initialize display
    icon = pygame.image.load(os.path.join("Assets", "Icon.png"))
    pygame.display.set_icon(icon)
    gameDisplay = pygame.display.set_mode((screen_width, screen_height), flags)
    pygame.display.set_caption('Ink and Incantations')
    gameDisplay.fill((0, 0, 0))

    savecompat = incompat_save(SaveUpdater.decode_save_file(), scale_y)
    if savecompat[0]:
        gameDisplay.fill((0, 0, 0))
        gameDisplay.blit(savecompat[1], savecompat[1].get_rect(
            center=(screen_width // 2, screen_height // 2)))
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


    # Mod save check
    if ModSave.decode_save_file() is None:
        ModSave.encode_save_file()

    mod_save = ModSave.decode_save_file()
    save = SaveUpdater.decode_save_file()

    title_font_size = int(scale_y * 60)
    speech_font_size = int(scale_y * 40)
    TitleFont = pygame.font.Font(os.path.join(
        "Assets", "Fonts", "Books-Vhasenti.ttf"), title_font_size)
    SpeechFont = pygame.font.Font(os.path.join(
        "Assets", "Fonts", "Speech.ttf"), speech_font_size)

    if check == "update":
        update = pygame.image.load(os.path.join(
            "Assets", "Updates", "Update.png"))
        updateHover = SpeechFont.render(
            "Update Avaliable", False, (255, 255, 255))
    elif check == "good":
        update = pygame.image.load(os.path.join(
            "Assets", "Updates", "NoUpdate.png"))
        updateHover = SpeechFont.render("No Updates", False, (255, 255, 255))
    elif check == "error":
        update = pygame.image.load(os.path.join(
            "Assets", "Updates", "Error.png"))
        updateHover = SpeechFont.render(
            "Error getting update", False, (255, 255, 255))
    else:
        update = pygame.image.load(os.path.join(
            "Assets", "Updates", "Error.png"))
    update_rect = update.get_rect(
        topleft=(screen_width * 0, screen_height * 0))  # Update message

    # Load assets
# Assets\Cards\cards\_cardBack\_cardBack_5x.png
    menu_background = pygame.image.load(os.path.join("Assets", "Cards", "cards", "_cardBack", "_cardBack_5x.png"))
    menu_background = pygame.transform.rotate(menu_background, 90)
    # Increase size by 50%
    menu_background = pygame.transform.scale2x(menu_background)

    # Darken the background
    darken_surface = pygame.Surface(
        (menu_background.get_width(), menu_background.get_height()))
    darken_surface.fill((0, 0, 0))
    darken_surface.set_alpha(200)  # Adjust alpha for darkness level
    menu_background.blit(darken_surface, (0, 0))


    # Load music
    music = pygame.mixer.Sound(os.path.join(
        "Assets", "Music", "Main_" + random.choice(["1", "2", "3"]) + ".mp3"))
    music.set_volume(1 if SaveUpdater.decode_save_file()[
                     'music'] else 0)  # Set volume based on saved state
    music.play(-1)  # Loop the music indefinitely

    # Scale factor for all assets

    # Scale images dynamically
    menu_background = pygame.transform.scale(
        menu_background,
        (int(menu_background.get_width() * scale_y),
         int(menu_background.get_height() * scale_y))
    )

    update = pygame.transform.scale(
        update,
        (int(update.get_width() * scale_y), int(update.get_height() * scale_y))
    )

    # Scale fonts dynamically

    AudioMute = pygame.image.load(os.path.join(
        "Assets", "Sprites", "Audio-Mute.png"))
    AudioUnmute = pygame.image.load(os.path.join(
        "Assets", "Sprites", "Audio-Unmute.png"))
    AudioMute = pygame.transform.scale(AudioMute, (int(
        AudioMute.get_width() * scale_y), int(AudioMute.get_height() * scale_y)))
    AudioUnmute = pygame.transform.scale(AudioUnmute, (int(
        AudioUnmute.get_width() * scale_y), int(AudioUnmute.get_height() * scale_y)))
    AudioMuteRect = AudioMute.get_rect(
        topleft=(screen_width - AudioMute.get_width(), 0))

    # Render scaled text
    title = TitleFont.render('Ink & Incantations', True, (255, 208, 128))
    subtitle = SpeechFont.render('Cards of Chaos', True, (255, 255, 255))
    play = SpeechFont.render('New Game', True, (255, 255, 255))
    Continue = SpeechFont.render('Continue', True, (255, 255, 255))
    Collection = SpeechFont.render('Collection', True, (255, 255, 255))
    warning = "Warning: This game is work in progress, some features are incomplete"
    _quit = SpeechFont.render('Quit', True, (255, 255, 255))

    AudioHoverUn = SpeechFont.render('Audio: Unmuted', False, (255, 255, 255))
    AudioHoverUnRect = AudioHoverUn.get_rect(
        topleft=(screen_width - AudioMute.get_width(), 0))
    AudioHoverMu = SpeechFont.render('Audio: Muted', False, (255, 255, 255))
    AudioHoverMuRect = AudioHoverMu.get_rect(
        topleft=(screen_width - AudioMute.get_width(), 0))

    # Center elements dynamically
    title_rect = title.get_rect(
        center=(screen_width // 2, screen_height * 0.3))
    
    subtitle_rect = subtitle.get_rect(
        center=(screen_width // 2, screen_height * 0.34))
    
    # Drop shadow for title and subtitle
    shadow_offset = int(5* scale_y)  # Offset for the shadow
    title_shadow = TitleFont.render('Ink & Incantations', True, (0, 0, 0))
    subtitle_shadow = SpeechFont.render('Cards of Chaos', True, (0, 0, 0))
    title_shadow.set_alpha(150)  # Make shadow semi-transparent
    subtitle_shadow.set_alpha(150)  # Make shadow semi-transparent
    title_shadow_rect = title_shadow.get_rect(
        center=(screen_width // 2 + shadow_offset, screen_height * 0.3 + shadow_offset))
    subtitle_shadow_rect = subtitle_shadow.get_rect(
        center=(screen_width // 2 + shadow_offset, screen_height * 0.34 + shadow_offset))
    


    # Some nerdy stuff going on here, we dont show continue if no mod save exists
    # but if it does, we show continue and move the other buttons down
    if mod_save['World'] != 1 or mod_save['Level'] != 1:
        play_rect = play.get_rect(center=(screen_width // 2, screen_height * 0.55))
        continue_rect = Continue.get_rect(center=(screen_width // 2, screen_height * 0.5))
        collection_rect = Collection.get_rect(center=(screen_width // 2, screen_height * 0.6))
        quit_rect = _quit.get_rect(center=(screen_width // 2, screen_height * 0.65))
    else:
        play_rect = play.get_rect(center=(screen_width // 2, screen_height * 0.5))
        collection_rect = Collection.get_rect(center=(screen_width // 2, screen_height * 0.55))
        quit_rect = _quit.get_rect(center=(screen_width // 2, screen_height * 0.60))
    

    menu_background_rect = menu_background.get_rect(
        center=(screen_width // 2, screen_height // 2))

    Audio = AudioUnmute if SaveUpdater.decode_save_file()[
        'music'] else AudioMute

    # Discord RPC
    pid = os.getpid()
    client_id = "1336631328195481722"
    epoch = int(time.time())
    try:
        RPC, Connect = connect_rpc(client_id)
    except Exception as e:
        # print(f"Failed to connect to Discord RPC: {e}")
        Connect = False
        RPC = Presence(client_id)

    # Main menu and game logic
    running = True
    a = 0
    for i in range(255):
        gameDisplay.fill((0, 0, 0))
        a += 1
        Combat.render_wrapped_text(gameDisplay, warning, TitleFont, (255, 0, 0), a, pygame.Rect(
            screen_width * 0.025, screen_height * 0.4, screen_width * 0.95, screen_height * 0.2), line_spacing=5)
        pygame.display.update()

    gameDisplay.fill((0, 0, 0))
    Combat.render_wrapped_text(gameDisplay, warning, TitleFont, (255, 0, 0), a, pygame.Rect(
        screen_width * 0.025, screen_height * 0.4, screen_width * 0.95, screen_height * 0.2), line_spacing=5)
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
        Combat.render_wrapped_text(gameDisplay, warning, TitleFont, (255, 0, 0), a, pygame.Rect(
            screen_width * 0.025, screen_height * 0.4, screen_width * 0.95, screen_height * 0.2), line_spacing=5)

        pygame.display.update()

    a = 0
    v = 0
    for i in range(255):
        gameDisplay.fill((0, 0, 0))
        a += 1
        v += 0.004
        pygame.mixer.music.set_volume(v)
        title.set_alpha(a)
        subtitle.set_alpha(a)
        play.set_alpha(a)
        _quit.set_alpha(a)

        if mod_save['World'] != 1 or mod_save['Level'] != 1:
            Continue.set_alpha(a)
        Collection.set_alpha(a)
        menu_background.set_alpha(a)
        title_shadow.set_alpha(a)
        subtitle_shadow.set_alpha(a)
        Audio.set_alpha(a)
        update.set_alpha(a)
        gameDisplay.blit(menu_background, menu_background_rect.topleft)
        gameDisplay.blit(Audio, AudioMuteRect.topleft)
        gameDisplay.blit(update, update_rect.topleft)
        gameDisplay.blit(title_shadow, title_shadow_rect.topleft)
        gameDisplay.blit(subtitle_shadow, subtitle_shadow_rect.topleft)
        gameDisplay.blit(title, title_rect.topleft)
        gameDisplay.blit(subtitle, subtitle_rect.topleft)
        
        if mod_save['World'] != 1 or mod_save['Level'] != 1:
            gameDisplay.blit(Continue, continue_rect.topleft)
            gameDisplay.blit(Collection, collection_rect.topleft)
        else:
            gameDisplay.blit(Collection, collection_rect.topleft)
        gameDisplay.blit(play, play_rect.topleft)
        gameDisplay.blit(_quit, quit_rect.topleft)
        pygame.display.update()

    ai = 'enchanter'
    pygame.event.clear()
    if ModSave.decode_save_file()['World'] == 1 and ModSave.decode_save_file()['Level'] == 1:
        saveBool = True
    else:
        saveBool = False

    while running:
        if Connect:
            RPC.update(
                pid=pid,
                state="Preparing for battle",
                details=f"In the main menu",
                start=epoch,
                large_image="icon",
                large_text="A Glimpse into the mirror...")
        gameDisplay.blit(menu_background, menu_background_rect.topleft)
        gameDisplay.blit(Audio, AudioMuteRect.topleft)
        gameDisplay.blit(update, update_rect.topleft)  # Update message
        gameDisplay.blit(title_shadow, title_shadow_rect.topleft)
        gameDisplay.blit(title, title_rect.topleft)
        
        gameDisplay.blit(subtitle_shadow, subtitle_shadow_rect.topleft)
        gameDisplay.blit(subtitle, subtitle_rect.topleft)
        gameDisplay.blit(play, play_rect.topleft)
       
        if mod_save['World'] != 1 or mod_save['Level'] != 1:
            gameDisplay.blit(Continue, continue_rect.topleft)
            gameDisplay.blit(Collection, collection_rect.topleft)
        else:
            gameDisplay.blit(Collection, collection_rect.topleft)
        gameDisplay.blit(_quit, quit_rect.topleft)
        gameDisplay.blit(update, (screen_width * 0, screen_height * 0))
        gameDisplay.blit(Audio, AudioMuteRect.topleft)
        music.set_volume(1) if SaveUpdater.decode_save_file()[
            'music'] else music.set_volume(0)
        for event in pygame.event.get():

            if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                running = False

            if event.type == MOUSEBUTTONDOWN and event.button == 2:
                pass
                # print(event.pos)

            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                # Select opponent
                # PLAY button
                if play_rect.collidepoint(event.pos):
                    ModSave.resetRun()
                    a = 255
                    v = 1
                    for i in range(255):
                        gameDisplay.fill((0, 0, 0))
                        a -= 1
                        v -= 0.004
                        pygame.mixer.music.set_volume(v)
                        title.set_alpha(a)
                        subtitle.set_alpha(a)
                        play.set_alpha(a)
                        _quit.set_alpha(a)
                        menu_background.set_alpha(a)

                        Continue.set_alpha(a)
                        Collection.set_alpha(a)
                        title_shadow.set_alpha(a)
                        subtitle_shadow.set_alpha(a)
                        Audio.set_alpha(a)
                        update.set_alpha(a)
                        gameDisplay.blit(
                            menu_background, menu_background_rect.topleft)
                        gameDisplay.blit(title, title_rect.topleft)

                        gameDisplay.blit(title_shadow, title_shadow_rect.topleft)
                        gameDisplay.blit(subtitle_shadow, subtitle_shadow_rect.topleft)
                        gameDisplay.blit(play, play_rect.topleft)
                        gameDisplay.blit(subtitle, subtitle_rect.topleft)
                        
                        if mod_save['World'] != 1 or mod_save['Level'] != 1:
                            gameDisplay.blit(Continue, continue_rect.topleft)
                            gameDisplay.blit(Collection, collection_rect.topleft)
                        else:
                            gameDisplay.blit(Collection, collection_rect.topleft)
                        gameDisplay.blit(Audio, AudioMuteRect.topleft)
                        gameDisplay.blit(update, update_rect.topleft)
                        gameDisplay.blit(_quit, quit_rect.topleft)
                        pygame.time.delay(1)
                        pygame.display.update()

                        # Call the story manager for new game here
                        #mute music
                        music.stop()
                        StoryManager.begin_story_mode(gameDisplay)

                    music = pygame.mixer.Sound(os.path.join(
                        "Assets", "Music", "Main_" + random.choice(["1", "2", "3"]) + ".mp3"))
                # QUIT button
                elif quit_rect.collidepoint(event.pos):
                    running = False
                # CONTINUE button
                elif mod_save['World'] != 1 and mod_save['Level'] != 1 and continue_rect.collidepoint(event.pos):
                    a = 255
                    v = 1
                    for i in range(255):
                        gameDisplay.fill((0, 0, 0))
                        a -= 1
                        v -= 0.004
                        pygame.mixer.music.set_volume(v)
                        title.set_alpha(a)
                        subtitle.set_alpha(a)
                        play.set_alpha(a)
                        _quit.set_alpha(a)

                        Continue.set_alpha(a)
                        Collection.set_alpha(a)
                        menu_background.set_alpha(a)
                        title_shadow.set_alpha(a)
                        subtitle_shadow.set_alpha(a)
                        Audio.set_alpha(a)
                        update.set_alpha(a)
                        gameDisplay.blit(
                            menu_background, menu_background_rect.topleft)
                        gameDisplay.blit(title, title_rect.topleft)

                        gameDisplay.blit(title_shadow, title_shadow_rect.topleft)
                        gameDisplay.blit(subtitle_shadow, subtitle_shadow_rect.topleft)
                        gameDisplay.blit(play, play_rect.topleft)
                        gameDisplay.blit(subtitle, subtitle_rect.topleft)
                        
                        if mod_save['World'] != 1 or mod_save['Level'] != 1:
                            gameDisplay.blit(Continue, continue_rect.topleft)
                            gameDisplay.blit(Collection, collection_rect.topleft)
                        else:
                            gameDisplay.blit(Collection, collection_rect.topleft)
                        gameDisplay.blit(Audio, AudioMuteRect.topleft)
                        gameDisplay.blit(update, update_rect.topleft)
                        gameDisplay.blit(_quit, quit_rect.topleft)
                        pygame.time.delay(1)
                        pygame.display.update()
                    
                    # mute music
                    music.stop()
                    StoryManager.resume_from_save(gameDisplay)

                    music = pygame.mixer.Sound(os.path.join(
                        "Assets", "Music", "Main_" + random.choice(["1", "2", "3"]) + ".mp3"))
                    # Call the story manager for continue here
                # COLLECTION button
                elif collection_rect.collidepoint(event.pos):
                    # Calls the card collection manager here, this should show guiled cards
                    StoryManager.SeeCollection(gameDisplay)
                elif AudioMuteRect.collidepoint(event.pos):
                    save = SaveUpdater.decode_save_file()
                    save['music'] = False if save['music'] else True
                    SaveUpdater.encode_save_file(save)
                    Audio = AudioUnmute if save['music'] else AudioMute
        if event.type == MOUSEMOTION:
            if AudioMuteRect.collidepoint(event.pos):
                pygame.draw.rect(gameDisplay, (0, 0, 0), AudioHoverUn.get_rect(topright=event.pos)) if SaveUpdater.decode_save_file()[
                    'music'] else pygame.draw.rect(gameDisplay, (0, 0, 0), AudioHoverMu.get_rect(topright=event.pos))
                gameDisplay.blit(AudioHoverUn, AudioHoverUn.get_rect(topright=event.pos)) if SaveUpdater.decode_save_file()[
                    'music'] else gameDisplay.blit(AudioHoverMu, AudioHoverMu.get_rect(topright=event.pos))

            if update_rect.collidepoint(event.pos):
                pygame.draw.rect(gameDisplay, (0, 0, 0),
                                 updateHover.get_rect(topleft=event.pos))
                gameDisplay.blit(
                    updateHover, updateHover.get_rect(topleft=event.pos))


        # Debug rect!!!
        # Drect = pygame.Rect(0, 0, screen_width, screen_height)
        # pygame.draw.rect(gameDisplay, (255, 0, 0), Drect, 1)
        
        pygame.display.flip()
        gameDisplay.fill((0, 0, 0))
    os._exit(0)
    RPC.close() if not Connect else None
    pygame.quit() # Exit the program