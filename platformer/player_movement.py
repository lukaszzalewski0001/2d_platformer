import pygame

class Movement:
    '''Class containing player's move and jump handling'''

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
        '''Handles player's movement'''
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
        '''Handles player's jumping'''
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