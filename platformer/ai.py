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

import math
import random

class EnemyAI:
    '''Creates EnemyAI object, that controls ai\'s behaviour'''

    def __init__(self, player, movement, ai_scheme, ai_level):
        self.player = player
        self.movement = movement
        self.ai_scheme = ai_scheme
        self.ai_level = ai_level
        self.weapon = None
        
    def tick(self):
        '''
        Runs enemy's ai depending on ai_scheme value
        
        ai_scheme = 1:
            ai moves left and right
        ai_scheme = 2:
            ai moves left and right, but also jumps
        ai_scheme = 3:
            ai moves towards player
        ai_scheme = 4:
            ai moves and jumps towards player
        '''

        if self.ai_scheme == 1:
            self.__dumb_moving_left_right_ai()
        elif self.ai_scheme == 2:
            self.__full_dumb_movement_ai()  
        elif self.ai_scheme == 3:
            self.__moving_to_player_ai() 
        elif self.ai_scheme == 4:
            self.__full_movement_ai()

    def shooting_ai(self):
        '''
        Responds for enemy's shooting depending on ai_level

        ai_level = 0:
            ai shoots in random direction
        ai_level = 1:
            ai shoots towards player
        '''

        if self.ai_level == 0:
             self.weapon.shoot([self.movement.enemy_pos[0] - 16, self.movement.enemy_pos[1]], math.radians(random.randrange(360)))
        if self.ai_level == 1:
            angle = math.atan2(self.player.player_pos[1] - self.movement.enemy_pos[1],
                               self.player.player_pos[0] - self.movement.enemy_pos[0])
            self.weapon.shoot([self.movement.enemy_pos[0] - 16, self.movement.enemy_pos[1]], angle) 

    def __dumb_moving_left_right_ai(self):
        '''AI moves left and right'''
        self.movement.moving = True
        if (self.movement.enemy_pos[0] == 0 and self.movement.move_dir == 0) or self.movement.map_.is_any_solid_block_left_from_entity(self.movement.enemy_pos):
              self.movement.move_dir = 1
        elif (self.movement.enemy_pos[0] == (self.movement.map_.map_size - 1) * 32 and self.movement.move_dir == 1) or self.movement.map_.is_any_solid_block_right_from_entity(self.movement.enemy_pos):
            self.movement.move_dir = 0

    def __full_dumb_movement_ai(self):
        '''AI moves left and right, but also jumps'''
        self.__dumb_moving_left_right_ai()

        if not self.movement.jumping:
            self.movement.jump_current_speed = self.movement.jump_max_speed
            self.movement.jumping = True
            self.movement.jump_dir = 0
    
    def __moving_to_player_ai(self):
        '''AI moves towards player'''
        self.movement.moving = True
        if abs(self.player.player_pos[0] - self.movement.enemy_pos[0]) <= 8:
            self.movement.moving = False
        elif self.player.player_pos[0] < self.movement.enemy_pos[0]:
            self.movement.move_dir = 0
        elif self.player.player_pos[0] > self.movement.enemy_pos[0]:
            self.movement.move_dir = 1
        
    def __full_movement_ai(self):
        '''AI moves and jumps towards player'''
        self.__moving_to_player_ai()

        if not self.movement.jumping:
            if self.player.player_pos[1] < self.movement.enemy_pos[1]:
                self.movement.jump_current_speed = self.movement.jump_max_speed
                self.movement.jumping = True
                self.movement.jump_dir = 0