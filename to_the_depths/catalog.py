import random
import discord
import logging
import asyncio 
import copy
import math
import ttd_tools
from ttd_tools import print

'''
Functions that propagate Entity.check_current_hp()'s boolean: 
Entity.take_damage() 
Entity.check_pressure_damage() 
Player.take_oxygen_damage() 
Player.check_current_oxygen() 

''' 

''' 

CURRENTLY WORKING ON: 
Deconstruct storage system
Stuff that happens before the player can act should be separated from stuff that happens upon their game turn starting
Embeds for everything

''' 

thumbs_up_emoji = chr(0x1F44D) 
thumbs_down_emoji = chr(0x1F44E) 
h_emoji = chr(0x1F1ED) 
t_emoji = chr(0x1F1F9) 
bullet_point = chr(9702) 

#useful functions

#top is the list to subtract from, bottom is the list to subtract from that
def subtract_lists(top, bottom): 
  difference = top.copy() 

  for item in bottom: 
    difference.remove(item) 
  
  return difference

def make_list(items, numbered=False): 
  to_join = list(items) 

  for index in range(len(to_join)): 
    if numbered: 
      point = '{}.'.format(index + 1) 
    else: 
      point = bullet_point
    
    to_join[index] = '{} {}'.format(point, to_join[index])  
  
  joined = '\n'.join(to_join) 

  return joined

def search(to_search, name): 
  for thing in to_search: 
    print('thing.name = {}'.format(thing.name.lower())) 
    print('name = {}'.format(name.lower())) 

    if thing.name.lower() == name.lower(): 
      return thing
  
  return None

#for all the random needs
#Die was honestly the best name i could think of
class Die(): 
  #this returns the emoji, followed by the name
  def flip_coin(self): 
    flip = random.random() 

    if flip < 0.5: 
      return h_emoji, 'heads' 
    else: 
      return t_emoji, 'tails' 
  
  async def call_and_flip(self, client, channel, member_id): 
    target_member = self.channel.guild.get_member(member_id) 

    coin_prompt = await self.channel.send(content="{}, heads or tails? React with {} for heads or {} for tails. This defaults to heads if you don't react within 10 seconds".format(target_member.mention, h_emoji, t_emoji)) 
    
    reaction_emoji = await self.client.prompt_for_reaction(coin_prompt, member_id, emojis=(h_emoji, t_emoji), timeout=10, default=h_emoji) 

    side_emoji, side_name = self.flip_coin() 

    await self.channel.send(content="It's {}! ".format(side_name)) 

    return reaction_emoji == side_emoji
  
  def roll_die(self): 
    return random.randint(1, 6) 
  
  def select_creature(self, level): 
    #makes sure that there are actually creatures in that level
    if len(levels[level]['creatures']) > 0: 
      level_creatures = levels[level]['creatures'] 
      creatures = sorted(level_creatures) 

      #calculates total amount of creatures here
      total_amount = 0

      for creature in creatures: 
        total_amount += level_creatures[creature] 
      
      #picks a random creature here
      to_pick = random.randint(1, total_amount) 
      running_sum = 0

      for creature in creatures: 
        running_sum += level_creatures[creature] 

        if running_sum >= to_pick: 
          return creature(current_level=level)  

die = Die() 

class Events(ttd_tools.Game_Object): 
  async def on_game_turn_start(self): 
    pass
  
  async def on_game_turn_end(self): 
    pass
  
  async def on_battle_start(self): 
    pass
  
  async def on_battle_end(self): 
    pass
  
  async def on_battle_round_start(self): 
    pass
  
  async def on_battle_round_end(self): 
    pass
  
  async def on_first_hit(self): 
    pass
  
  async def on_win_coinflip(self): 
    pass

class Item(Events): 
  name = '' 
  description = 'None'  
  obtainments = ('Not obtainable',) 
  effects = ('No effects',) 
  usages = ('Not usable',) 
  specials = ('None',) 
  recipe = None
  #can_stack is None if the item does not give bonuses anyways
  can_stack = None
  is_usable = False

  def __init__(self, client, channel, owner): 
    self.owner = owner
    self.usable = self.is_usable

    Events.__init__(self, client, channel) 
  
  def modify_deconstructed(self, deconstructed): 
    del deconstructed['owner'] 

    Events.modify_deconstructed(self, deconstructed) 
  
  @classmethod
  def has_in_recipe(self, item_class): 
    if self.recipe is not None: 
      recipe_items = tuple((item_class for item_class, amount in self.recipe)) 

      return item_class in recipe_items
    else: 
      return False
  
  @classmethod
  def crafts(self): 
    crafts_names = tuple((item_class.name for item_class in items if item_class.has_in_recipe(self))) 

    if len(crafts_names) > 0: 
      return crafts_names
    else: 
      return ('Nothing',) 
  
  def on_shutdown(self, amount): 
    pass
  
  async def on_turn_on(self, amount): 
    pass
  
  @classmethod
  def class_embed(self): 
    embed = discord.Embed(title=self.name, type='rich', description=self.description) 

    embed.add_field(name='Ways to obtain', value=make_list(self.obtainments)) 
    embed.add_field(name='Effects when received', value=make_list(self.effects)) 
    embed.add_field(name='Effects on use', value=make_list(self.usages)) 
    embed.add_field(name='Used to craft', value=make_list(self.crafts())) 
    embed.add_field(name='Special', value=make_list(self.specials)) 

    recipe_list = tuple(('{} {}'.format(amount, item_class.name) for item_class, amount in self.recipe)) if self.recipe is not None else ('Not craftable',) 

    embed.add_field(name='Recipe', value=make_list(recipe_list)) 
    embed.add_field(name='Stacks with itself', value=self.can_stack) 

    return embed
  
  def object_embed(self): 
    embed = self.class_embed() 

    embed.add_field(name='Owner', value=self.owner.name) 
    embed.add_field(name='Currently usable', value=self.usable) 

    return embed
  
  async def on_game_turn_start(self, amount): 
    pass
  
  async def on_game_turn_end(self, amount): 
    pass
  
  async def on_battle_start(self, amount): 
    pass
  
  async def on_battle_end(self, amount): 
    pass
  
  async def on_battle_round_start(self, amount): 
    pass
  
  async def on_battle_round_end(self, amount): 
    pass
  
  async def on_first_hit(self, amount): 
    pass
  
  async def on_win_coinflip(self, amount): 
    pass
  
  async def apply_bonuses(self, amount): 
    pass
  
  #this is like the inverse of apply_bonuses() 
  #returns whether the target died
  async def remove_bonuses(self, amount): 
    return False
  
  '''
  async def on_craft(self, target, amount): 
    final_recipe = [[recipe_item, recipe_amount * amount] for recipe_item, recipe_amount in self.recipe] 

    lacking_items = target.lacks_items(final_recipe) 

    if len(lacking_items) > 0: 
      for item, number in lacking_items: 
        await self.channel.send(content='{} lacks {} {}(s) to craft {} {}(s) '.format(target.name, number, item.name, amount, self.name)) 
    else: 
      target.can_move = False

      await target.lose_items(final_recipe) 
      await target.receive_items([self.__class__, amount]) 
  ''' 

  async def on_use(self, amount): 
    pass
  
  async def attempt_use(self, amount): 
    pass

class Meat(Item): 
  hp_regen = 10

  name = 'Meat' 
  description = 'I seafood' 
  obtainments = ('Dropped from certain creatures upon death', 'Attacks from Toxic Waste can be converted to Meat via the Bio-Wheel') 
  usages = ('Regens {} HP per piece to the player/pet it was used on'.format(hp_regen), 'Using it on a pet with full HP will instead regen its shield, for {} shield per piece'.format(hp_regen)) 
  usable = True
  
  async def on_use(self, target, amount): 
    final_hp_regen = self.hp_regen * amount

    target.current_hp += final_hp_regen
    await self.channel.send(content="{}'s current HP increased by {}! ".format(target.name, final_hp_regen)) 
    await target.check_current_hp() 
  
  async def attempt_use(self, target, amount): 
    if target.current_hp < target.max_hp: 
      self.on_use(target, amount) 
    else: 
      await self.channel.send(content="{} is already at full HP. ".format(target.name)) 

class Suit(Item): 
  hp_bonus = 50
  oxygen_bonus = 1
  access_levels_bonus = [2] 

  name = 'Suit' 
  description = 'Shell we try it on? ' 
  obtainments = ('Dropped by Turtles upon being killed',) 
  specials = ('Protects the wearer from pressure damage in the Middle', "Increases the wearer's base, current, and max HP by {}".format(hp_bonus), "Increases the wearer's current and max oxygen by {}".format(oxygen_bonus)) 
  can_stack = False
  usable = False
  
  def on_shutdown(self): 
    self.owner.base_hp -= self.hp_bonus
    self.owner.current_hp -= self.hp_bonus
    self.owner.max_hp -= self.hp_bonus
    self.owner.current_oxygen -= self.oxygen_bonus
    self.owner.max_oxygen -= self.oxygen_bonus
    self.owner.access_levels = subtract_lists(self.owner.access_levels, self.access_levels_bonus) 
  
  async def on_turn_on(self): 
    self.owner.base_hp += self.hp_bonus
    self.owner.current_hp += self.hp_bonus
    self.owner.max_hp += self.hp_bonus
    self.owner.max_oxygen += self.oxygen_bonus
    self.owner.access_levels.extend(self.access_levels_bonus) 
  
  async def apply_bonuses(self, amount): 
    self.owner.access_levels.extend(self.access_levels_bonus) 

    self.owner.base_hp += self.hp_bonus
    await self.channel.send(content="{}'s base HP increased by {}! ".format(self.owner.name, self.hp_bonus)) 
    self.owner.current_hp += self.hp_bonus
    await self.channel.send(content="{}'s current HP increased by {}! ".format(self.owner, self.hp_bonus)) 
    self.owner.max_hp += self.hp_bonus
    await self.channel.send(content="{}'s max HP increased by {}! ".format(self.owner.name, self.hp_bonus)) 
    #await self.owner.check_current_hp() 

    self.owner.current_oxygen += self.oxygen_bonus
    await self.channel.send(content="{}'s current oxygen increased by {}! ".format(self.owner.name, self.oxygen_bonus)) 
    self.owner.max_oxygen += self.oxygen_bonus
    await self.channel.send(content="{}'s max oxygen increased by {}! ".format(self.owner.name, self.oxygen_bonus)) 
    
    owner_died = await self.owner.check_current_hp() 

    return owner_died
  
  async def remove_bonuses(self, amount): 
    self.owner.access_levels = subtract_lists(self.owner.access_levels, self.access_levels_bonus)  
    
    self.owner.base_hp -= self.hp_bonus
    await self.channel.send(content="{}'s base HP decreased by {}! ".format(self.owner.name, self.hp_bonus)) 
    self.owner.current_hp -= self.hp_bonus
    await self.channel.send(content="{}'s current HP decreased by {}! ".format(self.owner.name, self.hp_bonus)) 
    self.owner.max_hp -= self.hp_bonus
    await self.channel.send(content="{}'s max HP decreased by {}! ".format(self.owner.name, self.hp_bonus)) 
    #owner_died = await self.owner.check_current_hp() 

    self.owner.current_oxygen -= self.oxygen_bonus
    await self.channel.send(content="{}'s current oxygen decreased by {}! ".format(self.owner.name, self.oxygen_bonus)) 
    self.owner.max_oxygen -= self.oxygen_bonus
    await self.channel.send(content="{}'s max oxygen decreased by {}! ".format(self.owner.name, self.oxygen_bonus)) 

    owner_died = await self.owner.check_current_hp() 
    
    return owner_died

class Coral(Item): 
  name = 'Coral' 
  description = 'Great building material for some reason' 
  obtainments = ('Obtained from farming in the Surface or Middle',) 

class Scale(Item): 
  name = 'Scale' 
  description = 'Extremely durable and hard to deform' 
  obtainments = ('Dropped by Saltwater Crocs upon death',) 

class Sky_Blade(Item): 
  name = 'Sky Blade' 
  description = "Really light but also quite sharp and durable" 
  obtainments = ('Dropped by Ariel Leviathans upon death',) 

class Hatchet_Fish_Corpse(Item): 
  name = 'Hatchet Fish Corpse' 
  description = 'Very hard skeleton' 
  obtainments = ('Dropped by Hatchet Fish upon death',) 

class Fishing_Net(Item): 
  name = 'Fishing Net' 
  description = "Can catch basically anything if you're skilled enough" 
  obtainments = ('Fisherman starts out with one',) 
  specials = ('Allows you to catch creatures and turn them into pets', 'Required to revive your pet') 

items = (Meat, Suit, Coral, Scale, Sky_Blade, Hatchet_Fish_Corpse, Fishing_Net) 

class Entity(Events): 
  name = '' 
  description = 'None' 
  specials = ('None',) 
  starting_min_hp = 0
  starting_hp = 0
  starting_shield = 0
  starting_attack = 0
  starting_enemy_attack_multiplier = 1
  starting_miss = (1,) 
  starting_crit = (6,) 
  starting_enemy_miss = () 
  starting_enemy_crit = () 
  starting_access_levels = () 
  starting_penetrates = () 
  starting_bleeds = () 

  def __init__(self, client, channel, current_level=None): 
    self.min_hp = self.starting_min_hp
    self.base_hp = self.current_hp = self.max_hp = self.starting_hp
    '''
    self.current_hp = base_hp
    self.max_hp = base_hp
    ''' 
    self.base_shield = self.current_shield = self.max_shield = self.starting_shield
    '''
    self.current_shield = base_shield
    self.max_shield = base_shield
    ''' 
    self.base_attack = self.current_attack = self.starting_attack
    #self.current_attack = base_attack
    self.enemy_attack_multiplier = self.starting_enemy_attack_multiplier
    self.miss = list(self.starting_miss) 
    self.crit = list(self.starting_crit) 
    self.enemy_miss = list(self.starting_enemy_miss) 
    self.enemy_crit = list(self.starting_enemy_crit) 
    #if your level is not in this, you can still go there, but you will take pressure damage. 
    self.access_levels = list(self.starting_access_levels) 
    #your attack bypasses these
    self.penetrates = list(self.starting_penetrates) 
    #your attack "bleeds" these (overkill is not wasted but rather is dealt to another entity) 
    self.bleeds = list(self.starting_bleeds) 
    #self.death_restore = copy.deepcopy(self) 
    self.current_level = current_level

    Events.__init__(self, client, channel) 
  
  def is_a(self, class_object): 
    return issubclass(self.__class__, class_object) 
  
  def final_miss(self, enemy): 
    total_miss = tuple(self.miss) + tuple(enemy.enemy_miss) 
    final_miss = tuple(chance for chance in range(1, 7) if chance in total_miss and -chance not in total_miss) 
    
    return final_miss
  
  def final_crit(self, enemy): 
    total_crit = tuple(self.crit) + tuple(enemy.enemy_crit) 
    final_crit = tuple(chance for chance in range(1, 7) if chance in total_crit and -chance not in total_crit) 

    return final_crit
  
  def on_shutdown(self): 
    self.min_hp -= self.starting_min_hp
    self.base_hp -= self.starting_hp
    self.current_hp -= self.starting_hp
    self.max_hp -= self.starting_hp
    self.base_shield -= self.starting_shield
    self.current_shield -= self.starting_shield
    self.max_shield -= self.starting_shield
    self.base_attack -= self.starting_attack
    self.current_attack = self.current_attack
    self.enemy_attack_multiplier /= self.starting_enemy_attack_multiplier
    self.miss = subtract_lists(self.miss, self.starting_miss) 
    self.crit = subtract_lists(self.crit, self.starting_crit) 
    self.enemy_miss = subtract_lists(self.enemy_miss, self.starting_enemy_miss) 
    self.enemy_crit = subtract_lists(self.enemy_crit, self.starting_enemy_crit) 
    self.access_levels = subtract_lists(self.access_levels, self.starting_access_levels) 
    self.penetrates = subtract_lists(self.penetrates, self.starting_penetrates) 
    self.bleeds = subtract_lists(self.bleeds, self.starting_bleeds) 
  
  async def on_turn_on(self): 
    self.min_hp += self.starting_min_hp
    self.base_hp += self.starting_hp
    self.current_hp += self.starting_hp
    self.max_hp += self.starting_hp
    self.base_shield += self.starting_shield
    self.current_shield += self.starting_shield
    self.max_shield += self.starting_shield
    self.base_attack += self.starting_attack
    self.current_attack += self.current_attack
    self.enemy_attack_multiplier *= self.starting_enemy_attack_multiplier
    self.miss.extend(self.starting_miss) 
    self.crit.extend(self.starting_crit) 
    self.enemy_miss.extend(self.starting_enemy_miss) 
    self.enemy_crit.extend(self.starting_enemy_crit) 
    self.access_levels.extend(self.starting_access_levels) 
    self.penetrates.extend(self.starting_penetrates) 
    self.bleeds.extend(self.starting_bleeds) 

    await self.check_current_hp() 
  
  @classmethod
  def class_embed(self): 
    embed = discord.Embed(name=self.name, type='rich', description=self.description) 

    embed.add_field(name='HP', value=self.starting_hp) 
  
  #inflicter is None unless the cause of the change in HP is being attacked, in which it's either a Player object or an Enemy object. 
  #this is so that if it dies due to attack credit can be given to the attacker
  #note that this function usually should not be called directly, rather it should be indirectly called through other functions such as current_hp_decrease and current_hp_increase
  #this returns 1 boolean, which indicates whether the entity has died, which CAN matter. 
  async def check_current_hp(self): 
    #hp must remain int
    self.current_hp = int(self.current_hp) 

    #current hp exceeds max hp
    self.current_hp = min(self.current_hp, self.max_hp) 
    self.current_hp = max(self.current_hp, self.min_hp) 
    #self died
    #there is actually a reason this is not elif, just in case somehow your max_hp is 0
    if self.current_hp <= 0: 
      #implement on_death() soon
      await self.on_death() 

      return True
    
    return False
  
  #the following two are just for being able to output a message in addition to changing HP. 
  #commented out for the moment while i think about how to do hp changes
  ''' 
  async def current_hp_decrease(self, decrease_by, inflicter=None): 
    await self.channel.send(content='{} lost {} HP! '.format(self.name, decrease_by)) 
    await self.check_current_hp(-decrease_by, inflicter=inflicter) 
  
  async def current_hp_increase(self, increase_by): 
    await self.channel.send(content='{} gained {} HP! '.format(self.name, increase_by)) 
    await self.check_current_hp(increase_by) 
  ''' 
  
  async def check_current_shield(self): 
    #current_shield exceeds max_shield
    self.current_shield = min(self.current_shield, self.max_shield) 
    self.current_shield = max(self.current_shield, 0) 
  
  #needs client passed in
  
  async def calculate_shield_bleed(self, inflicter, penetrates, bleeds): 
    bleed_damage = -self.current_shield

    await self.channel.send(content="{}'s shield bleeds onto HP! ".format(self.name)) 
    await self.take_damage(bleed_damage, inflicter=inflicter, penetrates=penetrates, bleeds=bleeds) 

  #intended to be overriden in each of the child classes Player, Pet, and Sub (Creature and Blubber_Base do not bleed and therefore will not override this method) 
  async def calculate_hp_bleed(self, inflicter, penetrates, bleeds): 
    pass
  
  async def take_damage(self, damage, inflicter=None, penetrates=(), bleeds=()): 
    self_died = False

    #no point doing any of this if damage is 0
    if damage != 0: 
      #if self still has shield, and the attack type does not penetrate shield, the attack strikes their shield
      if self.current_shield > 0 and 'shield' not in penetrates: 
        self.current_shield -= damage
        await self.channel.send(content="{}'s shield absorbed {} damage! ".format(self.name, damage)) 
        
        #calculate shield bleed here
        if self.current_shield < 0 and 'shield' in bleeds: 
          await self.calculate_shield_bleed(inflicter, penetrates, bleeds) 
        
        await self.check_current_shield() 
      #otherwise, they lose hp instead
      else: 
        #Pet and Sub classes are not yet defined, define them
        self.current_hp -= damage
        await self.channel.send(content='{} took {} damage! '.format(self.name, damage)) 
        
        #calculate bleed damage here. This is not finished yet
        if self.current_hp < self.min_hp: 
          self.calculate_hp_bleed(inflicter, penetrates, bleeds) 
        
        '''
        if self.current_hp < self.min_hp: 
          bleed_damage = self.min_hp - self.current_hp
          if self.is_a(Pet) and 'pet' in bleeds: 
            if self.owner.sub is not None and self.owner.sub.hp > 0: 
              self.owner.sub.take_damage(bleed_damage, inflicter=inflicter, penetrates=penetrates, bleeds=bleeds) 
            else: 
              self.owner.take_damage(bleed_damage, inflicter=inflicter, penetrates=penetrates, bleeds=bleeds) 
          elif self.is_a(Sub) and 'sub' in bleeds: 
            self.owner.take_damage(bleed_damage, inflicter=inflicter, penetrates=penetrates, bleeds=bleeds) 
        ''' 
      
        self_died = await self.check_current_hp() 
      
      if not(self_died): 
        await self.channel.send(content='{} has {}/{} HP remaining'.format(self.name, self.current_hp, self.max_hp)) 
        await self.channel.send(content='{} has {}/{} shield remaining'.format(self.name, self.current_shield, self.max_shield)) 
    
    return self_died
  
  async def check_pressure_damage(self): 
    self_died = False
    smallest_distance = math.inf

    for level in self.access_levels: 
      distance = abs(self.current_level - level) 

      smallest_distance = min(smallest_distance, distance) 
    
    if smallest_distance > 0: 
      damage = smallest_distance * 20

      await self.channel.send(content='{} takes pressure damage! '.format(self.name)) 
      self_died = await self.take_damage(damage, penetrates=['shield']) 
    
    return self_died
  
  async def check_pressure(self): 
    self_died = False

    if self.current_level not in self.access_levels: 
      self_died = await self.take_pressure_damage() 
    
    return self_died
  
  async def deal_damage(self, target, damage, penetrates=(), bleeds=()): 
    actual_damage = damage * target.enemy_attack_multiplier

    return target.take_damage(actual_damage, inflicter=self, penetrates=penetrates, bleeds=bleeds) 
  
  async def on_miss(self, target): 
    if target.is_a(Player) and 'blubber base' not in self.penetrates and target.blubber_base is not None and target.blubber_base.hp > 0: 
      damage = self.current_attack * target.blubber_base.enemy_attack_multiplier

      await self.channel.send(content="{} missed and hit {}'s Blubber Base instead! ".format(self.name, target.name)) 
      await target.blubber_base.take_damage(damage, inflicter=self, penetrates=self.penetrates, bleeds=self.bleeds) 
    else: 
      await self.channel.send(content='{} missed! '.format(self.name)) 
  
  async def on_regular_hit(self, target): 
    damage = self.current_attack * target.enemy_attack_multiplier

    await self.channel.send(content='{} got a regular hit! '.format(self.name)) 
    target_died = await target.take_damage(damage, inflicter=self, penetrates=self.penetrates, bleeds=self.bleeds) 

    return target_died
  
  async def on_crit(self, target): 
    damage = self.current_attack * 2 * target.enemy_attack_multiplier

    await self.channel.send(content='{} got a critical hit! '.format(self.name)) 
    target_died = await target.take_damage(damage, inflicter=self, penetrates=self.penetrates, bleeds=self.bleeds) 

    return target_died
  
  async def switch_hit(self, target): 
    target_died = False
    miss = self.final_miss(target) 
    crit = self.final_crit(target) 
    #here is the attack roll (representing a die roll) 
    attack_roll = die.roll_die() 
      
    await self.channel.send(content='{} rolled a {}! '.format(self.name, attack_roll)) 
    if attack_roll in miss: 
      await self.on_miss(target) 
    elif attack_roll in crit: 
      target_died = await self.on_crit(target) 
    else: 
      target_died = await self.on_regular_hit(target) 
    
    return target_died
  
  #receiver is an object representing the receiver of the items, items is a dict of items to donate, with key-value pairs of item (an Item object): amount
  #i am yet to find out whether custom objects can be dict keys. If there is a bug with items i should look HERE first! 
  #REWORK THIS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
  
  async def attack(self, defender): 
    if defender.is_a(Player): 
      #if defender is a Player, has a living pet, and the entity does not ignore the pet
      if 'pet' not in self.penetrates and defender.pet is not None and defender.pet.hp > 0: 
        #reaction_member = self.channel.guild.get_member(defender.member_id) 
        target_prompt = await self.channel.send(content='{}, will your pet take the hit? React with {} for yes and {} for no. This defaults to {2} if you do not respond after 20 seconds. '.format(defender.name, thumbs_up_emoji, thumbs_down_emoji)) 

        reaction_emoji = await self.client.prompt_for_reaction(target_prompt, defender.member_id, emojis=(thumbs_up_emoji, thumbs_down_emoji), timeout=20, default_emoji=thumbs_down_emoji) 

        '''
        target_prompt.add_reaction(thumbs_up_emoji) 
        target_prompt.add_reaction(thumbs_down_emoji) 

        def check(reaction, member): 
          return reaction.message is target_prompt and reaction.emoji in (thumbs_up_emoji, thumbs_down_emoji) and member is reaction_member
        
        try: 
          reaction, member = await self.client.wait_for('reaction_add', check=check, timeout=20) 
          reaction_emoji = reaction.emoji
        except asyncio.TimeoutError: 
          reaction_emoji = thumbs_down_emoji
        ''' 

        #if for some reason the pet still exists and is alive after this prompt
        if reaction_emoji == thumbs_up_emoji and defender.pet is not None and defender.pet.hp > 0: 
          target = defender.pet
        elif 'sub' not in self.penetrates and defender.sub is not None and defender.sub.current_hp > 0 and defender.sub.active: 
          target = defender.sub
        else: 
          target = defender
      
      #if the player is still the target but they have a living sub and self does not ignore subs
      elif 'sub' not in self.penetrates and defender.sub is not None and defender.sub.current_hp > 0 and defender.sub.active: 
        target = defender.sub
      else: 
        target = defender
    else: 
      target = defender
    
    await self.switch_hit(target) 
  
  async def on_death(self): 
    await self.channel.send(content='{} died! '.format(self.name)) 
    
    ''' 
    self.base_hp = self.death_restore.base_hp
    self.current_hp = self.death_restore.current_hp
    self.max_hp = self.death_restore.max_hp
    self.base_shield = self.death_restore.base_shield
    self.current_shield = self.death_restore.current_shield
    self.max_shield = self.death_restore.max_shield
    self.base_attack = self.death_restore.base_attack
    self.current_attack = self.death_restore.current_attack
    self.miss = copy.deepcopy(self.death_restore.miss) 
    self.crit = copy.deepcopy(self.death_restore.miss) 
    self.enemy_miss = copy.deepcopy(self.death_restore.enemy_miss) 
    self.enemy_crit = copy.deepcopy(self.death_restore.enemy_crit) 
    self.scaling_factor = self.death_restore.scaling_factor
    self.access_levels = copy.deepcopy(self.death_restore.access_levels) 
    self.penetrates = copy.deepcopy(self.death_restore.penetrates) 
    self.bleeds = copy.deepcopy(self.death_restore.bleeds) 
    ''' 
  
  async def on_battle_round_start(self): 
    await self.check_pressure_damage() 
        
  ''' async def give_items(self, receiver, items_to_give): 
    total_to_give = {} 
    
    for item, amount in items_to_give.items(): 
      to_receive = amount
      if 'all' in receiver.multipliers: 
          to_receive *= receiver.multipliers['all'] 
      elif item in receiver.multipliers: 
          to_receive *= receiver.multipliers[item] 
      total_to_give.update({item: to_receive}) 
    
    receiver.receive_items(total_to_give) ''' 
  
  #def on_death(self, killer): 
        
        
#might not be needing this anymore, gonna save for if i do later
'''class Multipliers: 
    def __init__(self, all_multiplier, food_multiplier, wood_multiplier, iron_multiplier, steel_multiplier, titanium_multiplier, feather_multiplier, cloud_multipler): 
        self.all_multiplier = all_multiplier
        self.food_multiplier = food_multiplier
        self.wood_multiplier = wood_multiplier
        self.iron_multiplier = iron_multiplier
        self.steel_multiplier = steel_multipler
        self.titanium_multiplier = titanium_multiplier
        self.feather_multiplier = feather_multiplier
        self.cloud_multiplier = cloud_multiplier ''' 

class Player(Entity): 
  '''
  name = '' 
  description = 'None' 
  specials = ('None',) 
  starting_min_hp = 0
  starting_shield = 0
  starting_enemy_attack_multiplier = 1
  starting_miss = [1] 
  starting_crit = [6] 
  starting_enemy_miss = [] 
  starting_enemy_crit = [] 
  starting_penetrates = [] 
  starting_bleeds = [] 
  ''' 

  starting_hp = 100
  starting_attack = 20
  starting_access_levels = (1,) 
  starting_multipliers = {} 
  starting_oxygen = 5
  starting_items = () 
  starting_priority = 0

  def __init__(self, client, channel, game, name='', member_id=0): 
    self.game = game
    self.name = name
    self.member_id = member_id
    self.game = game
    self.multipliers = copy.deepcopy(self.starting_multipliers) 
    self.current_oxygen = self.starting_oxygen
    self.max_oxygen = self.starting_oxygen
    self.items = [] 
    self.saved_items = [] 
    self.priority = self.starting_priority
    self.sub = None
    self.pet = None
    self.blubber_base = None
    self.enemy = None
    self.o_game_turn = False
    self.uo_game_turn = False
    self.can_move = False
    self.battle_turn = False
    #players cannot do anything at all when dead

    Entity.__init__(self, client, channel, current_level=1) 
  
  def modify_deconstructed(self, deconstructed): 
    del deconstructed['game'] 

    items_copy = [inv_entry.copy() for inv_entry in deconstructed['items']] 

    for inv_entry in items_copy: 
      inv_entry[0] = inv_entry[0].deconstruct() 
    
    deconstructed['items'] = items_copy
    
    if deconstructed['pet'] is not None: 
      deconstructed['pet'] = deconstructed['pet'].deconstruct() 
    if deconstructed['sub'] is not None: 
      deconstructed['sub'] = deconstructed['sub'].deconstruct() 
    if deconstructed['blubber_base'] is not None: 
      deconstructed['blubber_base'] = deconstructed['blubber_base'].deconstruct() 
    
    enemy = deconstructed['enemy'] 

    if enemy is not None: 
      if not(enemy.is_a(Player)): 
        deconstructed['enemy'] = enemy.deconstruct() 
      else: 
        deconstructed['enemy'] = enemy.member_id
    
    Entity.modify_deconstructed(self, deconstructed) 
  
  def reconstruct_next(self): 
    for inv_entry in self.items: 
      inv_entry[0] = reconstructed_item = self.reconstruct(inv_entry[0], self.client, self.channel, self) 
    
    if self.sub is not None: 
      self.sub = self.reconstruct(self.sub, self.client, self.channel, self) 
    if self.pet is not None: 
      self.pet = self.reconstruct(self.sub, self.client, self.channel, self) 
    if self.blubber_base is not None: 
      self.blubber_base = self.reconstruct(self.blubber_base, self.client, self.channel, self) 
    
    #if the enemy isn't a Player (Player enemies will be reconstructed in on_turn_on) 
    if type(self.enemy) is dict: 
      self.enemy = self.reconstruct(self.enemy, self.client, self.channel, self) 
    
    Entity.reconstruct_next(self) 
  
  def on_shutdown(self): 
    for item_class, bonus in self.starting_multipliers: 
      self.multipliers[item_class] /= bonus
    self.current_oxygen -= self.starting_oxygen
    self.max_oxygen -= self.starting_oxygen
    self.priority -= self.starting_priority
    
    Entity.on_shutdown(self) 
  
  async def on_turn_on(self): 
    for item_class, bonus in self.starting_multipliers: 
      if item_class in self.multipliers: 
        self.multipliers[item_class] *= bonus
      else: 
        self.multipliers[item_class] = bonus
    self.current_oxygen += self.starting_oxygen
    self.max_oxygen += self.starting_oxygen
    self.priority += self.starting_priority
    
    Entity.on_turn_on(self) 

  def get_inv_entry(self, item_class): 
    for inv_entry in self.items: 
      if inv_entry[0].__class__ is item_class: 
        return inv_entry
    
    return None, 0
  
  def lacks_items(self, required_items): 
    missing_items = [] 
    
    for required_item, required_amount in required_items: 
      if type(required_item) is type: 
        required_item_class = required_item
      else: 
        required_item_class = required_item.__class__ 
      
      own_item, own_item_amount = self.get_inv_entry(required_item_class) 

      if own_item_amount < required_amount: 
        deficit = required_amount - own_item_amount

        missing_items.append((required_item_class, deficit)) 
    
    return missing_items
  
  async def take_oxygen_damage(self): 
    await self.channel.send(content='{} takes oxygen damage! '.format(self.name)) 
    self_died = await self.take_damage(100, penetrates=['shield']) 

    return self_died
  
  async def check_current_oxygen(self): 
    self_died = False

    if self.current_oxygen <= 0: 
      self_died = await self.take_oxygen_damage() 
    
    return self_died
  
  async def start_battle(self, enemy, surprise_attack=False): 
    self.can_move = False
    self.enemy = enemy
    enemy.enemy = self

    await self.on_global_event('battle_start') 
    await enemy.on_global_event('battle_start') 

    self_died = await self.on_global_event('battle_round_start') 
    enemy_died = await enemy.on_global_event('battle_round_start') 

    stop_battle = self_died or enemy_died
    
    if not(stop_battle): 
      await self.decide_first(surprise_attack) 
  
  async def check_surprise_attack(self): 
    chance = self.current_level
    all_chances = range(1, chance) 
    die_roll = die.roll_die() 

    await self.channel.send(content='{} rolled a {}! '.format(self.name, die_roll)) 

    if die_roll in all_chances: 
      enemy = die.select_creature(self.current_level) 

      await self.channel.send(content='{} is surprise attacked by a {}! '.format(self.name, enemy.name)) 

      await self.start_battle(enemy, surprise_attack=True)  
    else: 
      self.can_move = True

      await self.channel.send(content='{} can act now! '.format(self.name)) 
  
  async def challenge_player(self, player): 
    challenge_prompt = await self.channel.send(content='{0} challenges {1} to a PVP battle! React with {2} to accept and {3} to decline! This defaults to {3} if you dont react within 20 seconds. '.format(self.name, player.name, thumbs_up_emoji, thumbs_down_emoji))  

    reaction_emoji = await self.client.prompt_for_reaction(challenge_prompt, player.member_id, emojis=(thumbs_up_emoji, thumbs_down_emoji), timeout=20, default_emoji=thumbs_down_emoji) 

    if reaction_emoji == thumbs_up_emoji: 
      await self.channel.send(content='{} accepts the challenge! '.format(player.name)) 
      await self.start_battle(player) 
    else: 
      await self.channel.send(content='{} declines the challenge. '.format(player.name)) 
    
  async def free_regen(self): 
    hp_regen = 20

    self.can_move = False
    self.current_hp += hp_regen
    await self.channel.send(content="{}'s current HP increased by {}! ".format(self.name, hp_regen)) 

    await self.check_current_hp() 

    '''
    if self.pet is not None and self.pet.current_hp > 0: 
      await self.pet.on_game_turn_start() 
    if self.sub is not None and self.sub.current_hp > 0: 
      await self.sub.on_game_turn_start() 
    if self.blubber_base is not None and self.blubber_base.current_hp > 0: 
      await self.blubber_base.on_game_turn_start() 

    #all their items do whatever the heck they need to do at turn start
    for item, amount in self.items.items(): 
      item.on_game_turn_start(self) 
    
    ''' 
  
  async def before_action(self): 
    self_died = False

    if self.current_level > 1: 
      #oxygen loss and possible oxygen damage
      self.current_oxygen -= 1

      await self.channel.send(content='{} lost 1 oxygen! '.format(self.name)) 
      self_died = await self.check_current_oxygen() 

      if self_died: 
        return self_died
      
      #surprise attack
      await self.check_surprise_attack() 
    elif self.current_oxygen < self.max_oxygen: 
      self.current_oxygen = self.max_oxygen

      await self.channel.send(content="{}'s current oxygen refilled to max! ".format(self.name)) 

      self.can_move = True

      await self.channel.send(content='{} can act now! '.format(self.name)) 

  async def on_life_start(self): 
    await self.receive_items(self.starting_items) 

    await self.channel.send(content='A wild {} appeared! '.format(self.name)) 
  
  async def on_game_turn_start(self): 
    self.uo_game_turn = True
  
  async def on_game_turn_end(self): 
    self.uo_game_turn = False
    self.can_move = False
  
  async def attempt_flee(self): 
    punishment = 2

    await self.channel.send(content='{} attempts to flee! They are vulnerable! '.format(self.name)) 

    won_flip = await die.call_and_flip(self.client, self.channel, self.member_id) 

    if won_flip: 
      await self.channel.send(content='{} successfully fled! '.format(self.name)) 
      #end battle stuff 
    else: 
      self.battle_turn = False
      self.enemy.battle_turn = True

      await self.channel.send(content='{} failed to flee! {} can now hit them {} times! '.format(self.name, self.enemy.name, punishment)) 

      for time in range(punishment): 
        if self.enemy.is_a(Player): 
          self_died = await self.enemy.switch_attack() 
        else: 
          self_died = await self.enemy.attack() 

        if self_died: 
          break
      
      self.enemy.battle_turn = False
  
  async def on_global_event(self, event_name): 
    self_died = False

    if self.pet is not None and self.pet.current_hp > 0: 
      await eval('self.pet.on_{}() '.format()) 
    if self.sub is not None and self.sub.current_hp > 0: 
      await eval('self.sub.on_{}() '.format(event_name)) 
    if self.blubber_base is not None and self.blubber_base.current_hp > 0: 
      await eval('self.blubber_base.on_{}() '.format(event_name)) 
    
    for item, amount in self.items: 
      await eval('item.on_{}(amount) '.format(event_name)) 
    
    self_died = await eval('self.on_{}() '.format(event_name)) 

    return self_died
  
  async def decide_first(self, surprise_attack): 
    if surprise_attack: 
      self.enemy.priority += 1
    
    if self.priority == self.enemy.priority: 
      won_flip = await die.call_and_flip(self.client, self.channel, self.member_id) 

      if won_flip: 
        more_first = self
      else: 
        more_first = self.enemy
    else: 
      more_first = max(self, self.enemy, key=lambda side: side.priority) 
    
    await self.channel.send(content='{} got first hit! '.format(more_first.name)) 

    await more_first.on_global_event('first_hit') 
    await more_first.on_global_event('win_coinflip') 
  
  async def calculate_hp_bleed(self, inflicter, penetrates, bleeds): 
    if 'player' in bleeds and 'blubber base' not in penetrates and self.blubber_base is not None and self.blubber_base.hp > 0: 
      bleed_damage = self.min_hp - self.current_hp
      
      await self.channel.send(content='{} bleeds onto their Blubber Base! '.format(self.name)) 
      await self.blubber_base.take_damage(bleed_damage, inflicter=inflicter, penetrates=penetrates, bleeds=bleeds) 
  
  async def on_death(self, allow_respawn=True): 
    self.uo_game_turn = False
    self.can_move = False

    await self.channel.send(content='{} died! '.format(self.name)) 

    for item_class, amount in self.saved_items: 
      item_class().salvage(self, amount) 

    if self.enemy is not None and self.enemy.is_a(Player): 
      await self.enemy.earn_items(self.items) 
    
    own_index = self.game.players.index(self) 

    if allow_respawn: 
      respawn_prompt = await self.channel.send(content='{}, do you want to respawn? React with {} for yes and {} for no. '.format(self.name, thumbs_up_emoji, thumbs_down_emoji)) 
      respawn_emoji = await self.client.prompt_for_reaction(respawn_prompt, self.member_id, emojis=(thumbs_up_emoji, thumbs_down_emoji), timeout=20, default_emoji=thumbs_up_emoji) 

      allow_respawn = respawn_emoji == thumbs_up_emoji

    if allow_respawn: 
      await self.channel.send(content='{}, choose the class you want to be. This defaults to your current class after 20 seconds. '.format(self.name)) 
      class_choice = await self.client.prompt_for_message(self.channel, self.member_id, custom_check=lambda message: search(classes, message.content) is not None, timeout=20) 

      if class_choice is not None: 
        chosen_class = search(classes, class_choice) 
      else: 
        chosen_class = self.__class__ 
      
      #the revived self replaces the old self
      new_self = chosen_class(client=self.client, channel=self.channel, name=self.name, member_id=self.member_id, game=self.game) 

      print('new self has been created') 

      self.game.players[own_index] = new_self

      print('new self has replaced old self') 

      #saved items and blubber base are transferred to new self
      await new_self.receive_items(self.saved_items) 

      if self.blubber_base is not None: 
        new_self.blubber_base = self.blubber_base
        new_self.blubber_base.owner = new_self

        await new_self.blubber_base.on_receive() 
      
      await new_self.on_life_start() 

      if self.o_game_turn: 
        await self.game.next_turn() 
    else: 
      await self.game.remove_player(self) 
  
  async def receive_items(self, to_receive): 
    for item, amount in to_receive: 
      if amount > 0: 
        first_receival = False

        if type(item) is type: 
          item_class = item
        else: 
          item_class = item.__class__ 
        
        entry_item, entry_amount = receiving_entry = self.get_inv_entry(item_class) 

        if entry_item is None: 
          entry_item = item_class(self.client, self.channel, self)   
          receiving_entry = [entry_item, 0] 

          self.items.append(receiving_entry) 
        
        if entry_amount == 0: 
          first_receival = True
        
        receiving_entry[1] += amount
        await self.channel.send(content='{} received {} {}(s)! '.format(self.name, item.name, amount)) 

        if entry_item.can_stack is not None and (entry_item.can_stack or first_receival): 
          await entry_item.apply_bonuses(amount) 
  
  async def earn_items(self, to_earn): 
    to_receive = [] 

    for item, amount in to_earn: 
      if type(item) is type: 
        item_class = item
      else: 
        item_class = item.__class__ 
      
      final_amount = amount

      if 'all' in self.multipliers: 
        all_multiplier = self.multipliers['all'] 

        final_amount *= all_multiplier
        await self.channel.send(content='{} receives a x{} multiplier on all items! '.format(self.name, all_multiplier)) 
      if item_class in self.multipliers: 
        item_multiplier = self.multipliers[item_class] 

        final_amount *= item_multiplier
        await self.channel.send(content='{} receives a x{} multiplier on {}s! '.format(self.name, item_multiplier, item.name)) 
      
      to_receive.append([item_class, final_amount]) 
    
    await self.receive_items(to_receive)  
  
  #forgive_debt means that it you don't have sufficient amounts of an item it will just take what you have. 
  async def lose_items(self, to_lose): 
    taken_items = [] 

    for item, amount in to_lose: 
      if amount > 0: 
        last_removal = False

        if type(item) is type: 
          item_class = item
        else: 
          item_class = item.__class__ 
        
        entry_item, entry_amount = losing_entry = self.get_inv_entry(item_class) 

        if entry_item is not None: 
          lost_amount = min(entry_amount, amount) 
          losing_entry[1] -= lost_amount

          taken_items.append([item_class, lost_amount]) 

          if losing_entry[1] == 0: 
            last_removal = True
          
          if entry_item.can_stack is not None and (entry_item.can_stack or last_removal): 
            entry_item.remove_bonuses(amount) 
    
    return taken_items
  
  async def craft(self, item_name, amount): 
    item_class = search(items, item_name) 

    if item_class is not None: 
      if item_class.recipe is not None: 
        final_recipe = [[recipe_item, recipe_amount * amount] for recipe_item, recipe_amount in item_class.recipe] 

        lacking_items = self.lacks_items(final_recipe) 

        if len(lacking_items) > 0: 
          for item, number in lacking_items: 
            await self.channel.send(content='{} lacks {} {}(s) to craft {} {}(s) '.format(self.name, number, item.name, amount, item_class.name)) 
        else: 
          self.can_move = False

          await self.lose_items(final_recipe) 
          await self.receive_items([[item_class, amount]]) 
      else: 
        await self.channel.send(content='{} is not craftable'.format(item_class.name)) 
    else: 
      await self.channel.send(content='{} is not a valid craftable item'.format(item_name)) 

class Forager(Player): 
  name = 'Forager' 
  description = "Nothing escapes dis boi's eye" 
  specials = ('Guaranteed flee on battle turn',) 
  starting_multipliers = {'all': 2} 
  
  async def attempt_flee(self): 
    await self.channel.send(content='{} successfully fled! '.format(self.name)) 
    #end battle stuff

class Beserker(Player): 
  starting_scaling_factor = 1
  name = 'Beserker' 
  description = 'REE REE TRIGGER TRIGGER REE REEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE'  
  specials = ('Attack increases with HP lost at a {} to 1 ratio'.format(starting_scaling_factor),) 

  def __init__(self, client, channel, game, name='', member_id=0): 
    self.scaling_factor = self.starting_scaling_factor

    Player.__init__(self, client, channel, game, name=name, member_id=member_id) 
  
  def on_shutdown(self): 
    self.scaling_factor /= self.starting_scaling_factor
    
    Player.on_shutdown(self) 
  
  async def on_turn_on(self): 
    self.scaling_factor *= self.starting_scaling_factor

    Player.on_turn_on(self) 
  
  async def check_current_hp(self): 
    self_died = await Player.check_current_hp(self) 

    if not(self_died): 
      self.current_attack = (self.max_hp - self.current_hp) * self.scaling_factor + self.base_attack

      await self.channel.send(content='{} now has {} attack! '.format(self.name, self.current_attack)) 
  
class Fisherman(Player): 
  name = 'Fisherman' 
  description = 'Lots of indentured servants'  
  starting_attack = 40
  starting_items = ([Fishing_Net, 1],) 

class Hunter(Player): 
  name = 'Hunter' 
  description = 'Head of the pack' 
  starting_hp = 150
  starting_attack = 50
  starting_multipliers = {Meat: 2} 

class Diver(Player): 
  allowed_level_deviation = 1
  starting_oxygen = 6
  name = 'Diver' 
  description = 'Dives so something' 
  specials = ('Is always allowed one additional level beyond allowed'.format(allowed_level_deviation), 'Starts with {} oxygen'.format(starting_oxygen), "Can move levels and drag their opponents with them on their battle turn...except this doesn't work cuz there is only one level hahahahahahahahahaha") 

  async def take_pressure_damage(self): 
    self_died = False
    smallest_distance = math.inf

    for level in self.access_levels: 
      distance = abs(self.current_level - level) - 1

      smallest_distance = min(smallest_distance, distance) 
    
    damage = smallest_distance * 20

    await self.channel.send(content='{} takes pressure damage! '.format(self.name)) 
    self_died = await self.take_damage(damage, penetrates=('shield'))  
    
    return self_died

''' 
def calculate_level_multipliers(self): 
  level = die.roll_die() 
  level_multiplier = (level + 1) / 5
  
  self.current_hp *= level_multiplier
  self.max_hp *= level_multiplier
  self.current_shield *= level_multiplier
  self.max_shield *= level_multiplier
  self.attack_damage *= level_multiplier
  for item, amount in self.drops.items(): 
    self.drops[item] = int(amount * level_multiplier) 
  
  return level
''' 

classes = (Forager, Beserker, Hunter, Diver, Fisherman) 

class Creature(Entity): 
  drops = () 
  stars = 0
  passive = False
  starting_priority = 0

  def __init__(self, client, channel, enemy, current_level=0): 
    self.priority = self.starting_priority
    self.enemy = enemy
    self.battle_turn = False

    Entity.__init__(self, client, channel, current_level=current_level) 
    #self.level = self.calculate_level_multipliers() 
  
  def modify_deconstructed(self, deconstructed): 
    del deconstructed['enemy'] 

    Entity.modify_deconstructed(self, deconstructed) 
  
  async def on_death(self): 
    await self.channel.send(content='{} died! '.format(self.name)) 

    #do drops here
    if self.drops is not None: 
      await self.enemy.earn_items(self.drops) 
    
    opponent = self.enemy
    
    self.enemy.enemy = None
    self.enemy = None

    await opponent.on_global_event('battle_end') 
  
  async def on_win_coinflip(self): 
    self.battle_turn = True

    await self.attack(self.enemy) 

    self.battle_turn = False
  
  async def on_first_hit(self): 
    if self.passive: 
      await self.channel.send(content='{} is passive and flees! '.format(self.name)) 
    else: 
      await Entity.on_first_hit() 
  
  async def on_global_event(self, event_name): 
    exec('await self.on_{}() '.format(event_name)) 
  
  async def switch_attack(self): 
    await self.attack(self.enemy) 

class Trout(Creature): 
  name = "Trout" 
  description = "Food - not a cat" 
  starting_hp = 50
  starting_attack = 10
  starting_access_levels = (1,) 
  drops = ([Meat, 2],) 
  stars = 1

class Ariel_Leviathan(Creature): 
  name = "Ariel Leviathan" 
  description = "A singular fragment of fecal matter that possesses 400 health points - Mastermind" 
  starting_hp = 400
  starting_attack = 10
  starting_access_levels = (1,) 
  drops = [Sky_Blade, 1], [Meat, 8] 
  stars = 1
  passive = True

class Saltwater_Croc(Creature): 
  name = "Saltwater Croc" 
  description = "What's for lunch - jlscientist" 
  starting_hp = 100
  starting_shield = 100
  starting_attack = 100
  starting_access_levels = (1,) 
  drops = [Scale, 1], [Meat, 5] 
  passive = True

class Tiger_Fish(Creature): 
  rage_threshold = 50
  rage_attack = 50
  name = "Tiger Fish" 
  description = "I don't know - RyantheKing" 
  specials = ("Damage increases to {} if the target of its attack has {} or more damage. ".format(rage_attack, rage_threshold),) 
  starting_hp = 100
  starting_attack = 30
  starting_access_levels = (1,) 
  drops = ([Meat, 1],) 
  stars = 1
  
  async def switch_hit(self, target): 
    miss = self.final_miss(target) 
    crit = self.final_crit(target) 
    #here is the attack roll (representing a die roll) 
    attack_roll = die.roll_die() 

    if target.current_attack >= self.rage_threshold: 
      self.current_attack = self.rage_attack

      await self.channel.send(content="{} rages, and its attack increases to {}! ".format(self.rage_attack)) 
      
    await self.channel.send(content='{} rolled a {}! '.format(self.name, attack_roll)) 
    if attack_roll in miss: 
      await self.on_miss(target) 
    elif attack_roll in crit: 
      await self.on_crit(target) 
    else: 
      await self.on_regular_hit(target) 
    
    self.current_attack = self.starting_attack

class Gar(Creature): 
  name = "Gar" 
  description = "Closely GARds its 1 meat - not a cat" 
  starting_hp = 100
  starting_attack = 30
  starting_access_levels = (1,) 
  drops = ([Meat, 1],) 
  stars = 1

class Turtle(Creature): 
  name = 'Turtle' 
  description = 'Turtles' 
  starting_hp = 80
  starting_shield = 90
  starting_attack = 10
  starting_access_levels = (1,) 
  drops = [Suit, 1], [Meat, 1] 
  stars = 1

class Pirahna(Creature): 
  per_round_attack_increase = 20
  name = 'Pirahna' 
  description = 'Om nom nom' 
  specials = ('Attack increases by {} every battle turn'.format(per_round_attack_increase),)  
  starting_hp = 70
  starting_attack = 10
  starting_access_levels = (1,) 
  drops = ([Meat, 1],) 
  stars = 1

  def __init__(self, client, channel, current_level=0, enemy=None): 
    self.elapsed_battle_turns = 0

    Creature.__init__(self, client, channel, current_level=current_level, enemy=enemy)  

  def on_shutdown(self): 
    self.base_attack -= self.elapsed_battle_turns * self.per_round_attack_increase
    self.current_attack -= self.elapsed_battle_turns * self.per_round_attack_increase

    Creature.on_shutdown(self) 
  
  async def on_turn_on(self): 
    self.base_attack += self.elapsed_battle_turns * self.per_round_attack_increase
    self.current_attack += self.elapsed_battle_turns * self.per_round_attack_increase

    Creature.on_shutdown(self) 
  
  async def on_battle_round_start(self): 
    self.elapsed_battle_turns += 1

    self.base_attack += self.per_round_attack_increase

    await self.channel.send(content="{}'s base attack increased by {}! ".format(self.name, self.per_round_attack_increase)) 

    self.current_attack += self.per_round_attack_increase

    await self.channel.send(content="{}'s current attack increased by {}! ".format(self.name, self.per_round_attack_increase)) 

    await Creature.on_battle_round_start(self) 
  
class Hatchet_Fish(Creature): 
  name = 'Hatchet Fish' 
  description = 'Chop chop' 
  starting_hp = 70
  starting_attack = 30
  starting_access_levels = (1,) 
  drops = ([Hatchet_Fish_Corpse, 1],) 
  stars = 1

class Octofish(Creature): 
  name = 'Octofish' 
  description = 'stuff' 
  starting_hp = 70
  starting_attack = 30
  starting_access_levels = (1,) 
  drops = ([Meat, 1],) 
  stars = 1

class Big_Trout(Creature): 
  name = 'Big Trout' 
  description = "it's like trout but big" 
  starting_hp = 60
  starting_attack = 20
  starting_access_levels = (1,) 
  drops = ([Meat, 4],) 
  stars = 1

class Water_Bug(Creature): 
  starting_miss = () 
  starting_crit = (1, 6) 
  starting_enemy_miss = (1, 2, 3) 
  name = 'Water Bug' 
  description = 'Where did it come from? Where did it go? ' 
  specials = ('Cannot miss', 'Crits on {}'.format(', '.join((str(crit_chance) for crit_chance in starting_crit))), 'Enemy misses on {}'.format(', '.join((str(miss_chance) for miss_chance in starting_enemy_miss))))  
  starting_hp = 50
  starting_attack = 10
  starting_access_levels = (1,) 
  stars = 1

class Tummy_Tetra(Creature): 
  steals = ([Meat, 2],) 
  steals_tuple = tuple((item.name, amount) for item, amount in steals) 
  steals_string = ', '.join(('{} {}'.format(item_name, amount) for item_name, amount in steals_tuple)) 

  name = 'Tummy Tetra' 
  description = 'yum' 
  specials = ('50% chance of stealing {} from players on hit'.format(steals_string),) 
  starting_hp = 50
  starting_attack = 30
  starting_access_levels = (1,) 
  stars = 1
  
  async def steal_stuff(self, target): 
    stolen_items = await target.lose_items(self.steals) 

    for item, amount in stolen_items: 
      await self.channel.send(content='{} stole and ate {} {}(s)! '.format(self.name, amount, item.name)) 
      if item.usable: 
        await item().attempt_use(self, amount) 
  
  async def attempt_steal(self, target): 
    #reaction_member = self.channel.guild.get_member(target.member_id) 
    
    await self.channel.send(content="{} lunges for your inventory! ".format(self.name)) 

    won_flip = await die.call_and_flip(self.client, self.channel, target.member_id) 

    '''
    coin_flip_prompt.add_reaction(h_emoji) 
    coin_flip_prompt.add_reaction(t_emoji) 

    def check(reaction, member): 
      return reaction.message == coin_flip_prompt and reaction.emoji in (h_emoji, t_emoji) and member == reaction_member
    
    try: 
      reaction, member = await self.client.wait_for('reaction_add', check=check, timeout=10) 
      reaction_emoji = reaction.emoji 
    except asyncio.TimeoutError: 
      reaction_emoji = h_emoji
    
    side_emoji, side_name = die.flip_coin() 
    ''' 

    if won_flip: 
      await self.channel.send(content='{} failed to steal anything. '.format(self.name)) 
    else: 
      await self.steal_stuff(target) 
  
  async def switch_hit(self, target): 
    target_died = await Creature.switch_hit(self, target) 

    if not(target_died) and target.is_a(Player): 
      await self.attempt_steal(target) 

class Toxic_Waste(Creature): 
  name = 'Toxic Waste' 
  description = 'oof' 
  specials = ('Always gets first hit', 'Hits once and then disappears', "Gives meat instead of attacking if you have biowheel but oh wait i haven't made the middle yet so you can't get it haaHaHhAahHAHHHaHhHHaHahaAHHaHaHA") 
  starting_hp = 0
  starting_attack = 30
  starting_access_levels = (1, 2, 3, 4) 
  starting_priority = 3
  
  async def attack(self, defender): 
    defender_died = await Creature.attack(self, defender) 

    if not(defender_died): 
      await self.channel.send(content='{} disappeared! '.format(self.name)) 
      opponent = self.enemy
      self.enemy = None
      opponent.enemy = None

      await opponent.on_global_event('battle_end') 

creatures = (Trout, Ariel_Leviathan, Saltwater_Croc, Tiger_Fish, Gar, Turtle, Pirahna, Hatchet_Fish, Octofish, Big_Trout, Tummy_Tetra, Water_Bug, Toxic_Waste) 

levels = {
  1: {
    'creatures': {
      Ariel_Leviathan: 1, 
      Saltwater_Croc: 1, 
      Tiger_Fish: 1, 
      Gar: 1, 
      Turtle: 3, 
      Pirahna: 1, 
      Hatchet_Fish: 1, 
      Octofish: 1, 
      Big_Trout: 1, 
      Water_Bug: 1, 
      Tummy_Tetra: 1, 
      Trout: 2, 
      Toxic_Waste: 2, 
    }
  }
} 

'''
async def apply_multipliers(self, target, amount): 
  if amount != 0: 
    if self.hp_bonus != 0: 
      hp_gain = self.hp_bonus * amount
      target.base_hp += hp_gain
      await self.channel.send(content="{}'s base HP increased by {}! ".format(target.name, hp_gain)) 
      target.current_hp += hp_gain
      await self.channel.send(content='{} gained {} HP! '.format(target.name, hp_gain)) 
      target.max_hp += hp_gain
      await self.channel.send(content="{}'s max HP increased by {}! ".format(target.name, hp_gain)) 
      
      target.check_current_hp() 
    
    if self.shield_bonus != 0: 
      shield_gain = self.shield_bonus * amount
      target.base_shield += shield_gain
      await self.channel.send(content="{}'s base shield increased by {}! ".format(target.name, shield_gain)) 
      target.current_shield += shield_gain
      await self.channel.send(content='{} gained {} shield! '.format(target.name, shield_gain)) 
      target.max_shield += shield_gain
      await self.channel.send(content="{}'s max shield increased by {}! ".format(target.name, shield_gain)) 
      
      target.check_current_shield() 
    
    if self.attack_bonus != 0: 
      attack_gain = self.attack_bonus * amount
      target.base_attack += attack_gain
      await self.channel.send(content="{}'s base attack increased by {}! ".format(target.name, attack_gain)) 
      target.current_attack += attack_gain
      await self.channel.send(content='{} gained {} attack! '.format(target.name, attack_gain)) 
    
    if self.oxygen_bonus != 0: 
      oxygen_gain = self.oxygen_bonus * amount
      target.current_oxygen += oxygen_gain
      await self.channel.send(content='{} gained {} oxygen! '.format(target.name, oxygen_gain)) 
      target.max_oxygen += oxygen_gain
''' 






































#experiment space

'''def apply_multiplier_to_dict(multiplier, stats): 
  for stat in stats: 
    if type(stats[stat]) is dict: 
      stats[stat] = apply_multiplier_to_dict(multiplier, stats[stat]) 
    else: 
      try: 
        stats[stat] *= multiplier
      except (TypeError, ValueError): 
        pass
  
  return stats ''' 
      

