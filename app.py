import pygame
import sys
import os
import math
import random

class Player:
    def __init__(self):
        self.finished = 0
        self.player_pos = [0, 448]
        self.player_pos_on_screen = [0, 448]
        self.weapon = None
        self.current_weapon = -1
        self.weapons = []
        self.keys = 0
        self.keys_to_collect = 0

    def set_starting_hp(self, hp):
        self.max_hp = hp
        self.hp = self.max_hp

    def add_weapon(self, weapon):
        self.weapons.append(weapon)
        if not self.weapon:
            self.current_weapon = 0
            self.weapon = self.weapons[self.current_weapon]

    def add_hp(self, hp):
        if self.hp == self.max_hp:
            return False
        else:
            self.hp += hp
            if self.hp > self.max_hp:
                self.hp = self.max_hp
            return True

    def change_weapon(self, next):
        if len(self.weapons) > 0:
            if self.current_weapon >= 0:
                if next:
                    self.current_weapon += 1
                    if self.current_weapon >= len(self.weapons):
                        self.current_weapon = 0
                else:
                    self.current_weapon -= 1
                    if self.current_weapon < 0:
                        self.current_weapon = len(self.weapons) - 1
            
            self.weapon = self.weapons[self.current_weapon]

    def calculate_player_pos_on_screen(self, map_size):
        if (self.player_pos[0] <= 320):
            self.player_pos_on_screen[0] = self.player_pos[0]
        elif (self.player_pos[0] >= map_size*32 - 320):
            self.player_pos_on_screen[0] = 640 - \
                (map_size*32 - self.player_pos[0])
        else:
            self.player_pos_on_screen[0] = 320

    def is_bullet_on_player(self, bullet_pos):
        if self.player_pos[0] <= bullet_pos[0] <= self.player_pos[0] + 32 and self.player_pos[1] <= bullet_pos[1] <= self.player_pos[1] + 32:
            return True
        
        return False

    def hit(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            return True

        return False

    def die(self):
        self.finished = 1


class Enemy:
    def __init__(self, image_name, block_pos, movement, hp, weapon):
        self.image_name = image_name
        self.start_block_pos = block_pos
        self.movement = movement
        self.pos = [self.start_block_pos[0] * 32, self.start_block_pos[1] * 32]
        self.movement.enemy_pos = self.pos
        self.pos_on_screen = []
        self.hp = hp
        self.weapon = weapon
        self.is_in_bigger_sight_ = False

    def set_ai(self, ai):
        self.ai = ai
        self.ai.weapon = self.weapon

    def is_bullet_on_enemy(self, bullet_pos):
        if self.pos[0] <= bullet_pos[0] <= self.pos[0] + 32 and self.pos[1] <= bullet_pos[1] <= self.pos[1] + 32:
            return True
        
        return False

    def hit(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            return True

        return False

    # zakladajac ze najwiekszy range broni to 960 wiec blockowy sight bedzie 30
    def is_in_bigger_sight(self, player_pos):
        if abs(self.pos[0] - player_pos[0]) <= 960:
            self.is_in_bigger_sight_ = True
        else:
            self.is_in_bigger_sight_ = False


class EnemyMovement:
    def __init__(self, solid, map_, move_default_max_speed, move_default_acceleration, jump_max_speed, jump_acceleration):
        self.solid = solid
        self.map_ = map_
        self.enemy_pos = None

        # Moving
        self.moving = False
        self.move_speed = 0
        self.move_default_max_speed = move_default_max_speed
        self.move_default_acceleration = move_default_acceleration
        self.move_max_speed = self.move_default_max_speed
        self.move_acceleration = self.move_default_acceleration
        self.move_current_speed = self.move_speed
        self.move_dir = 0  # 0 left 1 right
        self.move_tick_time = 15  # ms
        self.move_clock = pygame.time.Clock()
        self.move_clock_combined_time = 0

        # Jumping
        self.jumping = False
        self.jump_speed = 0
        self.jump_max_speed = jump_max_speed
        self.jump_acceleration = jump_acceleration
        self.jump_current_speed = self.jump_speed
        self.jump_dir = 0  # 0 up 1 down
        self.jump_tick_time = 20
        self.jump_clock = pygame.time.Clock()
        self.jump_clock_combined_time = 0

    def move(self):
        if self.moving:
            self.move_max_speed = self.move_default_max_speed
            self.move_acceleration = self.move_default_acceleration

            if self.move_current_speed < self.move_max_speed:
                self.move_current_speed += self.move_acceleration
            else:
                self.move_current_speed -= self.move_acceleration

                if self.move_dir == 0 and not self.map_.is_any_solid_block_left_from_entity(self.enemy_pos):
                    self.enemy_pos[0] = self.enemy_pos[0] - \
                        self.move_current_speed if self.enemy_pos[0] > self.move_current_speed else 0
                    if not self.map_.is_any_solid_block_below_entity(self.enemy_pos) and not self.jumping and self.enemy_pos[1] < 448:
                        self.jumping = True
                        self.jump_dir = 1
                        self.jump_current_speed = self.jump_speed
                elif self.move_dir == 1 and not self.map_.is_any_solid_block_right_from_entity(self.enemy_pos):
                    self.enemy_pos[0] = self.enemy_pos[0] + \
                    self.move_current_speed if self.enemy_pos[0] < self.map_.map_size * 32 - 32 else self.map_.map_size*32 - 32
                    if not self.map_.is_any_solid_block_below_entity(self.enemy_pos) and not self.jumping and self.enemy_pos[1] < 448:
                        self.jumping = True
                        self.jump_dir = 1
                        self.jump_current_speed = self.jump_speed

    def jump(self):
        if self.jumping:
            if self.jump_dir == 0 and not self.map_.is_any_solid_block_above_entity(self.enemy_pos):     
                self.jump_current_speed -= self.jump_acceleration
                self.enemy_pos[1] -= self.jump_current_speed
                if self.jump_current_speed <= 0:
                    self.jump_dir = 1
                    self.jump_current_speed = 0
            elif self.jump_dir == 1 and not self.map_.is_any_solid_block_below_entity(self.enemy_pos):
                self.jump_current_speed += self.jump_acceleration
                if self.enemy_pos[1] + self.jump_current_speed + 32 > 480:
                    self.enemy_pos[1] = 448
                    self.jumping = False
                else:
                    self.enemy_pos[1] += self.jump_current_speed
            else:
                if self.jump_dir == 0:
                    self.jump_dir = 1
                    self.jump_current_speed = 0
                else:
                    self.jumping = False


class EnemyAI:
    def __init__(self, player, movement, ai_scheme, ai_level):
        self.player = player
        self.movement = movement
        self.ai_scheme = ai_scheme
        self.ai_level = ai_level
        self.weapon = None
        
    def tick(self):
        if self.ai_scheme == 1:
            self.dumb_moving_left_right_ai()
        elif self.ai_scheme == 2:
            self.full_dumb_movement_ai()  
        elif self.ai_scheme == 3:
            self.moving_to_player_ai() 
        elif self.ai_scheme == 4:
            self.full_movement_ai()

    def shooting_ai(self):
        # just shooting
        if self.ai_level == 0:
             self.weapon.shoot([self.movement.enemy_pos[0] - 16, self.movement.enemy_pos[1]], math.radians(random.randrange(360)))
        if self.ai_level == 1:
            angle = math.atan2(self.player.player_pos[1] - self.movement.enemy_pos[1],
                               self.player.player_pos[0] - self.movement.enemy_pos[0])
            self.weapon.shoot([self.movement.enemy_pos[0] - 16, self.movement.enemy_pos[1]], angle) 

    def dumb_moving_left_right_ai(self):
        # moving left to right for no reason
        self.movement.moving = True
        if (self.movement.enemy_pos[0] == 0 and self.movement.move_dir == 0) or self.movement.map_.is_any_solid_block_left_from_entity(self.movement.enemy_pos):
              self.movement.move_dir = 1
        elif (self.movement.enemy_pos[0] == (self.movement.map_.map_size - 1) * 32 and self.movement.move_dir == 1) or self.movement.map_.is_any_solid_block_right_from_entity(self.movement.enemy_pos):
            self.movement.move_dir = 0

    def full_dumb_movement_ai(self):
        # moving and jumping for no reason
        self.dumb_moving_left_right_ai()

        if not self.movement.jumping:
            self.movement.jump_current_speed = self.movement.jump_max_speed
            self.movement.jumping = True
            self.movement.jump_dir = 0
    
    def moving_to_player_ai(self):
        # moving and jumping towards player
        self.movement.moving = True
        if abs(self.player.player_pos[0] - self.movement.enemy_pos[0]) <= 8:
            self.movement.moving = False
        elif self.player.player_pos[0] < self.movement.enemy_pos[0]:
            self.movement.move_dir = 0
        elif self.player.player_pos[0] > self.movement.enemy_pos[0]:
            self.movement.move_dir = 1
        

    def full_movement_ai(self):
        self.moving_to_player_ai()

        if not self.movement.jumping:
            if self.player.player_pos[1] < self.movement.enemy_pos[1]:
                self.movement.jump_current_speed = self.movement.jump_max_speed
                self.movement.jumping = True
                self.movement.jump_dir = 0


class Weapon:
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

    def shoot(self, player_pos, angle):
        weapon_pos = player_pos[:]
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
        for bullet in self.bullets:
            if bullet.calculate_new_pos(self.clock_combined_time):
                self.bullets.remove(bullet)


class ConsumableBlock:
    def __init__(self, block_pos, image_name):
        self.block_pos = block_pos
        self.image_name = image_name

    def on_pick_up(self, player):
        pass

    def is_player_on_block(self, player):
        if (player.player_pos[0] + 16) // 32 == self.block_pos[0] and (player.player_pos[1] + 16) // 32 == self.block_pos[1]:
            if self.on_pick_up(player):
                return True

        return False


class HealthBlock(ConsumableBlock):
    def __init__(self, block_pos, image_name, hp):
        super().__init__(block_pos, image_name)
        self.hp = hp

    def on_pick_up(self, player):
        return player.add_hp(self.hp)


class WeaponBlock(ConsumableBlock): 
    def __init__(self, block_pos, image_name, weapon):
        super().__init__(block_pos, image_name)
        self.weapon = weapon

    def on_pick_up(self, player):
        player.add_weapon(self.weapon)

        return True


class KeyBlock(ConsumableBlock):
    def __init__(self, block_pos, image_name):
        super().__init__(block_pos, image_name)

    def on_pick_up(self, player):
        player.keys += 1

        return True


class FinishBlock(ConsumableBlock):
    def __init__(self, block_pos, image_name):
        super().__init__(block_pos, image_name)

    def on_pick_up(self, player):
        if player.keys >= player.keys_to_collect:
            player.finished = 2
            return True

        return False


class Bullet:
    def __init__(self, pos, speed, solid, angle, range):
        self.pos = pos
        self.speed = speed
        self.solid = solid
        self.angle = angle
        self.range = range
        self.distance_traveled = 0
        
    def calculate_new_pos(self, time):
        distance = time / 1000 * self.speed
        self.distance_traveled += distance
        self.pos[0] += distance * math.cos(self.angle)
        self.pos[1] += distance * math.sin(self.angle)

        if self.distance_traveled >= self.range:
            return True

        return False


class Movement:
    def __init__(self, player, enemies, map_, graphics):
        self.player = player
        self.enemies = enemies
        self.map_ = map_
        self.graphics = graphics

        # Moving
        self.moving = False
        self.move_speed = 0
        self.move_default_max_speed = 7
        self.move_default_acceleration = 1
        self.move_max_speed = self.move_default_max_speed
        self.move_acceleration = self.move_default_acceleration
        self.move_current_speed = self.move_speed
        self.move_dir = 0  # 0 left 1 right
        self.move_tick_time = 15  # ms
        self.move_clock = pygame.time.Clock()
        self.move_clock_combined_time = 0

        # Jumping
        self.jumping = False
        self.jump_speed = 0
        self.jump_max_speed = 14
        self.jump_acceleration = 1
        self.jump_current_speed = self.jump_speed
        self.jump_dir = 0  # 0 up 1 down
        self.jump_tick_time = 20
        self.jump_clock = pygame.time.Clock()
        self.jump_clock_combined_time = 0

    def move(self):
        if self.moving:
            self.move_max_speed = self.move_default_max_speed
            self.move_acceleration = self.move_default_acceleration

            fx = self.map_.get_block_below_player_fx()
            if fx == None or fx == '0':
                pass
            else:
                if fx == 'speed0':
                    self.move_max_speed *= 1.5
                    self.move_acceleration *= 1.5
                elif fx == 'speed1':
                    self.move_max_speed *= 2.0
                    self.move_acceleration *= 2.0
                elif fx == 'speed2':
                    self.move_max_speed *= 3.0
                    self.move_acceleration *= 3.0

            if self.move_current_speed < self.move_max_speed:
                self.move_current_speed += self.move_acceleration
            else:
                self.move_current_speed -= self.move_acceleration

            if self.move_dir == 0 and not self.map_.is_any_solid_block_left_from_entity(self.player.player_pos):
                self.player.player_pos[0] = self.player.player_pos[0] - \
                    self.move_current_speed if self.player.player_pos[0] > self.move_current_speed else 0
                if not self.map_.is_any_solid_block_below_entity(self.player.player_pos) and not self.jumping and self.player.player_pos[1] < 448:
                    self.jumping = True
                    self.jump_dir = 1
                    self.jump_current_speed = self.jump_speed
            elif self.move_dir == 1 and not self.map_.is_any_solid_block_right_from_entity(self.player.player_pos):
                self.player.player_pos[0] = self.player.player_pos[0] + \
                self.move_current_speed if self.player.player_pos[0] < self.map_.map_size * 32 - 32 else self.map_.map_size*32 - 32
                if not self.map_.is_any_solid_block_below_entity(self.player.player_pos) and not self.jumping and self.player.player_pos[1] < 448:
                    self.jumping = True
                    self.jump_dir = 1
                    self.jump_current_speed = self.jump_speed

            self.player.calculate_player_pos_on_screen(self.map_.map_size)

    def jump(self):
        if self.jumping:
            if self.jump_dir == 0 and not self.map_.is_any_solid_block_above_entity(self.player.player_pos):     
                self.jump_current_speed -= self.jump_acceleration
                self.player.player_pos[1] -= self.jump_current_speed
                if self.jump_current_speed <= 0:
                    self.jump_dir = 1
                    self.jump_current_speed = 0
            elif self.jump_dir == 1 and not self.map_.is_any_solid_block_below_entity(self.player.player_pos):
                self.jump_current_speed += self.jump_acceleration
                if self.player.player_pos[1] + self.jump_current_speed + 32 > self.graphics.size[1]:
                    self.player.player_pos[1] = self.graphics.size[1] - 32
                    self.jumping = False
                else:
                    self.player.player_pos[1] += self.jump_current_speed
            else:
                if self.jump_dir == 0:
                    self.jump_dir = 1
                    self.jump_current_speed = 0
                else:
                    self.jumping = False

        self.player.player_pos_on_screen[1] = self.player.player_pos[1]


class Map:
    def __init__(self, player):
        self.player = player
        self.map_size = 0
        self.bg_image_name = None
        self.ground_list = []
        self.enemy_list = []
        self.consumable_blocks = []
        self.text_color = []

    def load(self, path):
        map_file = open(path, 'r')
        lines = map_file.readlines()

        objects = []

        for line in lines:
            splitted_lines = line.split(',')
            objects.append(splitted_lines)

        for obj in objects:
            obj[len(obj) - 1] = obj[len(obj) - 1].rstrip('\n')
            if obj[0] == 'i':
                obj.pop(0)
                self.read_map_info(obj)
            elif obj[0] == 'g':
                obj.pop(0)
                self.read_obj_info(obj)
            elif obj[0] == 'e':
                obj.pop(0)
                self.read_enemy_info(obj)
            elif obj[0] == 'h':
                obj.pop(0)
                self.read_health_consumable_info(obj)
            elif obj[0] == 'w':
                obj.pop(0)
                self.read_weapon_consumable_info(obj)
            elif obj[0] == 'k':
                obj.pop(0)
                self.read_key_consumable_info(obj)
            elif obj[0] == 'f':
                obj.pop(0)
                self.read_finish_consumable_info(obj)

    def read_map_info(self, list):
        self.bg_image_name = list[0]
        self.text_color = [int(list[1]), int(list[2]), int(list[3])]
        self.map_size = int(list[4])
        self.player.set_starting_hp(int(list[5]))
        self.player.keys_to_collect = int(list[6])

    def read_obj_info(self, list):
        for i in range(1, 5, 1):
            list[i] = int(list[i])
        self.ground_list.append(list)

    def read_enemy_info(self, list):
        for i in range(1, 17, 1):
            list[i] = int(list[i])
        list[13] = bool(list[13])
        self.enemy_list.append(list)

    def read_health_consumable_info(self, list):
        for i in range(1, 4, 1):
            list[i] = int(list[i])
        self.consumable_blocks.append(HealthBlock([list[1], list[2]], list[0], list[3]))

    def read_weapon_consumable_info(self, list):
        for i in range(1, 10, 1):
            list[i] = int(list[i])
        list[8] = bool(list[8])
        self.consumable_blocks.append(WeaponBlock([list[1], list[2]], list[0], 
                                      Weapon(list[3], list[4], list[5], list[6], list[7], list[8], list[9])))

    def read_key_consumable_info(self, list):
        for i in range(1, 3, 1):
            list[i] = int(list[i])
        self.consumable_blocks.append(KeyBlock([list[1], list[2]], list[0]))

    def read_finish_consumable_info(self, list):
        for i in range(1, 3, 1):
            list[i] = int(list[i])
        self.consumable_blocks.append(FinishBlock([list[1], list[2]], list[0]))

    def get_objects_in_sight(self):
        player_block = self.player.player_pos[0] // 32
        max_render_length = abs(320 - self.player.player_pos_on_screen[0]) // 32
        return [ground for ground in self.ground_list if abs(player_block - ground[1]) < max_render_length + 11 and ground[4] == 1]

    def get_consumable_blocks_in_sight(self):
        player_block = self.player.player_pos[0] // 32
        max_render_length = abs(320 - self.player.player_pos_on_screen[0]) // 32
        return [block for block in self.consumable_blocks if abs(player_block - block.block_pos[0]) < max_render_length + 11]

    def is_any_solid_block_left_from_entity(self, entity_pos):
        entity_block_x = entity_pos[0] // 32
        entity_block_y = entity_pos[1] // 32
        blocks = [ground for ground in self.ground_list if entity_block_x -
                  ground[1] == 0 and entity_block_y - ground[2] == 0 and ground[3] == 1]
        if blocks:
            return True
        return False

    def is_any_solid_block_right_from_entity(self, entity_pos):
        entity_block_x = entity_pos[0] // 32
        entity_block_y = entity_pos[1] // 32
        blocks = [ground for ground in self.ground_list if ground[1] -
                  entity_block_x == 1 and ground[2] - entity_block_y == 0
                  and ground[3] == 1]
        if blocks:
            return True
        return False

    def is_any_solid_block_above_entity(self, entity_pos):
        entity_block_x = entity_pos[0] // 32
        entity_block_x_rem = entity_pos[0] % 32
        entity_block_y = entity_pos[1] // 32
        blocks = [ground for ground in self.ground_list if
                  ((entity_block_x - ground[1] == 0 and entity_block_x_rem < 19) or
                  (entity_block_x - ground[1] == -1 and entity_block_x_rem > 13)) and 
                  entity_block_y - ground[2] == 0 and ground[3] == 1]
        if blocks:
            return True
        return False

    def is_any_solid_block_below_entity(self, entity_pos):
        entity_block_x = entity_pos[0] // 32
        entity_block_x_rem = entity_pos[0] % 32
        entity_block_y = entity_pos[1] // 32
        blocks = [ground for ground in self.ground_list if
                  ((entity_block_x - ground[1] == 0 and entity_block_x_rem < 19) or
                  (entity_block_x - ground[1] == -1 and entity_block_x_rem > 13)) and entity_block_y - ground[2] == -1 and ground[3] == 1]
        if blocks:
            entity_pos[1] = blocks[0][2] * 32 - 32
            return True
        return False

    def get_block_below_player_fx(self):
        player_block_x = self.player.player_pos[0] // 32
        player_block_x_rem = self.player.player_pos[0] % 32
        player_block_y = self.player.player_pos[1] // 32
        blocks = [ground for ground in self.ground_list if
                  ((player_block_x - ground[1] == 0 and player_block_x_rem < 19) or
                  (player_block_x - ground[1] == -1 and player_block_x_rem > 13)) and player_block_y - ground[2] == -1 and ground[3] == 1]
        if blocks:
            return blocks[0][5]
        return None

    def is_bullet_in_visible_objects(self, bullet_pos):
        objects = self.get_objects_in_sight()
        diff = self.player.player_pos[0] - self.player.player_pos_on_screen[0]
        for object_ in objects:
            if (object_[1]*32 <= bullet_pos[0] <= object_[1]*32 + 32) and (object_[2]*32 <= bullet_pos[1] <= object_[2]*32 + 32):
               return True
        
        return False


class Graphics:
    def __init__(self, player, enemies, map_, current_map, maps):
        self.player = player
        self.enemies = enemies
        self.map_ = map_

        self.size = (640, 480)
        self.display = pygame.display.set_mode(self.size)
        self.images = {}
        self.load_images('img\\')

        self.current_map = current_map
        self.maps = maps
        self.font = pygame.font.SysFont('arial', 20, 1)

    def load_images(self, path):
        files = os.listdir(path)
        files = [f for f in files if f.find('.png') != -1]
        for file_ in files:
            self.images[file_.replace('.png', '')] = pygame.image.load(
                path + file_)

    def render(self):
        self.display.fill((0, 0, 0))
        
        self.render_background()
        self.render_player()
        self.render_blocks()
        self.render_consumable_blocks()
        self.render_bullets()
        self.render_enemies_in_sight()
        self.render_enemy_bullets()
        self.render_texts()

        pygame.display.flip()

    def render_background(self):
        self.display.blit(self.images[self.map_.bg_image_name], pygame.Rect(0, 0, 640, 480))

    def render_player(self):
        self.display.blit(self.images['player'], pygame.Rect(
            self.player.player_pos_on_screen[0], self.player.player_pos_on_screen[1],
            self.player.player_pos_on_screen[0] + 32, self.player.player_pos_on_screen[1] + 32))

    def render_enemies_in_sight(self):
        player_block = self.player.player_pos[0] // 32
        max_render_length = abs(320 - self.player.player_pos_on_screen[0]) // 32
        enemies = [enemy for enemy in self.enemies if abs(player_block - enemy.pos[0]//32) < max_render_length + 12]

        diff = self.player.player_pos[0] - self.player.player_pos_on_screen[0]
        for enemy in enemies:
            self.display.blit(self.images[enemy.image_name], pygame.Rect(
                enemy.pos[0] - diff, enemy.pos[1],
                enemy.pos[0] - diff + 32, enemy.pos[1] + 32
            ))

    def render_blocks(self):
        for obj in self.map_.get_objects_in_sight():
            diff = self.player.player_pos[0] - self.player.player_pos_on_screen[0]
            self.display.blit(self.images[obj[0]], pygame.Rect(
                obj[1] * 32 - diff, obj[2] * 32, obj[1] * 32 + 32 - diff, obj[2] * 32 + 32))

    def render_consumable_blocks(self):
        for obj in self.map_.get_consumable_blocks_in_sight():
            diff = self.player.player_pos[0] - self.player.player_pos_on_screen[0]
            self.display.blit(self.images[obj.image_name], pygame.Rect(
                obj.block_pos[0] * 32 - diff, obj.block_pos[1] * 32, obj.block_pos[0] * 32 + 32 - diff, obj.block_pos[1] * 32 + 32))

    def render_bullets(self):
        if self.player.weapon:
            diff = self.player.player_pos[0] - self.player.player_pos_on_screen[0]
            for bullet in self.player.weapon.bullets:
                pygame.draw.line(self.display, (255, 255, 255), [bullet.pos[0]-diff, bullet.pos[1] - 2],
                                                                [bullet.pos[0]-diff, bullet.pos[1] + 2], 4)

    def render_enemy_bullets(self):
        player_block = self.player.player_pos[0] // 32
        max_render_length = abs(320 - self.player.player_pos_on_screen[0]) // 32
        enemies = [enemy for enemy in self.enemies if abs(player_block - enemy.pos[0]//32) < max_render_length + 12]

        diff = self.player.player_pos[0] - self.player.player_pos_on_screen[0]
        for enemy in enemies:
            for bullet in enemy.weapon.bullets:
                pygame.draw.line(self.display, (255, 0, 0), [bullet.pos[0]-diff, bullet.pos[1] - 2],
                                [bullet.pos[0]-diff, bullet.pos[1] + 2], 4)

    def render_texts(self):
        text_hp = self.font.render('Health: ' + str(self.player.hp) + ' / ' + str(self.player.max_hp), True, self.map_.text_color)
        text_weapon = self.font.render(f'Weapon: {self.player.current_weapon + 1} / {len(self.player.weapons)}', True, self.map_.text_color)
        text_keys = self.font.render('Keys: ' + str(self.player.keys) + ' / ' + str(self.player.keys_to_collect), True, self.map_.text_color)
        text_maps = self.font.render(f'Map: {str(self.current_map + 1)} / {str(self.maps)}', True, self.map_.text_color)

        self.display.blit(text_hp, (0, 0))
        self.display.blit(text_weapon, (0, 20))
        self.display.blit(text_keys, (640 - text_keys.get_rect().width, 0))
        self.display.blit(text_maps, (640 - text_maps.get_rect().width, 20))
        

class EventHandler:
    def __init__(self, player, enemies, map_, graphics, movement):
        self.player = player
        self.enemies = enemies
        self.map_ = map_
        self.graphics = graphics
        self.movement = movement

    def event_loop(self):
        while not self.player.finished:
            self.handle_input()

            self.handle_movement()
            self.handle_jumping()
            self.handle_shooting()
            self.handle_bullets_collision()
            self.set_enemies_in_bigger_sight()
            self.handle_enemy_ai()
            self.handle_enemy_movement()
            self.handle_enemy_jumping()
            self.handle_enemy_shooting()
            self.handle_enemy_bullets_collision()
            self.handle_consumable_blocks_step()

            self.graphics.render()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    self.movement.moving = True
                    self.movement.move_dir = 0
                    self.movement.move_current_speed = self.movement.move_speed
                elif event.key == pygame.K_d:
                    self.movement.moving = True
                    self.movement.move_dir = 1
                    self.movement.move_current_speed = self.movement.move_speed
                elif event.key == pygame.K_SPACE:
                    if not self.movement.jumping:
                        self.movement.jump_current_speed = self.movement.jump_max_speed

                        fx = self.map_.get_block_below_player_fx()
                        if fx == None or fx == '0':
                            pass
                        else:
                            if fx == 'jmp0':
                                self.movement.jump_current_speed *= 1.25
                            elif fx == 'jmp1':
                                self.movement.jump_current_speed *= 1.5
                            elif fx == 'jmp2':
                                self.movement.jump_current_speed *= 1.75

                        self.movement.jumping = True
                        self.movement.jump_dir = 0
            elif event.type == pygame.MOUSEBUTTONDOWN:           
                if event.button == 1: # left button
                    if self.player.weapon:
                        self.player.weapon.shooting = True        
                elif event.button == 4: 
                    self.player.change_weapon(True)
                elif event.button == 5:
                    self.player.change_weapon(False)   
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: # left button
                    if self.player.weapon:
                        self.player.weapon.shooting = False
            elif event.type == pygame.KEYUP:
                key = pygame.key.get_pressed()
                if not (key[pygame.K_a] or key[pygame.K_d]):
                    self.movement.moving = False

    def handle_movement(self):
        self.movement.move_clock.tick()
        self.movement.move_clock_combined_time += self.movement.move_clock.get_time()
        if self.movement.move_clock_combined_time > self.movement.move_tick_time:
            self.movement.move_clock_combined_time = 0
            self.movement.move()

    def handle_jumping(self):
        self.movement.jump_clock.tick()
        self.movement.jump_clock_combined_time += self.movement.jump_clock.get_time()
        if self.movement.jump_clock_combined_time > self.movement.jump_tick_time:
            self.movement.jump_clock_combined_time = 0
            self.movement.jump()

    def handle_shooting(self):
        if self.player.weapon:
            self.player.weapon.clock.tick()
            self.player.weapon.clock_combined_time += self.player.weapon.clock.get_time()
            self.player.weapon.calculate_bullets_pos()
            if self.player.weapon.clock_combined_time > self.player.weapon.shoot_tick_time:
                if self.player.weapon.clock_combined_time > 1000.0 / self.player.weapon.bullets_per_second:
                    self.player.weapon.clock_combined_time = 0
                    if self.player.weapon.shooting:
                        angle = math.atan2(pygame.mouse.get_pos()[1] - self.player.player_pos_on_screen[1] - 16,
                                             pygame.mouse.get_pos()[0] - self.player.player_pos_on_screen[0])
                        self.player.weapon.shoot(self.player.player_pos, angle)

    def handle_bullets_collision(self):
        if self.player.weapon:
            for bullet in self.player.weapon.bullets:
                for enemy in [en for en in self.enemies if en.is_in_bigger_sight_]:
                    if enemy.is_bullet_on_enemy(bullet.pos):
                        if enemy.hit(self.player.weapon.damage):
                            self.enemies.remove(enemy)
                        self.player.weapon.bullets.remove(bullet)
                        break
                else:
                    if self.player.weapon.bullets_solid:
                        if self.map_.is_bullet_in_visible_objects(bullet.pos):
                            self.player.weapon.bullets.remove(bullet)

    def set_enemies_in_bigger_sight(self):
        for enemy in self.enemies:
            enemy.is_in_bigger_sight(self.player.player_pos)

    def handle_enemy_ai(self):
        for enemy in [en for en in self.enemies if en.is_in_bigger_sight_]:
            enemy.ai.tick()

    def handle_enemy_movement(self):
        for enemy in [en for en in self.enemies if en.is_in_bigger_sight_]:
            enemy.movement.move_clock.tick()
            enemy.movement.move_clock_combined_time += enemy.movement.move_clock.get_time()
            if enemy.movement.move_clock_combined_time > enemy.movement.move_tick_time:
                enemy.movement.move_clock_combined_time = 0
                enemy.movement.move()

    def handle_enemy_jumping(self):
        for enemy in [en for en in self.enemies if en.is_in_bigger_sight_]:
            enemy.movement.jump_clock.tick()
            enemy.movement.jump_clock_combined_time += enemy.movement.jump_clock.get_time()
            if enemy.movement.jump_clock_combined_time > enemy.movement.jump_tick_time:
                enemy.movement.jump_clock_combined_time = 0
                enemy.movement.jump()

    def handle_enemy_shooting(self):
        for enemy in [en for en in self.enemies if en.is_in_bigger_sight_]:
            if enemy.weapon:
                enemy.weapon.clock.tick()
                enemy.weapon.clock_combined_time += enemy.weapon.clock.get_time()
                enemy.weapon.calculate_bullets_pos()
                if enemy.weapon.clock_combined_time > enemy.weapon.shoot_tick_time:
                    if enemy.weapon.clock_combined_time > 1000.0 / enemy.weapon.bullets_per_second:
                        enemy.weapon.clock_combined_time = 0
                        enemy.ai.shooting_ai()

    def handle_enemy_bullets_collision(self):
        for enemy in [en for en in self.enemies if en.is_in_bigger_sight_]:
            for bullet in enemy.weapon.bullets:
                if self.player.is_bullet_on_player(bullet.pos):
                    if self.player.hit(enemy.weapon.damage):
                        self.player.die()
                    enemy.weapon.bullets.remove(bullet)
                    break
                else:
                    if enemy.weapon.bullets_solid:
                        if self.map_.is_bullet_in_visible_objects(bullet.pos):
                            enemy.weapon.bullets.remove(bullet)

    def handle_consumable_blocks_step(self):
        for block in self.map_.get_consumable_blocks_in_sight():
            if block.is_player_on_block(self.player):
                self.map_.consumable_blocks.remove(block)


class Game:
    def __init__(self):
        pygame.init()

        self.map_path = input('Podaj sciezke do map: ')
        self.load_map_list(self.map_path)
        self.current_map = 0

    def load_map_list(self, path):
        self.maps = [map_ for map_ in os.listdir(path) if map_.find('.map') != -1]

    def load_next_map(self):
        self.player = Player()
        self.enemies = []
        self.map_ = Map(self.player)
        self.map_.load(f'{self.map_path}\\map{str(self.current_map)}.map')
        self.load_enemies()
        self.graphics = Graphics(self.player, self.enemies, self.map_, self.current_map, len(self.maps))
        self.movement = Movement(self.player, self.enemies, self.map_, self.graphics)
        self.event_handler = EventHandler(
            self.player, self.enemies, self.map_, self.graphics, self.movement)

    def load_enemies(self):
        for enemy_info in self.map_.enemy_list:
            enemy = Enemy(enemy_info[0], [enemy_info[1], enemy_info[2]], 
                          EnemyMovement(True, self.map_, enemy_info[3], enemy_info[4], enemy_info[5], enemy_info[6]),
                          enemy_info[7],
                          Weapon(enemy_info[8], enemy_info[9], enemy_info[10], enemy_info[11], enemy_info[12], enemy_info[13], enemy_info[14]))
            enemy.set_ai(EnemyAI(self.player, enemy.movement, enemy_info[15], enemy_info[16]))
            self.enemies.append(enemy)

    def play(self):
        while self.current_map < len(self.maps):
            self.load_next_map()
            self.event_handler.event_loop()
            if self.player.finished > 1:
                self.current_map += 1


game = Game()
game.play()

# zrobic kilka mapek
# packnac do exeka

