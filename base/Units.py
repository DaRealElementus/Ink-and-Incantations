"""A file containing all the summonable units"""
import pygame
import random
import os


class Unit:
    def __init__(self):
        self.hp = 1
        self.attack = 1
        self.cost = 1  # Default cost for a unit
        self.speed = 1
        self.x = 0
        self.y = 0
        self.true_x = self.x
        self.true_y = self.x
        self.target = [0, 0]
        self.lifetime = 0
        self.Goal = 'None'
        self.achived = True
        self.spawn_timer = 0
        self.move_timer = 0  # Initialize move timer for all units
        self.Asset = pygame.image.load(os.path.join(
            "Assets", "Sprites", "unit_sprites", "Footman.png"))

    def __str__(self):
        return "a unit of type " + self.__class__.__name__ + " with " + str(self.hp) + " HP and " + str(self.attack) + " attack at " + str(self.x) + " " + str(self.y) + " with a target of " + str(self.target) + " and a cost of " + str(self.cost) + " and a speed of " + str(self.speed)

    def move(self, dt: float, team: list, boundaries: dict, Scalars: list) -> None:
        if self.__class__.__name__ != "Generator":
            new_x, new_y = self.true_x, self.true_y
            scale_x, scale_y = Scalars[0], Scalars[1]
            speed_factor = dt * 4

            # Determine target
            if isinstance(self.target, Unit):
                target = [self.target.x, self.target.y]
            elif isinstance(self.target, (list, tuple)):
                target = self.target
            else:
                target = [self.x, self.y]

            # Calculate direction vector
            dx = target[0] - self.x
            dy = target[1] - self.y
            distance = (dx ** 2 + dy ** 2) ** 0.5

            # Only move if not at target
            if distance > 0:
                # Normalize direction
                norm_dx = dx / distance
                norm_dy = dy / distance

                # Calculate movement amount
                move_dist = min(self.speed * speed_factor, distance)
                move_x = norm_dx * move_dist * scale_x
                move_y = norm_dy * move_dist * scale_y

                # Summoner stays 10 pixels away from target
                if self.__class__.__name__ == "Summoner" and distance > 20:
                    new_x += move_x
                    new_y += move_y
                elif self.__class__.__name__ != "Summoner":
                    new_x += move_x
                    new_y += move_y

            # Check for collisions
            collision = any(t.true_x == new_x and t.true_y ==
                            new_y for t in team if t is not self)

            # Update position if no collision
            if not collision:
                self.true_x, self.true_y = new_x, new_y

            # Ensure the unit stays within bounds
            self.true_x = max(boundaries["left"], min(
                boundaries["right"], self.true_x))
            self.true_y = max(boundaries["top"], min(
                boundaries["bottom"], self.true_y))

            self.x, self.y = int(self.true_x), int(self.true_y)


# Subclasses with specific costs
class Footman(Unit):
    cost = 1  # Cost for Footman, does not change
    """The Footman Unit type (!:1/1/1)"""

    def __init__(self, xy: list, scalar: list = [1, 1]):
        super().__init__()
        self.hp = 1
        self.attack = 1
        self.speed = 1
        self.x = xy[0]
        self.y = xy[1]
        self.true_x, self.true_y = xy
        self.target = [0, 0]
        self.Asset = pygame.image.load(os.path.join(
            "Assets", "Sprites", "unit_sprites", "Footman.png"))
        self.Asset = pygame.transform.smoothscale(
            self.Asset, [self.Asset.get_width() * scalar[0], self.Asset.get_height() * scalar[1]])


class Horse(Unit):
    """The Horse Unit type (#:2/2/3)"""
    cost = 3  # Cost for Horse, does not change

    def __init__(self, xy: list, scalar: list = [1, 1]):
        super().__init__()
        self.hp = 2
        self.attack = 2
        self.speed = 3
        self.x = xy[0]
        self.y = xy[1]
        self.true_x, self.true_y = xy
        self.target = [0, 0]
        self.Asset = pygame.image.load(os.path.join(
            "Assets", "Sprites", "unit_sprites", "Horse.png"))
        self.Asset = pygame.transform.smoothscale(
            self.Asset, [self.Asset.get_width() * scalar[0], self.Asset.get_height() * scalar[1]])


class Soldier(Unit):
    """The Soldier Unit type (@:3/3/2)"""
    cost = 3  # Cost for Soldier, does not change

    def __init__(self, xy: list, scalar: list = [1, 1]):
        super().__init__()
        self.hp = 3
        self.attack = 3
        self.speed = 2
        self.x = xy[0]
        self.y = xy[1]
        self.true_x, self.true_y = xy
        self.target = [0, 0]
        self.Asset = pygame.image.load(os.path.join(
            "Assets", "Sprites", "unit_sprites", "Soldier.png"))
        self.Asset = pygame.transform.smoothscale(
            self.Asset, [self.Asset.get_width() * scalar[0], self.Asset.get_height() * scalar[1]])


class Summoner(Unit):
    """The Summoner Unit type ($:1/0/6)"""
    cost = 6  # Cost for Summoner, does not change

    def __init__(self, xy: list, scalar: list = [1, 1]):
        super().__init__()
        self.hp = 1
        self.attack = 0
        self.speed = 3
        self.x = xy[0]
        self.y = xy[1]
        self.true_x, self.true_y = xy
        self.target = [0, 0]
        self.Asset = pygame.image.load(os.path.join(
            "Assets", "Sprites", "unit_sprites", "Summoner.png"))
        self.Asset = pygame.transform.smoothscale(
            self.Asset, [self.Asset.get_width() * scalar[0], self.Asset.get_height() * scalar[1]])


class Minion(Unit):
    """The Minion Unit type (%:1/2/0), this unit is only summoned by the Summoner"""
    cost = 0  # Cost for Minion, never summoned by player

    def __init__(self, xy: list, scalar: list = [1, 1], Master: object = None):
        super().__init__()
        self.hp = 1
        self.attack = 1
        self.speed = 2
        self.x = xy[0]
        self.y = xy[1]
        self.true_x, self.true_y = xy
        self.lifetime = 0
        self.master = Master  # Reference to the Summoner that spawned this Minion
        self.target = [0, 0]
        self.Asset = pygame.image.load(os.path.join(
            "Assets", "Sprites", "unit_sprites", "Minion.png"))
        self.Asset = pygame.transform.smoothscale(
            self.Asset, [self.Asset.get_width() * scalar[0], self.Asset.get_height() * scalar[1]])


class Generator(Unit):
    """The Generator Unit type (^:4/0/0)"""
    cost = 0  # Cost for Generator, never summoned by player

    def __init__(self, xy: list, scalar: list = [1, 1]):
        super().__init__()
        self.hp = 4
        self.attack = 0
        self.speed = 0
        self.x = xy[0]
        self.y = xy[1]
        self.true_x, self.true_y = xy
        self.target = [0, 0]
        self.Asset = pygame.image.load(os.path.join(
            "Assets", "Sprites", "Generator.png"))
        self.Asset = pygame.transform.smoothscale(
            self.Asset, [self.Asset.get_width() * scalar[0], self.Asset.get_height() * scalar[1]])


class Runner(Unit):
    """The Runner Unit type (&:3/3/8)"""
    cost = 8  # Cost for Runner, does not change

    def __init__(self, xy: list, scalar: list = [1, 1]):
        super().__init__()
        self.hp = 3
        self.attack = 3
        self.speed = 10
        self.x = xy[0]
        self.y = xy[1]
        self.true_x, self.true_y = xy
        self.target = [0, 0]
        self.Asset = pygame.image.load(os.path.join(
            "Assets", "Sprites", "unit_sprites", "Runner.png"))
        self.Asset = pygame.transform.smoothscale(
            self.Asset, [self.Asset.get_width() * scalar[0], self.Asset.get_height() * scalar[1]])


class Tank(Unit):
    """The Tank Unit type (*:10/10/8)"""
    cost = 8  # Cost for Tank, does not change

    def __init__(self, xy: list, scalar: list = [1, 1]):
        super().__init__()
        self.hp = 10
        self.attack = 10
        self.speed = 3
        self.x = xy[0]
        self.y = xy[1]
        self.true_x, self.true_y = xy
        self.target = [0, 0]
        self.Asset = pygame.image.load(os.path.join(
            "Assets", "Sprites", "unit_sprites", "Tank.png"))
        self.Asset = pygame.transform.smoothscale(
            self.Asset, [self.Asset.get_width() * scalar[0], self.Asset.get_height() * scalar[1]])
