import sys
import blocks
import weapon

class Map:
    '''Map class. Responsible for loading level from file, reading all the information
    about the map and parsing it into attributes.
    It also contains functions needed to check collision and visibilty of some objects'''

    def __init__(self, player):
        self.player = player
        self.map_size = 0
        self.bg_image_name = None
        self.ground_list = []
        self.enemy_list = []
        self.consumable_blocks = []
        self.text_color = []

    def load(self, path):
        '''Loads and parses map from file. Parses every line of map's file
        independently. First it reads first letter in line, which contains
        information about line type. It can mean it's line with map's info,
        block's info, etc. then it runs appropriate function to parse informations
        
        Arguments:
            path {string} -- path to file
        '''

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
                self.__read_map_info(obj)
            elif obj[0] == 'g':
                obj.pop(0)
                self.__read_obj_info(obj)
            elif obj[0] == 'e':
                obj.pop(0)
                self.__read_enemy_info(obj)
            elif obj[0] == 'h':
                obj.pop(0)
                self.__read_health_consumable_info(obj)
            elif obj[0] == 'w':
                obj.pop(0)
                self.__read_weapon_consumable_info(obj)
            elif obj[0] == 'k':
                obj.pop(0)
                self.__read_key_consumable_info(obj)
            elif obj[0] == 'f':
                obj.pop(0)
                self.__read_finish_consumable_info(obj)

    def __read_map_info(self, list):
        '''Reads map\'s info from map's line
        
        Arguments:
            list {list(string)} -- map's line splitted into strings
        '''

        self.bg_image_name = list[0]
        self.text_color = [int(list[1]), int(list[2]), int(list[3])]
        self.map_size = int(list[4])
        self.player.set_starting_hp(int(list[5]))
        self.player.keys_to_collect = int(list[6])

    def __read_obj_info(self, list):
        '''Reads object's info from map's line
        
        Arguments:
            list {list(string)} -- map's line splitted into strings
        '''

        for i in range(1, 5, 1):
            list[i] = int(list[i])
        self.ground_list.append(list)

    def __read_enemy_info(self, list):
        '''Reads enemy's info from map's line
        
        Arguments:
            list {list(string)} -- map's line splitted into strings
        '''

        for i in range(1, 17, 1):
            list[i] = int(list[i])
        list[13] = bool(list[13])
        self.enemy_list.append(list)

    def __read_health_consumable_info(self, list):
        '''Reads health consumable block info from map's line
        
        Arguments:
            list {list(string)} -- map's line splitted into strings
        '''
        
        for i in range(1, 4, 1):
            list[i] = int(list[i])
        self.consumable_blocks.append(blocks.HealthBlock([list[1], list[2]], list[0], list[3]))

    def __read_weapon_consumable_info(self, list):
        '''Reads weapon consumable block info from map's line
        
        Arguments:
            list {list(string)} -- map's line splitted into strings
        '''

        for i in range(1, 10, 1):
            list[i] = int(list[i])
        list[8] = bool(list[8])
        self.consumable_blocks.append(blocks.WeaponBlock([list[1], list[2]], list[0], 
                                      weapon.Weapon(list[3], list[4], list[5], list[6], list[7], list[8], list[9])))

    def __read_key_consumable_info(self, list):
        '''Reads key consumable block info from map's line
        
        Arguments:
            list {list(string)} -- map's line splitted into strings
        '''

        for i in range(1, 3, 1):
            list[i] = int(list[i])
        self.consumable_blocks.append(blocks.KeyBlock([list[1], list[2]], list[0]))

    def __read_finish_consumable_info(self, list):
        '''Reads finish consumable block info from map's line
        
        Arguments:
            list {list(string)} -- map's line splitted into strings
        '''

        for i in range(1, 3, 1):
            list[i] = int(list[i])
        self.consumable_blocks.append(blocks.FinishBlock([list[1], list[2]], list[0]))

    def get_objects_in_sight(self):
        '''Returns list of objects beign in player's sight
        
        Returns:
            list() -- list of objects (non-consumable blocks) in player's sight
        '''

        player_block = self.player.player_pos[0] // 32
        max_render_length = abs(320 - self.player.player_pos_on_screen[0]) // 32
        return [ground for ground in self.ground_list if abs(player_block - ground[1]) < max_render_length + 11 and ground[4] == 1]

    def get_consumable_blocks_in_sight(self):
        '''Returns list of consumable blocks beign in player's sight
        
        Returns:
            list(blocks.ConsumableBlock) -- list of consumable blocks in player's
            sight
        '''

        player_block = self.player.player_pos[0] // 32
        max_render_length = abs(320 - self.player.player_pos_on_screen[0]) // 32
        return [block for block in self.consumable_blocks if abs(player_block - block.block_pos[0]) < max_render_length + 11]

    def is_any_solid_block_left_from_entity(self, entity_pos):
        '''Returns True if there is any solid block left from entity
        
        Arguments:
            entity_pos {list(int)} -- Entity's position
        
        Returns:
            bool
        '''

        entity_block_x = entity_pos[0] // 32
        entity_block_y = entity_pos[1] // 32
        blocks = [ground for ground in self.ground_list if entity_block_x -
                  ground[1] == 0 and entity_block_y - ground[2] == 0 and ground[3] == 1]
        if blocks:
            return True
        return False

    def is_any_solid_block_right_from_entity(self, entity_pos):
        '''Returns True if there is any solid block right from entity
        
        Arguments:
            entity_pos {list(int)} -- Entity's position
        
        Returns:
            bool
        '''

        entity_block_x = entity_pos[0] // 32
        entity_block_y = entity_pos[1] // 32
        blocks = [ground for ground in self.ground_list if ground[1] -
                  entity_block_x == 1 and ground[2] - entity_block_y == 0
                  and ground[3] == 1]
        if blocks:
            return True
        return False

    def is_any_solid_block_above_entity(self, entity_pos):
        '''Returns True if there is any solid block above entity
        
        Arguments:
            entity_pos {list(int)} -- Entity's position
        
        Returns:
            bool
        '''

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
        '''Returns True if there is any solid block above entity
        
        Arguments:
            entity_pos {list(int)} -- Entity's position
        
        Returns:
            bool
        '''

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
        '''Returns effect of block below player or None if there's no
        fx block below player
        
        Returns:
            string -- effect's name
        '''

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
        '''Returns True if bullet collides with any visible object, otherwise
        return False
        
        Arguments:
            bullet_pos {list(int)} -- bullet's position
        
        Returns:
            bool
        '''

        objects = self.get_objects_in_sight()
        for object_ in objects:
            if (object_[1]*32 <= bullet_pos[0] <= object_[1]*32 + 32) and (object_[2]*32 <= bullet_pos[1] <= object_[2]*32 + 32):
               return True
        
        return False
