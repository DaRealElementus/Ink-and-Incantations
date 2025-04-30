import os
import subprocess
import pygame
import sys

"""
Huge thank you to Liam for the idea and the code for this launcher. They wanted to break my game with their cheats, so they made this launcher
for easier testing and modding. They then provided it to me for free, and I am eternally grateful for that.

For marking, do not mark this code. It is not mine, and I do not want to take credit for it. I am only using it to make my own and everyone else who wants to work on this lives easier easier.
"""

def run_script(script_dir, script_name="Launcher.py"):
    pyver = "python" if os.name == "nt" else "python3" 
    try:
        subprocess.Popen([pyver, script_name], cwd=script_dir)
    except:
        subprocess.Popen(["python3", script_name], cwd=script_dir) # Despite the pyver line, clients using MS Store python launch through unix-like naming
    pygame.quit()
    sys.exit()

def main():
    mods_dir = "mods"
    base_dir = "base"
    font_path = os.path.join("base", "Assets", "Fonts", "Books-Vhasenti.ttf")

    # Get available mods
    # Check if mods directory exists
    if not os.path.exists(mods_dir):
        mods = []
    else:
        mods = [
            d for d in os.listdir(mods_dir)
            if os.path.isdir(os.path.join(mods_dir, d)) and os.path.isfile(os.path.join(mods_dir, d, "Launcher.py"))
        ]

    # If there's only the base game, no point in running the window
    if not mods:
        run_script(base_dir)
        return

    # If mods are present, show window
    pygame.init()
    screen = pygame.display.set_mode((600, 400))
    pygame.display.set_caption("I&I preloader by Liam")

    # Load fonts
    if os.path.isfile(font_path):
        title_font = pygame.font.Font(font_path, 48)
        button_font = pygame.font.Font(font_path, 28)
    else:
        title_font = pygame.font.SysFont(None, 48)
        button_font = pygame.font.SysFont(None, 28)

    clock = pygame.time.Clock()

    options = [("Base Game", base_dir)] + [(mod, os.path.join(mods_dir, mod)) for mod in mods]

    buttons = []
    spacing = 20
    btn_width = 500
    btn_height = 50
    start_y = 100

    for i, (name, path) in enumerate(options):
        rect = pygame.Rect(50, start_y + i * (btn_height + spacing), btn_width, btn_height)
        buttons.append((rect, name, path))

    while True:
        screen.fill((0, 0, 0))

        # finally got the title to render
        title_text = title_font.render("Ink And Incantations", True, (255, 255, 255))
        screen.blit(title_text, (screen.get_width() // 2 - title_text.get_width() // 2, 30))

        for rect, name, _ in buttons:
            pygame.draw.rect(screen, (120, 0, 120), rect, border_radius=8)
            text = button_font.render(name, True, (255, 255, 255))
            screen.blit(text, (rect.x + 10, rect.y + 10))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for rect, name, path in buttons:
                        if rect.collidepoint(event.pos):
                            print(f"Launching: {name}")
                            run_script(path)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()  