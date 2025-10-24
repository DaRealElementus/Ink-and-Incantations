"""Class to manage deck and cards"""


import pygame
import os
import time
import random
import Units



class Card():
    def __init__(self, guilded:bool=False, path='Assets/Cards/cards/0_theFool/0_theFool_2x.png', idNum:int|None=None):
        self.idNum:int|None = idNum
        self.guilded = guilded
        if self.guilded:
            # Turn the card rainbow
            card_img = pygame.image.load(os.path.join(*path.split("/")))
            card_img.set_colorkey((255, 208, 128))


            guilded_img = pygame.image.load(os.path.join('Assets','Cards','cards','Guilded.png')) # Cards Of Chaos DLC\Assets\Cards\cards\Guilded.png
            
            guilded_img = pygame.transform.scale(guilded_img, (card_img.get_width(), card_img.get_height()))
            
            guilded_img.blit(card_img, (0,0))
            self.img = guilded_img
        elif self.idNum in [7, 8, 13, 15]:
            # Special colours for Chariot, Justice, Death and Devil
            card_img = pygame.image.load(os.path.join(*path.split("/")))
            card_img.set_colorkey((255, 208, 128))


            special_img = pygame.image.load(os.path.join('Assets','Cards','cards','Cursed.png')) # Cards Of Chaos DLC\Assets\Cards\cards\Cursed.png

            special_img = pygame.transform.scale(special_img, (card_img.get_width(), card_img.get_height()))
            
            special_img.blit(card_img, (0,0))
            self.img = special_img
        else:
            # Default colours
            self.img = pygame.image.load(os.path.join(*path.split("/")))

class Fool(Card):
    def __init__(self, guilded:bool=False):
        super().__init__(guilded=guilded, path='Assets/Cards/cards/0_theFool/0_theFool_2x.png', idNum=0)
        self.idNum = 0

    def Invoke(self, owner:str):
        """Invoke the card's special ability
        Your Minions gain +4s lifespan (10s max).
        """

        return {'Name':self.__class__.__name__,
                'Owner':owner,
                'end':100000000}

class Magician(Card):
    def __init__(self, guilded:bool=False):
        super().__init__(guilded=guilded, path='Assets/Cards/cards/1_theMagician/1_theMagician_2x.png')
        self.idNum = 1

    def Invoke(self, owner:str):
        """Invoke the card's special ability
        Summon a copy of the last unit you played for free.
        """
        return {'Name':self.__class__.__name__,
                'Owner':owner,
                'end':1}

class HighPriestess(Card):
    def __init__(self, guilded:bool=False):
        super().__init__(guilded=guilded, path='Assets/Cards/cards/2_theHighPriestess/2_theHighPriestess_2x.png', idNum=2)
        self.idNum = 2
    
    def Invoke(self, owner: str):
        """Invoke the card's special ability
        For the next 10s, your units take half damage from attacks.
        """
        return {'Name':self.__class__.__name__,
                'Owner':owner,
                'end':10000}

class Empress(Card):
    def __init__(self, guilded:bool=False):
        super().__init__(guilded=guilded, path='Assets/Cards/cards/3_theEmpress/3_theEmpress_2x.png', idNum=3)
        self.idNum = 3
    def Invoke(self, owner: str):
        """Invoke the card's special ability
        Spawn 1-3 random basic troops (Footman, Soldier, Horse).
        """
        return {'Name':self.__class__.__name__,
                'Owner':owner,
                'end':1}
        

        

class Emperor(Card):
    def __init__(self, guilded:bool=False):
        super().__init__(guilded=guilded, path='Assets/Cards/cards/4_theEmperor/4_theEmperor_2x.png', idNum=4)
        self.idNum = 4

    def Invoke(self, owner :str):
        """Invoke the card's special ability
        Choose one of your Generators. It counts as two for the next 10s.
        """
        return {'Name':self.__class__.__name__,
                'Owner':owner,
                'end':10000}

class Hierophant(Card):
    def __init__(self, guilded:bool=False):
        super().__init__(guilded=guilded, path='Assets/Cards/cards/5_theHierophant/5_theHierophant_2x.png', idNum=5)
        self.idNum = 5

    def Invoke(self, owner:str):
        """Invoke the card's special ability
        a random unit type is chosen. Every unit summoned for the next 10s is of that type.
        """
        return {'Name':self.__class__.__name__,
                'Owner':owner,
                'end':10000}

class Lovers(Card):
    def __init__(self, guilded:bool=False):
        super().__init__(guilded=guilded, path='Assets/Cards/cards/6_theLovers/6_theLovers_2x.png', idNum=6)
        self.idNum = 6

    def Invoke(self, owner:str):
        """Invoke the card's special ability
        Two of your units are linked for 10s. They share damage taken and lifespan but deal combined damage."""
        return {'Name':self.__class__.__name__,
                'Owner':owner,
                'end':10000}

class Chariot(Card):
    def __init__(self, guilded:bool=False):
        super().__init__(guilded=guilded, path='Assets/Cards/cards/7_theChariot/7_theChariot_2x.png', idNum=7)
        self.idNum = 7

    def Invoke(self, owner:str):
        """Invoke the card's special ability
        Target a Runner (or summon one if none exist). It gains double speed and infinite damage vs units but is reduced to 1 HP. Lasts one encounter. Cursed."""
        return {'Name':self.__class__.__name__,
                'Owner':owner,
                'end':1}


class Justice(Card):
    def __init__(self, guilded:bool=False):
        super().__init__(guilded=guilded, path='Assets/Cards/cards/8_justice/8_justice_2x.png', idNum=8)
        self.idNum = 8

    def Invoke(self, owner:str):
        """Invoke the card's special ability
        Until your opponent's mana is depleted, you spend their mana instead of your own. Cursed."""
        return {'Name':self.__class__.__name__,
                'Owner':owner,
                'end':100000000000}

class Hermit(Card):
    def __init__(self, guilded:bool=False):
        super().__init__(guilded=guilded, path='Assets/Cards/cards/9_theHermit/9_theHermit_2x.png', idNum=9)
        self.idNum = 9

    def Invoke(self, owner:str):
        """Invoke the card's special ability
        Remove all your units from the field except one. it gains triple stats. does not affect Generators or minions"""
        return {'Name':self.__class__.__name__,
                'Owner':owner,
                'end':1}
class Wheel(Card):
    def __init__(self, guilded:bool=False):
        super().__init__(guilded=guilded, path='Assets/Cards/cards/10_wheelOfFortune/10_wheelOfFortune_2x.png', idNum=10)
        self.idNum = 10

    def Invoke(self, owner:str):
        """Invoke the cards special ability
        each unit randonly gains +50% or -50% to their stats for 30 seconds"""
        return {'Name':self.__class__.__name__,
                'Owner':owner,
                'end':30000}


class Strength(Card):
    def __init__(self, guilded:bool=False):
        super().__init__(guilded=guilded, path='Assets/Cards/cards/11_strength/11_strength_2x.png', idNum=11)
        self.idNum = 11
    
    def Invoke(self, owner:str):
        """Invoke the Cards special ability
        Find your least-used troop type. All of that type gain +10% damage for each of that type"""
        return {'Name':self.__class__.__name__,
                'Owner':owner,
                'end':1}

class Hanged(Card):
    def __init__(self, guilded:bool=False):
        super().__init__(guilded=guilded, path='Assets/Cards/cards/12_theHangedMan/12_theHangedMan_2x.png', idNum=12)
        self.idNum = 12

    def Invoke(self, owner:str):
        """Invoke the Cards special ability
        Sacrifice one unit for max mana"""
        return {'Name':self.__class__.__name__,
                'Owner':owner,
                'end':1}

class Death(Card):
    def __init__(self, guilded:bool=False):
        super().__init__(guilded=guilded, path='Assets/Cards/cards/13_death/13_death_2x.png', idNum=13)
        self.idNum = 13

    def Invoke(self, owner:str):
        """Invoke the Cards special ability
        1% chance to instantly kill you or your opponent. Cursed"""
        return {'Name':self.__class__.__name__,
                'Owner':owner,
                'end':1}

class Temperance(Card):
    def __init__(self, guilded:bool=False):
        super().__init__(guilded=guilded, path='Assets/Cards/cards/14_temperance/14_temperance_2x.png', idNum=14)
        self.idNum = 14

    def Invoke(self, owner:str):
       """Invoke the Cards special ability
       set every Units hp to the average HP of all units"""
       return {'Name':self.__class__.__name__,
               'Owner':owner,
               'end':1}

class Devil(Card):
    def __init__(self, guilded:bool=False):
        super().__init__(guilded=guilded, path='Assets/Cards/cards/15_devil/15_devil_2x.png', idNum=15)
        self.idNum = 15

    def Invoke(self, owner:str):
       """Invoke the Cards special ability
       Flip all probabilities for the rest of the match (20% -> 80%). Cursed."""
       return {'Name':self.__class__.__name__,
               'Owner':owner,
               'end':100000000}

class Tower(Card):
    def __init__(self, guilded:bool=False):
        super().__init__(guilded=guilded, path='Assets/Cards/cards/16_theTower/16_theTower_2x.png', idNum=16)
        self.idNum = 16

    def Invoke(self, owner:str):
       """Invoke the Cards special ability
       Destroy one Random Generator from the game"""
       return {'Name':self.__class__.__name__,
               'Owner':owner,
               'end':1}


class Star(Card):
    def __init__(self, guilded:bool=False):
        super().__init__(guilded=guilded, path='Assets/Cards/cards/17_theStar/17_theStar_2x.png', idNum=17)
        self.idNum = 17

    def Invoke(self, owner:str):
       """Invoke the Cards special ability
       Fully heal all units"""
       return {'Name':self.__class__.__name__,
               'Owner':owner,
               'end':1}

class Moon(Card):
    def __init__(self, guilded:bool=False):
        super().__init__(guilded=guilded, path='Assets/Cards/cards/18_theMoon/18_theMoon_2x.png', idNum=18)
        self.idNum = 18

    def Invoke(self, owner:str):
       """Invoke the Cards special ability
       half mana generation for the rest of the game, Must be in a deck with the Sun"""
       return {'Name':self.__class__.__name__,
               'Owner':owner,
               'end':1}

class Sun(Card):
    def __init__(self, guilded:bool=False):
        super().__init__(guilded=guilded, path='Assets/Cards/cards/19_theSun/19_theSun_2x.png', idNum=19)
        self.idNum = 19

    def Invoke(self, owner:str):
       """Invoke the Cards special ability
       Double mana generation for the rest of the game, Must be in a deck with the Moon"""
       return {'Name':self.__class__.__name__,
               'Owner':owner,
               'end':1}

class Judgement(Card):
    def __init__(self, guilded:bool=False):
        super().__init__(guilded=guilded, path='Assets/Cards/cards/20_judgement/20_judgement_2x.png', idNum=20)
        self.idNum = 20

    def Invoke(self, owner:str):
       """Invoke the Cards special ability
       each player randomly loses a troop"""
       return {'Name':self.__class__.__name__,
               'Owner':owner,
               'end':1}

class World(Card):
    def __init__(self, guilded:bool=False):
        super().__init__(guilded=guilded, path='Assets/Cards/cards/21_theWorld/21_theWorld_2x.png', idNum=21)
        self.idNum = 21

    def Invoke(self, owner:str):
       """Invoke the Cards special ability
       Tap the glass, you destory units when you next click on the battlefield"""
       return {'Name':self.__class__.__name__,
               'Owner':owner,
               'end':10000000000000}
