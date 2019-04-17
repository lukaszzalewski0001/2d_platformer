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
import sys
import math

class EventHandler:
    '''Class containing all kind of events handling'''

    def __init__(self, player, enemies, map_, graphics, movement):
        self.player = player
        self.enemies = enemies
        self.map_ = map_
        self.graphics = graphics
        self.movement = movement

    def event_loop(self):
        '''Main event loop. Works till player\'s object attribute finished is 0'''
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
        '''Handles all input'''
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
        '''Handles player's movement'''
        self.movement.move_clock.tick()
        self.movement.move_clock_combined_time += self.movement.move_clock.get_time()
        if self.movement.move_clock_combined_time > self.movement.move_tick_time:
            self.movement.move_clock_combined_time = 0
            self.movement.move()

    def handle_jumping(self):
        '''Handle's player jumping and falling down'''
        self.movement.jump_clock.tick()
        self.movement.jump_clock_combined_time += self.movement.jump_clock.get_time()
        if self.movement.jump_clock_combined_time > self.movement.jump_tick_time:
            self.movement.jump_clock_combined_time = 0
            self.movement.jump()

    def handle_shooting(self):
        '''Handles player's shooting'''
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
        '''Handle player's weapon's bullet collision'''
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
        '''Checks if enemies are in sight of the player'''
        for enemy in self.enemies:
            enemy.is_in_bigger_sight(self.player.player_pos)

    def handle_enemy_ai(self):
        '''Handles all enemies ai'''
        for enemy in [en for en in self.enemies if en.is_in_bigger_sight_]:
            enemy.ai.tick()

    def handle_enemy_movement(self):
        '''Handles all enemies movement'''
        for enemy in [en for en in self.enemies if en.is_in_bigger_sight_]:
            enemy.movement.move_clock.tick()
            enemy.movement.move_clock_combined_time += enemy.movement.move_clock.get_time()
            if enemy.movement.move_clock_combined_time > enemy.movement.move_tick_time:
                enemy.movement.move_clock_combined_time = 0
                enemy.movement.move()

    def handle_enemy_jumping(self):
        '''Handles all enemies jumping'''
        for enemy in [en for en in self.enemies if en.is_in_bigger_sight_]:
            enemy.movement.jump_clock.tick()
            enemy.movement.jump_clock_combined_time += enemy.movement.jump_clock.get_time()
            if enemy.movement.jump_clock_combined_time > enemy.movement.jump_tick_time:
                enemy.movement.jump_clock_combined_time = 0
                enemy.movement.jump()

    def handle_enemy_shooting(self):
        '''Handles all enemeies shooting'''
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
        '''Handles all enemies' bullets collision'''
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
        '''Checks if player stepped on any of consumable blocks'''
        for block in self.map_.get_consumable_blocks_in_sight():
            if block.is_player_on_block(self.player):
                self.map_.consumable_blocks.remove(block)