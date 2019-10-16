import math
import random
import enum
# noinspection PyPackageRequirements
import discord
import logging
import asyncio
import copy
from . import chars, printing, storage, ttd_tools
from .chars import * 
from .printing import print
from .ttd_tools import format_iterable, make_list

'''
Functions that propagate Entity.check_death()'s boolean: 
Entity.take_damage() 
Entity.check_pressure_damage() 
Player.take_oxygen_damage() 
Player.check_current_oxygen() 

'''

''' 

CURRENTLY WORKING ON: 
on_shutdown() and on_turn_on() functions
some global events ignore hp requirement
Entity.hp_multiplier

''' 

# useful functions

# top is the list to subtract from, bottom is the list to subtract from that
def subtract_lists(top, bottom):
    difference = top.copy()

    for item in bottom:
        difference.remove(item)

    return difference

def add_dicts(top, bottom, multiplier=1): 
    total = top.copy() 

    for key, value in bottom.items(): 
        to_add = value * multiplier

        if key in total: 
            total[key] += to_add
        else: 
            total[key] = to_add
    
    return total

def subtract_dicts(top, bottom): 
    return add_dicts(top, bottom, multiplier=-1) 

# for all the random needs
# Die was honestly the best name i could think of
class Die:
    # this returns the emoji, followed by the name
    @staticmethod
    def flip_coin(): 
        return random.choice(('heads', 'tails')) 

    @staticmethod
    def roll_die():
        return random.randint(1, 6) 
    
    '''
    @staticmethod
    def select_creature(client, channel, level):
        # makes sure that there are actually creatures in that level
        if len(levels[level]['creatures']) > 0:
            level_creatures = levels[level]['creatures']
            sorted_creatures = sorted(level_creatures)

            # calculates total amount of creatures here
            total_amount = 0

            for creature in sorted_creatures:
                total_amount += level_creatures[creature]

            # picks a random creature here
            to_pick = random.randint(1, total_amount)
            running_sum = 0

            for creature in sorted_creatures:
                running_sum += level_creatures[creature]

                if running_sum >= to_pick:
                    return creature(client, channel, current_level=level) 
    ''' 

def action(func): 
    async def action_func(self, report, *args, **kwargs): 
        if self.is_a(Entity): 
            async with self.acting(report): 
                print('executing {}'.format(func)) 

                result = await func(self, report, *args, **kwargs) 

                print('finished executing {}'.format(func)) 

                return result
        else: 
            return await func(self, report, *args, **kwargs) 
    
    return action_func

class Events(ttd_tools.Game_Object): 
    @action
    async def on_game_turn_start(self, report):
        pass
    
    @action
    async def on_game_turn_end(self, report):
        pass
    
    @action
    async def on_battle_start(self, report):
        pass

    @action
    async def on_battle_end(self, report):
        pass

    @action
    async def on_battle_round_start(self, report):
        pass

    @action
    async def on_battle_round_end(self, report):
        pass

    @action
    async def on_first_hit(self, report):
        pass

    @action
    async def on_win_coinflip(self, report):
        pass
    
    @action
    async def on_move_levels(self, report, move_by): 
        pass

class All(storage.D_Meta): 
    name = 'all items' 

# noinspection PyMethodOverriding

class Levels(enum.Enum): 
    def __init__(self, value): 
        self.creatures = {} 
        self.total_creatures = 0
        self.gatherables = {} 
        self.mineables = {} 

        enum.Enum.__init__(self) 
    
    def set_stats(self, stats): 
        level = level_stats[self] 

        self.creatures = level['creatures'] 
        
        for creature, amount in self.creatures.items(): 
            self.total_creatures += amount
        
        self.gatherables = level['gatherables'] 
        
        self.mineables = level['mineables'] 
    
    def __hash__(self): 
        return hash(id(self)) 
    
    def __gt__(self, other): 
        return self.value > other.value
    
    def __ge__(self, other): 
        return self.value >= other.value
    
    def __lt__(self, other): 
        return self.value < other.value
    
    def __le__(self, other): 
        return self.value <= other.value
    
    def __eq__(self, other): 
        return self.value == other.value
    
    def __add__(self, other): 
        return self.__class__(self.value + other) 
    
    def __sub__(self, other): 
        if type(other) is type(self): 
            return abs(self.value - other.value) 
        else: 
            return self.__add__(-other) 
    
    def help_embed(self): 
        embed = discord.Embed(title=self.name, type='rich') 

        creatures_gen = ('{} x{}'.format(creature.name, amount) for creature, amount in self.creatures.items()) 
        creatures_str = make_list(creatures_gen) 
        surprise_attack_str = format_iterable(range(1, self.value)) 

        embed.add_field(name='Creatures', value=creatures_str if len(creatures_str) > 0 else None, inline=False) 
        embed.add_field(name='Surprise attack chance', value=surprise_attack_str if len(surprise_attack_str) > 0 else 'No surprise attack') 

        gatherables_gen = ('{} - successful find yields {}'.format(item.name, amount) for item, amount in self.gatherables.items()) 
        gatherables_str = make_list(gatherables_gen) 
        mineables_gen = ('{} - successful mine yields {}'.format(item.name, amount) for item, amount in self.mineables.items()) 
        mineables_str = make_list(mineables_gen) 

        embed.add_field(name='Gatherable items', value=gatherables_str if len(gatherables_str) > 0 else None, inline=False) 
        embed.add_field(name='Mineable items (look up any of them with the `help` command for specific rules on mining them) ', value=mineables_str
        if len(mineables_str) > 0 else None, inline=False) 

        return embed
    
    async def select_creature(self): 
        index = random.randint(1, self.total_creatures) 

        running_sum = 0

        for creature, amount in self.creatures.items(): 
            running_sum += amount

            if running_sum >= index: 
                print(creature) 

                return creature
    
    Surface = enum.auto() 
    Middle = enum.auto() 

#this is to prevent errors from trying to view the incomplete Middle
levels = ttd_tools.Filterable(iterable=Levels) 

items_filters = {
    'usables': lambda item: item.is_usable, 
    'gatherables': lambda item: item.gatherable(), 
    'droppables': lambda item: item.droppable(), 
    'mineables': lambda item: item.is_a(Mineable), 
    'craftables': lambda item: item.recipe is not None, 
    'armors': lambda item: item.is_a(Armor), 
    'weapons': lambda item: item.is_a(Weapon), 
    'shields': lambda item: item.is_a(Shield), 
}
# noinspection PyMethodOverriding
items = ttd_tools.Filterable(**items_filters)  

class Item_Meta(ttd_tools.GO_Meta): 
    append_to = items

class Item(Events, metaclass=Item_Meta, append=False): 
    name = ''
    description = 'None' 
    obtainments = () 
    effects = () 
    usages = () 
    specials = () 
    recipe = None
    # can_stack is None if the item does not give bonuses anyways
    can_stack = False
    is_usable = False

    def __init__(self, client, channel, owner):
        self.owner = owner
        self.usable = self.is_usable

        Events.__init__(self, client, channel) 
    
    @staticmethod
    def modify_deconstructed(deconstructed): 
        del deconstructed['owner'] 

        Events.modify_deconstructed(deconstructed) 

    @classmethod
    def has_in_recipe(cls, item_class):
        if cls.recipe is not None:
            recipe_items = tuple((item_class for item_class, amount in cls.recipe))

            return item_class in recipe_items
        else:
            return False

    @classmethod
    def crafts(cls): 
        return (item_class.name for item_class in items if item_class.has_in_recipe(cls)) 
    
    @classmethod
    def gatherable_in(cls): 
        return tuple((level.name for level in Levels if cls in level.gatherables)) 
    
    @classmethod
    def gatherable(cls): 
        return len(cls.gatherable_in()) > 0
    
    @classmethod
    def dropped_by(cls): 
        dropped_by_list = [] 

        for creature in creatures: 
            for item, amount in creature.starting_drops.items(): 
                if item is cls: 
                    dropped_by_list.append(creature.name) 
        
        return tuple(dropped_by_list) 
    
    @classmethod
    def droppable(cls): 
        return len(cls.dropped_by()) > 0
    
    @classmethod
    def craftable(cls): 
        return cls.recipe is not None
    
    @classmethod
    def add_obtainments(cls, obtainments): 
        if cls.recipe is not None: 
            obtainments.append('Craftable') 

        if cls.gatherable(): 
            levels_str = format_iterable(cls.gatherable_in()) 

            obtainments.append('Can be gathered in {}'.format(levels_str)) 
        
        if cls.droppable(): 
            creatures_str = format_iterable(cls.dropped_by()) 

            obtainments.append('Dropped by {} upon death'.format(creatures_str)) 
    
    @classmethod
    def add_effects(cls, effects): 
        pass
    
    async def auto_amount(self, report): 
        return 1

    async def on_shutdown(self, report, amount):
        pass

    async def on_turn_on(self, report, amount):
        pass

    @classmethod
    def help_embed(cls):
        embed = discord.Embed(title=cls.name, type='rich', description=cls.description) 

        obtainments = list(cls.obtainments) 
        effects = list(cls.effects) 
        
        cls.add_obtainments(obtainments) 
        cls.add_effects(effects) 

        obtainments_str = make_list(obtainments) 
        effects_str = make_list(effects) 
        usages_str = make_list(cls.usages) 
        crafts_str = make_list(cls.crafts()) 
        specials_str = make_list(cls.specials) 

        recipe_gen = ('{} x{}'.format(item.name, amount) for item, amount in (cls.recipe if cls.recipe is not None else ()))  
        recipe_str = make_list(recipe_gen) 

        embed.add_field(name='Ways to obtain', value=obtainments_str if len(obtainments_str) > 0 else 'Not obtainable', inline=False) 
        embed.add_field(name='Effects when received', value=effects_str if len(effects_str) > 0 else 'No effects', inline=False) 
        embed.add_field(name='Effects on use', value=usages_str if len(usages_str) > 0 else 'Not usable', inline=False) 
        embed.add_field(name='Used to craft', value=crafts_str if len(crafts_str) > 0 else 'Nothing', inline=False) 
        embed.add_field(name='Specials', value=specials_str if len(specials_str) > 0 else None, inline=False) 
        embed.add_field(name='Recipe', value=recipe_str if len(recipe_str) > 0 else 'Not craftable', inline=False) 
        embed.add_field(name='Stacks with itself', value=cls.can_stack) 

        return embed

    # noinspection PyTypeChecker
    def stats_embed(self):
        embed = self.help_embed()

        embed.add_field(name='Owner', value=self.owner.name)
        embed.add_field(name='Currently usable', value=self.usable)

        return embed

    async def on_game_turn_start(self, report, amount):
        pass

    async def on_game_turn_end(self, report, amount):
        pass

    async def on_battle_start(self, report, amount):
        pass

    async def on_battle_end(self, report, amount):
        pass

    async def on_battle_round_start(self, report, amount):
        pass

    async def on_battle_round_end(self, report, amount):
        pass

    async def on_first_hit(self, report, amount):
        pass

    async def on_win_coinflip(self, report, amount):
        pass
    
    async def on_move_levels(self, report, amount, move_by): 
        pass

    async def apply_bonuses(self, report, amount):
        pass

    # this is like the inverse of apply_bonuses()
    # returns whether the target died
    async def remove_bonuses(self, report, amount): 
        pass

    async def on_use(self, report, amount): 
        pass
    
    async def can_use(self, report, amount): 
        return True
    
    async def attempt_use(self, report, amount): 
        if await self.can_use(report, amount): 
            await self.on_use(report, amount) 

class Mineable(Item, append=False): 
    mining_rules = '' 
    
    @classmethod
    def mineable_in(cls): 
        return tuple((level.name for level in levels if cls in level.mineables)) 
    
    @classmethod
    def add_obtainments(cls, obtainments): 
        super(Mineable, cls).add_obtainments(obtainments) 
        
        mineable_in_str = format_iterable(cls.mineable_in()) 
        
        obtainments.append('Mineable in {}'.format(mineable_in_str)) 
    
    @classmethod
    def help_embed(cls): 
        embed = super(Mineable, cls).help_embed() 
        
        embed.add_field(name='Rules for mining {}'.format(cls.name), value=cls.mining_rules) 
        
        return embed
    
    @classmethod
    async def on_successful_mine(cls, report, miner): 
        report.add(f'{miner.name} found {cls.name}! ') 
        
        reward = miner.current_level.mineables[cls] 
        
        await miner.earn_items(report, ((cls, reward),)) 
    
    @classmethod
    async def get_mined(cls, report, miner, side): 
        pass

class Armor(Item, append=False): 
    hp_bonus = 0
    
    async def on_shutdown(self, report, amount): 
        if amount > 0: 
            hp_decrease = self.hp_bonus * self.owner.hp_multiplier

            self.owner.base_hp -= hp_decrease
            self.owner.current_hp -= hp_decrease
            self.owner.max_hp -= hp_decrease
    
    async def on_turn_on(self, report, amount): 
        if amount > 0: 
            hp_increase = self.hp_bonus * self.owner.hp_multiplier

            self.owner.base_hp += hp_increase
            self.owner.current_hp += hp_increase
            self.owner.max_hp += hp_increase
    
    @classmethod
    def add_effects(cls, effects): 
        super(Armor, cls).add_effects(effects) 
        
        effects.append(f'Increases the player\'s base, current, and max HP by {cls.hp_bonus} (affected by "HP Multiplier" stat) ')  
    
    async def apply_bonuses(self, report, amount):
        hp_increase = self.hp_bonus * self.owner.hp_multiplier

        self.owner.base_hp += hp_increase
        self.owner.current_hp += hp_increase
        self.owner.max_hp += hp_increase

        report.add("{}'s base, current, and max HP increased by {}! ".format(self.owner.name, hp_increase))

        await self.owner.hp_changed(report) 
    
    async def remove_bonuses(self, report, amount):
        hp_decrease = self.hp_bonus * self.owner.hp_multiplier

        self.owner.base_hp -= hp_decrease
        self.owner.current_hp -= hp_decrease
        self.owner.max_hp -= hp_decrease

        report.add("{}'s base, current, and max HP decreased by {}! ".format(self.owner.name, hp_decrease))

        await self.owner.hp_changed(report) 

class Weapon(Item, append=False): 
    attack_bonus = 0

    async def on_shutdown(self, report, amount):
        if amount > 0: 
            attack_decrease = self.attack_bonus * self.owner.attack_multiplier

            self.owner.base_attack -= attack_decrease
            self.owner.current_attack -= attack_decrease

    async def on_turn_on(self, report, amount):
        if amount > 0: 
            attack_increase = self.attack_bonus * self.owner.attack_multiplier

            self.owner.base_attack += attack_increase
            self.owner.current_attack += attack_increase
    
    @classmethod
    def add_effects(cls, effects): 
        super(Weapon, cls).add_effects(effects) 
        
        effects.append(f'Increases the player\'s base and current attack damage by {cls.attack_bonus} (affected by "Attack Damage Multiplier" stat) ') 

    async def apply_bonuses(self, report, amount): 
        attack_increase = self.attack_bonus * self.owner.attack_multiplier

        self.owner.base_attack += attack_increase
        self.owner.current_attack += attack_increase

        report.add("{}'s base and current attack increased by {}! ".format(self.owner.name, attack_increase)) 

        await self.owner.attack_changed(report)

    async def remove_bonuses(self, report, amount): 
        attack_decrease = self.attack_bonus * self.owner.attack_multiplier

        self.owner.base_attack -= attack_decrease
        self.owner.current_attack -= attack_decrease

        report.add("{}'s base and current attack decreased by {}! ".format(self.owner.name, attack_decrease)) 

        await self.owner.attack_changed(report) 

class Shield(Item, append=False): 
    shield_bonus = 0
    watt_cost = 0
    
    async def on_shutdown(self, report, amount): 
        if amount > 0: 
            self.owner.base_shield -= self.shield_bonus
            self.owner.current_shield -= self.shield_bonus
            self.owner.max_shield -= self.shield_bonus
    
    async def on_turn_on(self, report, amount): 
        if amount > 0: 
            self.owner.base_shield += self.shield_bonus
            self.owner.current_shield += self.shield_bonus
            self.owner.max_shield += self.shield_bonus
    
    @classmethod
    def add_effects(cls, effects): 
        super(Shield, cls).add_effects(effects) 
        
        effects.append(f"Increases the player's base, current, and max shield by {cls.shield_bonus}") 
    
    @classmethod
    def help_embed(cls): 
        embed = super(Shield, cls).help_embed() 
        
        embed.add_field(name='Cost to regen', value=f'{cls.watt_cost} {Watt.name}s') 
        
        return embed
    
    async def apply_bonuses(self, report, amount): 
        self.owner.base_shield += self.shield_bonus
        self.owner.current_shield += self.shield_bonus
        self.owner.max_shield += self.shield_bonus
        
        report.add(f"{self.owner.name}'s base, current, and max shield increased by {self.shield_bonus}! ") 
        
        await self.owner.shield_changed(report) 
    
    async def remove_bonuses(self, report, amount): 
        self.owner.base_shield -= self.shield_bonus
        self.owner.current_shield -= self.shield_bonus
        self.owner.max_shield -= self.shield_bonus
        
        report.add(f"{self.owner.name}'s base, current, and max shield decreased by {self.shield_bonus}! ") 
        
        await self.owner.shield_changed(report) 

class Multiplier(Item, append=False): 
    multipliers_bonus = {} 
    
    async def on_shutdown(self, report, amount):
        if amount > 0:
            for item, multiplier in self.multipliers_bonus.items():
                self.owner.multipliers[item] /= multiplier

    async def on_turn_on(self, report, amount):
        if amount > 0:
            for item, multiplier in self.multipliers_bonus.items():
                if item in self.owner.multipliers:
                    self.owner.multipliers[item] *= multiplier
                else:
                    self.owner.multipliers[item] = multiplier
    
    @classmethod
    def bonus_str(cls): 
        bonus_str = format_iterable(cls.multipliers_bonus.items(), formatter='x{0[1]} {0[0].name}') 
        
        return bonus_str
    
    @classmethod
    def add_effects(cls, effects): 
        super(Multiplier, cls).add_effects(effects) 
        
        effects.append(f'Gives the player {cls.bonus_str()}') 

    async def apply_bonuses(self, report, amount):
        for item, multiplier in self.multipliers_bonus.items():
            if item in self.owner.multipliers:
                self.owner.multipliers[item] *= multiplier
            else:
                self.owner.multipliers[item] = multiplier

        report.add(f'{self.owner.name} now receives {self.bonus_str()}! ')

    async def remove_bonuses(self, report, amount):
        for item, multiplier in self.multipliers_bonus.items():
            self.owner.multipliers[item] /= multiplier

        report.add(f'{self.owner.name} no longer receives {self.bonus_str()}. ') 

class Meat(Item):
    hp_regen = 10

    name = 'Meat'
    description = 'I seafood' 
    obtainments = ('Attacks from Toxic Waste can be converted to Meat via the Bio-Wheel',) 
    usages = ('Regens {} HP per piece to the player/pet it was used on'.format(hp_regen),
              'Using it on a pet with full HP will instead regen its shield, for {} shield per piece'.format(hp_regen)) 
    is_usable = True

    async def auto_amount(self, report): 
        if self.owner.current_hp < self.owner.max_hp: 
            hp_deficit = self.owner.max_hp - self.owner.current_hp

            return math.ceil(hp_deficit / self.hp_regen) 
        else: 
            report.add("{} can't auto-use {} right now because they're at full HP. ".format(self.owner.name, self.name)) 

    async def on_use(self, report, amount): 
        final_hp_regen = self.hp_regen * amount

        self.owner.current_hp += final_hp_regen

        report.add("{}'s current HP increased by {}! ".format(self.owner.name, final_hp_regen)) 

        await self.owner.hp_changed(report) 

        if self.owner.is_a(Player): 
            await self.owner.lose_items(report, ((self, amount),)) 
    
    '''
    async def can_use(self, report, amount): 
        if self.owner.current_hp < self.owner.max_hp: 
            return True
        else: 
            report.add('{} is already at full HP. '.format(self.owner.name)) 
    ''' 

class Suit(Armor): 
    hp_bonus = 50
    oxygen_bonus = 1
    access_levels_bonus = (Levels.Middle,) 
    
    levels_str = format_iterable(access_levels_bonus, formatter='{.name}') 

    name = 'Suit'
    description = 'Shell we try it on? ' 
    effects = ('Protects the wearer from pressure damage in the {}'.format(levels_str), 
                "Increases the wearer's current and max oxygen by {}".format(oxygen_bonus)) 

    async def on_shutdown(self, report, amount): 
        await Armor.on_shutdown(self, report, amount) 
        
        if amount > 0: 
            self.owner.current_oxygen -= self.oxygen_bonus
            self.owner.max_oxygen -= self.oxygen_bonus
            
            self.owner.access_levels = subtract_lists(self.owner.access_levels, self.access_levels_bonus) 

    async def on_turn_on(self, report, amount): 
        await Armor.on_turn_on(self, report, amount) 
        
        if amount > 0: 
            self.owner.current_oxygen += self.oxygen_bonus
            self.owner.max_oxygen += self.oxygen_bonus
            
            self.owner.access_levels.extend(self.access_levels_bonus) 

    async def apply_bonuses(self, report, amount): 
        await Armor.apply_bonuses(self, report, amount) 
        
        self.owner.access_levels.extend(self.access_levels_bonus) 
        
        report.add('{} now protects {} from pressure damage in the {}! '.format(self.name, self.owner.name, self.levels_str)) 

        self.owner.current_oxygen += self.oxygen_bonus
        self.owner.max_oxygen += self.oxygen_bonus

        report.add("{}'s current and max oxygen increased by {}! ".format(self.owner.name, self.oxygen_bonus)) 

        await self.owner.oxygen_changed(report) 

    async def remove_bonuses(self, report, amount): 
        await Armor.remove_bonuses(self, report, amount) 
        
        self.owner.access_levels = subtract_lists(self.owner.access_levels, self.access_levels_bonus) 
        
        report.add("{} no longer has {}'s protection from pressure damage in the {}. ".format(self.owner.name, self.name, self.levels_str)) 

        self.owner.current_oxygen -= self.oxygen_bonus
        self.owner.max_oxygen -= self.oxygen_bonus

        report.add("{}'s current and max oxygen decreased by {}! ".format(self.owner.name, self.oxygen_bonus)) 

        await self.owner.oxygen_changed(report) 

class Coral(Item): 
    name = 'Coral'
    description = 'Great building material for some reason' 

class Scale(Item):
    name = 'Scale'
    description = 'Extremely durable and hard to deform' 

class Sky_Blade(Item):
    name = 'Sky Blade'
    description = "Really light but also quite sharp and durable" 

class Hatchet_Fish_Corpse(Item):
    name = 'Hatchet Fish Corpse'
    description = 'Very hard skeleton' 


class Fishing_Net(Item):
    name = 'Fishing Net'
    description = "Can catch basically anything if you're skilled enough"
    obtainments = ('Fisherman starts out with one',) 
    specials = ('Required to catch pets',) 

class Wood(Item): 
    name = 'Wood' 
    description = f"Why is this in the {Levels.Middle.name}? **{name}**n't it float to the {Levels.Surface.name}? " 

class Middle_Mineable(Mineable, append=False): 
    coin_flips = None
    mining_rules = "When mining for {0}, flip a coin {1} times. If all flips turn up the same, the mining is successful and you get {0}. However, " \
                   "if the result of the first flip doesn't match the side you called when mining, you get surprise attacked by a Stonefish immediately " \
                   "afterwards, regardless of whether your mining attempt was successful or not! "

    @classmethod
    async def get_mined(cls, report, miner, side):
        results = []

        for i in range(cls.coin_flips):
            result = Die.flip_coin()

            report.add(f'Flip {i + 1} was {result}! ')

            results.append(result)

        flip_1 = results[0]

        if results.count(flip_1) == len(results):
            await cls.on_successful_mine(report, miner)
        else:
            report.add(f'{miner.name} failed to get {cls.name}. ')

        if side.lower() != flip_1:
            report.add(f'Due to losing the first flip, {miner.name} is surprise attacked by a {C_Stonefish.name}! ') 
            
            to_fight = C_Stonefish(miner.client, miner.channel, miner, current_level=miner.current_level) 
            
            await miner.start_battle(report, to_fight, surprise_attack=True) 
        else: 
            report.add(f'{miner.name} evaded being surprise attacked by a {C_Stonefish.name}. ') 

class Iron(Middle_Mineable): 
    coin_flips = 2
    
    name = 'Iron' 
    description = 'Much useful' 
    mining_rules = Middle_Mineable.mining_rules.format(name, coin_flips) 

class Steel(Middle_Mineable): 
    coin_flips = 3
    
    name = 'Steel' 
    description = f'Much harder to **{name}** than {Iron.name}'
    mining_rules = Middle_Mineable.mining_rules.format(name, coin_flips) 

class Blubber(Item): 
    name = 'Blubber' 
    description = 'Fat' 

class Platinum_Elixir(Item): 
    name = 'Platinum Elixir' 
    description = 'Good source of platinum' 

class Marlin_Sword(Weapon): 
    attack_bonus = 20

    name = 'Marlin Sword' 
    description = 'Poke' 

class Shovelnose(Item): 
    name = 'Shovelnose' 
    description = 'Noses 4 shovels' 

class Slime_Coat(Item): 
    name = 'Slime Coat' 
    description = 'Poison begone' 
    effects = ('Protects the wearer from most forms of poison damage',) 

class Watt(Item): 
    name = 'Watt' 
    description = '**Watt** is this for' 
    obtainments = ('Generated by Generator',) 
    specials = ('Used for regenerating shields',) 

class Pufferfish_Corpse(Item): 
    name = 'Pufferfish Corpse' 
    description = 'Puffy' 

class Lamp(Item): 
    name = 'Lamp' 
    description = 'Lights the way' 
    effects = ("Decreases the player's surprise attack chance by 1 in all levels past the Middle",) 
    recipe = (Watt, 20), (Wood, 3) 

class Platinum_Juice(Item): 
    per_round_regen = 40

    name = 'Platinum Juice' 
    description = 'Juicy' 
    usages = ('Each one used heals the player by {} HP every battle round, for 1 battle'.format(per_round_regen),) 
    recipe = (Platinum_Elixir, 1), (Meat, 4), (Coral, 10) 
    is_usable = True

    def __init__(self, client, channel, owner): 
        self.used = 0

        Item.__init__(self, client, channel, owner) 
    
    async def on_battle_round_start(self, report, amount): 
        if self.used > 0: 
            to_regen = self.per_round_regen * self.used

            self.owner.current_hp += to_regen

            report.add("{}'s current HP increased by {}! ".format(self.owner.name, to_regen)) 

            await self.owner.hp_changed(report) 
    
    async def on_battle_end(self, report, amount): 
        if self.used > 0: 
            self.used = 0

            report.add("{}'s {}(s) have now worn off. ".format(self.owner.name, self.name)) 
    
    async def on_use(self, report, amount): 
        self.used += amount

        report.add('{} now has {} {}(s) active. '.format(self.owner.name, self.used, self.name)) 

        if self.owner.is_a(Player): 
            await self.owner.lose_items(report, ((self, amount),)) 

class Shovel(Item): 
    name = 'Shovel' 
    description = 'Works' 
    effects = ('Allows the player to mine',) 
    recipe = (Wood, 1), (Coral, 4) 

class Big_Shovel(Multiplier): 
    multipliers_bonus = {
        Iron: 2, 
        Steel: 2, 
    } 
    
    name = 'Big Shovel' 
    description = 'Just as the name says' 
    effects = Shovel.effects
    recipe = (Shovel, 1), (Shovelnose, 1) 

class Bio_Wheel(Item): 
    converts_to = ((Meat, 4),) 
    
    converts_to_str = format_iterable(converts_to, formatter='{0[1]} {0[0].name}') 
    
    name = 'Bio-Wheel' 
    description = '**Wheel**y useful' 
    effects = (f'Converts attacks from Toxic Waste into {converts_to_str}',) 
    recipe = (Coral, 20), (Meat, 5), (Iron, 5), (Wood, 6), (Watt, 10), (Steel, 2) 

class Oxygen_Tank(Item): 
    oxygen_bonus = 3
    
    name = 'Oxygen Tank' 
    description = 'Air' 
    effects = (f"Increases the player's current and max oxygen by {oxygen_bonus}",) 
    recipe = (Pufferfish_Corpse, 2), (Iron, 5) 
    
    async def on_shutdown(self, report, amount): 
        self.owner.current_oxygen -= self.oxygen_bonus
        self.owner.max_oxygen -= self.oxygen_bonus
    
    async def on_turn_on(self, report, amount): 
        self.owner.current_oxygen += self.oxygen_bonus
        self.owner.max_oxygen += self.oxygen_bonus
    
    async def apply_bonuses(self, report, amount): 
        self.owner.current_oxygen += self.oxygen_bonus
        self.owner.max_oxygen += self.oxygen_bonus
        
        report.add(f"{self.owner.name}'s current and max oxygen increased by {self.oxygen_bonus}! ") 
        
        await self.owner.oxygen_changed(report) 
    
    async def remove_bonuses(self, report, amount): 
        self.owner.current_oxygen -= self.oxygen_bonus
        self.owner.max_oxygen -= self.oxygen_bonus
        
        report.add(f"{self.owner.name}'s current and max oxygen decreased by {self.oxygen_bonus}! ") 
        
        await self.owner.oxygen_changed(report) 

class Generator(Item): 
    watts = 5
    
    name = 'Generator' 
    description = f'**{Watt.name}** a useful tool! ' 
    effects = (f'Gives the player {watts} {Watt.name}s every time they change levels',) 
    recipe = (Watt, 10), (Iron, 5), (Coral, 5) 
    
    async def on_move_levels(self, report, amount, move_by): 
        if amount > 0: 
            watts_generated = self.watts * abs(move_by) 
            
            report.add(f"{self.owner.name}'s {self.name} generated {watts_generated} {Watt.name}s! ") 
            
            await self.owner.earn_items(report, ((Watt, watts_generated),)) 

class Bio_Reactor(Item): 
    watts = 1
    accepts = (Meat, Wood) 
    
    accepts_str = format_iterable(accepts, formatter='{.name}', sep='/') 
    
    name = 'Bio-Reactor' 
    description = f'{Watt.name}s for cheap' 
    usages = (f"Takes a player-specified amount of {accepts_str} (per player's choice) and converts it into {Watt.name}s at a {watts} to 1 ratio",) 
    recipe = (Watt, 10), (Iron, 5), (Wood, 6) 
    is_usable = True
    
    async def can_use(self, report, amount): 
        print('b') 
        
        has_accepts_gen = (self.owner.has_item(item) for item in self.accepts) 
        
        if not any(has_accepts_gen): 
            report.add(f"{self.owner.name} can't use {self.name} because they don't have any {self.accepts_str}. ") 
        else: 
            return True
    
    async def on_use(self, report, amount): 
        print('a') 
        
        acceptable_items = [item.name for item in self.accepts if self.owner.has_item(item)] 
        
        report.add(f'{self.owner.name}, choose the item to use in the {self.name}. ') 
        
        to_burn = await self.client.prompt_for_message(report, self.owner.member_id, choices=acceptable_items, timeout=20) 
        
        if to_burn is None: 
            report.add(f'{self.owner.name} cancelled using their {self.name}. ') 
            
            return
        
        to_burn = ttd_tools.search(items, to_burn) 
        
        inv_item, inv_amount = self.owner.get_inv_entry(to_burn) 
        
        def custom_check(to_check): 
            content = to_check.content
            
            return content.isnumeric() and 0 < int(content) <= inv_amount
        
        report.add(f'{self.owner.name}, choose the amount of {inv_item.name} to use in the {self.name}. This must be a whole number greater than 0 '
                   f'and less than/equal to {inv_amount}. ') 
        
        amount_to_burn = await self.client.prompt_for_message(report, self.owner.member_id, custom_check=custom_check, timeout=20) 
        
        if amount_to_burn is None: 
            report.add(f'{self.owner.name} cancelled using their {self.name}. ') 
            
            return
        
        amount_to_burn = int(amount_to_burn) 
        generated = amount_to_burn * self.watts
        
        await self.owner.lose_items(report, ((inv_item, amount_to_burn),)) 
        await self.owner.earn_items(report, ((Watt, generated),))


class Infinity_Shield(Shield):
    shield_bonus = 10
    watt_cost = 20

    name = 'Infinity Shield'
    description = "No, it doesn't have anything to do with that"
    recipe = (Iron, 6), (Coral, 10), (Steel, 1), (Wood, 4) 

class Platinum_Chestplate(Armor): 
    hp_bonus = 75
    
    name = 'Platinum Chestplate' 
    description = 'Stronk armor' 
    recipe = (Platinum_Elixir, 2), (Iron, 8) 

class Platinum_Helmet(Armor): 
    hp_bonus = 50
    
    name = 'Platinum Helmet' 
    description = 'Semi-stronk armor' 
    recipe = (Platinum_Elixir, 1), (Iron, 8) 

class Platinum_Greaves(Armor): 
    hp_bonus = 25
    
    name = 'Platinum Greaves' 
    description = 'Not very stronk armor' 
    recipe = (Platinum_Elixir, 1), (Iron, 4) 

class Platinum_Boots(Armor): 
    hp_bonus = 50
    
    name = 'Platinum Boots' 
    description = 'Semi-stronk armor #2' 
    recipe = (Platinum_Elixir, 1), (Iron, 8) 

class Sky_Sword(Weapon): 
    attack_bonus = 50
    
    name = 'Sky Sword' 
    description = 'Up, up, and away! ' 
    usages = ('Moves the player up 1 level',) 
    specials = ('Only usable once per game turn', 'Not usable in battle, except by Diver')  
    recipe = (Sky_Blade, 1), (Iron, 6), (Wood, 2) 
    is_usable = True
    
    async def can_use(self, report, amount): 
        if self.owner.enemy is not None and not self.owner.is_a(Diver): 
            report.add(f'{self.owner.name}, only {Diver.name}s can use the {self.name} in battle. ') 
        elif self.owner.enemy is not None and not self.owner.battle_turn: 
            report.add(f'{self.owner.name}, {Diver.name} can only use the {self.name} on their battle turn when fighting. ') 
        else: 
            return True
    
    async def on_use(self, report, amount): 
        success = await self.owner.move_levels(report, 'up') 

        if success: 
            self.usable = False

            report.add(f'{self.owner.name} must wait until their next turn to use their {self.name} again. ')
    
    async def on_game_turn_start(self, report, amount): 
        if amount > 0: 
            self.usable = True
            
            report.add(f'{self.owner.name} can use their {self.name} again! ') 

class Flaming_Platinum_Sword(Weapon): 
    attack_bonus = 50
    per_round_attack_increase = 20
    
    name = 'Flaming Platinum Sword of Ultra Death' 
    description = 'An ultra-deadly flaming platinum sword' 
    specials = (f'Damage increases by {per_round_attack_increase} every battle round (still subject to "Attack Damage Multiplier" stat) ', 'Damage resets to normal at the end of every battle') 
    recipe = (Platinum_Elixir, 4), (Iron, 5) 
    
    def __init__(self, client, channel, owner): 
        self.elapsed_battle_rounds = 0
        
        Weapon.__init__(self, client, channel, owner) 
    
    async def on_shutdown(self, report, amount): 
        await Weapon.on_shutdown(self, report, amount) 
        
        if amount > 0: 
            attack_decrease = self.elapsed_battle_rounds * self.per_round_attack_increase * self.owner.attack_multiplier
            
            self.owner.base_attack -= attack_decrease
            self.owner.current_attack -= attack_decrease
    
    async def on_turn_on(self, report, amount): 
        await Weapon.on_turn_on(self, report, amount) 
        
        if amount > 0: 
            attack_increase = self.elapsed_battle_rounds * self.per_round_attack_increase * self.owner.attack_multiplier
            
            self.owner.base_attack += attack_increase
            self.owner.current_attack += attack_increase
    
    async def remove_bonuses(self, report, amount): 
        attack_decrease = (self.elapsed_battle_rounds * self.per_round_attack_increase + self.attack_bonus) * self.owner.attack_multiplier
        
        self.owner.base_attack -= attack_decrease
        self.owner.current_attack -= attack_decrease
        
        report.add(f"{self.owner.name}'s base and current attack decreased by {attack_decrease}! ") 
        
        await self.owner.attack_changed(report) 
        
        self.elapsed_battle_rounds = 0
    
    async def on_battle_round_start(self, report, amount): 
        if amount > 0: 
            self.elapsed_battle_rounds += 1

            attack_increase = self.per_round_attack_increase * self.owner.attack_multiplier
            
            self.owner.base_attack += attack_increase
            self.owner.current_attack += attack_increase
            
            report.add(f"{self.owner.name}'s {self.name}'s damage increased by {attack_increase}! ") 
            
            await self.owner.attack_changed(report) 
    
    async def on_battle_end(self, report, amount): 
        if amount > 0: 
            attack_decrease = self.elapsed_battle_rounds * self.per_round_attack_increase * self.owner.attack_multiplier
            
            self.owner.base_attack -= attack_decrease
            self.owner.current_attack -= attack_decrease
            
            report.add(f"{self.owner.name}'s {self.name} reset to normal damage. ") 
            report.add(f"{self.owner.name}'s base and current attack decreased by {attack_decrease}! ") 
            
            await self.owner.attack_changed(report) 
            
            self.elapsed_battle_rounds = 0

class Shifting_Armor(Armor): 
    hp_bonus = 70
    
    name = 'Shifting Armor' 
    description = 'Shifty' 
    specials = ('Negates pressure damage for the wearer',) 
    recipe = (Scale, 2), (Iron, 5) 

class Shotgun(Weapon): 
    attack_bonus = 30
    
    name = 'Shotgun' 
    description = 'pew' 
    recipe = (Wood, 2), (Steel, 2) 

class Hatchet(Weapon, Multiplier): 
    attack_bonus = 20
    multipliers_bonus = {
        Wood: 2, 
    } 
    
    name = 'Hatchet' 
    description = f'Not just for chopping {Wood.name}' 
    recipe = (Hatchet_Fish_Corpse, 1), (Iron, 1), (Wood, 1) 
    
    async def on_shutdown(self, report, amount): 
        await Weapon.on_shutdown(self, report, amount) 
        await Multiplier.on_shutdown(self, report, amount) 
    
    async def on_turn_on(self, report, amount): 
        await Weapon.on_turn_on(self, report, amount) 
        await Multiplier.on_turn_on(self, report, amount) 
    
    @classmethod
    def add_effects(cls, effects): 
        super(Hatchet, cls).add_effects(effects) 
    
    async def apply_bonuses(self, report, amount): 
        await Weapon.apply_bonuses(self, report, amount) 
        await Multiplier.apply_bonuses(self, report, amount) 
    
    async def remove_bonuses(self, report, amount): 
        await Weapon.remove_bonuses(self, report, amount) 
        await Multiplier.remove_bonuses(self, report, amount) 

class Vegan_Battle_Axe(Weapon): 
    attack_bonus = 60
    
    name = 'Vegan Battle Axe' 
    description = 'The superior weapon' 
    recipe = (Wood, 10), (Coral, 8), (Iron, 2) 

class Classical_Freeze_Gun(Weapon): 
    attack_bonus = 40
    
    name = 'Classical Freeze Gun' 
    description = 'Classy' 
    recipe = (Platinum_Elixir, 1), (Steel, 5), (Iron, 6) 

class Shark_Skin(Item): 
    name = 'Shark Skin' 
    description = 'Grates to the touch' 

class Shark_Armor(Armor): 
    hp_bonus = 30
    retal_percent = 0.3

    name = 'Shark Skin Armor' 
    description = 'Painful to hit' 
    effects = (f'When wearer is attacked, will deal an extra {retal_percent:.0%} of the damage taken back to the \
attacker',) 
    recipe = (Shark_Skin, 1), (Meat, 20) 

# noinspection PyTypeChecker
class Entity(Events): 
    pd_slope = 20
    per_round_fire_percent = 0.5
    
    name = ''
    description = '' 
    specials = () 
    starting_hp_multiplier = 1
    starting_hp = 0
    starting_shield = 0
    starting_attack = 0
    starting_attack_multiplier = 1
    starting_enemy_attack_multiplier = 1
    starting_miss = 1
    starting_crit = 6
    starting_enemy_miss_bonus = 0
    starting_enemy_crit_bonus = 0
    starting_anti_missed = 0
    starting_anti_critted = 0
    starting_access_levels = ()
    starting_penetrates = ()
    starting_bleeds = () 

    def __init__(self, client, channel, current_level=None): 
        self.hp_multiplier = self.starting_hp_multiplier
        self.attack_multiplier = self.starting_attack_multiplier
        self.base_hp = self.current_hp = self.max_hp = self.starting_hp * self.hp_multiplier
        '''
        self.current_hp = base_hp
        self.max_hp = base_hp
        '''
        self.base_shield = self.current_shield = self.max_shield = self.starting_shield
        '''
        self.current_shield = base_shield
        self.max_shield = base_shield
        '''
        self.base_attack = self.current_attack = self.starting_attack * self.attack_multiplier
        # self.current_attack = base_attack
        self.enemy_attack_multiplier = self.starting_enemy_attack_multiplier
        self.miss = self.starting_miss
        self.crit = self.starting_crit
        self.enemy_miss_bonus = self.starting_enemy_miss_bonus
        self.enemy_crit_bonus = self.starting_enemy_crit_bonus
        self.anti_missed = self.starting_anti_missed
        self.anti_critted = self.starting_anti_critted
        # if your level is not in this, you can still go there, but you will take pressure damage.
        self.access_levels = list(self.starting_access_levels)
        # your attack bypasses these
        self.penetrates = list(self.starting_penetrates)
        # your attack "bleeds" these (overkill is not wasted but rather is dealt to another entity)
        self.bleeds = list(self.starting_bleeds)
        # self.death_restore = copy.deepcopy(self)
        self.current_level = current_level

        self.stun_level = 0
        self.fire_damage = 0
        self.electric_damage = 0

        self.current_actions = 0
        self.dead = False

        Events.__init__(self, client, channel) 
    
    @staticmethod
    def modify_deconstructed(deconstructed): 
        deconstructed['access_levels'] = [level.value for level in deconstructed['access_levels']] 
        deconstructed['current_level'] = deconstructed['current_level'].value
        
        Events.modify_deconstructed(deconstructed) 
    
    def reconstruct_next(self): 
        self.access_levels = [Levels(value) for value in self.access_levels] 
        self.current_level = Levels(self.current_level) 

        Events.reconstruct_next(self) 
    
    def acting(self, report): 
        _report = report

        class Acting: 
            entity = self
            report = _report

            async def __aenter__(self): 
                self.entity.current_actions += 1

                print('{} is now running {} actions'.format(self.entity.name, self.entity.current_actions)) 
            
            async def __aexit__(self, typ, value, traceback): 
                self.entity.current_actions -= 1

                print('{} is now running {} actions'.format(self.entity.name, self.entity.current_actions)) 

                if self.entity.current_actions == 0: 
                    if self.entity.dead: 
                        await self.entity.die(self.report) 
        
        return Acting() 
    
    def stunned(self): 
        class Stunned: 
            entity = self

            def __enter__(self): 
                self.entity.stun_level += 1
            
            def __exit__(self, typ, value, traceback): 
                self.entity.stun_level -= 1
        
        return Stunned() 

    # noinspection PyUnreachableCode
    def final_miss(self, enemy):
        return self.miss + enemy.enemy_miss_bonus

    # noinspection PyUnreachableCode
    def final_crit(self, enemy):
        return self.crit - enemy.enemy_crit_bonus
    
    @action
    async def on_shutdown(self, report): 
        await self.change_hp_multiplier(None, 1, self.starting_hp_multiplier, updating=True) 
        await self.change_attack_multiplier(None, 1, self.starting_attack_multiplier) 

        hp_decrease = self.starting_hp * self.hp_multiplier
        attack_decrease = self.starting_attack * self.attack_multiplier

        self.base_hp -= hp_decrease
        self.current_hp -= hp_decrease
        self.max_hp -= hp_decrease
        self.base_shield -= self.starting_shield
        self.current_shield -= self.starting_shield
        self.max_shield -= self.starting_shield
        self.base_attack -= attack_decrease
        self.current_attack -= attack_decrease
        self.enemy_attack_multiplier /= self.starting_enemy_attack_multiplier
        self.miss -= self.starting_miss
        self.crit -= self.starting_crit
        self.enemy_miss_bonus -= self.starting_enemy_miss_bonus
        self.enemy_crit_bonus -= self.starting_enemy_crit_bonus
        self.anti_missed -= self.starting_anti_missed
        self.anti_critted -= self.starting_anti_critted
        self.access_levels = subtract_lists(self.access_levels, self.starting_access_levels)
        self.penetrates = subtract_lists(self.penetrates, self.starting_penetrates)
        self.bleeds = subtract_lists(self.bleeds, self.starting_bleeds) 
    
    @action
    async def on_turn_on(self, report): 
        await self.change_hp_multiplier(None, self.starting_hp_multiplier, updating=True) 
        await self.change_attack_multiplier(None, self.starting_attack_multiplier) 

        hp_increase = self.starting_hp * self.hp_multiplier
        attack_increase = self.starting_attack * self.attack_multiplier

        self.base_hp += hp_increase
        self.current_hp += hp_increase
        self.max_hp += hp_increase

        await self.hp_changed(None) 

        self.base_shield += self.starting_shield
        self.current_shield += self.starting_shield
        self.max_shield += self.starting_shield

        await self.shield_changed(None) 

        self.base_attack += attack_increase
        self.current_attack += attack_increase
        self.enemy_attack_multiplier *= self.starting_enemy_attack_multiplier
        self.miss += self.starting_miss
        self.crit += self.starting_crit
        self.enemy_miss_bonus += self.starting_enemy_miss_bonus
        self.enemy_crit_bonus += self.starting_enemy_crit_bonus
        self.anti_missed += self.starting_anti_missed
        self.anti_critted += self.starting_anti_critted
        self.access_levels.extend(self.starting_access_levels)
        self.penetrates.extend(self.starting_penetrates)
        self.bleeds.extend(self.starting_bleeds) 

        # noinspection PyTypeChecker
    
    @classmethod
    def gen_help_specials(cls, specials): 
        if cls.starting_hp_multiplier != 1: 
            specials.append(f'HP is always multiplied by {cls.starting_hp_multiplier}') 
        
        if cls.starting_attack_multiplier != 1: 
            specials.append(f'Attack damage is always multiplied by {cls.starting_attack_multiplier}') 
        
        if cls.starting_enemy_attack_multiplier != 1: 
            percent = cls.starting_enemy_attack_multiplier - 1

            specials.append(f'Takes {percent:+.0%} damage from enemy attacks') 
        
        if cls.starting_enemy_miss_bonus != 0: 
            specials.append(f'Entities get {cls.starting_enemy_miss_bonus:+} miss chance while \
attacking {cls.name}') 

        if cls.starting_enemy_crit_bonus != 0: 
            specials.append(f'Entities get {cls.starting_enemy_crit_bonus:+} crit chance while \
attacking {cls.name}') 

        if len(cls.starting_penetrates) > 0: 
            penetrates_str = format_iterable(cls.starting_penetrates) 

            specials.append(f'Penetrates {penetrates_str}') 
        
        if len(cls.starting_bleeds) > 0: 
            bleeds_str = format_iterable(cls.starting_bleeds) 

            specials.append(f'Bleeds {bleeds_str}') 
    
    # noinspection PyTypeChecker
    @classmethod
    def help_embed(cls): 
        embed = discord.Embed(title=cls.name, type='rich', description=cls.description) 

        specials = list(cls.specials) 

        cls.gen_help_specials(specials) 

        specials_str = make_list(specials) 
        
        embed.add_field(name='Special abilities', value=specials_str if len(specials_str) > 0 else None, inline=False) 

        embed.add_field(name='HP', value=cls.starting_hp) 
        embed.add_field(name='Shield', value=cls.starting_shield)
        embed.add_field(name='Attack Damage', value=cls.starting_attack) 

        miss_string = format_iterable(range(1, min(cls.starting_miss, 6) + 1))
        crit_string = format_iterable(range(max(cls.starting_crit, 1), 7))

        embed.add_field(name='Misses on', value=miss_string if len(miss_string) > 0 else 'Cannot miss')
        embed.add_field(name='Crits on', value=crit_string if len(crit_string) > 0 else 'Cannot crit') 

        access_levels_string = format_iterable((level.name for level in cls.starting_access_levels)) 

        embed.add_field(name='Can safely access', value=access_levels_string if len(access_levels_string) > 0 else 'nowhere') 

        return embed
    
    def gen_stats_specials(self, specials): 
        if self.starting_hp_multiplier != 1: 
            specials.append(f'HP is always multiplied by {self.starting_hp_multiplier}') 
        
        if self.starting_attack_multiplier != 1: 
            specials.append(f'Attack damage is always multiplied by {self.starting_attack_multiplier}') 
        
        if self.enemy_attack_multiplier != 1: 
            percent = self.enemy_attack_multiplier - 1

            specials.append(f'Takes {percent:+.0%} damage from enemy attacks') 
        
        if self.enemy_miss_bonus != 0: 
            specials.append(f'Entities get {self.enemy_miss_bonus:+} miss chance while \
attacking {self.name}') 

        if self.enemy_crit_bonus != 0: 
            specials.append(f'Entities get {self.enemy_crit_bonus:+} crit chance while \
attacking {self.name}') 

        if len(self.penetrates) > 0: 
            penetrates_str = format_iterable(self.penetrates) 

            specials.append(f'Penetrates {penetrates_str}') 
        
        if len(self.bleeds) > 0: 
            bleeds_str = format_iterable(self.bleeds) 

            specials.append(f'Bleeds {bleeds_str}') 

    def stats_embed(self): 
        embed = discord.Embed(title=self.name, type='rich', description=self.description) 

        embed.add_field(name='Type', value=self.__class__.name) 
        
        specials = list(self.specials) 

        self.gen_stats_specials(specials) 

        specials_str = make_list(specials) 

        embed.add_field(name='Special abilities', value=specials_str if len(specials_str) > 0 else None, inline=False) 

        embed.add_field(name='HP', value='{} / {}'.format(self.current_hp, self.max_hp)) 
        embed.add_field(name='Shield', value='{} / {}'.format(self.current_shield, self.max_shield))
        embed.add_field(name='Attack Damage', value=self.current_attack) 

        miss_string = format_iterable(range(1, min(self.miss, 6) + 1))
        crit_string = format_iterable(range(max(self.crit, 1), 7))

        embed.add_field(name='Misses on', value=miss_string if len(miss_string) > 0 else 'Cannot miss')
        embed.add_field(name='Crits on', value=crit_string if len(crit_string) > 0 else 'Cannot crit') 

        access_levels_string = format_iterable((level.name for level in self.access_levels))

        embed.add_field(name='Current Location', value=self.current_level.name)
        embed.add_field(name='Can safely access', value=access_levels_string if len(access_levels_string) > 0 else 'No levels') 
        
        embed.add_field(name='Attached fire damage', value=self.fire_damage) 
        embed.add_field(name='Attached electric potential damage', value=self.electric_damage) 

        return embed
    
    def level_deviation(self): 
        least_distance = self.current_level.value
        
        for level in set(self.access_levels): 
            distance = self.current_level - level
            
            least_distance = min(distance, least_distance) 
        
        return least_distance
    
    @action
    async def die(self, report): 
        try: 
            await self.on_death(report) 
        finally: 
            self.dead = False
    
    @action
    async def hp_changed(self, report): 
        self.current_hp = min(self.current_hp, self.max_hp) 
        self.current_hp = max(self.current_hp, 0) 
        
        if self.current_hp == 0: 
            self.dead = True
            
        if report is not None: 
            report.add('{} has {}/{} HP now! '.format(self.name, self.current_hp, self.max_hp)) 
    
    @action
    async def change_hp_multiplier(self, report, num, denom=1, updating=False): 
        self.hp_multiplier = self.hp_multiplier * num / denom

        self.base_hp = self.base_hp * num / denom
        self.current_hp = self.current_hp * num / denom
        self.max_hp = self.max_hp * num / denom

        if report is not None: 
            #report.add("{}'s HP multiplier was changed by a factor of {}! ".format(self.name, change_factor)) 
            report.add("{}'s HP multiplier is now x{}! ".format(self.name, self.hp_multiplier)) 
        
        if not updating: 
            await self.hp_changed(report) 
    
    @action
    async def change_attack_multiplier(self, report, num, denom=1): 
        self.attack_multiplier = self.attack_multiplier * num / denom
        
        self.base_attack = self.base_attack * num / denom
        self.current_attack = self.current_attack * num / denom

        if report is not None: 
            #report.add(f"{self.name}'s attack damage multiplier was changed by a factor of {change_factor}! ") 
            report.add(f"{self.name}'s attack damage multiplier is now x{self.attack_multiplier}! ") 

            await self.attack_changed(report) 
    
    @action
    async def shield_changed(self, report): 
        self.current_shield = min(self.current_shield, self.max_shield)
        self.current_shield = max(self.current_shield, 0) 

        if report is not None: 
            report.add('{} has {}/{} shield now! '.format(self.name, self.current_shield, self.max_shield)) 
    
    @action
    async def attack_changed(self, report): 
        report.add('{} has {} attack now! '.format(self.name, self.current_attack)) 

    # the following two are just for being able to output a message in addition to changing HP.
    # commented out for the moment while i think about how to do hp changes
    ''' 
    async def current_hp_decrease(self, decrease_by, inflicter=None): 
      report.add('{} lost {} HP! '.format(self.name, decrease_by)) 
      await self.check_death(-decrease_by, inflicter=inflicter) 
    
    async def current_hp_increase(self, increase_by): 
      report.add('{} gained {} HP! '.format(self.name, increase_by)) 
      await self.check_death(increase_by) 
    ''' 
    
    @action
    async def calculate_shield_bleed(self, report, inflicter, penetrates, bleeds):
        bleed_damage = -self.current_shield

        report.add("{}'s shield bleeds onto HP! ".format(self.name))
        await self.take_damage(report, bleed_damage, inflicter=inflicter, penetrates=penetrates, bleeds=bleeds)

        # intended to be overriden in each of the child classes Player, Pet, and Sub (Creature and Blubber_Base do not bleed and therefore will not override this method) 
    
    @action
    async def calculate_hp_bleed(self, report, inflicter, penetrates, bleeds):
        pass
    
    @action
    async def take_damage(self, report, damage, inflicter=None, penetrates=(), bleeds=(), crit=False): 
        # no point doing any of this if damage is 0
        if damage != 0:
            # if self still has shield, and the attack type does not penetrate shield, the attack strikes their shield
            if self.current_shield > 0 and 'shield' not in penetrates:
                self.current_shield -= damage

                report.add("{}'s shield absorbed {} damage! ".format(self.name, damage)) 

                # calculate shield bleed here
                if self.current_shield < 0 and 'shield' in bleeds:
                    await self.calculate_shield_bleed(report, inflicter, penetrates, bleeds) 
                
                await self.shield_changed(report) 
                # otherwise, they lose hp instead
            else:
                # Pet and Sub classes are not yet defined, define them
                self.current_hp -= damage

                report.add('{} took {} damage! '.format(self.name, damage)) 

                # calculate bleed damage here. This is not finished yet
                if self.current_hp < 0: 
                    await self.calculate_hp_bleed(report, inflicter, penetrates, bleeds) 
                
                await self.hp_changed(report) 

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
    
    @action
    async def calc_pressure_damage(self, report): 
        deviation = self.level_deviation() 
        
        if deviation > 0: 
            return deviation * self.pd_slope
    
    @action
    async def check_pressure_damage(self, report): 
        damage = await self.calc_pressure_damage(report) 
        
        if damage is not None: 
            report.add('{} takes pressure damage! '.format(self.name)) 
            
            await self.take_damage(report, damage, penetrates=['shield']) 
    
    @action
    async def check_pressure(self, report): 
        if self.current_level not in self.access_levels:
            await self.check_pressure_damage(report) 
    
    @action
    async def deal_damage(self, report, target, damage, crit=False, penetrates=(), bleeds=()): 
        actual_damage = damage * target.enemy_attack_multiplier

        return await target.take_damage(report, actual_damage, inflicter=self, penetrates=penetrates, bleeds=bleeds, crit=crit) 
    
    @action
    async def on_miss(self, report, target):
        if target.is_a(Player) and 'blubber base' not in self.penetrates and target.blubber_base is not None and target.blubber_base.hp > 0: 
            report.add("{} hit {}'s Blubber Base instead! ".format(self.name, target.name)) 
            
            await self.deal_damage(report, target.blubber_base, self.current_attack, penetrates=self.penetrates, bleeds=self.bleeds) 
    
    @action
    async def on_regular_hit(self, report, target): 
        await self.deal_damage(report, target, self.current_attack, penetrates=self.penetrates, bleeds=self.bleeds) 
    
    @action
    async def on_crit(self, report, target): 
        damage = self.current_attack * 2
        
        await self.deal_damage(report, target, damage, crit=True, penetrates=self.penetrates, bleeds=self.bleeds) 
    
    @action
    async def switch_hit(self, report, target): 
        async with target.acting(report): 
            miss = self.final_miss(target)
            crit = self.final_crit(target)
            # here is the attack roll (representing a die roll)
            attack_roll = Die.roll_die()

            report.add('{} rolled a {}! '.format(self.name, attack_roll))

            #can't miss if target is stunned
            if target.anti_missed <= 0 and target.stun_level == 0 and attack_roll <= miss: 
                report.add(f'{self.name} missed! ') 

                await self.on_miss(report, target)
            elif target.anti_critted <= 0 and attack_roll >= crit: 
                report.add(f'{self.name} got a critical hit! ') 

                await self.on_crit(report, target) 
            else: 
                report.add(f'{self.name} got a regular hit! ') 

                await self.on_regular_hit(report, target) 

    # receiver is an object representing the receiver of the items, items is a dict of items to donate, with key-value pairs of item (an Item object): amount
    # i am yet to find out whether custom objects can be dict keys. If there is a bug with items i should look HERE first!
    # REWORK THIS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 

    @action
    async def attack(self, report, defender): 
        async with defender.acting(report): 
            report.add(f'{self.name} attacks! ') 
            
            if defender.is_a(Player):
                # if defender is a Player, has a living pet, and the entity does not ignore the pet
                if 'pet' not in self.penetrates and defender.pet is not None and not defender.pet.dead:
                    # reaction_member = self.channel.guild.get_member(defender.member_id)
                    report.add('{0}, will your pet take the hit? React with {1} for yes and {1} for no. This defaults to {2} if you do not respond after 20 seconds. '.format(defender.name, thumbs_up_emoji, thumbs_down_emoji))

                    reaction_emoji = await self.client.prompt_for_reaction(report, defender.member_id, emojis=(thumbs_up_emoji, thumbs_down_emoji), timeout=20, default_emoji=thumbs_down_emoji)

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

                    # if for some reason the pet still exists and is alive after this prompt
                    if reaction_emoji == thumbs_up_emoji and defender.pet is not None and not defender.pet.dead:
                        target = defender.pet
                    elif 'sub' not in self.penetrates and defender.sub is not None and not defender.sub.dead and defender.sub.active:
                        target = defender.sub
                    else:
                        target = defender

                # if the player is still the target but they have a living sub and self does not ignore subs
                elif 'sub' not in self.penetrates and defender.sub is not None and not defender.sub.dead and defender.sub.active:
                    target = defender.sub
                else:
                    target = defender
            else:
                target = defender

            await self.switch_hit(report, target) 
    
    @action
    async def take_fire_damage(self, report): 
        ceiled_damage = math.ceil(self.fire_damage * self.per_round_fire_percent)
        fire_damage = min(ceiled_damage, self.fire_damage) 
        
        report.add(f'{self.name} takes {self.per_round_fire_percent:.0%} of their built-up fire damage! ') 
        
        await self.take_damage(report, fire_damage, penetrates=('shield',)) 
        
        self.fire_damage -= fire_damage
        
        report.add(f'{self.name} now has {self.fire_damage} fire damage remaining. ') 
    
    @action
    async def check_fire(self, report): 
        if self.fire_damage > 0: 
            await self.take_fire_damage(report) 
    
    @action
    async def get_burned(self, report, fire_damage): 
        self.fire_damage += fire_damage
        
        report.add(f'{self.name} was applied {fire_damage} fire damage! ') 
        report.add(f'{self.name} now has {self.fire_damage} fire damage. ') 
    
    @action
    async def on_death(self, report):
        report.add('{} died! '.format(self.name))

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
        self.enemy_miss_bonus = copy.deepcopy(self.death_restore.enemy_miss_bonus) 
        self.enemy_crit_bonus = copy.deepcopy(self.death_restore.enemy_crit_bonus) 
        self.scaling_factor = self.death_restore.scaling_factor
        self.access_levels = copy.deepcopy(self.death_restore.access_levels) 
        self.penetrates = copy.deepcopy(self.death_restore.penetrates) 
        self.bleeds = copy.deepcopy(self.death_restore.bleeds) 
        ''' 
    
    @action
    async def on_battle_round_start(self, report): 
        await self.check_pressure(report) 
        await self.check_fire(report) 
    
    @action
    async def on_move_levels(self, report, move_by): 
        self.current_level += move_by

        report.add('{} is now in the {}! '.format(self.name, self.current_level.name)) 

    ''' async def give_items(self, receiver, items_to_give): 
      total_to_give = {} 
      
      for item, amount in items_to_give.items(): 
        to_receive = amount
        if All in receiver.multipliers: 
            to_receive *= receiver.multipliers[All] 
        elif item in receiver.multipliers: 
            to_receive *= receiver.multipliers[item] 
        total_to_give.update({item: to_receive}) 
      
      receiver.receive_items(total_to_give) '''

    # def on_death(self, killer):


# might not be needing this anymore, gonna save for if i do later
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

class Commander(Entity): 
    starting_priority = 0

    def __init__(self, client, channel, enemy=None, current_level=None): 
        self.priority = self.starting_priority
        self.enemy = enemy
        self.battle_turn = False

        Entity.__init__(self, client, channel, current_level=current_level) 
    
    @action
    async def on_shutdown(self, report): 
        await Entity.on_shutdown(self, report) 

        self.priority -= self.starting_priority
    
    @action
    async def on_turn_on(self, report): 
        await Entity.on_turn_on(self, report) 

        self.priority += self.starting_priority
    
    @classmethod
    def help_embed(cls): 
        embed = super(Commander, cls).help_embed() 

        embed.add_field(name='Priority', value=cls.starting_priority) 

        return embed
    
    def stats_embed(self): 
        embed = Entity.stats_embed(self) 
        
        embed.add_field(name='Currently fighting against', value=self.enemy.name if self.enemy is not None else None) 
        embed.add_field(name='Battle Turn', value=self.battle_turn)
        embed.add_field(name='Priority', value=self.priority) 

        return embed
    
    @action
    async def start_battle_turn(self, report): 
        self.battle_turn = True

        report.add("It's now {}'s battle turn! ".format(self.name)) 
    
    @action
    async def end_battle_turn(self, report): 
        if self.battle_turn: 
            self.battle_turn = False

            report.add("It's no longer {}'s battle turn. ".format(self.name)) 
            
            await self.on_global_event(report, 'battle_round_end') 
            await self.enemy.on_global_event(report, 'battle_round_end') 
    
    @action
    async def leave_battle(self, report): 
        async with self.enemy.acting(report): 
            opponent = self.enemy
            self.enemy = None
            opponent.enemy = None

            await self.on_global_event(report, 'battle_end') 
            await opponent.on_global_event(report, 'battle_end') 

            report.add('{} and {} are no longer fighting each other. '.format(self.name, opponent.name)) 
    
    @action
    async def on_global_event(self, report, event_name, *args, **kwargs): 
        pass

classes = ttd_tools.Filterable() 

class Player_Meta(ttd_tools.GO_Meta): 
    append_to = classes

# noinspection PyTypeChecker
class Player(Commander, metaclass=Player_Meta, append=False): 
    name_limit = 50
    banned_chars = ('@', '\n') 
    
    def banned_repr_gen(chars): 
        for char in chars: 
            repr_str = repr(char) 
            
            to_yield = repr_str[1:len(repr_str) - 1] 
            
            yield to_yield
    
    banned_str = format_iterable(banned_repr_gen(banned_chars), formatter='`{}`') 
    
    regen_percent = 0.2
    failed_flee_punishment = 2
    oxygen_damage = 100

    '''
    name = ''
    description = 'None'
    specials = ('None',) 
    starting_shield = 0
    starting_enemy_attack_multiplier = 1
    starting_miss = 1
    starting_crit = 6
    starting_enemy_miss_bonus = 0
    starting_enemy_crit_bonus = 0
    starting_penetrates = []
    starting_bleeds = []
    '''

    starting_hp = 100
    starting_attack = 20
    starting_access_levels = (Levels.Surface,) 
    starting_oxygen = 5
    starting_items = () 
    starting_multipliers = {}
    starting_priority = 0

    def __init__(self, client, channel, game, member_id=None): 
        self.game = game
        self.member_id = member_id
        self.mention = '<@{}>'.format(self.member_id) 
        self.current_oxygen = self.starting_oxygen
        self.max_oxygen = self.starting_oxygen
        self.items = [] 
        self.saved_items = [] 
        self.multipliers = copy.deepcopy(self.starting_multipliers) 
        self.sub = None
        self.pet = None
        self.blubber_base = None
        self.o_game_turn = False
        self.uo_game_turn = False
        self.can_move = False

        self.suiciding = False
        # players cannot do anything at all when dead

        Commander.__init__(self, client, channel, current_level=Levels.Surface) 
    
    @staticmethod
    def modify_deconstructed(deconstructed): 
        del deconstructed['game']

        items_copy = [inv_entry.copy() for inv_entry in deconstructed['items']]

        for inv_entry in items_copy:
            inv_entry[0] = inv_entry[0].deconstruct()

        deconstructed['items'] = items_copy
        
        deconstructed['multipliers'] = {item.__name__: amount for item, amount in deconstructed['multipliers'].items()} 

        if deconstructed['pet'] is not None:
            deconstructed['pet'] = deconstructed['pet'].deconstruct()
        if deconstructed['sub'] is not None:
            deconstructed['sub'] = deconstructed['sub'].deconstruct()
        if deconstructed['blubber_base'] is not None:
            deconstructed['blubber_base'] = deconstructed['blubber_base'].deconstruct()

        enemy = deconstructed['enemy']

        if enemy is not None:
            if not (enemy.is_a(Player)):
                deconstructed['enemy'] = enemy.deconstruct()
            else:
                deconstructed['enemy'] = enemy.member_id
        
        Commander.modify_deconstructed(deconstructed) 

    def reconstruct_next(self): 
        for inv_entry in self.items:
            inv_entry[0] = self.reconstruct(inv_entry[0], self.client, self.channel, self) 
        
        self.multipliers = {eval(item_name): amount for item_name, amount in self.multipliers.items()} 

        if self.sub is not None:
            self.sub = self.reconstruct(self.sub, self.client, self.channel, self)
        if self.pet is not None:
            self.pet = self.reconstruct(self.sub, self.client, self.channel, self)
        if self.blubber_base is not None:
            self.blubber_base = self.reconstruct(self.blubber_base, self.client, self.channel, self) 
        
        if type(self.enemy) is dict:
            self.enemy = self.reconstruct(self.enemy, self.client, self.channel, self) 

        Commander.reconstruct_next(self) 
    
    @action
    async def on_shutdown(self, report): 
        await Commander.on_shutdown(self, report) 

        self.current_oxygen -= self.starting_oxygen
        self.max_oxygen -= self.starting_oxygen

        for item_class, bonus in self.starting_multipliers.items(): 
            self.multipliers[item_class] /= bonus
        
        if self.enemy is not None: 
            await self.enemy.on_global_event(report, 'shutdown') 
    
    @action
    async def on_turn_on(self, report): 
        await Commander.on_turn_on(self, report) 

        self.current_oxygen += self.starting_oxygen
        self.max_oxygen += self.starting_oxygen

        await self.oxygen_changed(None) 

        for item_class, bonus in self.starting_multipliers.items(): 
            if item_class in self.multipliers:
                self.multipliers[item_class] *= bonus
            else:
                self.multipliers[item_class] = bonus
        
        if self.enemy is not None: 
            await self.enemy.on_global_event(report, 'turn_on') 
        
        '''
        #corresponding member is no longer in the server
        if self.channel.guild.get_member(self.member_id) is None: 
            self.suiciding = True

            report.add('{} is no longer in this server, so they will now suicide. '.format(self.name)) 
        ''' 

    def get_inv_entry(self, item_class):
        for inv_entry in self.items:
            if inv_entry[0].__class__ is item_class:
                return inv_entry

        return None, 0
    
    def has_item(self, item): 
        inv_entry, inv_amount = self.get_inv_entry(item) 

        return inv_amount > 0

    def lacks_items(self, required_items):
        missing_items = []

        for required_item, required_amount in required_items:
            if type(required_item) is type(Item):
                required_item_class = required_item
            else:
                required_item_class = required_item.__class__

            own_item, own_item_amount = self.get_inv_entry(required_item_class)

            if own_item_amount < required_amount:
                deficit = required_amount - own_item_amount

                missing_items.append((required_item_class, deficit))

        return missing_items
    
    @classmethod
    def gen_help_specials(cls, specials): 
        super(Player, cls).gen_help_specials(specials) 

        if len(cls.starting_multipliers) > 0: 
            multipliers_gen = (f'x{multiplier} {item.name}' for item, multiplier in cls.starting_multipliers.items()) 
            multipliers_str = format_iterable(multipliers_gen) 

            specials.append(f'Receives {multipliers_str} (except from crafting and donating) ') 
        
        if len(cls.starting_items) > 0: 
            items_gen = (f'{amount} {item.name}(s)' for item, amount in cls.starting_items) 
            items_str = format_iterable(items_gen) 

            specials.append(f'Spawns with {items_str}') 

    # noinspection PyTypeChecker
    @classmethod
    def help_embed(cls): 
        embed = super(Player, cls).help_embed() 

        embed.add_field(name='Oxygen', value=cls.starting_oxygen) 

        return embed
    
    def gen_stats_specials(self, specials): 
        Commander.gen_stats_specials(self, specials) 

        if len(self.multipliers) > 0: 
            multipliers_gen = (f'x{multiplier} {item.name}' for item, multiplier in self.multipliers.items()) 
            multipliers_str = format_iterable(multipliers_gen) 

            specials.append(f'Receives {multipliers_str} (except from crafting and donating) ') 

    def stats_embed(self): 
        embed = Commander.stats_embed(self)

        embed.add_field(name='Oxygen', value='{} / {}'.format(self.current_oxygen, self.max_oxygen)) 

        embed.add_field(name='Game Turn', value=self.uo_game_turn)
        embed.add_field(name='Can move', value=self.can_move) 

        embed.add_field(name='User', value=self.mention, inline=False) 

        return embed
    
    @classmethod
    def name_custom_check(cls, content): 
        banned_gen = ((char in content) for char in cls.banned_chars) 

        return len(content) <= cls.name_limit and not any(banned_gen) 
    
    '''
    @acms.asynccontextmanager
    async def acting(self): 
        self.currently_acting = True

        yield

        self.currently_acting = False
    ''' 

    '''
    def acting(self): 
        class Acting: 
            entity = self

            async def __aenter__(self): 
                self.entity.current_actions += 1

                print('{} is now running {} actions'.format(self.entity.name, self.entity.current_actions)) 
            
            async def __aexit__(self, typ, value, traceback): 
                self.entity.current_actions -= 1

                print('{} is now running {} actions'.format(self.entity.name, self.entity.current_actions)) 
        
        return Acting() 
    ''' 

    @classmethod
    async def setname_args_check(cls, client, report, author, name=None): 
        if name is not None and not cls.name_custom_check(name): 
            report.add('{}, argument `name` must not exceed {} characters or contain the following symbols: {}. '.format(author.mention, cls.name_limit, cls.banned_str)) 
        else: 
            return True
    
    @action
    async def take_damage(self, report, damage, inflicter=None, penetrates=(), bleeds=(), crit=False): 
        await Commander.take_damage(self, report, damage, inflicter=inflicter, penetrates=penetrates, bleeds=bleeds, crit=crit) 

        if inflicter is not None and self.has_item(Shark_Armor): 
            report.add(f"{inflicter.name} is hurt by {self.name}'s {Shark_Armor.name}! ") 

            retal_damage = damage * Shark_Armor.retal_percent * inflicter.enemy_attack_multiplier

            await inflicter.take_damage(report, retal_damage) 

    @action
    async def use_move(self, report): 
        if self.can_move: 
            self.can_move = False
    
            report.add("{}'s move is now used up. ".format(self.name)) 
    
    @action
    async def call_and_flip(self, report): 
        report.add('Call the side! ') 

        called_side = await self.client.prompt_for_message(report, self.member_id, choices=('heads', 'tails'), timeout=10, default_choice='heads') 

        actual_side = Die.flip_coin() 

        report.add('{} calls {}! '.format(self.name, called_side)) 
        report.add("It's {}! ".format(actual_side)) 

        return called_side.lower() == actual_side
    
    async def display_items(self, report): 
        def generator(inv): 
            if len(inv) > 0: 
                for item, amount in inv: 
                    yield '{} x {}'.format(item.name, amount) 
            else: 
                yield 'Nothing' 
        
        report.add("{}'s current items: ```{}```".format(self.name, make_list(generator(self.items)))) 
        report.add('Items that will be received after death: ```{}```'.format(make_list(generator(self.saved_items)))) 
    
    @action
    async def take_oxygen_damage(self, report):
        report.add('{} takes oxygen damage! '.format(self.name)) 

        await self.take_damage(report, self.oxygen_damage, penetrates=('shield',)) 
    
    @action
    async def check_current_oxygen(self, report): 
        if self.current_oxygen <= 0: 
            await self.take_oxygen_damage(report) 
    
    @action
    async def oxygen_changed(self, report): 
        self.current_oxygen = max(self.current_oxygen, 0) 

        if report is not None: 
            report.add('{} now has {}/{} oxygen! '.format(self.name, self.current_oxygen, self.max_oxygen)) 
    
    @action
    async def calc_pressure_damage(self, report): 
        deviation = self.level_deviation() 
        
        if deviation > 0: 
            if self.has_item(Shifting_Armor): 
                report.add(f"{self.name}'s {Shifting_Armor.name} negates pressure damage! ") 
            else: 
                return deviation * self.pd_slope
    
    @action
    async def move_levels(self, report, direction): 
        movement = None

        if direction.lower() == 'down': 
            if self.current_level < Levels.Middle: 
                movement = 1
            else: 
                report.add("{} can't move down because they are already in the lowest level. ".format(self.name)) 
        else: 
            if self.current_level > Levels.Surface: 
                movement = -1
            else: 
                report.add("{} can't move up because they are already in the highest level. ".format(self.name)) 
        
        if movement is not None: 
            await self.on_global_event(report, 'move_levels', movement) 

            if self.enemy is not None: 
                report.add('{} drags {} with them! '.format(self.name, self.enemy.name)) 

                await self.enemy.on_global_event(report, 'move_levels', movement) 

            return True
    
    @action
    async def start_battle(self, report, enemy, surprise_attack=False): 
        await self.use_move(report) 

        self.enemy = enemy
        enemy.enemy = self

        async with enemy.acting(report): 
            report.add('{} is now fighting {}! '.format(self.name, enemy.name)) 

            await self.on_global_event(report, 'battle_start') 
            await self.enemy.on_global_event(report, 'battle_start') 

            await self.on_global_event(report, 'battle_round_start') 
            await self.enemy.on_global_event(report, 'battle_round_start') 

            proceed = not self.dead and not self.enemy.dead

            # noinspection PyRedundantParentheses
            if proceed: 
                await self.decide_first(report, surprise_attack) 
    
    @action
    async def check_surprise_attack(self, report): 
        chance = self.current_level.value - 1
        die_roll = Die.roll_die() 

        report.add('{} rolled a {}! '.format(self.name, die_roll)) 

        if die_roll <= chance: 
            report.add('{} is surprise attacked! '.format(self.name)) 

            await self.fight_creature(report, surprise_attack=True) 
        else: 
            report.add('{} is not surprise attacked. '.format(self.name)) 

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
    
    @action
    async def regain_move(self, report): 
        self.can_move = True

        report.add('{} regained their move! '.format(self.name)) 
    
    @action
    async def before_action(self, report):
        # noinspection PyUnusedLocal
        await self.regain_move(report) 

        await self.check_pressure(report) 

        if self.current_level > Levels.Surface: 
            # oxygen loss and possible oxygen damage
            self.current_oxygen -= 1

            report.add('{} lost 1 oxygen! '.format(self.name)) 

            await self.oxygen_changed(report) 

            await self.check_current_oxygen(report) 

            if not self.dead: 
                # surprise attack
                await self.check_surprise_attack(report) 
    
    async def set_name(self, report, name): 
        if name is None: 
            def custom_check(to_check): 
                return self.name_custom_check(to_check.content) 
            
            report.add('Enter your name (it must not exceed {} characters or contain any of the following symbols: {}): '.format(self.name_limit, self.banned_str)) 

            self.name = await self.client.prompt_for_message(report, self.member_id, custom_check=custom_check, timeout=20, default_choice=self.name) 
        else: 
            self.name = name

        report.add('{} successfully set their name to {}. '.format(self.mention, self.name)) 
    
    @action
    async def on_life_start(self, report): 
        await self.set_name(report, None) 

        if self.member_id in self.game.saved_stuff: 
            saved_items = tuple(((eval(item_name), amount) for item_name, amount in self.game.saved_stuff[self.member_id]['saved_items'])) 
            to_receive = self.starting_items + saved_items

            del self.game.saved_stuff[self.member_id] 
        else: 
            to_receive = self.starting_items

        await self.receive_items(report, to_receive) 

        report.add('A wild {} appeared! '.format(self.name)) 
    
    @action
    async def on_game_turn_start(self, report):
        self.uo_game_turn = True
    
    @action
    async def on_game_turn_end(self, report):
        self.uo_game_turn = False
        self.can_move = False
    
    @action
    async def on_battle_start(self, report): 
        if not self.o_game_turn: 
            await self.on_global_event(report, 'game_turn_start') 
    
    @action
    async def on_battle_end(self, report): 
        if not self.o_game_turn: 
            await self.on_global_event(report, 'game_turn_end') 
    
    @action
    async def on_win_coinflip(self, report): 
        await self.start_battle_turn(report) 

        report.add("{}, on your battle turn you can attack or flee. You can also do anything that doesn't require a move. ".format(self.mention)) 
    
    @action
    async def on_move_levels(self, report, move_by): 
        await Commander.on_move_levels(self, report, move_by) 

        if self.current_level is Levels.Surface and self.current_oxygen < self.max_oxygen: 
            self.current_oxygen = self.max_oxygen

            report.add("{}'s oxygen refilled to max! ".format(self.name)) 

            await self.oxygen_changed(report) 
    
    @action
    async def attempt_flee(self, report): 
        async with self.enemy.acting(report): 
            report.add('{} attempts to flee! They are vulnerable! '.format(self.name))

            won_flip = await self.call_and_flip(report)

            if won_flip:
                report.add('{} successfully fled! '.format(self.name)) 

                await self.end_battle_turn(report) 
                await self.leave_battle(report) 
            else: 
                report.add('{} failed to flee! {} can now hit them {} times! '.format(self.name, self.enemy.name, self.failed_flee_punishment)) 

                for time in range(self.failed_flee_punishment): 
                    await self.enemy.switch_attack(report) 
            
                await self.end_battle_turn(report) 
    
    # noinspection PyUnusedLocal,PyUnusedLocal,PyUnusedLocal
    @action
    async def on_global_event(self, report, event_name, *args, **kwargs): 
        if self.pet is not None: 
            await eval('self.pet.on_{}(report, *args, **kwargs) '.format(event_name)) 
        if self.sub is not None: 
            await eval('self.sub.on_{}(report, *args, **kwargs) '.format(event_name)) 
        if self.blubber_base is not None: 
            await eval('self.blubber_base.on_{}(report, *args, **kwargs) '.format(event_name))

        for item, amount in self.items:
            await eval('item.on_{}(report, amount, *args, **kwargs) '.format(event_name)) 
        
        await eval('self.on_{}(report, *args, **kwargs) '.format(event_name)) 

    @action
    async def decide_first(self, report, surprise_attack): 
        if surprise_attack:
            self.enemy.priority += 1

            report.add("{}'s priority is raised by 1 due to having the element of surprise! ".format(self.enemy.name)) 

        if self.priority == self.enemy.priority:
            won_flip = await self.call_and_flip(report)

            if won_flip:
                more_first = self
            else:
                more_first = self.enemy
                
            report.add('{} got first hit due to winning the coin flip! '.format(more_first.name)) 
        else:
            more_first = max(self, self.enemy, key=lambda side: side.priority) 
            
            report.add('{} got first hit due to having the higher priority! '.format(more_first.name)) 

        if more_first.is_a(Creature) and more_first.passive: 
            report.add('{} is passive and flees! '.format(more_first.name)) 

            await more_first.leave_battle(report) 
        else: 
            await more_first.on_global_event(report, 'first_hit')
            await more_first.on_global_event(report, 'win_coinflip') 

    @action
    async def calculate_hp_bleed(self, report, inflicter, penetrates, bleeds):
        if 'player' in bleeds and 'blubber base' not in penetrates and self.blubber_base is not None and self.blubber_base.hp > 0: 
            bleed_damage = -self.current_hp

            report.add('{} bleeds onto their Blubber Base! '.format(self.name))
            await self.blubber_base.take_damage(report, bleed_damage, inflicter=inflicter, penetrates=penetrates, bleeds=bleeds) 
    
    @action
    async def on_death(self, report): 
        self.current_hp = 0

        print(1) 

        await self.hp_changed(None) 

        print(2) 

        report.add('{} died! '.format(self.name)) 

        print(3) 

        if self.enemy is not None: 
            async with self.enemy.acting(report): 
                print(4) 

                await self.end_battle_turn(report) 

                print(5) 
                
                enemy = self.enemy

                await self.leave_battle(report) 

                print(6) 
                
                if enemy.is_a(Player): 
                    await enemy.earn_items(report, self.items) 
                
                print(7) 
        
        print(8) 
        
        saved_items = tuple(((item.__name__, amount) for item, amount in self.saved_items)) 

        self.game.saved_stuff[self.member_id] = {
            'saved_items': saved_items, 
        } 

        print(9) 

        await self.game.remove_player(report, self) 

        print(10) 

        self.suiciding = False

        print(11) 

        '''
        for item_class, amount in self.saved_items:
            item_class().salvage(self, amount) 

        own_index = self.game.players.index(self) 

        if allow_respawn:
            respawn_prompt = report.add(
                content='{}, do you want to respawn? React with {} for yes and {} for no. '.format(self.name, thumbs_up_emoji, thumbs_down_emoji))
            respawn_emoji = await self.client.prompt_for_reaction(respawn_prompt, self.member_id, emojis=(thumbs_up_emoji, thumbs_down_emoji),
                                                                  timeout=20, default_emoji=thumbs_up_emoji)

            allow_respawn = respawn_emoji == thumbs_up_emoji

        if allow_respawn:
            report.add(
                content='{}, choose the class you want to be. This defaults to your current class after 20 seconds. '.format(self.name))
            class_choice = await self.client.prompt_for_message(self.channel, self.member_id,
                                                                custom_check=lambda message: search(classes, message.content) is not None, timeout=20)

            if class_choice is not None:
                chosen_class = search(classes, class_choice)
            else:
                chosen_class = self.__class__

                # the revived self replaces the old self
            new_self = chosen_class(client=self.client, channel=self.channel, name=self.name, member_id=self.member_id, game=self.game)

            print('new self has been created')

            self.game.players[own_index] = new_self

            print('new self has replaced old self')

            # saved items and blubber base are transferred to new self
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
        
        ''' 
    
    @action
    async def suicide(self, report): 
        report.add(f'{self.mention}, suiciding will instantly kill your character. You will lose \
**everything** that you have on you right now. ARE YOU SURE? ') 

        emoji = await self.client.prompt_for_reaction(report, self.member_id, emojis=(thumbs_up_emoji, 
thumbs_down_emoji), timeout=10, default_emoji=thumbs_down_emoji) 

        if emoji == thumbs_up_emoji: 
            self.dead = True

            report.add('{} suicides! '.format(self.name)) 
        else: 
            report.add(f"{self.name} didn't suicide. ") 

    @action
    async def receive_items(self, report, to_receive):
        for item, amount in to_receive:
            if amount > 0:
                first_receival = False

                if type(item) is type(Item):
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

                report.add('{} received {} {}(s)! '.format(self.name, amount, item.name))

                if entry_item.can_stack or first_receival: 
                    await entry_item.apply_bonuses(report, amount) 
                
                report.add('{} now has {} {}(s)! '.format(self.name, receiving_entry[1], receiving_entry[0].name)) 

    @action
    async def earn_items(self, report, to_earn):
        to_receive = []

        for item, amount in to_earn:
            if type(item) is type(Item): 
                item_class = item
            else:
                item_class = item.__class__

            final_amount = amount

            if All in self.multipliers:
                all_multiplier = self.multipliers[All]

                final_amount *= all_multiplier

                report.add('{} receives a x{} multiplier on all items! '.format(self.name, all_multiplier))
            if item_class in self.multipliers:
                item_multiplier = self.multipliers[item_class]

                final_amount *= item_multiplier

                report.add('{} receives a x{} multiplier on {}s! '.format(self.name, item_multiplier, item.name)) 
            
            final_amount = math.ceil(final_amount) 

            to_receive.append([item_class, final_amount])

        await self.receive_items(report, to_receive)

        # forgive_debt means that it you don't have sufficient amounts of an item it will just take what you have.

    @action
    async def lose_items(self, report, to_lose):
        taken_items = []

        for item, amount in to_lose:
            if amount > 0:
                last_removal = False

                if type(item) is type(Item):
                    item_class = item
                else:
                    item_class = item.__class__

                entry_item, entry_amount = losing_entry = self.get_inv_entry(item_class)

                if entry_item is not None:
                    lost_amount = min(entry_amount, amount) 

                    if lost_amount > 0: 
                        losing_entry[1] -= lost_amount

                        taken_items.append([item_class, lost_amount])

                        if losing_entry[1] == 0:
                            last_removal = True
                        
                        report.add('{} lost {} {}(s)! '.format(self.name, lost_amount, entry_item.name)) 

                        if entry_item.can_stack or last_removal: 
                            await entry_item.remove_bonuses(report, amount) 
                        
                        report.add('{} now has {} {}(s)! '.format(self.name, losing_entry[1], entry_item.name)) 

        return taken_items

    @action
    async def craft(self, report, item, amount): 
        item = ttd_tools.search(items, item) 
        amount = int(amount) 

        final_recipe = [(recipe_item, recipe_amount * amount) for recipe_item, recipe_amount in item.recipe] 

        lacking_items = self.lacks_items(final_recipe) 

        if len(lacking_items) == 0: 
            await self.lose_items(report, final_recipe) 
            await self.receive_items(report, ((item, amount),)) 

            await self.use_move(report) 
        else: 
            lacking_str = format_iterable(lacking_items, formatter='{0[1]} {0[0].name}(s)') 

            report.add(f'{self.name} lacks {lacking_str} to craft {amount} {item.name}(s). ') 
    
    @action
    async def donate(self, report, target, to_donate): 
        async with target.acting(report): 
            await self.lose_items(report, to_donate) 
            await target.receive_items(report, to_donate) 

            report.add('{} successfully donated to {}. '.format(self.name, target.name)) 
    
    @action
    async def whitelist_donate(self, report, target, to_donate): 
        final_to_donate = [] 

        for item, amount in to_donate: 
            if type(amount) is str: 
                inv_item, inv_amount = self.get_inv_entry(item) 

                if inv_amount > 0: 
                    actual_amount = inv_amount
                else: 
                    report.add("Skipping {} because {} doesn't have any. ".format(item.name, self.name)) 

                    continue
            else: 
                actual_amount = amount
            
            final_to_donate.append((item, actual_amount)) 
        
        lacking_items = self.lacks_items(final_to_donate) 

        if len(lacking_items) == 0: 
            await self.donate(report, target, final_to_donate) 
        else: 
            lacking_str = format_iterable(lacking_items, formatter='{0[1]} {0[0].name}(s)') 

            report.add(f'{self.name} lacks {lacking_str} to perform the donation. ') 
        
    @action
    async def blacklist_donate(self, report, target, blacklist): 
        final_to_donate = {item.__class__: amount for item, amount in self.items} 

        for item, amount in blacklist.items(): 
            if item in final_to_donate: 
                if type(amount) is str or final_to_donate[item] <= amount: 
                    del final_to_donate[item] 
                else: 
                    final_to_donate[item] -= amount
        
        final_to_donate = {item: amount for item, amount in final_to_donate.items() if amount > 0} 
        
        if len(final_to_donate) > 0: 
            donation_list = [[item, amount] for item, amount in final_to_donate.items()] 

            await self.donate(report, target, donation_list) 

            reproduce_list = [(item.name.replace(' ', '_'), amount) for item, amount in donation_list] 
            reproduce_str = format_iterable(reproduce_list, formatter='{0[0]} {0[1]}', sep=' ') 

            report.add(f'The items list to reproduce this donation is `{reproduce_str}`. ') 
        else: 
            report.add(f'There is nothing to donate. ') 
    
    @action
    async def switch_attack(self, report): 
        print('{} is now attacking {}'.format(self.name, self.enemy.name)) 

        async with self.enemy.acting(report): 
            await self.attack(report, self.enemy) 

            await self.end_battle_turn(report) 
    
    @action
    async def fight_creature(self, report, surprise_attack=False): 
        creature = await self.current_level.select_creature() 

        #print(creature.__init__) 

        to_fight = creature(self.client, self.channel, self, current_level=self.current_level) 

        print('{} is now starting battle with {}'.format(self.name, to_fight.name)) 
        
        await self.start_battle(report, to_fight, surprise_attack=surprise_attack) 
    
    @action
    async def gather(self, report, to_gather): 
        item = ttd_tools.search(items, to_gather) 

        if item in self.current_level.gatherables: 
            flip_1 = Die.flip_coin() 

            report.add('The first flip was {}! '.format(flip_1)) 

            flip_2 = Die.flip_coin() 

            report.add('The second flip was {}! '.format(flip_2)) 

            if flip_1 != flip_2: 
                report.add('{} found {}! '.format(self.name, item.name)) 

                await self.earn_items(report, ((item, self.current_level.gatherables[item]),)) 
            else: 
                report.add('{} did not find any {}'.format(self.name, item.name)) 
            
            await self.use_move(report) 
        else: 
            report.add("{} is not gatherable in {}'s current level, the {}".format(item.name, self.name, self.current_level.name)) 
    
    @action
    async def mine(self, report, to_mine, side): 
        if to_mine in self.current_level.mineables: 
            await to_mine.get_mined(report, self, side) 
            
            await self.use_move(report) 
        else: 
            report.add(f"{to_mine.name} is not mineable in {self.name}'s current level, the {self.current_level.name}. ") 
    
    @action
    async def end_turn(self, report): 
        proceed = not self.can_move

        if not proceed: 
            report.add(f'{self.name}, you have not used your move yet! Do you still want to end your turn \
early? ') 

            emoji = await self.client.prompt_for_reaction(report, self.member_id, emojis=(thumbs_up_emoji, 
    thumbs_down_emoji), timeout=10, default_emoji=thumbs_down_emoji) 

            proceed = emoji == thumbs_up_emoji

        if proceed: 
            await self.game.next_turn(report) 
        else: 
            report.add(f"{self.name} didn't end their turn early. ") 
    
    @action
    async def invite_members(self, report, members): 
        for member in members: 
            await self.game.add_member(report, member) 
    
    @action
    async def start_game(self, report): 
        await self.game.start(report) 
    
    @action
    async def use_item(self, report, item, amount): 
        target_item = ttd_tools.search(items, item) 
        
        inv_item, inv_amount = self.get_inv_entry(target_item) 

        if amount.lower() == 'auto': 
            if inv_amount > 0: 
                auto_amount = await inv_item.auto_amount(report) 

                if auto_amount is not None: 
                    to_use = min(auto_amount, inv_amount) 
                else: 
                    return
            else: 
                report.add("{} can't auto-use {} because they don't have any. ".format(self.name, target_item.name)) 

                return
        else: 
            to_use = int(amount) 
        
        if inv_amount >= to_use: 
            if inv_item.usable: 
                await inv_item.attempt_use(report, to_use) 
            else: 
                report.add('{}, your {}(s) are not currently usable. '.format(self.name, inv_item.name)) 
        else: 
            report.add('{}, you tried to use {} {}(s) but you only have {}. '.format(self.name, to_use, target_item.name, inv_amount)) 
    
    @action
    async def change_levels(self, report, direction): 
        success = await self.move_levels(report, direction) 

        if success: 
            await self.use_move(report) 

    @action
    async def free_regen(self, report): 
        hp_increase = self.max_hp * self.regen_percent

        self.current_hp += hp_increase

        report.add("{}'s current HP increased by {}! ".format(self.name, hp_increase)) 

        await self.hp_changed(report) 

        await self.use_move(report) 
    
    @action
    async def regen_shield(self, report): 
        if self.max_shield > 0: 
            watt_cost = 0
            
            for item, amount in self.items: 
                if item.is_a(Shield) and amount > 0: 
                    watt_cost += item.watt_cost
            
            lacking_items = self.lacks_items(((Watt, watt_cost),)) 
            
            if len(lacking_items) == 0: 
                self.current_shield = self.max_shield
                
                report.add(f'{self.name} regenned their shield to full! ') 
                
                await self.shield_changed(report) 
                
                await self.lose_items(report, ((Watt, watt_cost),)) 
            else: 
                lacking_str = format_iterable(lacking_items, formatter='{0[1]} {0[0].name}(s)') 

                report.add(f'{self.name} lacks {lacking_str} to regen their shield. ') 
        else: 
            report.add(f"{self.name} doesn't have a shield to regen. ") 
    
    @action
    async def pick_fight(self, report): 
        await self.fight_creature(report) 
    
    @action
    async def battle_call(self, report, side): 
        print('{} is now calling against {}'.format(self.name, self.enemy.name)) 

        async with self.enemy.acting(report): 
            await self.on_global_event(report, 'battle_round_start') 
            await self.enemy.on_global_event(report, 'battle_round_start') 

            if not self.dead and not self.enemy.dead: 
                flip_side = Die.flip_coin() 

                report.add('{} calls {}! '.format(self.name, side)) 
                report.add("It's {}! ".format(flip_side)) 

                if side.lower() == flip_side: 
                    await self.on_global_event(report, 'win_coinflip') 
                else: 
                    await self.enemy.on_global_event(report, 'win_coinflip') 

class Forager(Player):
    name = 'Forager'
    description = "Nothing escapes dis boi's eye" 
    specials = ('Guaranteed flee on battle turn in the Surface',) 
    starting_multipliers = {All: 2,} 

    @action
    async def attempt_flee(self, report): 
        if self.current_level is Levels.Surface: 
            async with self.enemy.acting(report): 
                report.add('{} successfully fled! '.format(self.name)) 
                        
                await self.end_battle_turn(report) 
                await self.leave_battle(report) 
        else: 
            await Player.attempt_flee(self, report) 
        # end battle stuff

class Berserker(Player): 
    scaling_factor = 1
    name = 'Berserker'
    description = 'REE REE TRIGGER TRIGGER REE REEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE' 
    specials = ('Attack increases with HP lost at a {} to 1 ratio'.format(scaling_factor), 'Berserker Mode - \
when {0} dies against a living opponent, it goes for a final hit directly to the opponent. If this hit kills \
the opponent, {0} is revived with 1 HP! '.format(name), f'After using Berserker Mode, {name} must regen to \
full HP before they can use it again') 
    starting_miss = 2 
    
    def __init__(self, client, channel, game, member_id=None): 
        self.can_revive = True

        Player.__init__(self, client, channel, game, member_id=member_id) 
    
    def stats_embed(self): 
        embed = Player.stats_embed(self) 

        embed.add_field(name='Can use Berserker Mode', value=self.can_revive) 

        return embed
    
    @action
    async def hp_changed(self, report): 
        await Player.hp_changed(self, report) 

        if self.current_hp == self.max_hp and not self.can_revive: 
            self.can_revive = True

            if report is not None: 
                report.add('{} can use Berserker Mode again! '.format(self.name)) 

        self.current_attack = (self.max_hp - self.current_hp) * self.scaling_factor * self.attack_multiplier + self.base_attack

        if report is not None: 
            await self.attack_changed(report) 
    
    @action
    async def on_death(self, report): 
        self.current_hp = 0

        await self.hp_changed(None) 

        if self.enemy is not None and not self.enemy.dead: 
            if self.can_revive: 
                async with self.enemy.acting(report): 
                    await self.end_battle_turn(report) 
                    
                    report.add('{0} is so triggered that they did not die immediately. {0} enters Berserker Mode and goes for a final hit! '.format(self.name)) 

                    await self.switch_hit(report, self.enemy) 

                    if self.enemy.dead: 
                        self.current_hp = 1

                        report.add("{} is so happy about killing {} that they revived with 1 HP! ".format(self.name, self.enemy.name)) 

                        await self.hp_changed(report) 

                        self.suiciding = False

                        self.can_revive = False

                        report.add('{} must now heal to full HP before they can use Berserker Mode again. '.format(self.name)) 
                    else: 
                        report.add("But the final hit didn't kill {}... ".format(self.enemy.name)) 

                        await Player.on_death(self, report) 
            else: 
                report.add("{} couldn't use Berserker Mode because they didn't heal to full HP after last using it. ".format(self.name)) 

                await Player.on_death(self, report) 
        else: 
            await Player.on_death(self, report) 

class Fisherman(Player):
    name = 'Fisherman'
    description = 'Lots of indentured servants' 
    specials = ('Can catch 1-star creatures without a coin flip', 'Can catch 2-star creatures with a coin flip') 
    starting_attack = 40
    starting_items = Player.starting_items + ([Fishing_Net, 1],)


class Hunter(Player):
    name = 'Hunter'
    description = 'Head of the pack' 
    starting_hp = 125
    starting_hp_multiplier = 1.2
    starting_attack = 40
    starting_attack_multiplier = 1.25
    starting_multipliers = {Meat: 2} 

class Diver(Player):
    allowed_level_deviation = 1
    free_moves = 1
    
    starting_hp = 130
    starting_oxygen = 6
    name = 'Diver'
    description = 'Dives so something'
    specials = (
        f'Is always allowed {allowed_level_deviation} additional level beyond listed', 
        'Can move levels and drag their opponents with them on their battle turn') 

    # noinspection PyUnusedLocal
    def level_deviation(self): 
        return Player.level_deviation(self) - self.allowed_level_deviation
    
    @action
    async def on_win_coinflip(self, report): 
        await Player.on_win_coinflip(self, report) 
        
        report.add('As a Diver, you can also drag. ') 
    
    async def drag(self, report, direction): 
        async with self.enemy.acting(report): 
            success = await self.move_levels(report, direction) 

            if success: 
                await self.end_battle_turn(report) 

''' 
def calculate_level_multipliers(self): 
  level = Die.roll_die() 
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

class Cryomancer(Player): 
    fb_threshold = 0.5
    fb_eam = 0.7
    fb_attack_multiplier = 1.3
    
    name = 'Cryomancer' 
    description = 'Brrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr' 
    specials = (f'Frostbite - when {name} is at or below {fb_threshold:.0%} HP, damage taken from enemy attacks is reduced by \
{1 - fb_eam:.0%}, and its own damage is increased by {fb_attack_multiplier - 1:.0%}. This effect disappears when {name} \
goes above {fb_threshold:.0%} HP. ',) 
    starting_hp = 110
    starting_attack = 30
    
    def __init__(self, client, channel, game, member_id=None): 
        self.fb_activated = False
        
        Player.__init__(self, client, channel, game, member_id=member_id) 
    
    @action
    async def on_shutdown(self, report): 
        if self.fb_activated: 
            self.enemy_attack_multiplier /= self.fb_eam
            
            await self.change_attack_multiplier(None, 1, self.fb_attack_multiplier) 
        
        await Player.on_shutdown(self, report) 
    
    @action
    async def on_turn_on(self, report): 
        if self.fb_activated: 
            self.enemy_attack_multiplier *= self.fb_eam
            
            await self.change_attack_multiplier(None, self.fb_attack_multiplier) 
        
        await Player.on_turn_on(self, report) 
    
    def stats_embed(self): 
        embed = Player.stats_embed(self) 

        embed.add_field(name='Frostbite activated', value=self.fb_activated) 

        return embed
    
    @action
    async def hp_changed(self, report): 
        await Player.hp_changed(self, report) 
        
        if self.current_hp / self.max_hp <= self.fb_threshold: 
            if not self.fb_activated: 
                self.fb_activated = True
                
                self.enemy_attack_multiplier *= self.fb_eam

                if report is not None: 
                    report.add(f"{self.name}'s Frostbite ability is now active! ") 
                    report.add(f'{self.name} now takes {self.fb_eam - 1:+.0%} damage from enemy attacks! ') 

                await self.change_attack_multiplier(report, self.fb_attack_multiplier) 
        elif self.fb_activated: 
            self.fb_activated = False
            self.enemy_attack_multiplier /= self.fb_eam
            
            if report is not None: 
                report.add(f"{self.name}'s Frostbite ability is no longer active. ") 
                report.add(f'{self.name} no longer takes {self.fb_eam - 1:+.0%} damage from enemy attacks. ') 
            
            await self.change_attack_multiplier(report, 1, self.fb_attack_multiplier) 

class Scorch(Player): 
    crit_fire_percent = 1
    aura_percent = 0.2
    
    name = 'Scorch' 
    description = 'Fiery' 
    specials = (f"Crits apply {crit_fire_percent:.0%} of {name}'s attack damage as fire damage to the victim instead \
of dealing extra damage", f'Surrounded by an aura of fire that inflicts {aura_percent:.0%} of its attack \
damage on its opponent each battle round (penetrates shield) ') 
    starting_attack = 30
    starting_crit = 4
    
    @action
    async def on_crit(self, report, target): 
        await self.deal_damage(report, target, self.current_attack, crit=True, penetrates=self.penetrates, bleeds=self.bleeds) 

        fire_damage = self.current_attack * self.crit_fire_percent * target.enemy_attack_multiplier

        report.add(f'{self.name} adds {self.crit_fire_percent:.0%} of their attack damage as fire damage to {target.name}! ') 
        await target.get_burned(report, fire_damage) 
    
    @action
    async def on_battle_round_start(self, report): 
        await Player.on_battle_round_start(self, report) 

        aura_damage = self.current_attack * self.aura_percent * self.enemy.enemy_attack_multiplier

        report.add(f"{self.enemy.name} is damaged by {self.name}'s fiery aura! ") 

        await self.enemy.take_damage(report, aura_damage, penetrates=('shield',))

class Shock(Player): 
    self_charge = 0.1
    target_charge = 0.4
    leech_percent = 1
    stunning_crit_bonus = 1
    
    name = 'Shock' 
    description = 'Zap' 
    specials = (f'Each hit {name} gets, regardless of type, adds {self_charge:.0%} of its damage as electric \
potential damage to itself, and {target_charge:.0%} to the victim', f"Crit combines the victim and \
{name}'s own potential damage and deals it all to the victim. {name} then gains {leech_percent:.0%} of the \
dealt damage as HP. ", f"Critting stuns the target; {name}'s own crit chance is temporarily raised by \
{stunning_crit_bonus} while stunning", 'Potential damage, when released, bypasses shield', 
f"When {name} misses, it deals its own stored damage to itself, and gets stunned") 
    starting_hp = 100
    starting_attack = 30

    def __init__(self, client, channel, game, member_id=None): 
        self.stunning_level = 0

        Player.__init__(self, client, channel, game, member_id=member_id) 
    
    def stunning(self, _report): 
        class Stunning: 
            entity = self
            report = _report

            async def __aenter__(self): 
                if self.entity.stunning_level == 0: 
                    self.entity.crit -= self.entity.stunning_crit_bonus

                    self.report.add(f"{self.entity.name}'s crit chance temporarily increases by \
{self.entity.stunning_crit_bonus}! ") 

                self.entity.stunning_level += 1

            async def __aexit__(self, typ, value, traceback): 
                self.entity.stunning_level -= 1

                if self.entity.stunning_level == 0: 
                    self.entity.crit += self.entity.stunning_crit_bonus

                    self.report.add(f"{self.entity.name}'s crit chance reset to normal. ") 
        
        return Stunning() 
    
    @staticmethod
    async def charge_thing(report, target, electric_damage): 
        target.electric_damage += electric_damage
        
        report.add(f'{target.name} received {electric_damage} potential damage! ') 
        report.add(f'{target.name} has {target.electric_damage} potential damage now! ') 
    
    @action
    async def charge(self, report, target): 
        self_charge = self.current_attack * self.self_charge * self.enemy_attack_multiplier
        target_charge = self.current_attack * self.target_charge * target.enemy_attack_multiplier

        await self.charge_thing(report, self, self_charge) 
        await self.charge_thing(report, target, target_charge) 
    
    @staticmethod
    async def release_charge(report, target, damage): 
        await target.take_damage(report, damage, penetrates=('shield',)) 
    
    @staticmethod
    async def stun_target(report, stunner, stunned): 
        with stunned.stunned(): 
            report.add(f'{stunned.name} is stunned, and {stunner.name} gets a free hit on them! ') 

            await stunner.switch_hit(report, stunned)
    
    @action
    async def on_miss(self, report, target): 
        report.add(f'{self.name} self-damages! ') 
        
        damage = self.electric_damage

        await self.release_charge(report, self, damage) 

        self.electric_damage = 0

        await self.stun_target(report, target, self) 
        
        '''
        with self.stunned(): 
            report.add(f'{self.name} is stunned, and {target.name} gets a free hit on them! ') 

            await target.switch_hit(report, self) 
        ''' 
    
    @action
    async def on_crit(self, report, target): 
        report.add(f"{self.name} releases {target.name}'s and their own combined electric damage! ") 

        damage = self.electric_damage + target.electric_damage

        await self.release_charge(report, target, damage) 

        self.electric_damage = 0
        target.electric_damage = 0

        to_regen = damage * self.leech_percent

        self.current_hp += to_regen

        report.add(f'{self.name} regenerates {self.leech_percent:.0%} of the released damage as HP! ') 

        await self.hp_changed(report) 

        async with self.stunning(report): 
            await self.stun_target(report, self, target) 
    
    @action
    async def switch_hit(self, report, target): 
        async with target.acting(report): 
            await self.charge(report, target) 

            await Player.switch_hit(self, report, target) 
        
        '''
        with target.stunned(): 
            report.add(f'{target.name} is stunned, and {self.name} gets a free hit on them! ') 
            
            await self.switch_hit(report, target) 
        ''' 

creatures_filters = {
    'drops-stuff': lambda creature: len(creature.starting_drops) > 0, 
    'passive': lambda creature: creature.passive, 
} 

def gen_filter(level): 
    return lambda creature: creature in level.creatures

for level in Levels: 
    creatures_filters[level.name.lower()] = gen_filter(level) 

creatures = ttd_tools.Filterable(**creatures_filters) 

class Creature_Meta(ttd_tools.GO_Meta): 
    append_to = creatures

class Creature(Commander, metaclass=Creature_Meta, append=False): 
    starting_drops = {} 
    stars = 0
    passive = False
        # self.level = self.calculate_level_multipliers() 
    
    def __init__(self, client, channel, enemy, current_level=None): 
        self.drops = self.starting_drops.copy() 

        Commander.__init__(self, client, channel, enemy=enemy, current_level=current_level) 
    
    @staticmethod
    def modify_deconstructed(deconstructed): 
        del deconstructed['enemy'] 

        deconstructed['drops'] = {item.__name__: amount for item, amount in deconstructed['drops'].items()} 
        
        Commander.modify_deconstructed(deconstructed) 
    
    def reconstruct_next(self): 
        self.drops = {eval(item_name): amount for item_name, amount in self.drops.items()} 

        Commander.reconstruct_next(self) 
    
    @action
    async def on_shutdown(self, report): 
        self.drops = subtract_dicts(self.drops, self.starting_drops) 

        await Commander.on_shutdown(self, report) 
    
    @action
    async def on_turn_on(self, report): 
        self.drops = add_dicts(self.drops, self.starting_drops) 

        await Commander.on_turn_on(self, report) 
    
    @classmethod
    def gen_help_specials(cls, specials): 
        super(Creature, cls).gen_help_specials(specials) 

        if cls.passive: 
            specials.append('Passive - will flee the battle upon getting first hit') 
    
    @classmethod
    def help_embed(cls): 
        embed = super(Creature, cls).help_embed() 

        drops_gen = ('{} x{}'.format(item.name, amount) for item, amount in cls.starting_drops.items()) 
        drops_str = make_list(drops_gen) 

        embed.add_field(name='Drops', value=drops_str if len(drops_str) > 0 else 'Nothing', inline=False) 

        embed.add_field(name='Stars', value=cls.stars) 

        return embed
    
    def gen_stats_specials(self, specials): 
        Commander.gen_stats_specials(self, specials) 

        if self.passive: 
            specials.append('Passive - will flee the battle upon getting first hit') 
    
    def stats_embed(self): 
        embed = Commander.stats_embed(self) 

        drops_gen = ('{} x{}'.format(item.name, amount) for item, amount in self.drops.items()) 
        drops_str = make_list(drops_gen) 
        
        embed.add_field(name='Drops', value=drops_str if len(drops_str) > 0 else 'Nothing', inline=False) 

        embed.add_field(name='Stars', value=self.stars) 

        return embed 
    
    @action
    async def drop_stuff(self, report, drop_to): 
        drops_list = [(item, amount) for item, amount in self.drops.items()] 

        await drop_to.earn_items(report, drops_list) 
    
    @action
    async def on_death(self, report): 
        report.add('{} died! '.format(self.name)) 

        if self.enemy is not None: 
            async with self.enemy.acting(report): 
                enemy = self.enemy

                await self.leave_battle(report) 

                await self.drop_stuff(report, enemy) 

        # do drops here

    @action
    async def on_win_coinflip(self, report): 
        await self.start_battle_turn(report) 

        await self.switch_attack(report) 

    @action
    # noinspection PyMethodMayBeStatic
    async def on_global_event(self, report, event_name, *args, **kwargs): 
        await eval('self.on_{}(report, *args, **kwargs) '.format(event_name)) 

    @action
    async def switch_attack(self, report): 
        async with self.enemy.acting(report): 
            await self.attack(report, self.enemy) 

            await self.end_battle_turn(report) 

pets = ttd_tools.Filterable() 

class Pet_Meta(ttd_tools.GO_Meta): 
    append_to = pets

class Pet(Entity, metaclass=Pet_Meta, append=False): 
    effects = () 
    usages = () 

    def __init__(self, client, channel, owner, current_level=None): 
        self.owner = owner

        Entity.__init__(self, client, channel, current_level=current_level) 

class Trout(Entity):
    name = "Trout"
    description = "Food - not a cat"
    starting_hp = 50
    starting_attack = 10
    starting_access_levels = (Levels.Surface,) 

class C_Trout(Trout, Creature): 
    starting_drops = {Meat: 2,} 

class Ariel_Leviathan(Entity):
    name = "Ariel Leviathan"
    description = "A singular fragment of fecal matter that possesses 400 health points - Mastermind"
    starting_hp = 400
    starting_attack = 10
    starting_access_levels = (Levels.Surface,) 

class C_Ariel_Leviathan(Ariel_Leviathan, Creature): 
    starting_drops = {
        Sky_Blade: 1, 
        Meat: 6, 
    }
    passive = True

class Saltwater_Croc(Entity):
    name = "Saltwater Croc"
    description = "What's for lunch - jlscientist"
    starting_hp = 100
    starting_shield = 100
    starting_attack = 100
    starting_access_levels = (Levels.Surface,) 

class C_Saltwater_Croc(Saltwater_Croc, Creature): 
    starting_drops = {
        Scale: 1, 
        Meat: 5, 
    }
    passive = True

class Tiger_Fish(Entity):
    rage_threshold = 50
    rage_attack = 50
    name = "Tiger Fish"
    description = "I don't know - RyantheKing"
    specials = ("Damage increases to {} if the target of its attack has {} or more damage. ".format(rage_attack, rage_threshold),)
    starting_hp = 100
    starting_attack = 30
    starting_access_levels = (Levels.Surface,) 

    @action
    async def switch_hit(self, report, target):
        former_attack = self.current_attack

        if target.current_attack >= self.rage_threshold:
            self.current_attack = self.rage_attack

            report.add('{} rages, and its attack increases! '.format(self.name)) 

            await self.attack_changed(report) 
        
        await Entity.switch_hit(self, report, target)

        self.current_attack = former_attack

class C_Tiger_Fish(Tiger_Fish, Creature): 
    starting_drops = {Meat: 5,}

class Gar(Entity):
    name = "Gar"
    description = "Closely GARds its 1 meat - not a cat"
    starting_hp = 100
    starting_attack = 40
    starting_access_levels = (Levels.Surface,) 

class C_Gar(Gar, Creature): 
    starting_drops = {Meat: 4,} 

class Turtle(Entity):
    name = 'Turtle'
    description = 'Turtles' 
    starting_hp = 80
    starting_shield = 90
    starting_attack = 10
    starting_access_levels = (Levels.Surface,) 

class C_Turtle(Turtle, Creature): 
    starting_drops = {
        Suit: 1, 
        Meat: 1, 
    }

class Piranha(Entity): 
    name = 'Piranha'
    description = 'Om nom nom' 
    starting_hp = 70
    starting_attack = 10
    starting_access_levels = (Levels.Surface,) 

class C_Piranha(Piranha, Creature): 
    per_round_attack_increase = 20
    drops_scaling = {Meat: 2,} 

    drops_scaling_str = format_iterable(drops_scaling.items(), formatter='{0[1]} {0[0].name}(s)') 

    specials = Piranha.specials + ('Attack increases by {} every battle round'.format(per_round_attack_increase), 
f'Drops increases by {drops_scaling_str} every battle round')  
    starting_drops = {Meat: 1,} 
    
    def __init__(self, client, channel, enemy, current_level=None):
        self.elapsed_battle_rounds = 0

        Creature.__init__(self, client, channel, enemy, current_level=current_level) 
    
    @action
    async def on_shutdown(self, report): 
        await Creature.on_shutdown(self, report) 

        attack_decrease = self.elapsed_battle_rounds * self.per_round_attack_increase * self.attack_multiplier

        self.base_attack -= attack_decrease
        self.current_attack -= attack_decrease

        increased_drops = {item: amount * self.elapsed_battle_rounds for item, amount in 
self.drops_scaling.items()} 

        self.drops = subtract_dicts(self.drops, increased_drops) 
    
    @action
    async def on_turn_on(self, report): 
        await Creature.on_turn_on(self, report) 

        attack_increase = self.elapsed_battle_rounds * self.per_round_attack_increase * self.attack_multiplier

        self.base_attack += attack_increase
        self.current_attack += attack_increase

        increased_drops = {item: amount * self.elapsed_battle_rounds for item, amount in 
self.drops_scaling.items()} 

        self.drops = add_dicts(self.drops, increased_drops) 
    
    @action
    async def on_battle_round_start(self, report):
        self.elapsed_battle_rounds += 1

        attack_increase = self.per_round_attack_increase * self.attack_multiplier

        self.base_attack += attack_increase
        self.current_attack += attack_increase

        report.add("{}'s base and current attack increased by {}! ".format(self.name, attack_increase)) 

        await self.attack_changed(report) 

        self.drops = add_dicts(self.drops, self.drops_scaling) 

        report.add(f"{self.name}'s drops increased by {self.drops_scaling_str}! ") 

        await Creature.on_battle_round_start(self, report) 


class Hatchet_Fish(Entity):
    name = 'Hatchet Fish'
    description = 'Chop chop'
    starting_hp = 70
    starting_attack = 30
    starting_access_levels = (Levels.Surface,) 

class C_Hatchet_Fish(Hatchet_Fish, Creature): 
    starting_drops = {Hatchet_Fish_Corpse: 1,} 

class Octofish(Entity):
    name = 'Octofish'
    description = 'stuff'
    starting_hp = 70
    starting_attack = 30
    starting_access_levels = (Levels.Surface,) 

class C_Octofish(Octofish, Creature): 
    starting_drops = {Meat: 3,} 

class Big_Trout(Entity): 
    name = 'Big Trout'
    description = "it's like trout but big"
    starting_hp = 60
    starting_attack = 20
    starting_access_levels = (Levels.Surface,) 

class C_Big_Trout(Big_Trout, Creature): 
    starting_drops = {Meat: 4,} 

class Water_Bug(Entity): 
    starting_miss = 0
    starting_crit = 5
    starting_enemy_miss_bonus = 2
    name = 'Water Bug'
    description = 'Where did it come from? Where did it go? '
    starting_hp = 50
    starting_attack = 10
    starting_access_levels = (Levels.Surface,) 

class C_Water_Bug(Water_Bug, Creature): 
    pass

class Tummy_Tetra(Entity): 
    steals = ((Meat, 1),) 
    steals_gen = ((item.name, amount) for item, amount in steals) 
    steals_string = ', '.join(('{} {}'.format(amount, item_name) for item_name, amount in steals_gen)) 

    name = 'Tummy Tetra'
    description = 'yum'
    specials = ('50% chance of stealing {} from players on hit'.format(steals_string),)
    starting_hp = 50
    starting_attack = 30
    starting_access_levels = (Levels.Surface,) 

    @action
    async def steal_stuff(self, report, target): 
        report.add("{} is now looting {}'s items! ".format(self.name, target.name)) 

        stolen_items = await target.lose_items(report, self.steals) 

        if len(stolen_items) > 0: 
            for item, amount in stolen_items:
                report.add('{} stole and ate {} {}(s)! '.format(self.name, amount, item.name)) 

                if item.is_usable: 
                    to_use = item(self.client, self.channel, self) 

                    await to_use.on_use(report, amount) 
        else: 
            report.add("But {} didn't have anything that {} wanted... ".format(target.name, self.name)) 
    
    @action
    async def attempt_steal(self, report, target):
        # reaction_member = self.channel.guild.get_member(target.member_id) 

        report.add("{} lunges for {}'s inventory! ".format(self.name, target.name)) 

        won_flip = await target.call_and_flip(report) 

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
        '''

        if won_flip:
            report.add('{} failed to steal anything. '.format(self.name))
        else:
            await self.steal_stuff(report, target) 
    
    @action
    async def switch_hit(self, report, target): 
        await Entity.switch_hit(self, report, target) 

        # noinspection PyRedundantParentheses
        if target.is_a(Player): 
            await self.attempt_steal(report, target) 

class C_Tummy_Tetra(Tummy_Tetra, Creature): 
    pass

class Toxic_Waste(Entity): 
    name = 'Toxic Waste'
    description = 'oof' 
    starting_hp = float('inf') 
    starting_attack = 30
    starting_access_levels = (Levels.Surface, Levels.Middle) 
    starting_penetrates = ('shield',) 

class C_Toxic_Waste(Toxic_Waste, Creature): 
    specials = Toxic_Waste.specials + ('Always gets first hit', 'Hits once and then disappears', f'Attacks can be converted to '
                                                                                                 f'{Bio_Wheel.converts_to_str} through the '
                                                                                                 f'{Bio_Wheel.name}') 
    starting_priority = float('inf') 
    
    @action
    async def switch_hit(self, report, target): 
        if target.has_item(Bio_Wheel): 
            report.add(f"{target.name}'s {Bio_Wheel.name} converts {self.name}'s attack into {Bio_Wheel.converts_to_str}! ") 
            
            await target.earn_items(report, Bio_Wheel.converts_to) 
        else: 
            await Toxic_Waste.switch_hit(self, report, target) 

    @action
    async def switch_attack(self, report): 
        async with self.enemy.acting(report): 
            await Creature.switch_attack(self, report) 

            report.add('{} disappeared! '.format(self.name)) 

            await self.leave_battle(report) 

class Blue_Whale(Entity): 
    name = 'Blue Whale' 
    description = 'Mucho big' 
    starting_hp = 600
    starting_attack = 10
    starting_access_levels = (Levels.Middle,) 

class C_Blue_Whale(Blue_Whale, Creature): 
    starting_drops = {
        Blubber: 1, 
        Meat: 8, 
    }
    passive = True

class Great_White_Shark(Entity): 
    name = 'Great White Shark' 
    description = 'RIP' 
    starting_hp = 300
    starting_attack = 200
    starting_access_levels = (Levels.Middle,) 

class C_Great_White_Shark(Great_White_Shark, Creature): 
    starting_drops = {
        Shark_Skin: 1, 
        Meat: 20, 
    }
    passive = True

class Albino_Tiger_Oscar(Entity): 
    name = 'Albino Tiger Oscar' 
    description = 'Rare and contains valuable resources' 
    starting_hp = 250
    starting_attack = 70
    starting_access_levels = (Levels.Middle,) 

class C_Albino_Tiger_Oscar(Albino_Tiger_Oscar, Creature): 
    starting_drops = {
        Platinum_Elixir: 1, 
        Meat: 8, 
    }

class Giant_Lionfish(Entity): 
    revenge_damage = 60

    name = 'Giant Lionfish' 
    description = 'Puts up a fierce fight, but the result is so worth it' 
    specials = ('Deals {} damage back to attacker when hit. If the damage comes from a critical hit, it deals double damage! '.format(revenge_damage),) 
    starting_hp = 250
    starting_attack = 60
    starting_access_levels = (Levels.Middle,) 

    @action
    async def take_damage(self, report, damage, inflicter=None, penetrates=(), bleeds=(), crit=False): 
        await Entity.take_damage(self, report, damage, inflicter=inflicter, penetrates=penetrates, bleeds=bleeds, crit=crit) 

        if inflicter is not None: 
            if crit: 
                revenge_damage = self.revenge_damage * 2

                report.add('{} retaliates the crit with double damage! '.format(self.name)) 
            else: 
                revenge_damage = self.revenge_damage
            
            await self.deal_damage(report, inflicter, revenge_damage, penetrates=('shield',))  

class C_Giant_Lionfish(Giant_Lionfish, Creature): 
    starting_drops = {
        Platinum_Elixir: 1, 
        Meat: 12, 
    }

class Marlin(Entity): 
    name = 'Marlin' 
    description = 'Stab' 
    starting_hp = 150
    starting_attack = 70
    starting_access_levels = (Levels.Middle,) 

class C_Marlin(Marlin, Creature): 
    starting_drops = {
        Marlin_Sword: 1, 
        Meat: 6, 
    }
    passive = True

class Mushroom_Fish(Entity): 
    name = 'Mushroom Fish' 
    description = 'What' 
    starting_hp = 150
    starting_attack = 50
    starting_access_levels = (Levels.Middle,) 

class C_Mushroom_Fish(Mushroom_Fish, Creature): 
    starting_drops = {Meat: 6,} 

class Tiger_Oscar(Entity): 
    name = 'Tiger Oscar' 
    description = 'Significantly weaker than its albino counterpart' 
    starting_hp = 150
    starting_attack = 30
    starting_access_levels = (Levels.Middle,) 

class C_Tiger_Oscar(Tiger_Oscar, Creature): 
    starting_drops = {Meat: 5,} 

class Barracuda(Entity): 
    name = 'Barracuda' 
    description = 'Better not let it save up' 
    starting_hp = 100
    starting_attack = 30
    starting_access_levels = (Levels.Middle,) 

class C_Barracuda(Barracuda, Creature): 
    per_round_hp_increase = 30
    per_round_attack_increase = 30
    drops_scaling = {Meat: 5,} 

    drops_scaling_str = format_iterable(drops_scaling.items(), formatter='{0[1]} {0[0].name}(s)') 
    
    specials = Barracuda.specials + ('HP increases by {} every battle round'.format(per_round_hp_increase), 'Attack damage increases by {} every '
'battle round'.format(per_round_attack_increase), f'Drops increases by {drops_scaling_str} every battle round') 

    starting_drops = {Meat: 3,} 
    passive = True

    def __init__(self, client, channel, enemy, current_level=None):
        self.elapsed_battle_rounds = 0

        Creature.__init__(self, client, channel, enemy, current_level=current_level) 
    
    @action
    async def on_shutdown(self, report): 
        await Creature.on_shutdown(self, report) 

        hp_decrease = self.elapsed_battle_rounds * self.per_round_hp_increase * self.hp_multiplier

        self.base_hp -= hp_decrease
        self.current_hp -= hp_decrease
        self.max_hp -= hp_decrease

        attack_decrease = self.elapsed_battle_rounds * self.per_round_attack_increase * self.attack_multiplier

        self.base_attack -= attack_decrease
        self.current_attack -= attack_decrease

        increased_drops = {item: amount * self.elapsed_battle_rounds for item, amount in 
self.drops_scaling.items()} 

        self.drops = subtract_dicts(self.drops, increased_drops) 
    
    @action
    async def on_turn_on(self, report): 
        await Creature.on_turn_on(self, report) 

        hp_increase = self.elapsed_battle_rounds * self.per_round_hp_increase * self.hp_multiplier

        self.base_hp += hp_increase
        self.current_hp += hp_increase
        self.max_hp += hp_increase

        await self.hp_changed(None) 

        attack_increase = self.elapsed_battle_rounds * self.per_round_attack_increase * self.attack_multiplier

        self.base_attack += attack_increase
        self.current_attack += attack_increase

        increased_drops = {item: amount * self.elapsed_battle_rounds for item, amount in 
self.drops_scaling.items()} 

        self.drops = add_dicts(self.drops, increased_drops) 
    
    @action
    async def on_battle_round_start(self, report):
        self.elapsed_battle_rounds += 1

        hp_increase = self.per_round_hp_increase * self.hp_multiplier

        self.base_hp += hp_increase
        self.current_hp += hp_increase
        self.max_hp += hp_increase

        report.add("{}'s base, current, and max HP increased by {}! ".format(self.name, hp_increase)) 

        await self.hp_changed(report) 

        attack_increase = self.per_round_attack_increase * self.attack_multiplier

        self.base_attack += attack_increase
        self.current_attack += attack_increase

        report.add("{}'s base and current attack increased by {}! ".format(self.name, attack_increase)) 

        await self.attack_changed(report) 

        self.drops = add_dicts(self.drops, self.drops_scaling) 

        report.add(f"{self.name}'s drops increased by {self.drops_scaling_str}! ") 

        await Creature.on_battle_round_start(self, report) 

class Shovelnose_Guitar_Fish(Entity): 
    name = 'Shovelnose Guitar Fish' 
    description = 'Has an interesting head shape' 
    starting_hp = 100
    starting_attack = 30
    starting_access_levels = (Levels.Middle,) 

class C_Shovelnose_Guitar_Fish(Shovelnose_Guitar_Fish, Creature): 
    starting_drops = {Shovelnose: 1,} 

class Vortex_Fish(Entity): 
    steal_amount = 3

    name = 'Vortex Fish' 
    description = 'Succ' 
    specials = ("When attacking, will attempt to steal {} items of the player's choice".format(steal_amount),) 
    starting_hp = 100
    starting_attack = 20
    starting_access_levels = (Levels.Middle,) 

    @action
    async def steal_stuff(self, report, target): 
        report.add("{} is now looting {}'s items! ".format(self.name, target.name)) 

        available_amounts = (amount for item, amount in target.items if amount > 0) 
        total_amount = sum(available_amounts) 

        num_steals = min(self.steal_amount, total_amount) 

        if num_steals > 0: 
            stealables = {item.__class__: amount for item, amount in target.items if amount > 0} 
            stolen = {} 

            for i in range(num_steals): 
                choices = [item.name for item, amount in stealables.items() if amount > 0] 

                report.add('{}, choose item {} to lose. '.format(target.name, i + 1)) 

                to_lose = await self.client.prompt_for_message(report, target.member_id, choices=choices, timeout=20, default_choice=choices[0]) 

                item_to_lose = ttd_tools.search(items, to_lose) 

                stealables[item_to_lose] -= 1

                if item_to_lose in stolen: 
                    stolen[item_to_lose] += 1
                else: 
                    stolen[item_to_lose] = 1
            
            final_loss = [(item, amount) for item, amount in stolen.items()] 

            await target.lose_items(report, final_loss) 
        else: 
            report.add("But {} didn't have anything for {} to steal... ".format(target.name, self.name)) 
    
    @action
    async def attempt_steal(self, report, target):
        # reaction_member = self.channel.guild.get_member(target.member_id) 

        report.add("{} lunges for {}'s inventory! ".format(self.name, target.name)) 

        won_flip = await target.call_and_flip(report) 

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
        '''

        if won_flip:
            report.add('{} failed to steal anything. '.format(self.name))
        else:
            await self.steal_stuff(report, target) 
    
    @action
    async def switch_hit(self, report, target): 
        await Entity.switch_hit(self, report, target) 

        # noinspection PyRedundantParentheses
        await self.attempt_steal(report, target) 

class C_Vortex_Fish(Vortex_Fish, Creature): 
    starting_drops = {Meat: 4,} 

class Largemouth_Bass(Entity): 
    name = 'Largemouth Bass' 
    description = "It's all about it" 
    starting_hp = 80
    starting_attack = 50
    starting_access_levels = (Levels.Middle,) 

class C_Largemouth_Bass(Largemouth_Bass, Creature): 
    starting_drops = {Meat: 4,} 

class Tuna(Entity): 
    name = 'Tuna' 
    description = 'Un-piano-able' 
    starting_hp = 70
    starting_attack = 20
    starting_access_levels = (Levels.Middle,) 

class C_Tuna(Tuna, Creature): 
    starting_drops = {Meat: 5,} 

class Moray_Eel(Entity): 
    name = 'Moray Eel' 
    description = 'Slimy' 
    starting_hp = 50
    starting_attack = 50
    starting_access_levels = (Levels.Middle,) 

class C_Moray_Eel(Moray_Eel, Creature): 
    starting_drops = {Slime_Coat: 1,} 

class Electric_Eel(Entity): 
    name = 'Electric Eel' 
    description = '**Shock**ingly strong' 
    specials = (f'When {name} attacks, a coin flip is used to determine if it stuns its target. If it successfully gets the stun, it gets to hit again! ', 
    f'{name} is unable to miss while attacking a stunned target')  
    starting_hp = 50
    starting_attack = 20
    starting_access_levels = (Levels.Middle,) 

    @action
    async def switch_hit(self, report, target): 
        await Entity.switch_hit(self, report, target) 

        report.add('{} attempts to stun {}! '.format(self.name, target.name)) 

        stunned = not await target.call_and_flip(report) 

        if stunned: 
            with target.stunned(): 
                report.add('{} is stunned! {} gets to hit again! '.format(target.name, self.name)) 

                await self.switch_hit(report, target) 
        else: 
            report.add('{} failed to stun {}. '.format(self.name, target.name)) 

class C_Electric_Eel(Electric_Eel, Creature): 
    starting_drops = {Watt: 5,} 

class Pufferfish(Entity): 
    name = 'Pufferfish' 
    description = 'Puffy' 
    starting_hp = 50
    starting_attack = 35
    starting_access_levels = (Levels.Middle,) 

class C_Pufferfish(Pufferfish, Creature): 
    oxygen_drop = 1
    
    specials = ('Gives the player {} oxygen upon death'.format(oxygen_drop),) 
    starting_drops = {Pufferfish_Corpse: 1,} 

    @action
    async def drop_stuff(self, report, drop_to): 
        await Creature.drop_stuff(self, report, drop_to) 

        drop_to.current_oxygen += self.oxygen_drop

        report.add("{}'s current oxygen increased by {}! ".format(drop_to.name, self.oxygen_drop)) 

        await drop_to.oxygen_changed(report) 

class Great_Diving_Minnow(Entity): 
    name = 'Great Diving Minnow' 
    description = 'Good at diving' 
    starting_hp = 50
    starting_attack = 10
    starting_access_levels = (Levels.Middle,) 

class C_Great_Diving_Minnow(Great_Diving_Minnow, Creature): 
    pass

class Reefback(Entity): 
    name = 'Reefback' 
    description = 'Near-invincible, so creatures like to hide behind it for protection. The {} itself, however, is peaceful and never engages in combat. '.format(name) 
    starting_hp = float('inf') 
    starting_access_levels = (Levels.Middle,) 

class C_Reefback(Reefback, Creature): 
    hp_multiplier_bonus = 1.5
    
    specials = Reefback.specials + ('When fought, instead of engaging, it gets replaced with another random Middle creature. This creature will then '
                               'fight you with a {}x increase in HP. '.format(hp_multiplier_bonus),) 
    
    @action
    async def on_battle_start(self, report): 
        invalid = True

        while invalid: 
            new_creature = await Levels.Middle.select_creature() 

            invalid = new_creature is self.__class__ 
        
        new_enemy = new_creature(self.client, self.channel, self.enemy, current_level=self.current_level) 

        self.enemy.enemy = new_enemy

        report.add('{} is replaced with {}! '.format(self.name, new_enemy.name)) 

        report.add("{} gains extra HP thanks to {}'s protection! ".format(new_enemy.name, self.name)) 

        await new_enemy.change_hp_multiplier(report, self.hp_multiplier_bonus) 

        await new_enemy.on_battle_start(report) 

class Stonefish(Entity): 
    name = 'Stonefish' 
    description = 'Highly poisonous' 
    starting_hp = 50
    starting_attack = 20
    starting_access_levels = (Levels.Middle,) 

class C_Stonefish(Stonefish, Creature): 
    poison_damage = 20
    
    specials = Stonefish.specials + (f'Deals {poison_damage} poison damage to the player upon dying (can be negated with {Slime_Coat.name}) ',) 
    
    @action
    async def drop_stuff(self, report, drop_to): 
        await Creature.drop_stuff(self, report, drop_to) 
        
        if not drop_to.has_item(Slime_Coat): 
            report.add(f'{drop_to.name} takes poison damage! ') 
            
            await self.deal_damage(report, drop_to, self.poison_damage, penetrates=('shield',)) 
        else: 
            report.add(f"{drop_to.name}'s {Slime_Coat.name} negated {self.name}'s poison damage! ") 

level_stats = {
    Levels.Surface: {
        #surface
        'creatures': {
            C_Ariel_Leviathan: 1,
            C_Saltwater_Croc: 1,
            C_Tiger_Fish: 1,
            C_Gar: 1,
            C_Turtle: 3,
            C_Piranha: 1,
            C_Hatchet_Fish: 1,
            C_Octofish: 1,
            C_Big_Trout: 1,
            C_Water_Bug: 1,
            C_Tummy_Tetra: 1,
            C_Trout: 2,
            C_Toxic_Waste: 2, 
        }, 
        'gatherables': {
            Coral: 2, 
        }, 
        'mineables': {}, 
    }, 
    
    Levels.Middle: {
        'creatures': {
            C_Blue_Whale: 1, 
            C_Great_White_Shark: 1, 
            C_Albino_Tiger_Oscar: 1, 
            C_Giant_Lionfish: 1, 
            C_Marlin: 1, 
            C_Mushroom_Fish: 1, 
            C_Tiger_Oscar: 1, 
            C_Barracuda: 1, 
            C_Shovelnose_Guitar_Fish: 1,
            C_Vortex_Fish: 1, 
            C_Largemouth_Bass: 1, 
            C_Tuna: 1, 
            C_Moray_Eel: 1, 
            C_Electric_Eel: 1, 
            C_Pufferfish: 1, 
            C_Great_Diving_Minnow: 1, 
            C_Reefback: 1, 
            C_Toxic_Waste: 3, 
        }, 
        'gatherables': {
            Wood: 1, 
            Coral: 2, 
        }, 
        'mineables': {
            Iron: 1, 
            Steel: 1, 
        }
    }, 
} 

for level in Levels: 
    level.set_stats(level_stats) 
    
'''
def select_creature(self, client, channel): 
    # picks a random creature here
    to_pick = random.randint(1, self.total_creatures) 
    running_sum = 0

    for creature, amount in self.creatures.items(): 
        running_sum += amount

        if running_sum >= to_pick: 
            return creature(client, channel, current_level=self) 

Surface = enum.auto() 
''' 

'''
async def apply_multipliers(self, target, amount): 
  if amount != 0:  
    if self.hp_bonus != 0: 
      hp_gain = self.hp_bonus * amount
      target.base_hp += hp_gain
      report.add("{}'s base HP increased by {}! ".format(target.name, hp_gain)) 
      target.current_hp += hp_gain
      report.add('{} gained {} HP! '.format(target.name, hp_gain)) 
      target.max_hp += hp_gain
      report.add("{}'s max HP increased by {}! ".format(target.name, hp_gain)) 
      
      target.check_death() 
    
    if self.shield_bonus != 0: 
      shield_gain = self.shield_bonus * amount
      target.base_shield += shield_gain
      report.add("{}'s base shield increased by {}! ".format(target.name, shield_gain)) 
      target.current_shield += shield_gain
      report.add('{} gained {} shield! '.format(target.name, shield_gain)) 
      target.max_shield += shield_gain
      report.add("{}'s max shield increased by {}! ".format(target.name, shield_gain)) 
      
      target.check_current_shield() 
    
    if self.attack_bonus != 0: 
      attack_gain = self.attack_bonus * amount
      target.base_attack += attack_gain
      report.add("{}'s base attack increased by {}! ".format(target.name, attack_gain)) 
      target.current_attack += attack_gain
      report.add('{} gained {} attack! '.format(target.name, attack_gain)) 
    
    if self.oxygen_bonus != 0: 
      oxygen_gain = self.oxygen_bonus * amount
      target.current_oxygen += oxygen_gain
      report.add('{} gained {} oxygen! '.format(target.name, oxygen_gain)) 
      target.max_oxygen += oxygen_gain
'''

# experiment space

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
