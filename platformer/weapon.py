import pygame
import math

class Bullet:
    '''Class defining bullet'''

    def __init__(self, pos, speed, solid, angle, range):
        self.pos = pos
        self.speed = speed
        self.solid = solid
        self.angle = angle
        self.range = range
        self.distance_traveled = 0
        
    def calculate_new_pos(self, time):
        '''Calculates and sets new bullet's position and also removes
        bullet if it's extended its range. Returns True if bullet extended its range,
        otherwise False
        
        Arguments:
            time {int} -- time in miliseconds
        
        Returns:
            bool
        '''

        distance = time / 1000 * self.speed
        self.distance_traveled += distance
        self.pos[0] += distance * math.cos(self.angle)
        self.pos[1] += distance * math.sin(self.angle)

        if self.distance_traveled >= self.range:
            return True

        return False

class Weapon:
    '''Class defining weapon'''

    def __init__(self, shooting_type, shooting_type_arg, damage, bullets_speed, bullets_per_second, bullets_solid, bullets_range):
        self.shooting = False
        self.shooting_type = shooting_type
        self.shooting_type_arg = shooting_type_arg
        self.damage = damage
        self.bullets_speed = bullets_speed
        self.bullets_per_second = bullets_per_second
        self.bullets_solid = bullets_solid
        self.bullets = []
        self.clock = pygame.time.Clock()
        self.clock_combined_time = 0
        self.shoot_tick_time = 10
        self.bullets_range = bullets_range

    def shoot(self, entity_pos, angle):
        '''Shoots new bullet from player's position in given angle
        
        Arguments:
            player_pos {list(int)} -- entity position
            angle {float} -- angle in radians
        '''

        weapon_pos = entity_pos[:]
        weapon_pos[0] += 32
        weapon_pos[1] += 16
        if self.shooting_type == 0:
            self.bullets.append(Bullet(weapon_pos, self.bullets_speed, self.bullets_solid, angle, self.bullets_range))
        elif self.shooting_type == 1:
            for i in range(self.shooting_type_arg):
                self.bullets.append(Bullet([weapon_pos[0], weapon_pos[1]], self.bullets_speed, self.bullets_solid,
                                    math.radians((i/self.shooting_type_arg) * 360), self.bullets_range))
        elif self.shooting_type == 2:
            for i in range(-(self.shooting_type_arg // 2), (self.shooting_type_arg // 2) + 1, 1):
                self.bullets.append(Bullet([weapon_pos[0], weapon_pos[1]], self.bullets_speed, self.bullets_solid,
                                    angle + math.radians(45 * (i / self.shooting_type_arg)), self.bullets_range))
            
    def calculate_bullets_pos(self):
        '''Calculates positions for all bullets shot by weapon's object'''
        for bullet in self.bullets:
            if bullet.calculate_new_pos(self.clock_combined_time):
                self.bullets.remove(bullet)


