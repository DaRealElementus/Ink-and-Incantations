"""Story Manager for Cards of Chaos DLC

Handles animations and story sequences including dialogue, cutscenes, interactable cinematics, vendors, NPCs, and more."""


from ast import Tuple
from tkinter.font import Font

from matplotlib.backend_bases import MouseButton
from matplotlib.colors import CenteredNorm
from numpy import full
import Combat
import pygame
import os
from pygame.locals import *
import random
import math
import typing

import Units
import ModSave
import CardManager



"""
This is the timeline of events that are to occur in the story mode

some notes beforehand:
the player starts a run with only their guilded cards (They can only guild one card at the end of a run, either via death or victory, victory guilds current deck)
the game is played in a mirror, this means some assets should be mirrored, however, some things also dont need to be mirrored as they are reflections themselves

the player starts with 3 lives
the player starts with 0 gold

gold is determined by dividing score by 1000 and rounding down

key characters:
Clockwork (main opponent, trapped in the mirror)
Clockwork roleplays as most of the NPCs. Final boss is Clockwork

Enchanter (first opponent)
Enchanter kinda acts like a a**hole, this is cuz he trapped Clockwork in the mirror

Monarch (second opponent)
Monarch is nice, she wants to defend everyone and is seen as untouchable.

Madman (third opponent)
madman is essentially clockwork before he got trapped in the mirror, he talks about clocks because of this

Vendor (sells items to the player)
Vendor is another roleplayed version of clockwork, he is 'neutral', but he also has a massive moment where clockwork reveals himself

timeline of events:

1. start of the run, player has 3 lives, we also fade in the deck of cards that the player obtains
2. the player has a moment to prepare their deck


3. player fights enchanter 1
4. if the player wins, they go to the vendor, if they lose, they lose a life and go to the vendor
5. player fights enchanter 2
6. introduce the vendors gambling game. where the player can gamble their gold
7. if the player wins, they go to the vendor, if they lose, they lose a life and go to the vendor
8. player fights enchanter 3

9. clockwork likes this game and thus restores all the players lives
10. player fights monarch 1
11. if the player wins, they go to the vendor, if they lose, they lose a life and go to the vendor
12. player fights monarch 2
13. players can now lose their health for gold at the vendor gambling game
14. if the player wins, they go to the vendor, if they lose, they lose a life and go to the vendor
15. player fights monarch 3

16. clockwork is getting bored of this, he restores all the players lives again

17. player fights madman 1
18. if the player wins, they go to the vendor, if they lose, they lose
19. player fights madman 2
20. the player has their final chance at vendor gambling game + shop

21. clockwork is done playing around, he restores all the players lives again
22. player fights clockwork 1
23. player fights clockwork 2
24. player fights clockwork 3

25. end of the run, if the player has reached this point, they win the game and thus we guild their deck


IF THE PLAYER LOSES ALL THEIR LIVES, THEY DIE AND THE RUN ENDS, HOWEVER,
FOR 50 GOLD, THEY CAN UNGUILD A CARD AND CONTINUE THE RUN


the player can always change their deck at the vendor"""

enchanter_img = pygame.image.load(os.path.join("Enemy_Faces", "Enchanter.png"))
monarch_img = pygame.image.load(os.path.join("Enemy_Faces", "Monarch.png"))
madman_img = pygame.image.load(os.path.join("Enemy_Faces", "Madman.png"))
vendor_img = pygame.image.load(os.path.join("Enemy_Faces", "Vendor.png"))


diologue_array=["You approach a mirror and see a familiar face.", # start of game
                "I hate him, his smile, all to similar to yours", #enchanter
                "You think you can beat him? you couldnt even beat me.",
                "You are nothing but a reflection of my world.",

                "Get out.", #enchanter 1
                "Quick, while hes distracted, grab some things to help you on your travels", #vendor
                "You again? I thought I told you to leave.", #enchanter 2
                "Interesting play, you have potential.", #vendor
                "No more shackles now, I am free to do as I please.", #enchanter 3
                "Go away, you foul wretch.", #enchanter defeat

                "I like this." #clockwork

                "Ignore him, he is a sad old man who lost everything", #monarch
                "let me train you, I can make you stronger", #monarch 1
                "You have potential, but you lack discipline.", #vendor
                "You fight well, but you are still weak.", #monarch 2
                "Mmmmm, Your soul is still fresh...", #vendor
                "I will not hold back anymore.", #monarch 3
                "I cannot help you anymore, go, free us all.", #monarch defeat

                "Now that was boring to watch" #clockwork

                "A stage, filled with sickness. its your fault", #madman
               
                "Poor man, he doesnt realise what he will become", #vendor
                "I feel it all, the shift, the change, the power.", #madman 2
                "its best he doesnt see this next bit.", #vendor

                "I dont want to betray you, but you cannot set them free", #clockwork
                "This ends now.", #clockwork 1
                "Youve been fighting versions of me this whole time.", #clockwork 2 p1
                "what makes you think that I would give those cards freely", #clockwork 2 p2
                "This mirror is my prison, but also my domain.", #clockwork 3

                "How about a deal, I let you keep a card, you let me keep my toys.",
                "Deal?",
                "This isnt your choice.", # if the player refuses to guild a card, one is guilded for them randomly
                "My advice, dont stare at my reflection." #end of game
                ]



Battleground = pygame.image.load(os.path.join(
        "Assets", "Sprites", "Mirror.png"))

enchanter_img.set_colorkey((0,255,0))
monarch_img.set_colorkey((0,255,0))
madman_img.set_colorkey((0,255,0))
vendor_img.set_colorkey((0,255,0))
enchanter_img.set_alpha(100)
monarch_img.set_alpha(100)
madman_img.set_alpha(100)
vendor_img.set_alpha(100)


scale_x, scale_y = 1, 1
screen_x, screen_y = 1, 1


def get_curved_positions(center_x, center_y, radius, num_cards, arc_angle_deg):
    positions = []
    start_angle = math.pi/2 - math.radians(arc_angle_deg)/2
    angle_step = math.radians(arc_angle_deg) / (num_cards - 1 if num_cards > 1 else 1)
    for i in range(num_cards):
        angle = start_angle + i * angle_step
        x = center_x + radius * math.cos(angle)
        y = center_y - radius * math.sin(angle)
        positions.append((int(x), int(y)))
    return positions


# --- Story helpers (persist after every change) ---
def _save_load() -> dict:
    s = ModSave.decode_save_file()
    if not isinstance(s, dict):
        s = {}
    return s

def _save_commit(save: dict):
    try:
        ModSave.encode_save_file(save)
    except Exception:
        pass

def _reduce_life(save: dict, amount: int = 1):
    save['lives'] = max(0, int(save.get('lives', 0)) - amount)
    _save_commit(save)

def _restore_all_lives(save: dict, amount: int = 3):
    save['lives'] = int(amount)
    _save_commit(save)

def guild_one_card_at_run_end(save: dict, chosen_card_id: int | None = None) -> int | None:
    """
    Guild exactly one card at the end of a run. Prefer deck cards; persist immediately.
    """
    if not isinstance(save, dict):
        return None
    save.setdefault('Cards', [])
    save.setdefault('Deck', [])
    # map existing cards
    card_map = {cid: bool(flag) for cid, flag in save['Cards']}
    # candidates: deck then all
    deck_candidates = [cid for cid in save.get('Deck', []) if not card_map.get(cid, False)]
    all_candidates = [cid for cid, flag in save['Cards'] if not flag]
    chosen = None
    if chosen_card_id is not None:
        if chosen_card_id in save.get('Deck', []) and not card_map.get(chosen_card_id, False):
            chosen = chosen_card_id
        elif chosen_card_id in [c for c, _ in save['Cards']] and not card_map.get(chosen_card_id, False):
            chosen = chosen_card_id
    if chosen is None:
        if deck_candidates:
            chosen = random.choice(deck_candidates)
        elif all_candidates:
            chosen = random.choice(all_candidates)
    if chosen is None:
        _save_commit(save)
        return None
    card_map[chosen] = True
    # rebuild Cards preserving order
    existing_order = [cid for cid, _ in save['Cards']]
    new_cards = []
    seen = set()
    for cid in existing_order:
        new_cards.append((cid, bool(card_map.get(cid, False))))
        seen.add(cid)
    for cid, flag in card_map.items():
        if cid not in seen:
            new_cards.append((cid, bool(flag)))
    save['Cards'] = new_cards
    _save_commit(save)
    return chosen

# --- fight wrapper ---
def _fight(opponent_key: str, gamedisplay: pygame.Surface, save: dict) -> bool:
    """
    Run a combat against opponent_key. Attempts to call Combat.BatStart if available,
    else falls back to a deterministic RNG result. Persists no changes here; caller must handle rewards/lives.
    """
    try:
        # map opponent_key -> Ai string used by Combat.BatStart
        if opponent_key.lower().startswith("enchanter"):
            Ai = 'enchanter'
            # enchanter hand is fool, high priestess, empress, magician
            opponent_hand = ['fool', 'high priestess', 'empress', 'magician']
        elif opponent_key.lower().startswith("monarch"):
            Ai = 'monarch'
            # monarch hand is emperor, justice, lovers, strength
            opponent_hand = ['emperor', 'justice', 'lovers', 'strength']

        elif opponent_key.lower().startswith("madman"):
            Ai = 'madman'
            # madman hand is death, hanged, tower, chariot
            opponent_hand = ['death', 'hanged', 'tower', 'chariot']
        elif opponent_key.lower().startswith("clockwork"):
            Ai = 'clockwork'  # no explicit clockwork AI; reuse enchanter behaviour
            # clockwork hand is moon, sun, star, world, judgement
            opponent_hand = ['moon', 'sun', 'star', 'world', 'judgement']
        else:
            Ai = 'enchanter'
            opponent_hand = ['fool', 'high priestess', 'empress', 'magician']
        Won, score = Combat.BatStart(Ai, gamedisplay, False, None, os.getpid(), Units, ModSave, [scale_x, scale_y], [screen_x, screen_y], opponent_hand)
        return bool(Won)
    except Exception:
        return False

# --- Shop enter implementation (simple, persists immediately) ---
class Shop:
    """A class for the shop in the story mode. Presents a GUI with the vendor's face inside the mirror
    and buttons for the two gamble options, deck editing and exit. All changes persist immediately.
    """
    def __init__(self, items: list):
        self.items = items

    def display(self, screen):
        # Placeholder kept for compatibility
        pass

    def gambling_game(self, cash, numwins):
        cash -= 1
        win = False
        if numwins > cash:
            outcome = random.randint(0, 1)
            if outcome:
                cash += 2
                numwins += 1
                win = True
        else:
            outcome = random.randint(0, 2)
            if outcome == 0:
                cash += 2
                numwins += 1
                win = True
        return cash, numwins, win

    def gamble_life_for_gold(self, lives, gold):
        """Spend 1 life for a 50% chance to get +1 gold. Returns (lives, gold, won)."""
        won = False
        if lives > 1:
            lives -= 1
            if random.randint(0, 1):
                gold += 1
                won = True
        return lives, gold, won

    def enter_shop(self, screen, save: dict):
        """
        GUI-driven shop:
          - Shows vendor face in the mirror
          - Buttons: Gold Gamble, Spend Life->Gold, Edit Deck, Exit
          - Keyboard shortcuts: 1=Gold Gamble, 2=Life->Gold, 3=Edit Deck, Esc=Exit
        Persists save after every action.
        """
        if not isinstance(save, dict):
            return
        _save_commit(save)

        w, h = screen.get_width(), screen.get_height()
        font = pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), max(16, int(scale_y * 26)))

        # Prepare battleground mirror and vendor face scaled to fit
        bg = pygame.transform.smoothscale(Battleground, (int(Battleground.get_width() * (h / 1000) * 1.1),
                                                        int(Battleground.get_height() * (h / 1000) * 1.1)))
        bg_rect = bg.get_rect(center=(w // 2, int(h * 0.38)))

        face_sz = (int(bg_rect.width * 0.5), int(bg_rect.height * 0.5))
        face_surf = pygame.transform.smoothscale(vendor_img, face_sz)
        face_rect = face_surf.get_rect(center=bg_rect.center)

        # Button layout: four buttons beneath mirror
        button_w = int(w * 0.28)
        button_h = max(36, int(scale_y * 48))
        gap = 12
        total_w = button_w * 2 + gap
        start_x = (w - total_w) // 2
        top_y = int(h * 0.7)

        btn_gold_rect = pygame.Rect(start_x, top_y, button_w, button_h)
        btn_life_rect = pygame.Rect(start_x + button_w + gap, top_y, button_w, button_h)
        btn_edit_rect = pygame.Rect(start_x, top_y + button_h + gap, button_w, button_h)
        btn_exit_rect = pygame.Rect(start_x + button_w + gap, top_y + button_h + gap, button_w, button_h)

        def draw_button(r: pygame.Rect, text: str, col_bg=(40, 40, 60), col_fg=(255, 255, 255)):
            pygame.draw.rect(screen, col_bg, r, border_radius=8)
            txt = font.render(text, True, col_fg)
            txt_r = txt.get_rect(center=r.center)
            screen.blit(txt, txt_r)

        running = True
        clock = pygame.time.Clock()
        while running:
            screen.fill((0, 0, 0))
            # Mirror + face
            screen.blit(bg, bg_rect)
            screen.blit(face_surf, face_rect)

            # Status
            gold_txt = font.render(f"Gold: {int(save.get('gold',0))}", True, (255, 220, 120))
            lives_txt = font.render(f"Lives: {int(save.get('lives',0))}", True, (200, 200, 255))
            screen.blit(gold_txt, (20, 20))
            screen.blit(lives_txt, (20, 20 + gold_txt.get_height() + 6))

            # Buttons with descriptions
            draw_button(btn_gold_rect, "Gold Gamble (-1 gold)")
            draw_button(btn_life_rect, "Spend 1 Life → 50% +1 gold")
            draw_button(btn_edit_rect, "Edit Deck")
            draw_button(btn_exit_rect, "Exit Shop")

            # Small helper hint
            hint = font.render("1=Gold Gamble  2=Life→Gold  3=Edit Deck  Esc=Exit", True, (160,160,160))
            screen.blit(hint, (w//2 - hint.get_width()//2, btn_exit_rect.bottom + 12))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    elif event.key == K_1:
                        # Gold gamble
                        g = int(save.get('gold', 0))
                        nw = int(save.get('NumWins', 0))
                        if g > 0:
                            g, nw, won = self.gambling_game(g, nw)
                            save['gold'] = int(g)
                            save['NumWins'] = int(nw)
                            _save_commit(save)
                    elif event.key == K_2:
                        # Spend life -> gold
                        l = int(save.get('lives', 0))
                        g = int(save.get('gold', 0))
                        l, g, won = self.gamble_life_for_gold(l, g)
                        save['lives'] = int(l)
                        save['gold'] = int(g)
                        _save_commit(save)
                    elif event.key == K_3:
                        BuildDeck(screen, pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), max(12, int(scale_y * 24))))
                        save = _save_load()
                        _save_commit(save)
                elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    if btn_gold_rect.collidepoint((mx, my)):
                        g = int(save.get('gold', 0))
                        nw = int(save.get('NumWins', 0))
                        if g > 0:
                            g, nw, won = self.gambling_game(g, nw)
                            save['gold'] = int(g)
                            save['NumWins'] = int(nw)
                            _save_commit(save)
                    elif btn_life_rect.collidepoint((mx, my)):
                        l = int(save.get('lives', 0))
                        g = int(save.get('gold', 0))
                        l, g, won = self.gamble_life_for_gold(l, g)
                        save['lives'] = int(l)
                        save['gold'] = int(g)
                        _save_commit(save)
                    elif btn_edit_rect.collidepoint((mx, my)):
                        BuildDeck(screen, pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), max(12, int(scale_y * 24))))
                        save = _save_load()
                        _save_commit(save)
                    elif btn_exit_rect.collidepoint((mx, my)):
                        running = False

            clock.tick(60)

        _save_commit(save)
# --- Story flow: begin_story_mode and resume_from_save ---
def begin_story_mode(gamedisplay: pygame.Surface):
    """
    Linear story flow. Persist save after every important event.
    """
    save = _save_load()
    # Ensure fields
    save.setdefault('Deck', [])
    save.setdefault('Hand', [])
    save.setdefault('Cards', [])
    save.setdefault('World', 0)
    save.setdefault('Level', 0)
    save.setdefault('lives', 3)
    save.setdefault('gold', int(save.get('gold', 0)))
    _save_commit(save)

    # Start run
    save['World'] = 1
    save['Level'] = 0
    _save_commit(save)

    vendor = Shop([])

    # Preparation phase (player edits deck via BuildDeck UI)
    BuildDeck(gamedisplay, pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), max(12, int(scale_y * 30))))
    # BuildDeck persists deck/hand on exit
    save = _save_load()

    # Enchanter sequence (3 fights)
    for i in range(1, 4):
        save['Level'] = i
        _save_commit(save)
        # show dialogue from array if available
        idx = min(i+3, len(diologue_array)-1)
        dialogue(gamedisplay, pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), max(12, int(scale_y * 26))), "Enchanter", diologue_array[idx], 0.2)
        won = _fight(f"Enchanter_{i}", gamedisplay, save)
        if won:
            save['gold'] = int(save.get('gold',0)) + 10
            _save_commit(save)
        else:
            _reduce_life(save, 1)
        # vendor
        dialogue(gamedisplay, pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), max(12, int(scale_y * 24))), "Vendor", "A vendor appears.", 0.2)
        vendor.enter_shop(gamedisplay, save)
        save = _save_load()

    # Clockwork restores lives
    _restore_all_lives(save, 3)

    # Monarch sequence
    save['World'] = 2
    _save_commit(save)
    for i in range(1, 4):
        save['Level'] = 10 + i
        _save_commit(save)
        dialogue(gamedisplay, pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), max(12, int(scale_y * 26))), "Monarch", "Prepare yourself.", 0.2)
        won = _fight(f"Monarch_{i}", gamedisplay, save)
        if won:
            save['gold'] = int(save.get('gold',0)) + 20
            _save_commit(save)
        else:
            _reduce_life(save, 1)
        dialogue(gamedisplay, pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), max(12, int(scale_y * 24))), "Vendor", "Vendor time.", 0.2)
        vendor.enter_shop(gamedisplay, save)
        save = _save_load()

    # Restore again
    _restore_all_lives(save, 3)

    # Madman sequence
    save['World'] = 3
    _save_commit(save)
    for i in range(1, 4):
        save['Level'] = 20 + i
        _save_commit(save)
        dialogue(gamedisplay, pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), max(12, int(scale_y * 26))), "Madman", "Chaos awaits.", 0.2)
        won = _fight(f"Madman_{i}", gamedisplay, save)
        if won:
            save['gold'] = int(save.get('gold',0)) + 30
            _save_commit(save)
        else:
            _reduce_life(save, 1)
        dialogue(gamedisplay, pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), max(12, int(scale_y * 24))), "Vendor", "Vendor time.", 0.2)
        vendor.enter_shop(gamedisplay, save)
        save = _save_load()

    # Restore before final gauntlet
    _restore_all_lives(save, 3)

    # Clockwork fights (final)
    save['World'] = 4
    _save_commit(save)
    for i in range(1, 4):
        save['Level'] = 30 + i
        _save_commit(save)
        dialogue(gamedisplay, pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), max(12, int(scale_y * 26))), "Clockwork", "The mirror cracks.", 0.2)
        won = _fight(f"Clockwork_{i}", gamedisplay, save)
        if won:
            save['gold'] = int(save.get('gold',0)) + 50
            _save_commit(save)
        else:
            _reduce_life(save, 1)
            if save.get('lives', 0) <= 0:
                # run ended by death: persist and guild one card
                save['RunEnded'] = True
                _save_commit(save)
                guild_one_card_at_run_end(save)
                return

    # Victory: guild exactly one card
    chosen = guild_one_card_at_run_end(save)
    save['RunCompleted'] = True
    _save_commit(save)
    dialogue(gamedisplay, pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), max(12, int(scale_y * 26))), "None", "You have freed something from the mirror.", 0.2)

def resume_from_save(gamedisplay: pygame.Surface):
    """
    Resume flow based on save['World'] and ['Level'].
    Saves after every resumed event.
    """
    save = _save_load()
    world = int(save.get('World', 0))
    level = int(save.get('Level', 0))

    # If nothing to resume, start new
    if world <= 1:
        begin_story_mode(gamedisplay)
        return

    vendor = Shop([])

    if world == 2:
        # resume in Monarch sequence
        start_idx = 1
        if level >= 11:
            start_idx = min(3, level - 10)
        for i in range(start_idx, 4):
            save['Level'] = 10 + i
            _save_commit(save)
            dialogue(gamedisplay, pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), max(12, int(scale_y * 26))), "Monarch", "Resuming...", 0.2)
            won = _fight(f"Monarch_{i}", gamedisplay, save)
            if won:
                save['gold'] = int(save.get('gold',0)) + 20
                _save_commit(save)
            else:
                _reduce_life(save, 1)
            vendor.enter_shop(gamedisplay, save)
            save = _save_load()
        begin_story_mode(gamedisplay)
    elif world == 3:
        start_idx = 1
        if level >= 21:
            start_idx = min(3, level - 20)
        for i in range(start_idx, 4):
            save['Level'] = 20 + i
            _save_commit(save)
            dialogue(gamedisplay, pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), max(12, int(scale_y * 26))), "Madman", "Resuming...", 0.2)
            won = _fight(f"Madman_{i}", gamedisplay, save)
            if won:
                save['gold'] = int(save.get('gold',0)) + 30
                _save_commit(save)
            else:
                _reduce_life(save, 1)
            vendor.enter_shop(gamedisplay, save)
            save = _save_load()
        begin_story_mode(gamedisplay)
    elif world >= 4:
        start_idx = 1
        if level >= 31:
            start_idx = min(3, level - 30)
        for i in range(start_idx, 4):
            save['Level'] = 30 + i
            _save_commit(save)
            dialogue(gamedisplay, pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), max(12, int(scale_y * 26))), "Clockwork", "Resuming final gauntlet...", 0.2)
            won = _fight(f"Clockwork_{i}", gamedisplay, save)
            if won:
                save['gold'] = int(save.get('gold',0)) + 50
                _save_commit(save)
            else:
                _reduce_life(save, 1)
                if save.get('lives', 0) <= 0:
                    save['RunEnded'] = True
                    _save_commit(save)
                    guild_one_card_at_run_end(save)
                    return
        chosen = guild_one_card_at_run_end(save)
        save['RunCompleted'] = True
        _save_commit(save)
def diologueTest(gamedisplay :pygame.Surface, font: Font):
    """Testing the diologue animation"""
    testtext = "Testing testing 1234 I cant count to 5 or 6"

    for i in range(len(testtext)):

        currentText:pygame.Surface = font.render(''.join(list(testtext)[:i]), True, (255,255,255))
        currentText_box = currentText.get_rect(center=(gamedisplay.get_width()//2, gamedisplay.get_height()//2))
        gamedisplay.fill((0,0,0))
        gamedisplay.blit(currentText, currentText_box)
        pygame.time.delay(25)
        pygame.display.flip()
    fulltext = font.render(testtext, True, (255, 255, 255))
    fulltext_rect = fulltext.get_rect(center=(gamedisplay.get_width()//2, gamedisplay.get_height()//0.75))
    pygame.time.delay(100)
    running = True
    while running:
        gamedisplay.fill((0,0,0))
        gamedisplay.blit(fulltext, fulltext_rect)

        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                running = False
        pygame.time.delay(1)
        pygame.display.flip()
def cardTest(gamedisplay: pygame.Surface):
    card = CardManager.Justice()
    Guilded_card = CardManager.Justice(True)

    # Store original images
    card_img_orig = card.img
    guilded_img_orig = Guilded_card.img

    # Set fixed centers for both cards
    card_center = (gamedisplay.get_width() // 2 - card_img_orig.get_width(), gamedisplay.get_height() // 2)
    guilded_center = (gamedisplay.get_width() // 2 + guilded_img_orig.get_width(), gamedisplay.get_height() // 2)

    running = True
    while running:
        gamedisplay.fill((0,0,0))

        mouse_pos = pygame.mouse.get_pos()

        # Handle hover for card
        card_img = card_img_orig
        if pygame.Rect(0,0,card_img.get_width(),card_img.get_height()).move(card_center[0]-card_img.get_width()//2, card_center[1]-card_img.get_height()//2).collidepoint(mouse_pos):
            card_img = pygame.transform.scale(card_img_orig, (int(card_img_orig.get_width()*1.5), int(card_img_orig.get_height()*1.5)))
        card_rect = card_img.get_rect(center=card_center)

        # Handle hover for guilded card
        guilded_img = guilded_img_orig
        if pygame.Rect(0,0,guilded_img.get_width(),guilded_img.get_height()).move(guilded_center[0]-guilded_img.get_width()//2, guilded_center[1]-guilded_img.get_height()//2).collidepoint(mouse_pos):
            guilded_img = pygame.transform.scale(guilded_img_orig, (int(guilded_img_orig.get_width()*1.5), int(guilded_img_orig.get_height()*1.5)))
        guilded_rect = guilded_img.get_rect(center=guilded_center)

        gamedisplay.blit(card_img, card_rect)
        gamedisplay.blit(guilded_img, guilded_rect)

        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                running = False

        pygame.time.delay(1)
        pygame.display.flip()

def SeeCollection(gamedisplay: pygame.Surface):
    """Show the players collection of cards on a 3x6 grid, we hide the cursed cards"""

    save = ModSave.decode_save_file()
    cards:list[Tuple[int, bool]] = save['Cards']

    id_matrix = {id: False for id in [0,1,2,3,4,5,6,9,10,11,12,14,16,17,18,19,20,21]}
    for card in cards:
        if card[0] in id_matrix:
            if card[1]:
                id_matrix[card[0]] = 'Guilded'
            else:
                id_matrix[card[0]] = True
    

    # List of card IDs in grid order
    card_ids = [0,1,2,3,4,5,6,9,10,11,12,14,16,17,18,19,20,21,]
    # Map IDs to CardManager class names
    id_to_class = {
        0: 'Fool', 1: 'Magician', 2: 'HighPriestess', 3: 'Empress', 4: 'Emperor', 5: 'Hierophant', 6: 'Lovers',
        7: 'Chariot', 8: 'Justice', 9: 'Hermit', 10: 'Wheel', 11: 'Strength', 12: 'Hanged', 13: 'Death',
        14: 'Temperance', 15: 'Devil', 16: 'Tower', 17: 'Star', 18: 'Moon', 19: 'Sun', 20: 'Judgement', 21: 'World'
    }


    back_card = pygame.image.load(os.path.join('Assets','Cards','cards','_cardBack','_cardBack_2x.png'))
    image_matrix = []
    for id in card_ids:
        status = id_matrix[id]
        if status == 'Guilded':
            card_img = getattr(CardManager, id_to_class[id])(guilded=True).img
        elif status is True:
            card_img = getattr(CardManager, id_to_class[id])().img
        else:
            card_img = back_card
        image_matrix.append(card_img)
        


   

    # Now we have to make a 3x6 grid on the screen
        rows, cols = 3, 6
    cell_width, cell_height = back_card.get_width()*1.2, back_card.get_height()*1.2
    grid_width = cols * cell_width
    grid_height = rows * cell_height
    grid_x = (gamedisplay.get_width() - grid_width) // 2
    grid_y = (gamedisplay.get_height() - grid_height) // 2

    running = True
    pygame.event.clear()

    while running:
        gamedisplay.fill((0,0,0))
        grid_rects = []
        for row in range(rows):
            for col in range(cols):
                x = grid_x + col * cell_width
                y = grid_y + row * cell_height
                rect = pygame.Rect(x, y, cell_width, cell_height)
                grid_rects.append(rect)
        for i, rect in enumerate(grid_rects):
            if i < len(image_matrix):
                gamedisplay.blit(image_matrix[i], rect)
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                running = False

        pygame.time.delay(1)
        pygame.display.flip()

def BuildDeck(gamedisplay: pygame.Surface, font: Font):
    """Display the Deckbuilder (deck and hand are persisted using save['Deck'] and save['Hand'])."""

    save = ModSave.decode_save_file()
    if save is None:
        # Ensure a save exists
        try:
            ModSave.encode_save_file()
            save = ModSave.decode_save_file() or {}
        except Exception:
            save = {}

    cards: list[tuple] = save.get('Cards', [])
    # Build availability matrix
    id_matrix = {i: False for i in range(0, 22)}
    for card in cards:
        cid = card[0]
        if cid in id_matrix:
            if card[1] and cid not in (7, 8, 13, 15):
                id_matrix[cid] = 'Guilded'
            else:
                id_matrix[cid] = True

    # canonical id -> class map
    id_to_class = {
        0: 'Fool', 1: 'Magician', 2: 'HighPriestess', 3: 'Empress', 4: 'Emperor', 5: 'Hierophant', 6: 'Lovers',
        7: 'Chariot', 8: 'Justice', 9: 'Hermit', 10: 'Wheel', 11: 'Strength', 12: 'Hanged', 13: 'Death',
        14: 'Temperance', 15: 'Devil', 16: 'Tower', 17: 'Star', 18: 'Moon', 19: 'Sun', 20: 'Judgement', 21: 'World'
    }

    # unlocked ids in the same ordering as elsewhere
    card_ids = list(range(0, 22))
    unlocked_ids = []
    for cid in card_ids:
        if id_matrix.get(cid) == 'Guilded' or id_matrix.get(cid) is True:
            unlocked_ids.append(cid)

    # Load deck/hand from save (do not create a new save id)
    deck_ids = list(save.get('Deck', []))
    hand_ids = list(save.get('Hand', []))

    # If no saved deck/hand, default to first 4 -> deck, rest -> hand
    if not deck_ids and not hand_ids:
        deck_ids = unlocked_ids[:4]
        hand_ids = unlocked_ids[4:]
    else:
        # Sanitize lists: remove ids not unlocked, preserve order, then append remaining unlocked ids
        def sanitize_list(lst):
            return [cid for cid in lst if cid in unlocked_ids]

        deck_ids = sanitize_list(deck_ids)
        hand_ids = sanitize_list(hand_ids)

        # Ensure no duplicates between deck and hand
        combined = deck_ids + hand_ids
        seen = set()
        new_combined = []
        for cid in combined:
            if cid not in seen:
                new_combined.append(cid)
                seen.add(cid)

        # append any unlocked ids missing from combined
        for cid in unlocked_ids:
            if cid not in seen:
                new_combined.append(cid)
                seen.add(cid)

        # Re-split into deck (first 4) and hand (remainder)
        deck_ids = new_combined[:4]
        hand_ids = new_combined[4:]

    # Convert ids -> images
    back_card = pygame.image.load(os.path.join('Assets', 'Cards', 'cards', '_cardBack', '_cardBack_2x.png'))
    def img_for_id(cid):
        status = id_matrix.get(cid)
        if status == 'Guilded':
            return getattr(CardManager, id_to_class[cid])(guilded=True).img
        elif status is True:
            return getattr(CardManager, id_to_class[cid])().img
        else:
            return back_card

    deck = [img_for_id(cid) for cid in deck_ids]
    hand = [img_for_id(cid) for cid in hand_ids]

    card_w, card_h = back_card.get_width(), back_card.get_height()
    center_x = gamedisplay.get_width() // 2

    hand_center_x = center_x - (card_w // 4)
    deck_y = int(gamedisplay.get_height() // 2 - card_h - 40)
    hand_center_y = int(gamedisplay.get_height() * 0.85)
    deck_spacing = card_w + 40
    deck_start_x = center_x - ((deck_spacing * 3) // 2)

    deck_radius = 180
    arc_angle = 180  # degrees

    running = True
    selected_deck_idx = None

    while running:
        gamedisplay.fill((0, 0, 0))

        # Draw deck
        deck_rects = []
        mouse_pos = pygame.mouse.get_pos()
        for i, img in enumerate(deck):
            x = deck_start_x + i * deck_spacing
            rect = img.get_rect(center=(x, deck_y))
            deck_rects.append(rect)
            gamedisplay.blit(img, rect)
            if selected_deck_idx == i:
                pygame.draw.rect(gamedisplay, (255, 255, 0), rect, 4)

        # Draw hand (curved)
        hand_positions = get_curved_positions(hand_center_x, hand_center_y, deck_radius, len(hand), arc_angle)
        hand_rects = []
        min_dist = float('inf')
        closest_idx = None
        for i, pos in enumerate(hand_positions):
            dist = math.hypot(mouse_pos[0] - pos[0], mouse_pos[1] - pos[1])
            if dist < min_dist:
                min_dist = dist
                closest_idx = i

        for i, (img, pos) in enumerate(zip(hand, hand_positions)):
            if i == closest_idx and min_dist < max(img.get_width(), img.get_height()):
                hover_radius = deck_radius + 180
                hover_pos = get_curved_positions(center_x, hand_center_y, hover_radius, len(hand), arc_angle)[i]
                img_scaled = pygame.transform.smoothscale(img, (int(card_w * 1.2), int(card_h * 1.2)))
                rect = img_scaled.get_rect(center=hover_pos)
                gamedisplay.blit(img_scaled, rect)
            else:
                rect = img.get_rect(center=pos)
                gamedisplay.blit(img, rect)
            hand_rects.append(rect)

        # Continue button
        text = font.render("Continue", True, (255, 255, 255))
        text_rect = text.get_rect(center=(hand_center_y, center_x))
        gamedisplay.blit(text, text_rect)

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                mpos = event.pos
                # select deck card
                for i, rect in enumerate(deck_rects):
                    if rect.collidepoint(mpos):
                        selected_deck_idx = i
                # swap deck <-> hand
                if selected_deck_idx is not None and closest_idx is not None:
                    if hand_rects[closest_idx].collidepoint(mpos):
                        # swap ids and images
                        deck[selected_deck_idx], hand[closest_idx] = hand[closest_idx], deck[selected_deck_idx]
                        deck_ids[selected_deck_idx], hand_ids[closest_idx] = hand_ids[closest_idx], deck_ids[selected_deck_idx]
                        selected_deck_idx = None
                # continue
                if text_rect.collidepoint(mpos):
                    running = False

        pygame.display.flip()
        pygame.time.delay(10)

    # Persist to save using existing keys (no new save id)
    save['Deck'] = deck_ids
    save['Hand'] = hand_ids
    try:
        ModSave.encode_save_file(save)
    except Exception:
        # keep in-memory order if saving fails
        pass
def get_curved_positions(center_x, center_y, radius, num_cards, arc_angle_deg):
    positions = []
    start_angle = math.pi/2 - math.radians(arc_angle_deg)/2
    angle_step = math.radians(arc_angle_deg) / (num_cards - 1 if num_cards > 1 else 1)
    for i in range(num_cards):
        angle = start_angle + i * angle_step
        x = center_x + radius * math.cos(angle)
        y = center_y - radius * math.sin(angle)
        positions.append((int(x), int(y)))
    return positions


def dialogue(gamedisplay: pygame.Surface, font: Font, displayface:typing.Literal["Enchanter","Monarch" ,"Madman","Vendor","Clockwork", "None"], text:str, speech_pos:float, show_bkg:bool=True):
    # Should prolly dictionary map this but whatev
    if displayface in ("Enchanter", "Monarch"):
        if displayface == "Enchanter":
            face = enchanter_img
        elif displayface == "Monarch":
            face = monarch_img
    elif displayface in ("Madman","Vendor","Clockwork"):
        if displayface == "Madman":
            face = madman_img
        elif displayface in ("Vendor","Clockwork"):
            face = vendor_img
    else:
        # Display face == "None" so we dont show a face
        face:pygame.Surface = pygame.surface((1, 1))
        
    if speech_pos > 1:
        speech_pos = 1.0

    face = pygame.transform.scale(
        face,
        (int(face.get_width() * scale_y),
         int(face.get_height() * scale_y)))
    
    face_rect = face.get_rect(center=(screen_x//2, screen_y//2))

    BattleGround = pygame.transform.smoothscale(
        Battleground,  # 1000x1000 Asset
        # Height should be scaled to max y of screen, which is the same scalar as width
        (int(Battleground.get_width() * (screen_y / 1000) * 1.25),
         int(Battleground.get_height() * (screen_y / 1000) * 1.25)))
    battle_rect = BattleGround.get_rect(center=(screen_x // 2, screen_y // 2 - (BattleGround.get_height() * 0.05)))


    # Text
    testtext = text

    for i in range(len(testtext)):

        currentText:pygame.Surface = font.render(''.join(list(testtext)[:i]), True, (255,255,255))
        currentText_box = currentText.get_rect(center=(gamedisplay.get_width()//2, gamedisplay.get_height()*speech_pos))
        gamedisplay.fill((0,0,0))
        if show_bkg:
            gamedisplay.blit(BattleGround, battle_rect)
        gamedisplay.blit(face, face_rect)
        gamedisplay.blit(currentText, currentText_box)
        pygame.time.delay(25)
        pygame.display.flip()
    fulltext = font.render(testtext, True, (255, 255, 255))
    fulltext_rect = fulltext.get_rect(center=(gamedisplay.get_width()//2, gamedisplay.get_height()*speech_pos))
    pygame.time.delay(100)
    running = True
    while running:
        gamedisplay.fill((0,0,0))
        if show_bkg:
            gamedisplay.blit(BattleGround, battle_rect)
        gamedisplay.blit(face, face_rect)
        gamedisplay.blit(fulltext, fulltext_rect)
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                running = False
        pygame.time.delay(1)
        pygame.display.flip()


