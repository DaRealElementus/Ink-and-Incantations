# pip installed/default libs
import time
import os
import multiprocessing
import ctypes
import random

import requests


import Units
import Combat
import SaveUpdater


# pip install/imported libs
# auto pip install if missing
try:
    import pygame
    from pygame.locals import *
    from pypresence import Presence, exceptions
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
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/DaRealElementus/Ink-and-Incantations/refs/heads/OnlinePVPOfficial-mod/Online%20Mode/Version.txt"


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
    except exceptions as e:  # Catches Discord-related issues
        # print(f"Failed to connect: {e}")
        pass
    except Exception as e:
        # print(f"Failed to connect: {e}")
        pass


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
        elif save_data['modded']:
            text = font.render(
                "This save file is modded, and thus invalid", True, (255, 0, 0))
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


    DEFAULT_ADDR = 'http://127.0.0.1'
    DEFAULT_PORT = '54321'
    # Initialize Pygame
    pygame.init()
    pygame.font.init()
    pygame.mixer.init()

    # Get screen dimensions dynamically
    screen_width, screen_height = get_physical_screen_resolution() if os.name == 'nt' else (
        pygame.display.Info().current_w, pygame.display.Info().current_h)
    screen_height, screen_width = 720, 1280
    scale_x = screen_width / 1536
    scale_y = screen_height / 864
    # for all assets, use y scaling <- this is for ultrawide support

    # print(scale_x, scale_y)
    # print(screen_width, screen_height)
    # Initialize display
    icon = pygame.image.load(os.path.join("Assets", "Icon.png"))
    pygame.display.set_icon(icon)
    gameDisplay = pygame.display.set_mode((screen_width, screen_height), flags)
    pygame.display.set_caption('Ink and Incantations')
    gameDisplay.fill((0, 0, 0))

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

    menu_background = pygame.image.load(os.path.join("Assets", "Openbook.png"))

    # Load music
    music = pygame.mixer.Sound(os.path.join(
        "Assets", "Music", "Main_" + random.choice(["1", "2", "3"]) + ".mp3"))
    music.set_volume(1)  # Set volume based on saved state
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
    title = TitleFont.render('Ink & Incantations', True, (255, 0, 255))
    play = SpeechFont.render('MATCHMAKE', True, (255, 255, 255))
    subtitle = SpeechFont.render('Online Mode', True, (255, 255, 255))
    searching = SpeechFont.render('Searching for Match...', True, (255, 255, 255))
    warning = "Warning: This Expansion is work in progress, some features are incomplete"
    _quit = SpeechFont.render('QUIT', True, (255, 255, 255))


    AudioHoverUn = SpeechFont.render('Audio: Unmuted', False, (255, 255, 255))
    AudioHoverUnRect = AudioHoverUn.get_rect(
        topleft=(screen_width - AudioMute.get_width(), 0))
    AudioHoverMu = SpeechFont.render('Audio: Muted', False, (255, 255, 255))
    AudioHoverMuRect = AudioHoverMu.get_rect(
        topleft=(screen_width - AudioMute.get_width(), 0))

    # Center elements dynamically
    title_rect = title.get_rect(
        center=(screen_width // 2, screen_height * 0.3))
    play_rect = play.get_rect(center=(screen_width // 2, screen_height * 0.5))
    subtitle_rect = subtitle.get_rect(
        center=(screen_width // 2, title_rect.bottom + (10 * scale_y)))
    searchin_rect = searching.get_rect(center=(screen_width // 2, screen_height * 0.5))
    quit_rect = _quit.get_rect(
        center=(screen_width // 2, screen_height * 0.55))
    menu_background_rect = menu_background.get_rect(
        center=(screen_width // 2, screen_height // 2))

    Audio = AudioUnmute

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
        menu_background.set_alpha(a)
        Audio.set_alpha(a)
        update.set_alpha(a)
        gameDisplay.blit(menu_background, menu_background_rect.topleft)
        gameDisplay.blit(Audio, AudioMuteRect.topleft)
        gameDisplay.blit(update, update_rect.topleft)
        gameDisplay.blit(title, title_rect.topleft)
        gameDisplay.blit(subtitle, subtitle_rect.topleft)
        gameDisplay.blit(play, play_rect.topleft)
        gameDisplay.blit(_quit, quit_rect.topleft)
        pygame.display.update()

    pygame.event.clear()

    while running:
        if Connect:
            RPC.update(
                pid=pid,
                state="Preparing for battle",
                details=f"Searching the Libary",
                start=epoch,
                large_image="icon",
                large_text="The Enchanters Book awaits....")
        gameDisplay.blit(menu_background, menu_background_rect.topleft)
        gameDisplay.blit(Audio, AudioMuteRect.topleft)
        gameDisplay.blit(update, update_rect.topleft)  # Update message
        gameDisplay.blit(title, title_rect.topleft)
        gameDisplay.blit(subtitle, subtitle_rect.topleft)
        gameDisplay.blit(play, play_rect.topleft)
        gameDisplay.blit(_quit, quit_rect.topleft)
        # Update message
        gameDisplay.blit(update, (screen_width * 0, screen_height * 0))
        gameDisplay.blit(Audio, AudioMuteRect.topleft)
        music.set_volume(1)
        for event in pygame.event.get():

            if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                running = False

            if event.type == MOUSEBUTTONDOWN and event.button == 2:
                pass
                # print(event.pos)

            if event.type == MOUSEBUTTONDOWN and event.button == 1:
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
                        subtitle.set_alpha(a)
                        play.set_alpha(a)
                        _quit.set_alpha(a)
                        menu_background.set_alpha(a)
                        Audio.set_alpha(a)
                        update.set_alpha(a)
                        gameDisplay.blit(
                            menu_background, menu_background_rect.topleft)
                        gameDisplay.blit(title, title_rect.topleft)
                        gameDisplay.blit(subtitle, subtitle_rect.topleft)
                        gameDisplay.blit(play, play_rect.topleft)
                        gameDisplay.blit(Audio, AudioMuteRect.topleft)
                        gameDisplay.blit(update, update_rect.topleft)
                        gameDisplay.blit(_quit, quit_rect.topleft)
                        pygame.time.delay(1)
                        pygame.display.update()
                    pygame.time.delay(1000)
                    music.stop()
                    gameDisplay.fill((0, 0, 0))
                    resp = {'Success':None}
                    while not resp['Success']:
                        resp = (requests.get(f"{DEFAULT_ADDR}:{DEFAULT_PORT}/queue-up")).json()
                    q_position = resp['Position']
                    resp = {'RoomID':None}
                    cancel = False
                    while not type(resp['RoomID']) == type(1) and not cancel:

                        gameDisplay.fill((0, 0, 0))
                        gameDisplay.blit(searching, searchin_rect.topleft)
                        pygame.display.flip()
                        resp = requests.post(f"{DEFAULT_ADDR}:{DEFAULT_PORT}/check-queue", json={
                            'Position':q_position
                        }).json()
                        # print(resp)
                        resp['RoomID'] = int(resp['RoomID']) if resp['RoomID'] else None
                        time.sleep(0.1)
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                                cancel = True
                                resp['RoomID'] = None
                                break

                    PlayID = requests.post(f"{DEFAULT_ADDR}:{DEFAULT_PORT}/join-room", json={'RoomID':resp['RoomID']}).json()['PlayerID']

                    state = requests.post(f"{DEFAULT_ADDR}:{DEFAULT_PORT}/get-state", json={'RoomID':resp['RoomID']}).json()['State']

                    if not cancel:
                        Again = Combat_loader.BatStart(resp["RoomID"], PlayID, gameDisplay, Connect, RPC, pid, Unit_loader, SaveUpdater, [
                                                    scale_x, scale_y], [screen_width, screen_height], state)
                    music = pygame.mixer.Sound(os.path.join(
                        "Assets", "Music", "Main_" + random.choice(["1", "2", "3"]) + ".mp3"))
                    a = 255
                    title.set_alpha(a)
                    subtitle.set_alpha(a)
                    play.set_alpha(a)
                    _quit.set_alpha(a)
                    menu_background.set_alpha(a)
                    Audio.set_alpha(a)
                    update.set_alpha(a)
                # QUIT button
                elif quit_rect.collidepoint(event.pos):
                    running = False

        if event.type == MOUSEMOTION:
            # Selector: Show names of villains on hover, each villain occupies 1/3 of the selector's width

            if update_rect.collidepoint(event.pos):
                pygame.draw.rect(gameDisplay, (0, 0, 0),
                                 updateHover.get_rect(topleft=event.pos))
                gameDisplay.blit(
                    updateHover, updateHover.get_rect(topleft=event.pos))

        mouseloc = pygame.mouse.get_pos()

        # Debug rect!!!
        # Drect = pygame.Rect(0, 0, screen_width, screen_height)
        # pygame.draw.rect(gameDisplay, (255, 0, 0), Drect, 1)

        pygame.display.flip()
        gameDisplay.fill((0, 0, 0))
