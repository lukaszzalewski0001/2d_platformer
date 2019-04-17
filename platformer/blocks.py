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

import abc

class ConsumableBlock:
    '''Base class for consumable blocks. Consumable blocks are blocks
    that player can step onto, then they disappear giving player some benefits'''

    def __init__(self, block_pos, image_name):
        self.block_pos = block_pos
        self.image_name = image_name

    @abc.abstractmethod
    def on_pick_up(self, player):
        '''Abstract method defining what happens when player steps on block'''
        pass

    def is_player_on_block(self, player):
        '''Returns True if player is on block, otherwise returns False
        
        Arguments:
            player {Player.player.Player}
        
        Returns:
            bool
        '''

        if (player.player_pos[0] + 16) // 32 == self.block_pos[0] and (player.player_pos[1] + 16) // 32 == self.block_pos[1]:
            if self.on_pick_up(player):
                return True

        return False


class HealthBlock(ConsumableBlock):
    '''Health consumable block. Returns some health to player'''
    
    def __init__(self, block_pos, image_name, hp):
        super().__init__(block_pos, image_name)
        self.hp = hp

    def on_pick_up(self, player):
        '''Defines what happens when player steps on block'''
        return player.add_hp(self.hp)


class WeaponBlock(ConsumableBlock): 
    '''Weapon consumable block. On step adds weapon to player\'s inventory'''

    def __init__(self, block_pos, image_name, weapon):
        super().__init__(block_pos, image_name)
        self.weapon = weapon

    def on_pick_up(self, player):
        '''Defines what happens when player steps on block'''
        player.add_weapon(self.weapon)

        return True


class KeyBlock(ConsumableBlock):
    '''Key consumable block. Keys are needed to finish level'''

    def __init__(self, block_pos, image_name):
        super().__init__(block_pos, image_name)

    def on_pick_up(self, player):
        '''Defines what happens when player steps on block'''
        player.keys += 1

        return True


class FinishBlock(ConsumableBlock):
    '''Finish consumable block. On step finishes level, if player has 
    collected all keys'''

    def __init__(self, block_pos, image_name):
        super().__init__(block_pos, image_name)

    def on_pick_up(self, player):
        '''Defines what happens when player steps on block'''
        if player.keys >= player.keys_to_collect:
            player.finished = 2
            return True

        return False