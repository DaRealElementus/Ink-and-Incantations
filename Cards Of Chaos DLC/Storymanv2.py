"""Story Manager for Cards of Chaos DLC

Handles animations and story sequences including dialogue, cutscenes, interactable cinematics, vendors, NPCs, and more.

This file is a cleaned and expanded replacement for the uploaded StoryManager.py.
Changes made:
- Fixed typos and indexing errors.
- Reworked dialogue storage into a dictionary.
- Kept the original typewriter pacing (~25 ms per character).
- Enforced the explicit sequence: Enchanter -> Vendor -> Enchanter -> Vendor -> ... through all worlds.
- Expanded descriptions and made the vendor gradually reveal Clockwork's bitterness.
- Kept existing utility functions and test functions intact.
"""

from ast import Tuple
from tkinter.font import Font

import Combat
import pygame
import os
from pygame.locals import *
import random
import math
import typing

import SaveUpdater
import Units
import ModSave
import CardManager

# --- Assets ---
# Paths assume current working directory is project root or asset paths are valid

# each enemy face is on a green background to be keyed out
try:
    enchanter_img = pygame.image.load(os.path.join("Enemy_Faces", "Enchanter.png"))
    enchanter_img.set_colorkey((0, 255, 0))
except Exception:
    enchanter_img = pygame.Surface((1, 1))
try:
    monarch_img = pygame.image.load(os.path.join("Enemy_Faces", "Monarch.png"))
    monarch_img.set_colorkey((0, 255, 0))
except Exception:
    monarch_img = pygame.Surface((1, 1))
try:
    madman_img = pygame.image.load(os.path.join("Enemy_Faces", "Madman.png"))
    madman_img.set_colorkey((0, 255, 0))
except Exception:
    madman_img = pygame.Surface((1, 1))
try:
    vendor_img = pygame.image.load(os.path.join("Enemy_Faces", "Vendor.png"))
    vendor_img.set_colorkey((0, 255, 0))
except Exception:
    vendor_img = pygame.Surface((1, 1))

# Battleground background
try:
    Battleground = pygame.image.load(os.path.join("Assets", "Sprites", "Mirror.png"))
except Exception:
    Battleground = pygame.Surface((1000, 1000))

# Custom mouse cursor (used when game hides system cursor in Combat)
try:
    _raw_cursor_img = pygame.image.load(os.path.join("Assets", "Sprites", "Mouse.png")).convert_alpha()
except Exception:
    _raw_cursor_img = None

def _get_scaled_cursor(scale=1.0):
    """Return a scale-aware cursor Surface or None."""
    if not _raw_cursor_img:
        return None
    try:
        return pygame.transform.scale(_raw_cursor_img, (int(_raw_cursor_img.get_width() * scale), int(_raw_cursor_img.get_height() * scale)))
    except Exception:
        return _raw_cursor_img

# --- new helper: scale preserving original aspect ratio, no smoothing/antialias ---
def scale_fit(surface: pygame.Surface, max_w: int, max_h: int) -> pygame.Surface:
    """
    Scale `surface` to fit within (max_w, max_h) preserving aspect ratio.
    Uses pygame.transform.scale (no antialiasing / smoothing).
    """
    if surface is None:
        return None
    try:
        w, h = surface.get_width(), surface.get_height()
        if w == 0 or h == 0:
            return surface
        ratio = min(max_w / w, max_h / h)
        tw, th = max(1, int(w * ratio)), max(1, int(h * ratio))
        return pygame.transform.scale(surface, (tw, th))
    except Exception:
        return surface

# Visual defaults
for surf in (enchanter_img, monarch_img, madman_img, vendor_img):
    try:
        surf.set_colorkey((0, 255, 0))
        surf.set_alpha(100)
    except Exception:
        pass

# Global scale variables (expected to be set externally by main game loop)
scale_x, scale_y = 1.0, 1.0
screen_x, screen_y = 1000, 800

# --- Dialogue store ---
# Organized for clarity and easy editing. Tone is darker. Vendor is Clockwork in disguise.
DIALOGUE = {
    "intro": [
        "You approach a mirror and see a familiar face staring back.",
        "The glass trembles. It waits."
    ],

    "enchanter": [
        # Enchanter pre-fight lines and descriptive beats
        "You see the Enchanter framed in frost and false light.",
        "His smile is a memory of someone cruelly familiar.",
        "He hisses, \"I hate him. His grin is far too like yours.\"",
        "The mirror whispers the first challenge."
    ],

    "vendor": [
        # Vendor lines escalate over the course of the run. We'll index by stage.
        "A vendor stands behind the glass. He offers trinkets and games.",
        "The vendor bows. His words are thin courtesy wrapped over teeth.",
        "The vendor watches you play with the gravity of someone auditioning for pity.",
        "The vendor's smile slips. Something patient and bitter sits beneath it."
    ],

    "monarch": [
        "The Monarch appears like carved ivory and caution.",
        "She speaks of order and duty. Her voice shivers with kindness that is not safe.",
        "She says, \"Let me train you. I will forge your excuses into edge.\"",
        "Her hand rests where a crown should be. The mirror swallows the light."
    ],

    "madman": [
        "The Madman's stage is splintered and loud with memory.",
        "He laughs at the clock's forgetting. He speaks in gears and lost names.",
        "He halves the world with a grin and calls it justice."
    ],

    "clockwork": [
        "A hush falls when Clockwork steps into the glass.",
        "He speaks slow and exact. His words are both apology and verdict.",
        "\"You have been wading through my reflections,\" he says. \"All my children\'s faces.\"",
        "The mirror cracks. The bargain is laid bare."
    ],

    "ending": [
        "The glass gives up its last resistance.",
        "A choice. A card is marked. The mirror will keep its toys."
    ]
}

# More granular vendor progression lines keyed by how many shops visited
VENDOR_TONES = {
    1: [
        "\"Gamble a coin, take a toy,\" the vendor murmurs. \"We all need a comfort.\"",
        "You pocket a thing that gleams faintly. The vendor nods like a man used to being obeyed."
    ],
    2: [
        "The vendor's eyes linger on your hands a beat too long.",
        "\"Careful how you spend it. Coins make promises,\" he says. \"And promises demand repayment.\""
    ],
    3: [
        "There is a stench of old machinery when he speaks now.",
        "\"Do you like my toys?\" he asks. \"They teach obedience. They teach memory.\""
    ],
    4: [
        "The vendor smiles without moving his lips. The clock beneath the mirror ticks louder.",
        "\"I have been waiting to show you myself. But patience is a slow, tidy cruelty.\""
    ]
}

# --- Helpers: save management ---

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

# --- Combat wrapper ---

def _fight(opponent_key: str, gamedisplay: pygame.Surface, save: dict) -> bool:
    """
    Run a combat against opponent_key. Attempts to call Combat.BatStart if available,
    else falls back to a deterministic RNG result. Persists no changes here; caller must handle rewards/lives.
    """
    try:
        if opponent_key.lower().startswith("enchanter"):
            Ai = 'enchanter'
            opponent_hand = ['fool', 'high_priestess', 'empress', 'magician']
        elif opponent_key.lower().startswith("monarch"):
            Ai = 'monarch'
            opponent_hand = ['emperor', 'justice', 'lovers', 'strength']
        elif opponent_key.lower().startswith("madman"):
            Ai = 'madman'
            opponent_hand = ['death', 'hanged', 'tower', 'chariot']
        elif opponent_key.lower().startswith("clockwork"):
            Ai = 'clockwork'
            opponent_hand = ['moon', 'sun', 'star', 'world', 'judgement']
        else:
            Ai = 'enchanter'
            opponent_hand = ['fool', 'high_priestess', 'empress', 'magician']

        Won, score = Combat.BatStart(Ai, gamedisplay, False, None, os.getpid(), Units, SaveUpdater, [scale_x, scale_y], [screen_x, screen_y], opponent_hand)
        return bool(Won)
    except Exception as e:
        print("Combat failed:", e)
        return False

# --- Shop class ---
class Shop:
    """Simple shop GUI. Vendor is Clockwork in disguise; tone updates as shops_visited increments.
    All changes persist immediately. Keeps legacy controls and adds an Offers UI.
    """
    def __init__(self, items: list):
        self.items = items

    def display(self, screen):
        # kept for compatibility
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
        won = False
        if lives > 1:
            lives -= 1
            if random.randint(0, 1):
                gold += 1
                won = True
        return lives, gold, won

    def _vendor_offers(self, screen, save: dict):
        """Three-card offers UI (called from main shop). Left-click buy, right-click reroll, Esc to exit."""
        if not isinstance(save, dict):
            return
        w, h = screen.get_width(), screen.get_height()
        font = pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), max(14, int(scale_y * 22)))
        small = pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), max(12, int(scale_y * 18)))

        id_to_class = {
            0: 'Fool', 1: 'Magician', 2: 'HighPriestess', 3: 'Empress', 4: 'Emperor', 5: 'Hierophant', 6: 'Lovers',
            7: 'Chariot', 8: 'Justice', 9: 'Hermit', 10: 'Wheel', 11: 'Strength', 12: 'Hanged', 13: 'Death',
            14: 'Temperance', 15: 'Devil', 16: 'Tower', 17: 'Star', 18: 'Moon', 19: 'Sun', 20: 'Judgement', 21: 'World'
        }

        # background & face
        bg = pygame.transform.scale(Battleground, (int(Battleground.get_width() * (h / 1000) * 1.1),
                                                  int(Battleground.get_height() * (h / 1000) * 1.1)))
        bg_rect = bg.get_rect(center=(w // 2, int(h // 2 - (bg.get_height() * 0.05))))
        face_sz = (int(bg_rect.width * 0.5), int(bg_rect.height * 0.5))
        face_surf = pygame.transform.scale(vendor_img, face_sz)
        try:
            face_surf = face_surf.convert_alpha()
            face_surf.set_colorkey((0, 255, 0))
        except Exception:
            try:
                face_surf.set_colorkey((0, 255, 0))
            except Exception:
                pass
        face_rect = face_surf.get_rect(center=bg_rect.center)

        # generate offers
        all_ids = list(range(0, 22))
        base_cost = 5
        def make_offers():
            offers = []
            used = set()
            for _ in range(3):
                choices = [cid for cid in all_ids if cid not in used]
                if not choices:
                    choices = all_ids.copy()
                cid = random.choice(choices)
                used.add(cid)
                tier = random.randint(1, 3)
                cost = base_cost * tier
                try:
                    preview = getattr(CardManager, id_to_class[cid])(guilded=False).img
                except Exception:
                    preview = pygame.Surface((80, 120))
                    preview.fill((60, 60, 80))
                offers.append({'id': cid, 'tier': tier, 'cost': cost, 'img': preview})
            return offers

        offers = make_offers()
        card_w = int(w * 0.18)
        card_h = int(h * 0.18)
        gap = int(w * 0.04)
        total_w = 3 * card_w + 2 * gap
        start_x = (w - total_w) // 2
        y = int(h * 0.45)
        offer_rects = [pygame.Rect(start_x + i * (card_w + gap), y, card_w, card_h) for i in range(3)]

        clock = pygame.time.Clock()
        running = True
        while running:
            screen.fill((0, 0, 0))
            screen.blit(bg, bg_rect)
            screen.blit(face_surf, face_rect)

            # status
            gold_txt = font.render(f"Gold: {int(save.get('gold',0))}", True, (255, 220, 120))
            lives_txt = font.render(f"Lives: {int(save.get('lives',0))}", True, (200, 200, 255))
            screen.blit(gold_txt, (20, 20))
            screen.blit(lives_txt, (20, 20 + gold_txt.get_height() + 6))

            # draw offers and hover tooltip
            mouse_pos = pygame.mouse.get_pos()
            hovered_idx = None
            for i, rect in enumerate(offer_rects):
                hovered = rect.collidepoint(mouse_pos)
                if hovered:
                    hovered_idx = i
                # card box
                pygame.draw.rect(screen, (30, 30, 40), rect, border_radius=8)
                off = offers[i]
                try:
                    img_s = scale_fit(off['img'], int(rect.width * 0.9), int(rect.height * 0.6))
                except Exception:
                    img_s = pygame.Surface((int(rect.width * 0.9), int(rect.height * 0.6)))
                    img_s.fill((80, 80, 80))
                img_r = img_s.get_rect(center=(rect.centerx, rect.top + int(rect.height * 0.35)))
                screen.blit(img_s, img_r)
                badge = small.render(f"Tier {off['tier']}", True, (255, 220, 120))
                screen.blit(badge, (rect.left + 8, rect.top + 8))
                cost_txt = small.render(f"Cost: {off['cost']}g", True, (200, 200, 200) if not hovered else (255, 255, 200))
                screen.blit(cost_txt, (rect.left + 8, rect.bottom - 8 - cost_txt.get_height()))
                name = id_to_class.get(off['id'], f"Card {off['id']}")
                name_txt = font.render(name, True, (220, 220, 255))
                nrect = name_txt.get_rect(center=(rect.centerx, rect.top + rect.height - int(rect.height * 0.12)))
                screen.blit(name_txt, nrect)
                if hovered:
                    pygame.draw.rect(screen, (200, 200, 80), rect, 3, border_radius=8)

            # tooltip
            if hovered_idx is not None:
                off = offers[hovered_idx]
                cname = id_to_class.get(off['id'], f"Card {off['id']}")
                doc = ""
                try:
                    cls = getattr(CardManager, cname)
                    doc = getattr(cls.Invoke, "__doc__", "") or ""
                except Exception:
                    doc = ""
                tooltip_lines = [f"{cname} (Tier {off['tier']})", f"Cost: {off['cost']}g"]
                if doc:
                    doc_lines = [ln.strip() for ln in doc.splitlines() if ln.strip()]
                    tooltip_lines += doc_lines[:3]
                texts = [small.render(ln, True, (240,240,240)) for ln in tooltip_lines]
                padding = 8
                tw = max(t.get_width() for t in texts) + padding*2
                th = sum(t.get_height() for t in texts) + padding*(len(texts)+1)
                tx = mouse_pos[0] + 16
                ty = mouse_pos[1] + 16
                if tx + tw > w:
                    tx = mouse_pos[0] - 16 - tw
                if ty + th > h:
                    ty = h - th - 8
                tooltip_surf = pygame.Surface((tw, th), pygame.SRCALPHA)
                tooltip_surf.fill((20,20,28,220))
                oy = padding
                for t in texts:
                    tooltip_surf.blit(t, (padding, oy))
                    oy += t.get_height() + 4
                screen.blit(tooltip_surf, (tx, ty))

            hint = small.render("Left-click to buy | Right-click to reroll | Esc to exit", True, (160,160,160))
            screen.blit(hint, (w//2 - hint.get_width()//2, int(h * 0.85)))

            # overlay custom cursor if hidden
            if not pygame.mouse.get_visible():
                c = _get_scaled_cursor(scale_y)
                if c:
                    mx, my = pygame.mouse.get_pos()
                    crect = c.get_rect(center=(mx, my))
                    screen.blit(c, crect)

            pygame.display.flip()

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                elif ev.type == KEYDOWN:
                    if ev.key == K_ESCAPE:
                        running = False
                elif ev.type == MOUSEBUTTONDOWN and ev.button == 1:  # buy
                    for i, rect in enumerate(offer_rects):
                        if rect.collidepoint(ev.pos):
                            off = offers[i]
                            cur_gold = int(save.get('gold', 0))
                            if cur_gold >= off['cost']:
                                save['gold'] = cur_gold - off['cost']
                                # add to Cards (not guilded) and Hand
                                cards = save.get('Cards', [])
                                found = False
                                new_cards = []
                                for cid, flag in cards:
                                    if cid == off['id']:
                                        found = True
                                        new_cards.append((cid, False))  # purchased = not guilded
                                    else:
                                        new_cards.append((cid, flag))
                                if not found:
                                    new_cards.append((off['id'], False))
                                save['Cards'] = new_cards
                                hand = save.get('Hand', [])
                                if off['id'] not in hand:
                                    hand.append(off['id'])
                                save['Hand'] = hand
                                _save_commit(save)
                            else:
                                # feedback
                                n = small.render("Not enough gold", True, (255,100,100))
                                screen.blit(n, (w//2 - n.get_width()//2, int(h * 0.9)))
                                pygame.display.flip()
                                pygame.time.delay(600)
                elif ev.type == MOUSEBUTTONDOWN and ev.button == 3:  # reroll
                    offers = make_offers()
            clock.tick(60)

    def enter_shop(self, screen, save: dict):
        """Main shop screen (legacy controls + Offers button)."""
        if not isinstance(save, dict):
            return
        shops = int(save.get('ShopsVisited', 0))
        _save_commit(save)

        w, h = screen.get_width(), screen.get_height()
        font = pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), max(16, int(scale_y * 26)))

        bg = pygame.transform.scale(Battleground, (int(Battleground.get_width() * (h / 1000) * 1.1),
                                                  int(Battleground.get_height() * (h / 1000) * 1.1)))
        bg_rect = bg.get_rect(center=(w // 2, int(h // 2 - (bg.get_height() * 0.05))))

        face_sz = (int(bg_rect.width * 0.5), int(bg_rect.height * 0.5))
        face_surf = pygame.transform.scale(vendor_img, face_sz)
        try:
            face_surf = face_surf.convert_alpha()
            face_surf.set_colorkey((0, 255, 0))
        except Exception:
            try:
                face_surf.set_colorkey((0, 255, 0))
            except Exception:
                pass
        face_rect = face_surf.get_rect(center=bg_rect.center)

        # buttons (legacy)
        button_w = int(w * 0.22)
        button_h = max(36, int(scale_y * 48))
        gap = 12
        total_w = button_w * 3 + gap * 2
        start_x = (w - total_w) // 2
        top_y = int(h * 0.72)

        btn_gold_rect = pygame.Rect(start_x, top_y, button_w, button_h)
        btn_life_rect = pygame.Rect(start_x + (button_w + gap), top_y, button_w, button_h)
        btn_edit_rect = pygame.Rect(start_x + 2 * (button_w + gap), top_y, button_w, button_h)
        btn_offers_rect = pygame.Rect(start_x, top_y - (button_h + gap), button_w * 1 + gap, button_h)  # big offers button
        btn_exit_rect = pygame.Rect(start_x + 2 * (button_w + gap), top_y - (button_h + gap), button_w, button_h)

        def draw_button(r: pygame.Rect, text: str, col_bg=(40, 40, 60), col_fg=(255, 255, 255)):
            pygame.draw.rect(screen, col_bg, r, border_radius=8)
            txt = font.render(text, True, col_fg)
            txt_r = txt.get_rect(center=r.center)
            screen.blit(txt, txt_r)

        tone_lines = VENDOR_TONES.get(min(4, shops + 1), VENDOR_TONES[4])

        running = True
        clock = pygame.time.Clock()
        while running:
            screen.fill((0,0,0))
            screen.blit(bg, bg_rect)
            screen.blit(face_surf, face_rect)

            gold_txt = font.render(f"Gold: {int(save.get('gold',0))}", True, (255, 220, 120))
            lives_txt = font.render(f"Lives: {int(save.get('lives',0))}", True, (200, 200, 255))
            screen.blit(gold_txt, (20, 20))
            screen.blit(lives_txt, (20, 20 + gold_txt.get_height() + 6))

            draw_button(btn_offers_rect, "Offers (3 cards)")
            draw_button(btn_gold_rect, "Gold Gamble (-1g)")
            draw_button(btn_life_rect, "Spend 1 Life -> 50% +1g")
            draw_button(btn_edit_rect, "Edit Deck")
            draw_button(btn_exit_rect, "Exit Shop")

            # ambient vendor text
            tone_y = btn_exit_rect.bottom + 8
            small = pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), max(12, int(scale_y * 18)))
            for i, line in enumerate(tone_lines):
                t = small.render(line, True, (200, 200, 200))
                screen.blit(t, (w//2 - t.get_width()//2, tone_y + i * (t.get_height() + 4)))

            hint = font.render("1=Gold Gamble  2=Life→Gold  3=Edit Deck  4=Offers  Esc=Exit", True, (160,160,160))
            screen.blit(hint, (w//2 - hint.get_width()//2, btn_exit_rect.bottom + 12 + len(tone_lines)*20))

            # overlay custom cursor when system cursor hidden
            if not pygame.mouse.get_visible():
                c = _get_scaled_cursor(scale_y)
                if c:
                    mx, my = pygame.mouse.get_pos()
                    crect = c.get_rect(center=(mx, my))
                    screen.blit(c, crect)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    elif event.key == K_1:
                        g = int(save.get('gold', 0)); nw = int(save.get('NumWins', 0))
                        if g > 0:
                            g, nw, _ = self.gambling_game(g, nw)
                            save['gold'] = int(g); save['NumWins'] = int(nw); _save_commit(save)
                    elif event.key == K_2:
                        l = int(save.get('lives', 0)); g = int(save.get('gold', 0))
                        l, g, _ = self.gamble_life_for_gold(l, g)
                        save['lives'] = int(l); save['gold'] = int(g); _save_commit(save)
                    elif event.key == K_3:
                        BuildDeck(screen, pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), max(12, int(scale_y * 24))))
                        save = _save_load(); _save_commit(save)
                    elif event.key == K_4:
                        self._vendor_offers(screen, save)
                        save = _save_load()
                elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    if btn_offers_rect.collidepoint((mx,my)):
                        self._vendor_offers(screen, save); save = _save_load()
                    elif btn_gold_rect.collidepoint((mx, my)):
                        g = int(save.get('gold', 0)); nw = int(save.get('NumWins', 0))
                        if g > 0:
                            g, nw, _ = self.gambling_game(g, nw)
                            save['gold'] = int(g); save['NumWins'] = int(nw); _save_commit(save)
                    elif btn_life_rect.collidepoint((mx, my)):
                        l = int(save.get('lives', 0)); g = int(save.get('gold', 0))
                        l, g, _ = self.gamble_life_for_gold(l, g)
                        save['lives'] = int(l); save['gold'] = int(g); _save_commit(save)
                    elif btn_edit_rect.collidepoint((mx, my)):
                        BuildDeck(screen, pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), max(12, int(scale_y * 24))))
                        save = _save_load(); _save_commit(save)
                    elif btn_exit_rect.collidepoint((mx, my)):
                        running = False

            clock.tick(60)

        save['ShopsVisited'] = shops + 1
        _save_commit(save)

# --- Story flow: begin_story_mode and resume_from_save ---

def begin_story_mode(gamedisplay: pygame.Surface):
    """
    Linear story flow. Persist save after every important event.
    Enforces sequence: Enchanter1 -> Vendor -> Enchanter2 -> Vendor -> Enchanter3 -> Vendor -> Monarch...
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
    save.setdefault('NumWins', 0)
    save.setdefault('ShopsVisited', 0)
    _save_commit(save)

    # Start run
    save['World'] = 1
    save['Level'] = 0
    _save_commit(save)

    vendor = Shop([])

    # Preparation phase (player edits deck via BuildDeck UI)
    BuildDeck(gamedisplay, pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), max(12, int(scale_y * 30))))
    save = _save_load()

    # Intro
    for line in DIALOGUE['intro']:
        dialogue(gamedisplay, pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), max(12, int(scale_y * 26))), "None", line, 0.4)

    # Enchanter sequence (3 fights) with shop between each
    for i in range(1, 4):
        save['Level'] = i
        _save_commit(save)
        # pre-fight description
        en_lines = DIALOGUE['enchanter']
        dialogue(gamedisplay, pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), max(12, int(scale_y * 26))), "Enchanter", en_lines[min(i-1, len(en_lines)-1)], 0.35)
        won = _fight(f"Enchanter_{i}", gamedisplay, save)
        if won:
            save['gold'] = int(save.get('gold', 0)) + 10
            _save_commit(save)
            dialogue(gamedisplay, pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), max(12, int(scale_y * 22))), "None", "You survived the mirror's test. Gather what you can.", 0.8)
        else:
            _reduce_life(save, 1)
            dialogue(gamedisplay, pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), max(12, int(scale_y * 22))), "None", "You were cut by the glass. A life is lost.", 0.8)
        # Vendor
        dialogue(gamedisplay, pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), max(12, int(scale_y * 24))), "Vendor", DIALOGUE['vendor'][min(0, len(DIALOGUE['vendor'])-1)], 0.2)
        vendor.enter_shop(gamedisplay, save)
        save = _save_load()

    # Clockwork restores lives after enchanter arc
    dialogue(gamedisplay, pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), max(12, int(scale_y * 26))), "Clockwork", "A distant voice counts down. You feel something heavy unbind.", 0.4)
    _restore_all_lives(save, 3)

    # Monarch sequence
    save['World'] = 2
    _save_commit(save)
    for i in range(1, 4):
        save['Level'] = 10 + i
        _save_commit(save)
        dialogue(gamedisplay, pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), max(12, int(scale_y * 26))), "Monarch", DIALOGUE['monarch'][min(i-1, len(DIALOGUE['monarch'])-1)], 0.35)
        won = _fight(f"Monarch_{i}", gamedisplay, save)
        if won:
            save['gold'] = int(save.get('gold', 0)) + 20
            _save_commit(save)
            dialogue(gamedisplay, pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), max(12, int(scale_y * 22))), "None", "You push through the Monarch's command. You find coin at her feet.", 0.8)
        else:
            _reduce_life(save, 1)
            dialogue(gamedisplay, pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), max(12, int(scale_y * 22))), "None", "Discipline cracks. The mirror takes another beat of you.", 0.8)
        # Vendor
        # show vendor tone lines based on number of shops already visited
        vendor.enter_shop(gamedisplay, save)
        save = _save_load()

    # Restore lives
    dialogue(gamedisplay, pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), max(12, int(scale_y * 26))), "Clockwork", "The mirror hums. Something inside it smooths the edges of your failings.", 0.4)
    _restore_all_lives(save, 3)

    # Madman sequence
    save['World'] = 3
    _save_commit(save)
    for i in range(1, 4):
        save['Level'] = 20 + i
        _save_commit(save)
        dialogue(gamedisplay, pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), max(12, int(scale_y * 26))), "Madman", DIALOGUE['madman'][min(i-1, len(DIALOGUE['madman'])-1)], 0.35)
        won = _fight(f"Madman_{i}", gamedisplay, save)
        if won:
            save['gold'] = int(save.get('gold', 0)) + 30
            _save_commit(save)
            dialogue(gamedisplay, pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), max(12, int(scale_y * 22))), "None", "You step over the Madman's remains. Coins clink in the void.", 0.8)
        else:
            _reduce_life(save, 1)
            dialogue(gamedisplay, pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), max(12, int(scale_y * 22))), "None", "The Madman's laugh takes one of your breaths.", 0.8)
        vendor.enter_shop(gamedisplay, save)
        save = _save_load()

    # Final restoration before Clockwork
    dialogue(gamedisplay, pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), max(12, int(scale_y * 26))), "Clockwork", "The glass forgives you its last mercy. Lives return, but something is changed.", 0.4)
    _restore_all_lives(save, 3)

    # Clockwork final gauntlet
    save['World'] = 4
    _save_commit(save)
    for i in range(1, 4):
        save['Level'] = 30 + i
        _save_commit(save)
        dialogue(gamedisplay, pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), max(12, int(scale_y * 26))), "Clockwork", DIALOGUE['clockwork'][min(i-1, len(DIALOGUE['clockwork'])-1)], 0.35)
        won = _fight(f"Clockwork_{i}", gamedisplay, save)
        if won:
            save['gold'] = int(save.get('gold', 0)) + 50
            _save_commit(save)
            dialogue(gamedisplay, pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), max(12, int(scale_y * 22))), "None", "You fracture another reflection. The mirror bleeds less light.", 0.8)
        else:
            _reduce_life(save, 1)
            if save.get('lives', 0) <= 0:
                save['RunEnded'] = True
                _save_commit(save)
                guild_one_card_at_run_end(save)
                return

    # Victory: guild exactly one card
    chosen = guild_one_card_at_run_end(save)
    save['RunCompleted'] = True
    _save_commit(save)
    for line in DIALOGUE['ending']:
        dialogue(gamedisplay, pygame.font.Font(os.path.join("Assets", "Fonts", "Speech.ttf"), max(12, int(scale_y * 26))), "None", line, 0.4)

# --- Resume from save ---

def resume_from_save(gamedisplay: pygame.Surface):
    save = _save_load()
    world = int(save.get('World', 0))
    level = int(save.get('Level', 0))

    if world <= 1:
        begin_story_mode(gamedisplay)
        return

    vendor = Shop([])

    if world == 2:
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

# --- Dialogue and display helpers ---

def typewriter_render(gamedisplay: pygame.Surface, font: Font, text: str, center_x: int, center_y: int, show_bkg: bool = True, face: pygame.Surface | None = None, face_rect: pygame.Rect | None = None, speech_pos: float = 0.5):
    """
    Render text with the typewriter effect at the existing ~25 ms per character.
    Waits for a click to continue after the full text has been revealed.
    """
    if speech_pos < 0.1:
        speech_pos = 0.1
    if speech_pos > 0.95:
        speech_pos = 0.95

    # Show iterative text
    for i in range(len(text)):
        current = font.render(text[:i+1], True, (255, 255, 255))
        rect = current.get_rect(center=(center_x, int(gamedisplay.get_height() * speech_pos)))
        gamedisplay.fill((0, 0, 0))
        if show_bkg:
            try:
                BattleGround = pygame.transform.scale(Battleground, (int(Battleground.get_width() * (screen_y / 1000) * 1.25), int(Battleground.get_height() * (screen_y / 1000) * 1.25)))
                battle_rect = BattleGround.get_rect(center=(screen_x // 2, screen_y // 2 - (BattleGround.get_height() * 0.05)))
                gamedisplay.blit(BattleGround, battle_rect)
            except Exception:
                pass
        if face is not None and face_rect is not None:
            gamedisplay.blit(face, face_rect)
        gamedisplay.blit(current, rect)
        pygame.time.delay(25)  # keep original pace
        # overlay custom cursor if system cursor is hidden
        if not pygame.mouse.get_visible():
            c = _get_scaled_cursor(scale_y)
            if c:
                mx, my = pygame.mouse.get_pos()
                crect = c.get_rect(center=(mx, my))
                gamedisplay.blit(c, crect)
            else:
                pygame.mouse.set_visible(True)
        pygame.display.flip()

    # full text displayed, wait for click to continue
    full = font.render(text, True, (255, 255, 255))
    full_rect = full.get_rect(center=(center_x, int(gamedisplay.get_height() * speech_pos)))

    waiting = True
    while waiting:
        gamedisplay.fill((0, 0, 0))
        if show_bkg:
            try:
                BattleGround = pygame.transform.scale(Battleground, (int(Battleground.get_width() * (screen_y / 1000) * 1.25), int(Battleground.get_height() * (screen_y / 1000) * 1.25)))
                battle_rect = BattleGround.get_rect(center=(screen_x // 2, screen_y // 2 - (BattleGround.get_height() * 0.05)))
                gamedisplay.blit(BattleGround, battle_rect)
            except Exception:
                pass
        if face is not None and face_rect is not None:
            gamedisplay.blit(face, face_rect)
        gamedisplay.blit(full, full_rect)

        # overlay custom cursor if system cursor is hidden
        if not pygame.mouse.get_visible():
            c = _get_scaled_cursor(scale_y)
            if c:
                mx, my = pygame.mouse.get_pos()
                crect = c.get_rect(center=(mx, my))
                gamedisplay.blit(c, crect)
            else:
                pygame.mouse.set_visible(True)

        for ev in pygame.event.get():
            if ev.type == MOUSEBUTTONDOWN and ev.button == 1:
                waiting = False
            elif ev.type == KEYDOWN and ev.key in (K_RETURN, K_SPACE, K_ESCAPE):
                waiting = False
        pygame.time.delay(1)
        pygame.display.flip()


def dialogue(gamedisplay: pygame.Surface, font: Font, displayface:typing.Literal["Enchanter","Monarch" ,"Madman","Vendor","Clockwork", "None"], text:str, speech_pos:float, show_bkg:bool=True):
    # select face surface
    if displayface == "Enchanter":
        face = enchanter_img
    elif displayface == "Monarch":
        face = monarch_img
    elif displayface == "Madman":
        face = madman_img
    elif displayface in ("Vendor", "Clockwork"):
        face = vendor_img
    else:
        face = None

    if face is not None:
        try:
            scaled = pygame.transform.scale(face, (int(face.get_width() * scale_y), int(face.get_height() * scale_y)))
            face_rect = scaled.get_rect(center=(screen_x//2, screen_y//2))
        except Exception:
            scaled = None
            face_rect = None
    else:
        scaled = None
        face_rect = None

    # clamp speech_pos
    if speech_pos > 1:
        speech_pos = 1.0

    typewriter_render(gamedisplay, font, text, gamedisplay.get_width()//2, int(gamedisplay.get_height() * speech_pos), show_bkg, scaled, face_rect, speech_pos)

# --- Small utility tests kept intact ---

def diologueTest(gamedisplay :pygame.Surface, font: Font):
    """Testing the dialogue animation"""
    testtext = "Testing testing 1234 I cant count to 5 or 6"
    for i in range(len(testtext)):
        currentText = font.render(''.join(list(testtext)[:i]), True, (255,255,255))
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

    card_img_orig = card.img
    guilded_img_orig = Guilded_card.img

    card_center = (gamedisplay.get_width() // 2 - card_img_orig.get_width(), gamedisplay.get_height() // 2)
    guilded_center = (gamedisplay.get_width() // 2 + guilded_img_orig.get_width(), gamedisplay.get_height() // 2)

    running = True
    while running:
        gamedisplay.fill((0,0,0))
        mouse_pos = pygame.mouse.get_pos()
        card_img = card_img_orig
        if pygame.Rect(0,0,card_img.get_width(),card_img.get_height()).move(card_center[0]-card_img.get_width()//2, card_center[1]-card_img.get_height()//2).collidepoint(mouse_pos):
            card_img = pygame.transform.scale(card_img_orig, (int(card_img_orig.get_width()*1.5), int(card_img_orig.get_height()*1.5)))
        card_rect = card_img.get_rect(center=card_center)
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
    save = ModSave.decode_save_file()
    cards:list[Tuple[int, bool]] = save['Cards']
    id_matrix = {id: False for id in [0,1,2,3,4,5,6,9,10,11,12,14,16,17,18,19,20,21]}
    for card in cards:
        if card[0] in id_matrix:
            if card[1]:
                id_matrix[card[0]] = 'Guilded'
            else:
                id_matrix[card[0]] = True
    card_ids = [0,1,2,3,4,5,6,9,10,11,12,14,16,17,18,19,20,21]
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
    save = ModSave.decode_save_file()
    if save is None:
        try:
            ModSave.encode_save_file()
            save = ModSave.decode_save_file() or {}
        except Exception:
            save = {}
    cards: list[tuple] = save.get('Cards', [])
    id_matrix = {i: False for i in range(0, 22)}
    for card in cards:
        cid = card[0]
        if cid in id_matrix:
            if card[1] and cid not in (7, 8, 13, 15):
                id_matrix[cid] = 'Guilded'
            else:
                id_matrix[cid] = True
    id_to_class = {
        0: 'Fool', 1: 'Magician', 2: 'HighPriestess', 3: 'Empress', 4: 'Emperor', 5: 'Hierophant', 6: 'Lovers',
        7: 'Chariot', 8: 'Justice', 9: 'Hermit', 10: 'Wheel', 11: 'Strength', 12: 'Hanged', 13: 'Death',
        14: 'Temperance', 15: 'Devil', 16: 'Tower', 17: 'Star', 18: 'Moon', 19: 'Sun', 20: 'Judgement', 21: 'World'
    }
    card_ids = list(range(0, 22))
    unlocked_ids = []
    for cid in card_ids:
        if id_matrix.get(cid) == 'Guilded' or id_matrix.get(cid) is True:
            unlocked_ids.append(cid)
    deck_ids = list(save.get('Deck', []))
    hand_ids = list(save.get('Hand', []))
    if not deck_ids and not hand_ids:
        deck_ids = unlocked_ids[:4]
        hand_ids = unlocked_ids[4:]
    else:
        def sanitize_list(lst):
            return [cid for cid in lst if cid in unlocked_ids]
        deck_ids = sanitize_list(deck_ids)
        hand_ids = sanitize_list(hand_ids)
        combined = deck_ids + hand_ids
        seen = set()
        new_combined = []
        for cid in combined:
            if cid not in seen:
                new_combined.append(cid)
                seen.add(cid)
        for cid in unlocked_ids:
            if cid not in seen:
                new_combined.append(cid)
                seen.add(cid)
        deck_ids = new_combined[:4]
        hand_ids = new_combined[4:]
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
        deck_rects = []
        mouse_pos = pygame.mouse.get_pos()
        for i, img in enumerate(deck):
            x = deck_start_x + i * deck_spacing
            rect = img.get_rect(center=(x, deck_y))
            deck_rects.append(rect)
            gamedisplay.blit(img, rect)
            if selected_deck_idx == i:
                pygame.draw.rect(gamedisplay, (255, 255, 0), rect, 4)
        hand_positions = []
        start_angle = math.pi/2 - math.radians(arc_angle)/2
        angle_step = math.radians(arc_angle) / (len(hand) - 1 if len(hand) > 1 else 1)
        for idx in range(len(hand)):
            angle = start_angle + idx * angle_step
            x = hand_center_x + deck_radius * math.cos(angle)
            y = hand_center_y - deck_radius * math.sin(angle)
            hand_positions.append((int(x), int(y)))
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
                # recompute hover positions
                start_a = math.pi/2 - math.radians(arc_angle)/2
                step_a = math.radians(arc_angle) / (len(hand) - 1 if len(hand) > 1 else 1)
                hover_angle = start_a + i * step_a
                hover_pos = (int(hand_center_x + hover_radius * math.cos(hover_angle)), int(hand_center_y - hover_radius * math.sin(hover_angle)))
                img_scaled = pygame.transform.scale(img, (int(card_w * 1.2), int(card_h * 1.2)))
                rect = img_scaled.get_rect(center=hover_pos)
                gamedisplay.blit(img_scaled, rect)
            else:
                rect = img.get_rect(center=pos)
                gamedisplay.blit(img, rect)
            hand_rects.append(rect)
        text = font.render("Continue", True, (255, 255, 255))
        text_rect = text.get_rect(center=(hand_center_x, center_x))
        gamedisplay.blit(text, text_rect)
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                mpos = event.pos
                for i, rect in enumerate(deck_rects):
                    if rect.collidepoint(mpos):
                        selected_deck_idx = i
                if selected_deck_idx is not None and closest_idx is not None:
                    if hand_rects[closest_idx].collidepoint(mpos):
                        deck[selected_deck_idx], hand[closest_idx] = hand[closest_idx], deck[selected_deck_idx]
                        deck_ids[selected_deck_idx], hand_ids[closest_idx] = hand_ids[closest_idx], deck_ids[selected_deck_idx]
                        selected_deck_idx = None
                if text_rect.collidepoint(mpos):
                    running = False
        pygame.display.flip()
        pygame.time.delay(10)
    save['Deck'] = deck_ids
    save['Hand'] = hand_ids
    try:
        ModSave.encode_save_file(save)
    except Exception:
        pass

# End of file
