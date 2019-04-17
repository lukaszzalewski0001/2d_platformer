'''
    Copyright 2019 Łukasz Zalewski.

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0
        
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
'''

import pygame

class EnemyMovement:
    '''Class containing enemy's move and jump handling'''

    def __init__(self, solid, map_, move_default_max_speed, move_default_acceleration, jump_max_speed, jump_acceleration):
        self.solid = solid
        self.map_ = map_
        self.enemy_pos = []

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
        '''Handles enemy's movement'''
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
        '''Handles enemy jumping'''
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