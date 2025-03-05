"""A file containing all the summonable units"""
import pygame, random
class Unit:
    def __init__(self):
        self.hp = 1
        self.attack = 1
        self.cost = 1
        self.speed = 1
        self.x = 0
        self.y = 0
        self.target = [0,0]
        self.Asset = pygame.image.load("Assets\Sprites\\unit_sprites\Footman.png")
    def __str__(self):
        return "A Unit was summoned"
    
    def move(self, frame:int, team:list):
        """
        Move the troop towards its Target
        """

        if frame in range(0, 500, 20) and self.__class__.__name__ != "Generator":
            new_x = self.x
            new_y = self.y

            if self.target[0] > self.x:
                new_x += random.randint(1, self.speed)
            else:
                new_x -= random.randint(1, self.speed)

            if self.target[1] > self.y:
                new_y += random.randint(1, self.speed)
            else:
                new_y -= random.randint(1, self.speed)
            # Check for collisions with other units in the team
            collision = False
            for t in team:
                if t.x == new_x and t.y == new_y:
                    collision = True
                    break

            if not collision:
                self.x = new_x
                self.y = new_y

            # Ensure the unit stays within bounds
            if self.x > 1322:
                self.x = 1322
            elif self.x < 598:
                self.x = 598   
            if self.y > 876:
                self.y = 876
            elif self.y < 154:
                self.y = 154
            
        

class Footman(Unit):
    """The Footman Unit type (!:1/1/1)"""
    def __init__(self, xy:list):
        """
        Create Troop Footman at xy:(x, y) coordinates
        """
        self.hp = 1
        self.attack = 1
        self.cost = 1
        self.speed = 1
        self.x = xy[0]
        self.y = xy[1]
        self.target = [0,0]
        self.Asset = pygame.image.load("Assets\Sprites\\unit_sprites\Footman.png")

class Horse(Unit):
    """The Horse Unit type (#:2/2/3)"""
    def __init__(self, xy:list):
        """
        Create Troop Horse at xy:(x, y) coordinates
        """
        self.hp = 2
        self.attack = 2
        self.cost = 3
        self.speed = 3
        self.x = xy[0]
        self.y = xy[1]
        self.target = [0,0]
        self.Asset = pygame.image.load("Assets\Sprites\\unit_sprites\Horse.png")

class Soldier(Unit):
    """The Soldier Unit type (@:3/3/2)"""
    def __init__(self, xy:list):
        """
        Create Troop Solider at xy:(x, y) coordinates
        """
        self.hp = 3
        self.attack = 3
        self.cost = 3
        self.speed = 2
        self.x = xy[0]
        self.y = xy[1]
        self.target = [0,0]
        self.Asset = pygame.image.load("Assets\Sprites\\unit_sprites\Soldier.png")

class Summoner(Unit):
    """The Summoner Unit type ($:1/0/6)"""
    def __init__(self, xy:list):
        """
        Create Troop Summoner at xy:(x, y) coordinates
        """
        self.hp = 1
        self.attack = 0
        self.cost = 6
        self.speed = 3
        self.x = xy[0]
        self.y = xy[1]
        self.target = [0,0]
        self.Asset = pygame.image.load("Assets\Sprites\\unit_sprites\Summoner.png")

class Minion(Unit):
    """The Minion Unit type (%:1/2/0)"""
    def __init__(self, xy:list):
        """
        Create Troop minion at xy:(x, y) coordinates
        """
        self.hp = 1
        self.attack = 2
        self.cost = 0
        self.speed = 2
        self.x = xy[0]
        self.y = xy[1]
        self.lifetime = 0
        self.target = [0,0]
        self.Asset = pygame.image.load("Assets\Sprites\\unit_sprites\Minion.png")

class Generator(Unit):
    """The Generator Unit type (^:4/0/0)"""
    def __init__(self, xy:list):
        """
        control Troop generator at xy:(x, y) coordinates
        """
        self.hp = 4
        self.attack = 0
        self.cost = 0
        self.speed = 0
        self.x = xy[0]
        self.y = xy[1]
        self.target = [0,0]
        self.Asset = pygame.image.load("Assets\Sprites\Generator.png")

class Runner(Unit):
    """The Runner Unit type (&:3/3/8)"""
    def __init__(self, xy:list):
        """
        Create Troop Runner at xy:(x, y) coordinates
        """
        self.hp = 3
        self.attack = 3
        self.cost = 8
        self.speed = 10
        self.x = xy[0]
        self.y = xy[1]
        self.target = [0,0]
        self.Asset = pygame.image.load("Assets\Sprites\\unit_sprites\Runner.png")

class Tank(Unit):
    """The Tank Unit type (*:10/10/8)"""
    def __init__(self, xy:list):
        """
        Create Troop Tank at xy:(x, y) coordinates
        """
        self.hp = 10
        self.attack = 10
        self.cost = 8
        self.speed = 3
        self.x = xy[0]
        self.y = xy[1]
        self.target = [0,0]
        self.Asset = pygame.image.load("Assets\Sprites\\unit_sprites\Tank.png")