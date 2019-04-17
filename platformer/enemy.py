class Enemy:
    '''Create enemy object'''

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
        '''Sets ai and gives ai weapon'''

        self.ai = ai
        self.ai.weapon = self.weapon

    def is_bullet_on_enemy(self, bullet_pos):
        '''Returns True if bullet hit enemy, otherwise returns False
        
        Arguments:
            bullet_pos {list(int, int)} -- bullet's position
        
        Returns:
            bool
        '''

        if self.pos[0] <= bullet_pos[0] <= self.pos[0] + 32 and self.pos[1] <= bullet_pos[1] <= self.pos[1] + 32:
            return True
        
        return False

    def hit(self, damage):
        '''Substracts damage from enemy's health. Returns True if enemy's hp is lesser than 0,
        otherwise returns False
        
        Arguments:
            damage {int} -- damage
        
        Returns:
            bool -- True if enemy's hp is lesser than 0, otherwise False
        '''

        self.hp -= damage
        if self.hp <= 0:
            return True

        return False

    def is_in_bigger_sight(self, player_pos):
        '''Sets attribute is_in_bigger_sight_ to True if enemy is in player's sight
        position, otherwise sets it to False
        
        Arguments:
            player_pos {list(int, int)} -- player's positon
        '''

        if abs(self.pos[0] - player_pos[0]) <= 960:
            self.is_in_bigger_sight_ = True
        else:
            self.is_in_bigger_sight_ = False