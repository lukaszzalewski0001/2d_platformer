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
import os

class Graphics:
    '''Class responsible for rendering and loading images'''

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
        '''Loads all images to container. All files that ends with \'.png\' are loaded
        
        Arguments:
            path {string} -- path to directory
        '''

        files = os.listdir(path)
        files = [f for f in files if f.find('.png') != -1]
        for file_ in files:
            self.images[file_.replace('.png', '')] = pygame.image.load(
                path + file_)

    def render(self):
        '''Main render function'''
        self.display.fill((0, 0, 0))
        
        self.__render_background()
        self.__render_player()
        self.__render_blocks()
        self.__render_consumable_blocks()
        self.__render_bullets()
        self.__render_enemies_in_sight()
        self.__render_enemy_bullets()
        self.__render_texts()

        pygame.display.flip()

    def __render_background(self):
        '''Renders background'''
        self.display.blit(self.images[self.map_.bg_image_name], pygame.Rect(0, 0, 640, 480))

    def __render_player(self):
        '''Renders player'''
        self.display.blit(self.images['player'], pygame.Rect(
            self.player.player_pos_on_screen[0], self.player.player_pos_on_screen[1],
            self.player.player_pos_on_screen[0] + 32, self.player.player_pos_on_screen[1] + 32))

    def __render_enemies_in_sight(self):
        '''Renders all enemies in player's sight'''
        player_block = self.player.player_pos[0] // 32
        max_render_length = abs(320 - self.player.player_pos_on_screen[0]) // 32
        enemies = [enemy for enemy in self.enemies if abs(player_block - enemy.pos[0]//32) < max_render_length + 12]

        diff = self.player.player_pos[0] - self.player.player_pos_on_screen[0]
        for enemy in enemies:
            self.display.blit(self.images[enemy.image_name], pygame.Rect(
                enemy.pos[0] - diff, enemy.pos[1],
                enemy.pos[0] - diff + 32, enemy.pos[1] + 32
            ))

    def __render_blocks(self):
        '''Renders all non-consumable blocks in player's sight'''
        for obj in self.map_.get_objects_in_sight():
            diff = self.player.player_pos[0] - self.player.player_pos_on_screen[0]
            self.display.blit(self.images[obj[0]], pygame.Rect(
                obj[1] * 32 - diff, obj[2] * 32, obj[1] * 32 + 32 - diff, obj[2] * 32 + 32))

    def __render_consumable_blocks(self):
        '''Renders all consumable blocks in player's sight'''
        for obj in self.map_.get_consumable_blocks_in_sight():
            diff = self.player.player_pos[0] - self.player.player_pos_on_screen[0]
            self.display.blit(self.images[obj.image_name], pygame.Rect(
                obj.block_pos[0] * 32 - diff, obj.block_pos[1] * 32, obj.block_pos[0] * 32 + 32 - diff, obj.block_pos[1] * 32 + 32))

    def __render_bullets(self):
        '''Renders all player's bullets'''
        if self.player.weapon:
            diff = self.player.player_pos[0] - self.player.player_pos_on_screen[0]
            for bullet in self.player.weapon.bullets:
                pygame.draw.line(self.display, (255, 255, 255), [bullet.pos[0]-diff, bullet.pos[1] - 2],
                                                                [bullet.pos[0]-diff, bullet.pos[1] + 2], 4)

    def __render_enemy_bullets(self):
        '''Renders all enemy's bullets'''
        player_block = self.player.player_pos[0] // 32
        max_render_length = abs(320 - self.player.player_pos_on_screen[0]) // 32
        enemies = [enemy for enemy in self.enemies if abs(player_block - enemy.pos[0]//32) < max_render_length + 12]

        diff = self.player.player_pos[0] - self.player.player_pos_on_screen[0]
        for enemy in enemies:
            for bullet in enemy.weapon.bullets:
                pygame.draw.line(self.display, (255, 0, 0), [bullet.pos[0]-diff, bullet.pos[1] - 2],
                                [bullet.pos[0]-diff, bullet.pos[1] + 2], 4)

    def __render_texts(self):
        '''Renders all texts'''
        text_hp = self.font.render('Health: ' + str(self.player.hp) + ' / ' + str(self.player.max_hp), True, self.map_.text_color)
        text_weapon = self.font.render(f'Weapon: {self.player.current_weapon + 1} / {len(self.player.weapons)}', True, self.map_.text_color)
        text_keys = self.font.render('Keys: ' + str(self.player.keys) + ' / ' + str(self.player.keys_to_collect), True, self.map_.text_color)
        text_maps = self.font.render(f'Map: {str(self.current_map + 1)} / {str(self.maps)}', True, self.map_.text_color)

        self.display.blit(text_hp, (0, 0))
        self.display.blit(text_weapon, (0, 20))
        self.display.blit(text_keys, (640 - text_keys.get_rect().width, 0))
        self.display.blit(text_maps, (640 - text_maps.get_rect().width, 20))
        