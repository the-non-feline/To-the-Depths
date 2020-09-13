import discord
from . import file_io, ttd_tools
from .file_io import debug
from .ttd_tools import format_iterable

'''
add special notes for commands
''' 

class Command: 
    func = None
    name = '' 
    description = '' 
    special_note = None
    groups = () 
    indefinite_args = () 
    required_args = () 
    optional_args = () 
    special_args_check = None

    def __init__(self, client, channel): 
        self.client = client
        self.channel = channel
        self.total_args = list(self.required_args) + list(self.optional_args) 

        if self.indefinite_args: 
            self.total_args[-1] = f'*{self.total_args[-1]}' 
        
        for index in range(len(self.total_args)): 
            val = self.total_args[index] 

            if val in self.required_args: 
                self.total_args[index] = f'({val})' 
            else: 
                self.total_args[index] = f'[{val}]' 

        #debug(self.total_args) 
        
        prefix = self.client.prefix(self.channel) 
        args_str = format_iterable(self.total_args, formatter=' {}', sep='') 
        self.syntax = prefix + self.name + args_str

    '''
    def __init__(self, func, name, description, indefinite_args, required_args, optional_args, special_args_check): 
        self.func = func
        self.name = name
        self.description = description
        self.indefinite_args = indefinite_args
        self.required_args = required_args
        self.optional_args = tuple(('[{}]'.format(arg) for arg in optional_args)) 
        self.total_args = list(self.required_args + self.optional_args) 

        if self.indefinite_args: 
            self.total_args[-1] = '*{}'.format(self.total_args[-1]) 
        
        args_str = format_iterable(self.total_args, formatter=' {}', sep=' ') 
        self.syntax = '(prefix)' + self.name + args_str
        
        self.special_args_check = special_args_check
    ''' 

    def help_embed(self): 
        embed = discord.Embed(title=self.name, type='rich', description=self.description) 

        embed.add_field(name='Usage', value=f'''`{self.syntax}` 

`(` and `)` mean required arguments, `[` and `]` mean optional arguments; `*` means "unlimited" arguments (you can put as many arguments as you want there) ''', 
inline=False) 

        if self.special_note is not None: 
            embed.add_field(name='Important note', value=self.special_note, inline=False) 
        
        groups_str = ttd_tools.format_iterable(self.groups) or None

        embed.add_field(name='Categories', value=groups_str) 

        '''
        embed.add_field(name='Usage - `[` and `]` denote optional arguments; `*` denotes "indefinite" arguments (that is, you can put as many arguments as you want there) ', value='`{}`'.format(self.syntax)) 
        ''' 

        return embed
    
    async def check_args(self, report, author, args): 
        valid = False

        if len(args) < len(self.required_args): 
            missing_args = self.required_args[len(args):] 
            missing_str = format_iterable(missing_args, formatter='`{}`') 

            report.add('{}, `{}` is missing arguments {}. '.format(author.mention, self.name, missing_str)) 
        elif not self.indefinite_args and len(args) > len(self.total_args): 
            report.add('{}, you gave too many arguments to `{}`; it only needs {}. '.format(author.mention, self.name, len(self.total_args))) 
        elif await self.__class__.special_args_check(self.client, report, author, *args): 
            valid = True
        
        return valid
    
    async def run(self, report, author, args): 
        #debug(self.func) 
        #debug(self.special_args_check) 

        if await self.check_args(report, author, args): 
            return await self.__class__.func(self.client, report, author, *args) 
        else: 
            report.add(self.help_embed()) 

''' 
async def default_special_args_check(report, author, args): 
    return True

def command(name, description, indefinite_args=False, required_args=(), optional_args=(), special_args_check=default_special_args_check): 
    def decorator(func): 
        return Command(func, name, description, indefinite_args, required_args, optional_args, special_args_check) 
    
    return decorator
''' 

def requires_owner(func): 
    async def arequiring_func(self, report, author, *args): 
        if author.id == self.owner_id: 
            return await func(self, report, author, *args) 
        else: 
            report.add('But it failed! ') 
    
    return arequiring_func

def requires_no_game(func): 
    async def brequiring_func(self, report, author, *args): 
        if report.channel.id not in self.game_data: 
            return await func(self, report, author, *args) 
        else: 
            report.add('{}, there is already a game here. '.format(author.mention)) 
    
    return brequiring_func

def requires_game(func): 
    async def crequiring_func(self, report, author, *args): 
        if report.channel.id in self.game_data: 
            game = self.game_data[report.channel.id] 

            return await func(self, report, game, author, *args) 
        else: 
            report.add('{}, there is no game here. '.format(author.mention)) 
    
    return crequiring_func

def requires_no_player(func): 
    @requires_game
    async def drequiring_func(self, report, game, author, *args): 
        player = game.get_player(author.id) 

        if player is None: 
            return await func(self, report, game, author, *args) 
        else: 
            report.add('{}, you are already in the game as {}. '.format(author.mention, player.name)) 
    
    return drequiring_func

def requires_player(func): 
    async def erequiring_func(self, report, game, author, *args): 
        player = game.get_player(author.id) 

        if player is not None: 
            return await func(self, report, player, *args) 
        else: 
            report.add('{}, you are not in this game. '.format(author.mention)) 
    
    return erequiring_func

def requires_pet(func): 
    async def pet_requiring_func(self, report, player, *args): 
        if player.pet: 
            return await func(self, report, player, *args) 
        else: 
            report.add(f"{player.mention}, you don't have a pet. ") 
    
    return pet_requiring_func

def modifying(func): 
    async def modifying_func(self, report, *args): 
        try: 
            result = await func(self, report, *args) 
        except: 
            self.needs_reloading = True

            debug('error, client now needs reloading') 

            report.add(f'An epic error occurred, the bot will reload from the last save point so that \
everything is good. ')

            await self.change_presence(status=discord.Status.do_not_disturb, activity=discord.Game('recovering from error')) 

            raise
        else: 
            self.needs_saving = True

            debug('successful, client now needs saving') 

            return result
    
    return modifying_func

def action(func): 
    @modifying
    async def action_func(self, report, player, *args): 
        if player.current_actions > 0: 
            report.add('{} cannot do this right now because they are in the middle of something. '.format(player.name)) 
        else: 
            return await func(self, report, player, *args) 
    
    return action_func

def blockable_action(func): 
    @action
    async def blockable_func(self, report, player, *args): 
        if player.enemy and not player.decided_first: 
            report.add(f'{player.name}, you must start the first round of your current fight before you can \
do anything. Use the `fight` command to do so. ') 
        else: 
            return await func(self, report, player, *args) 
    
    return blockable_func

def requires_uo_game_turn(func): 
    @blockable_action
    async def frequiring_func(self, report, player, *args): 
        if player.game.current_turn_index < 0: 
            report.add('{}, the game has not started yet. '.format(player.name)) 
        elif not player.uo_game_turn: 
            report.add("{}, it's not your game turn. ".format(player.name)) 
        elif player.enemy is not None and player.enemy.battle_turn: 
            report.add("{}, you can't do this on your enemy's battle turn. ".format(player.name)) 
        else: 
            return await func(self, report, player, *args) 
    
    return frequiring_func

def requires_no_battle(func): 
    async def grequiring_func(self, report, player, *args): 
        if player.enemy is None: 
            return await func(self, report, player, *args) 
        else: 
            report.add("{}, you can't do this in the middle of a battle. ".format(player.name)) 
    
    return grequiring_func

def requires_battle(func): 
    async def hrequiring_func(self, report, player, *args): 
        if player.enemy is not None: 
            return await func(self, report, player, *args) 
        else: 
            report.add('{}, you are not currently fighting anyone. '.format(player.name)) 
    
    return hrequiring_func

def requires_neither_battle_turn(func): 
    @requires_battle
    async def irequiring_func(self, report, player, *args): 
        if player.battle_turn: 
            report.add("{}, you can't do this right now since it's your battle turn. ".format(player.name)) 
        elif player.enemy.battle_turn: 
            report.add("{}, you can't do this right now since it's your opponent {}'s battle turn. ".format(player.name, player.enemy.name)) 
        else: 
            return await func(self, report, player, *args) 
    
    return irequiring_func

def requires_battle_turn(func): 
    @requires_battle
    async def jrequiring_func(self, report, player, *args): 
        if player.battle_turn: 
            return await func(self, report, player, *args) 
        else: 
            report.add("{}, you can't do this right now since it's not your battle turn. ".format(player.name)) 
    
    return jrequiring_func

def requires_o_game_turn(func): 
    @requires_uo_game_turn
    @requires_no_battle
    async def requiring_func(self, report, player, *args): 
        if not player.o_game_turn: 
            report.add("{}, it's not your game turn. ".format(player.name)) 
        else: 
            return await func(self, report, player, *args) 
    
    return requiring_func

def requires_can_move(func): 
    @requires_o_game_turn
    async def requiring_func(self, report, player, *args): 
        if player.can_move: 
            return await func(self, report, player, *args) 
        else: 
            report.add('{}, you already used your move. '.format(player.name)) 
    
    return requiring_func
