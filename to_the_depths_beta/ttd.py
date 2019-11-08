# -*- coding: utf-8 -*- 

import sys
import pickle
import asyncio
import logging
import os
import copy
# noinspection PyPackageRequirements
import discord
from . import chars, printing, reports, storage, ttd_tools, catalog, game as g, commands, help_articles
from .chars import * 
from .printing import print

'''
add help message for when the user enters an invalid command
fix TTD_Bot.prompt_for_message() to return the original message instead of the lowercase version
''' 

def clear_file(file):
    file.seek(0)
    file.truncate(0)

    print('cleared') 

def text_dump(file, thing): 
    thing = str(thing) 
    
    print('thing = {}'.format(thing)) 

    clear_file(file) 
    
    file.write(thing) 
    
    file.flush()
    os.fsync(file.fileno()) 

    print('successfully dumped') 

def text_load(file, default): 
    file.seek(0) 
    
    contents = file.read() 
    
    print(contents) 
    
    if len(contents) > 0: 
        result = eval(contents) 
        
        print(result) 
        
        return result
    else: 
        print('empty') 

        return default

class TTD_Bot(discord.Client, storage.Deconstructable): 
    command_groups = ('other', 'battle', 'items', 'game', 'movement', 'helpful', 'player') 

    command_filters = {filter_name: eval(f"lambda command_obj: {repr(filter_name)} in command_obj.groups") for filter_name in command_groups} 

    bot_commands = ttd_tools.Filterable(**command_filters) 

    categories = {
        'levels': catalog.levels, 
        'items': catalog.items, 
        'classes': catalog.classes, 
        'creatures': catalog.creatures, 
        'guides': help_articles.articles, 
    } 

    #help stuff
    #print(catalog.levels) 
    #print(catalog.items) 
    #print(catalog.classes) 
    #print(catalog.creatures) 

    def __init__(self, storage_file_name, safely_shutdown_file_name, owner_id, default_prefix, logs_file_name=None): 
        self.owner_id = owner_id
        self.default_prefix = default_prefix
        self.tasks = 0
        self.listening = False
        self.shutting_down = False
        self.needs_reloading = False
        self.needs_saving = False
        self.storage_file_name = storage_file_name
        self.storage_file = open(storage_file_name, mode='r+') 
        self.logs_file_name = logs_file_name
        self.logs_file = open(logs_file_name, mode='w+') if logs_file_name else sys.stdout
        self.safely_shutdown_file_name = safely_shutdown_file_name
        self.safely_shutdown_file = open(safely_shutdown_file_name, mode='r+') 
        self.status = discord.Status.offline
        self.current_activity = None
        self.afk = False
        self.game_data = {} 

        self.client = self
        
        sys.stderr = sys.stdout = self.logs_file

        discord.Client.__init__(self, status=self.status, activity=self.current_activity) 
        storage.Deconstructable.__init__(self) 
    
    def prefix(self, channel): 
        return self.default_prefix
    
    def sendable_filenames(self): 
        return {
            'storage', self.storage_file_name, 
            'logs', self.logs_file_name, 
        } 
    
    def channel_commands(self, channel): 
        return ttd_tools.Filterable((command(self, channel) for command in self.bot_commands), **self.command_filters) 
    
    @classmethod
    def bare_categories(cls): 
        categories = cls.categories.copy() 

        categories['commands'] = cls.bot_commands
        
        return categories.copy() 
    
    def help_categories(self, channel): 
        categories = self.categories

        categories['commands'] = self.channel_commands(channel) 
        
        return categories.copy() 
    
    def all_help_categories(self, channel): 
        categories = self.help_categories(channel) 

        all_categories = ttd_tools.Filterable() 

        for category, entries in categories.items(): 
            all_categories.extend(entries) 
        
        return all_categories.copy() 
    
    '''
    @contextlib.contextmanager
    def tuning_out(self): 
        self.listening = False

        yield

        self.listening = True
    ''' 

    @staticmethod
    async def default_special_args_check(self, report, author, *args): 
        return True
    
    @classmethod
    def command(cls, name, description, special_note=None, groups=('other',), indefinite_args=False, required_args=(), optional_args=(), special_args_check=default_special_args_check): 
        _name = name
        _description = description
        _special_note = special_note
        _groups = groups
        _indefinite_args = indefinite_args
        _required_args = required_args
        _optional_args = optional_args
        _special_args_check = special_args_check

        def decorator(func): 
            _func = func

            class New_Command(commands.Command): 
                func = _func
                name = _name
                description = _description
                special_note = _special_note
                groups = _groups
                indefinite_args = _indefinite_args
                required_args = _required_args
                optional_args = _optional_args
                special_args_check = _special_args_check
            
            cls.bot_commands.append(New_Command) 

            return New_Command
        
        return decorator

    async def change_presence(self, **kwargs): 
        #print(kwargs) 

        self.status = status = kwargs.get('status', self.status) 
        self.current_activity = activity = kwargs.get('activity', self.current_activity) 
        self.afk = afk = kwargs.get('afk', self.afk) 

        await discord.Client.change_presence(self, status=status, activity=activity, afk=afk) 

        print('successfully changed status to {}, activity to {}, and afk to {}'.format(self.status, self.current_activity, self.afk)) 
    
    async def load(self): 
        with self.tuning_out(): 
            self.game_data = text_load(self.storage_file, {}) 
            
            for channel_id, game_info in self.game_data.items(): 
                channel = self.get_channel(channel_id) 

                if channel is not None: 
                    self.game_data[channel_id] = reconstructed_game = self.reconstruct(game_info, self, channel)  
                    
                    print('{} in {}'.format(reconstructed_game, reconstructed_game.channel.name)) 
                else: 
                    del self.game_data[channel_id] 

                    print(f'channel with id {channel_id} is no longer accessible, game with data \
{game_info} was deleted') 
            
            await self.do_on_turn_on() 

            await self.save() 

            print('successfully loaded') 
            
            self.needs_reloading = False
    
    async def save(self, safely_shutdown=False): 
        with self.tuning_out(): 
            deconstructed = {channel_id: game.deconstruct() for channel_id, game in self.game_data.items()} 

            '''
            copied = {} 

            for channel_id, game in self.game_data.items(): 
            copied[channel_id] = game.deconstruct() 
            ''' 

            text_dump(self.storage_file, deconstructed) 

            text_dump(self.safely_shutdown_file, safely_shutdown) 

            print('successfully saved') 

            self.needs_saving = False

    async def edit_tasks(self, amount):
        self.tasks += amount

        print('now running {} tasks'.format(self.tasks))

        if self.tasks == 0: 
            print('all tasks done') 

            if self.needs_reloading: 
                print('reloading') 

                await self.load() 
            elif self.needs_saving: 
                print('saving') 

                await self.save() 

            if self.shutting_down: 
                print('all tasks done, will now shut down') 

                await self.logout() 
            else: 
                print('nothing to do here now') 

                await self.change_presence(status=discord.Status.online, activity=discord.Game('To the Depths')) 
    
    '''
    @acms.asynccontextmanager
    async def handling_task(self): 
        await self.edit_tasks(1) 

        yield

        await self.edit_tasks(-1) 
    ''' 

    def decode_mentions(self, report, mentions): 
        mentioned = [] 

        for mention in mentions: 
            to_append = None

            if mention.startswith('<@') and mention.endswith('>'): 
                stripped = mention[2:len(mention) - 1] 

                if stripped.startswith('!'): 
                    stripped = stripped[1:] 
                
                try: 
                    member_id = int(stripped) 
                except ValueError: 
                    pass
                else: 
                    to_append = report.channel.guild.get_member(member_id) 
            
            mentioned.append(to_append) 
        
        return set(mentioned) 
    
    def pulse_presence(self, **kwargs): 
        class Pulse_Presence: 
            client = self

            def __init__(self, status=client.status, activity=client.current_activity, afk=client.afk): 
                #print(kwargs) 

                self.old_status = self.client.status
                self.old_activity = self.client.current_activity
                self.old_afk = self.client.afk
                self.new_status = status
                self.new_activity = activity
                self.new_afk = afk
            
            async def __aenter__(self): 
                await self.client.change_presence(status=self.new_status, activity=self.new_activity, afk=self.new_afk) 

                print('temporarily changed to new presence') 
            
            async def __aexit__(self, typ, value, traceback): 
                await self.client.change_presence(status=self.old_status, activity=self.old_activity, afk=self.old_afk) 

                print('switched back to old presence') 
        
        return Pulse_Presence(**kwargs) 
    
    def tuning_out(self): 
        class Tuning_Out: 
            client = self

            def __enter__(self): 
                self.client.listening = False

                print('tuned out') 
            
            def __exit__(self, typ, value, traceback): 
                self.client.listening = True

                print('tuned back in') 
        
        return Tuning_Out() 
    
    def handling_message(self, message): 
        class Handling_Message: 
            client = self

            def __init__(self, message): 
                self.message = message
                self.channel = message.channel
                self.author = message.author
                self.report = reports.Report(self.client, self.channel) 

            async def __aenter__(self): 
                await self.client.edit_tasks(1) 

                print('handling: {}'.format(self.message.content)) 

                return self.report
            
            async def __aexit__(self, typ, value, traceback): 
                try: 
                    if typ is not None: 
                        owner_dm = self.client.get_user(self.client.owner_id) 
                        
                        await owner_dm.send(content='`{}` in channel `{}` in server `{}`: `{}`'.format(typ.__name__, self.channel, self.channel.guild if hasattr(self.channel, 'guild') else None, value)) 
                        
                        self.report.add('{}, something went wrong while running your command. A team of \
highly trained {}s has been dispatched to deal with this situation. '.format(self.author.mention, monkey_head_emoji)) 
                    
                    await self.report.send_self() 
                finally: 
                    print('finished handling: {}'.format(self.message.content)) 

                    await self.client.edit_tasks(-1) 
        
        return Handling_Message(message) 
    
    async def do_on_shutdown(self): 
        for channel_id, game in self.game_data.items(): 
            await game.on_shutdown() 
        
        await self.save(safely_shutdown=True) 
    
    async def do_on_turn_on(self): 
        should_continue = text_load(self.safely_shutdown_file, False) 

        if should_continue: 
            print('doing on_turn_ons') 

            for channel_id, game in self.game_data.items(): 
                report = reports.Report(self, game.channel) 

                await game.on_turn_on(report) 

                await report.send_self() 

    async def on_ready(self): 
        await self.load() 

        await self.change_presence(status=discord.Status.online, activity=discord.Game('To the Depths'))

        self.listening = True

        print('IM READY AF')

    async def logout(self):
        '''
        for channel_id, game in self.game_data.items():
          self.game_data[channel_id] = game.deconstruct()
  
        pickle_dump(self.storage_file, self.game_data) 
        ''' 

        await self.do_on_shutdown() 

        print('logging out! ')

        await discord.Client.logout(self) 
    
    @staticmethod
    async def do(to_do): 
        try: 
            return await to_do
        except discord.errors.Forbidden: 
            print('{} was forbidden'.format(to_do)) 

    async def prompt_for_message(self, report, member_id, choices=None, custom_check=lambda to_check: True, timeout=None, default_choice=None): 
        channel = report.channel
        mention = '<@{}>'.format(member_id) 

        extension = '{}, reply to this message with '.format(mention) 

        if choices is not None: 
            options = ttd_tools.format_iterable(choices, formatter='`{}`') 

            extension += 'one of the following: {}. '.format(options) 
        else: 
            extension += 'anything. ' 

        if timeout is not None:
            if default_choice is not None: 
                extension += 'There is a time limit of {} seconds to reply, after which your answer will default to `{}`'.format(timeout, default_choice) 
            else: 
                extension += 'There is a time limit of {} seconds to reply. '.format(timeout) 

        # noinspection PyShadowingNames
        def check(to_check): 
            valid_choice = choices is None or any(((to_check.content.lower() == choice.lower()) for choice in choices)) 
            
            print(to_check.channel.id == channel.id) 
            print(to_check.author.id == member_id) 
            print(valid_choice) 
            print(custom_check(to_check)) 
            
            return to_check.channel.id == channel.id and to_check.author.id == member_id and valid_choice and custom_check(to_check) 

        to_return = None

        report.add(extension) 

        await report.send_self() 

        try:
            message = await self.wait_for('message', check=check, timeout=timeout) 
        except asyncio.TimeoutError: 
            report.add('{}, time limit exceeded, going with default. '.format(mention)) 

            to_return = default_choice
        else: 
            to_return = message.content
        
        return to_return

    async def prompt_for_reaction(self, report, member_id, emojis=None, custom_check=lambda reaction, member: True, timeout=None, default_emoji=None): 
        channel = report.channel
        mention = '<@{}>'.format(member_id) 

        to_return = None

        extension = '{}, react to this message with '.format(mention) 

        if emojis is not None: 
            options = ttd_tools.format_iterable(emojis) 

            extension += 'one of the following: {}. '.format(options) 
        else: 
            extension += 'anything. ' 
        
        if timeout is not None:
            if default_emoji is not None: 
                extension += 'There is a time limit of {} seconds to react, after which your reaction will default to {}. '.format(timeout, default_emoji) 
            else: 
                extension += 'There is a time limit of {} seconds to react. '.format(timeout) 
        
        report.add(extension) 

        sent_messages = await report.send_self() 

        last_message = sent_messages[-1] 
        
        if last_message is not None: 
            if emojis is not None:
                for emoji in emojis: 
                    await self.do(last_message.add_reaction(emoji)) 
    
            # noinspection PyShadowingNames,PyShadowingNames
            def check(reaction, member):
                return reaction.message.id == last_message.id and member.id == member_id and (emojis is None or reaction.emoji in emojis) and custom_check(reaction, member) 
    
            try:
                reaction, member = await self.wait_for('reaction_add', check=check, timeout=timeout) 
            except asyncio.TimeoutError: 
                report.add('{}, time limit exceeded, going with default. '.format(mention)) 
    
                to_return = default_emoji
            else: 
                to_return = reaction.emoji
        else: 
            report.add(f'{mention}, something went wrong, going with default. ') 
            
            to_return = default_emoji
        
        return to_return
    
    async def run_command(self, report, author, command, args): 
        command_object = command(self, report.channel) 

        await command_object.run(report, author, args) 

    async def on_message(self, message): 
        if not self.shutting_down and not self.needs_reloading and self.listening and message.author.id != self.user.id: 
            channel = message.channel
            prefix = self.prefix(channel) 
            words = message.content.split() 

            if len(words) >= 1 and words[0].startswith(prefix): 
                async with self.handling_message(message) as report: 
                    author = message.author
                    
                    if not hasattr(channel, 'guild'): 
                        report.add("{}, you can't use me in a DM channel. ".format(author.mention)) 
                    else: 
                        permissions = channel.permissions_for(channel.guild.me) 
                        
                        if permissions.send_messages: 
                            async with channel.typing(): 
                                command, *arguments = words
                                command = command[len(prefix):] 
            
                                target_command = ttd_tools.search(self.bot_commands, command) 
            
                                if target_command is not None: 
                                    await self.run_command(report, author, target_command, arguments) 
                                else: 
                                    report.add(f"{author.mention}, that wasn't a valid command. Type `{prefix}{display_topics.name} commands` to view a list of all the commands for this bot. ") 
                        else: 
                            await self.do(message.add_reaction(zipper_mouth_emoji)) 

@TTD_Bot.command('shutdown', "Initiates the bot's shutdown sequence") 
@commands.requires_owner
async def shut_down(self, report, author): 
    await self.change_presence(activity=discord.Game('shutting down'), status=discord.Status.do_not_disturb) 

    self.shutting_down = True

    report.add("It's super effective! ") 
    report.add('{} fainted! '.format(self.user.mention)) 

async def creategame_args_check(self, report, author, *mentions): 
    actual_mentions = self.decode_mentions(report, mentions) 
    
    if None in actual_mentions: 
        report.add('{}, argument `mentions` must contain all valid mentions. '.format(author.mention)) 
    else: 
        return True

@TTD_Bot.command('creategame', 'Creates a new game in the current channel, and invites all mentioned people plus the sender into the game', groups=('game',), indefinite_args=True, optional_args=('mentions',), special_args_check=creategame_args_check) 
@commands.requires_no_game
@commands.modifying
async def create_game(self, report, author, *mentions): 
    if hasattr(report.channel, 'guild'): 
        to_invite = set(tuple(self.decode_mentions(report, mentions)) + (author,)) 
        
        new_game = g.Game(self, report.channel) 

        for member in to_invite: 
            await new_game.add_member(report, member) 

        self.game_data[report.channel.id] = new_game

        report.add('Success! A new game was created. ') 
    else: 
        report.add('Games cannot be created in DM channels. ') 

@TTD_Bot.command('invite', 'Invites all mentioned people into the game', groups=('game',), indefinite_args=True, required_args=('mentions',), special_args_check=creategame_args_check) 
@commands.requires_game
@commands.requires_player
@commands.action
async def invite_members(self, report, player, *mentions): 
    to_invite = self.decode_mentions(report, mentions) 

    await player.invite_members(report, to_invite) 

async def enter_args_check(self, report, author, class_choice): 
    target_class = ttd_tools.search(catalog.classes, class_choice) 

    if target_class is not None: 
        return True
    else: 
        report.add(f'{author.mention}, argument `class` must be a player class. Type `{self.prefix(report.channel)}{display_topics.name} classes` to see a list of all valid player classes. ') 

@TTD_Bot.command('enter', 'Enters the game as a player with the specified class', groups=('game',), required_args=('class',), special_args_check=enter_args_check) 
@commands.requires_no_player
@commands.modifying
async def enter_game(self, report, game, author, class_choice): 
    await game.add_player(report, author, class_choice) 

@TTD_Bot.command('start', 'Starts the game', groups=('game',)) 
@commands.requires_game
@commands.requires_player
@commands.modifying
async def start_game(self, report, player): 
    await player.start_game(report) 

@TTD_Bot.command('leave', "Leaves the game's **queue**", special_note="To leave the game's players list use `suicide` instead", groups=('game',)) 
@commands.requires_game
@commands.modifying
async def leave_game(self, report, game, author): 
    await game.remove_member(report, author) 

@TTD_Bot.command('viewgame', 'Displays info on the current game', groups=('game',)) 
@commands.requires_game
async def display_game(self, report, game, author): 
    report.add(game.stats_embed()) 

@TTD_Bot.command('suicide', 'Commits suicide', groups=('player',)) 
@commands.requires_game
@commands.requires_player
@commands.action
async def suicide(self, report, player): 
    await player.suicide(report) 

@TTD_Bot.command('endturn', 'Ends your game turn', groups=('game',)) 
@commands.requires_game
@commands.requires_player
@commands.requires_o_game_turn
async def end_turn(self, report, player): 
    await player.end_turn(report) 

@TTD_Bot.command('viewstats', "Without mentions, displays your own player's stats. With mentions, displays the stats of all mentioned people's players. ", groups=('player',), indefinite_args=True, optional_args=('mentions',), special_args_check=creategame_args_check) 
@commands.requires_game
async def display_players(self, report, game, author, *mentions): 
    if len(mentions) > 0: 
        mentioned = self.decode_mentions(report, mentions) 
    else: 
        mentioned = [author] 
    
    for member in mentioned: 
        player = game.get_player(member.id) 

        if player is not None: 
            report.add(player.stats_embed()) 
        else: 
            report.add('{} is not in this game. '.format(member.mention)) 

@TTD_Bot.command('viewitems', "Without mentions, displays your own player's items. With mentions, displays the items of all mentioned people's players. ", groups=('player', 'items'), indefinite_args=True, optional_args=('mentions',), special_args_check=creategame_args_check) 
@commands.requires_game
async def display_items(self, report, game, author, *mentions): 
    if len(mentions) > 0: 
        mentioned = self.decode_mentions(report, mentions) 
    else: 
        mentioned = [author] 
    
    for member in mentioned: 
        player = game.get_player(member.id) 

        if player is not None: 
            await player.display_items(report) 
        else: 
            report.add('{} is not in this game. '.format(member.mention)) 

@TTD_Bot.command('viewenemy', "Without mentions, displays your own opponent's stats. With mentions, displays the stats of the opponents of all mentioned people's players. ", groups=('battle',), indefinite_args=True, optional_args=('mentions',), special_args_check=creategame_args_check) 
@commands.requires_game
async def display_enemies(self, report, game, author, *mentions): 
    if len(mentions) > 0: 
        mentioned = self.decode_mentions(report, mentions) 
    else: 
        mentioned = [author] 
    
    for member in mentioned: 
        player = game.get_player(member.id) 

        if player is not None: 
            if player.enemy is not None: 
                report.add(player.enemy.stats_embed()) 
            else: 
                report.add('{} is not currently fighting anyone. '.format(player.name)) 
        else: 
            report.add('{} is not in this game. '.format(member.mention)) 

async def gather_args_check(self, report, author, item): 
    target_item = ttd_tools.search(catalog.items, item) 

    if target_item is not None and target_item.gatherable(): 
        return True
    else: 
        report.add('{}, argument `item` must be a gatherable item. '.format(author.mention)) 

@TTD_Bot.command('gather', 'Attempts to gather the specified item', special_note='This command takes your move', groups=('items', 'movement'), required_args=('item',), special_args_check=gather_args_check) 
@commands.requires_game
@commands.requires_player
@commands.requires_can_move
async def gather_item(self, report, player, item): 
    await player.gather(report, item) 

async def help_args_check(self, report, author, *topics): 
    total_topics = self.all_help_categories(report.channel) 

    results = ttd_tools.bulk_search(total_topics, topics) 

    if None in results: 
        report.add('{}, argument `topics` must contain all valid help topics. '.format(author.mention)) 
    else: 
        return True

@TTD_Bot.command('help', f'Without arguments, displays help on the `{help_articles.Introduction.name}` guide. With arguments, displays help on all specified topics. ', 
                 special_note="Use the `list` command to view a list of all the valid help entries (look it up with this command for more "
                              "info on how to use it). ", groups=('helpful',), 
                 indefinite_args=True, 
                 optional_args=(
            'topics',), 
                 special_args_check=help_args_check) 
async def display_help(self, report, author, *topics): 
    total_topics = self.all_help_categories(report.channel)

    if len(topics) == 0: 
        topics = (help_articles.Introduction.name,) 
    
    results = ttd_tools.bulk_search(total_topics, topics) 

    for topic in results: 
        report.add(topic.help_embed()) 

async def list_args_check(self, report, author, category, *filters): 
    help_categories = self.help_categories(report.channel) 
    
    if category.lower() not in help_categories: 
        categories_str = ttd_tools.format_iterable(help_categories.keys(), formatter='`{}`') 
        
        report.add('{}, argument `category` must be one of the following: {}. '.format(author.mention, categories_str)) 
    else: 
        entries = help_categories[category.lower()] 

        valid_filters = entries.valid_names(filters) 

        if not valid_filters: 
            names_str = ttd_tools.format_iterable(entries.filters.keys(), formatter='`{}`') or None

            report.add(f'{author.mention}, valid filters for category `{category}` can only be the following: \
{names_str}. ') 
        else: 
            return True

bare_categories = TTD_Bot.bare_categories() 

categories_str = ttd_tools.format_iterable(bare_categories.keys(), formatter='`{}`') 

category_filters = [] 

for category, entries in bare_categories.items(): 
    filters_str = ttd_tools.format_iterable(entries.filters.keys(), formatter='`{}`') if entries.filters \
else None

    category_filters.append(f'`{category}` - {filters_str}') 

category_filters_str = ttd_tools.make_list(category_filters) 

@TTD_Bot.command('list', 'Lists all the valid help entries corresponding to the specified category \
that pass the specified filters', 
special_note=f'''Valid categories and filters for each category are: 

{category_filters_str}

Filters stack; specifying multiple filters means listing entries that pass **all** of them. ''', 
groups=('helpful',), indefinite_args=True, required_args=('category',), optional_args=('filters',), 
                 special_args_check=list_args_check) 
async def display_topics(self, report, author, category, *filters): 
    help_categories = self.help_categories(report.channel) 
    
    all_topics = help_categories[category.lower()] 

    filtered = all_topics.get_filtered(filters) 
    
    filtered.sort(key=lambda item: item.name.lower()) 

    topic_names = (topic.name for topic in filtered) 
    topics_str = ttd_tools.make_list(topic_names) or 'None' 

    filters_set = set(map(str.lower, filters)) 
    filters_str = ttd_tools.format_iterable(filters_set, formatter='`{}`') or None
    
    embed = discord.Embed(title=f'All help entries in category `{category}` with filter(s) {filters_str}', description=topics_str)  

    embed.add_field(name='Important note', value='Look up any topics with the `help` command for more info about them. For multi-word topics, '
                                                 'such as `Sky Blade`, all spaces must be '
                                                 'replaced with underscores (`_`) for \
            the `help` command to recognize them. ') 

    report.add(embed) 

@TTD_Bot.command('announce', 'Announces') 
@commands.requires_owner
async def announce(self, report, author): 
    report.add('{}, what to announce? '.format(author.mention)) 
    
    announcement = await self.prompt_for_message(report, author.id) 

    if announcement != 'CANCEL': 
        for guild in self.guilds: 
            messageables = tuple((channel for channel in guild.text_channels if channel.permissions_for(guild.me).send_messages)) 

            if len(messageables) > 0: 
                to_message = messageables[0] 

                await to_message.send(content=announcement) 
            else: 
                print('{} has no messageable channels'.format(guild.name)) 

@TTD_Bot.command('fight', 'Starts a battle with a random creature from your current level', special_note='This command takes your move', groups=('battle', 'movement')) 
@commands.requires_game
@commands.requires_player
@commands.requires_can_move
async def start_battle(self, report, player): 
    await player.pick_fight(report) 

async def coinflip_args_check(self, report, author, side): 
    if side.lower() in ('heads', 'tails'): 
        return True
    else: 
        report.add('{}, argument `side` can only be `heads` or `tails`. '.format(author.mention)) 

@TTD_Bot.command('call', 'Call a side in a coin flip to decide who gets the next battle turn', groups=('battle',), required_args=('side',), special_args_check=coinflip_args_check) 
@commands.requires_game
@commands.requires_player
@commands.requires_neither_battle_turn
@commands.action
async def battle_call(self, report, player, side): 
    await player.battle_call(report, side) 

@TTD_Bot.command('attack', 'Attacks your opponent', special_note='This command takes your battle turn', groups=('battle',)) 
@commands.requires_game
@commands.requires_player
@commands.requires_battle_turn
@commands.action
async def attack(self, report, player): 
    await player.switch_attack(report) 

async def use_args_check(self, report, author, item, amount='1'): 
    target_item = ttd_tools.search(catalog.items, item) 

    if target_item is not None and target_item.is_usable: 
        if amount.lower() == 'auto' or (amount.isnumeric() and int(amount) > 0): 
            return True
        else: 
            report.add('{}, argument `amount` must either be `auto` or a whole number greater than 0. '.format(author.mention)) 
    else: 
        report.add('{}, argument `item` must be a usable item. '.format(author.mention)) 

@TTD_Bot.command('use', 'Uses the specified amount of the specified item', special_note='The amount can be auto-decided based on the item if amount is set to '
                        '`auto`. Omitting the amount makes it default to 1. ', groups=('items',), required_args=('item',), optional_args=('amount',), 
                 special_args_check=use_args_check) 
@commands.requires_game
@commands.requires_player
@commands.requires_uo_game_turn
async def use_item(self, report, player, item, amount='1'): 
    await player.use_item(report, item, amount) 

@TTD_Bot.command('regen', f'Regens {catalog.Player.regen_percent:.0%} of your max HP', special_note='This command takes your move', groups=('player', 'movement'))  
@commands.requires_game
@commands.requires_player
@commands.requires_can_move
async def free_regen(self, report, player): 
    await player.free_regen(report) 

@TTD_Bot.command('flee', 'Attempts to flee the battle', special_note='This command takes your battle turn', groups=('battle',))  
@commands.requires_game
@commands.requires_player
@commands.requires_battle_turn
@commands.action
async def attempt_flee(self, report, player): 
    await player.attempt_flee(report) 

@TTD_Bot.command('crash', 'Makes the bot have an error') 
@commands.requires_owner
@commands.modifying
async def crash(self, report, author): 
    report.add('crashing! ') 

    print('crashing! ') 

    raise ZeroDivisionError('test') 

async def donate_args_check(self, report, author, target, *to_donate): 
    items = to_donate[::2] 
    amounts = to_donate[1::2] 
    
    if None in self.decode_mentions(report, (target,)): 
        report.add('{}, argument `target` must be a valid mention. '.format(author.mention)) 
    elif len(items) != len(amounts): 
        report.add('{}, each item must correspond with an amount. '.format(author.mention)) 
    else: 
        item_results = ttd_tools.bulk_search(catalog.items, items) 
        valid_amounts = ((amount.lower() == 'all' or (amount.isnumeric() and int(amount) > 0)) for amount in amounts) 

        if None in item_results: 
            report.add('{}, not all the items you specified are valid. '.format(author.mention)) 
        elif not all(valid_amounts): 
            report.add('{}, not all the amounts you specified are valid. Valid amounts are `all` and whole numbers greater than 0. '.format(author.mention)) 
        else: 
            return True

def convert_donation(specified): 
    items = specified[::2] 
    amounts = specified[1::2] 

    items = (ttd_tools.search(catalog.items, item) for item in items) 
    
    donation_dict = {} 
    
    for item, amount in zip(items, amounts): 
        if not amount.isnumeric(): 
            donation_dict[item] = amount
        elif item not in donation_dict: 
            donation_dict[item] = int(amount) 
        elif type(donation_dict[item]) is int: 
            donation_dict[item] += int(amount) 
    
    return donation_dict

@TTD_Bot.command('donate', 'Donates the specified amounts of the specified items to the mentioned player', special_note='Items and amounts to '
'donate are specified in '
'pairs of item and amount, '
'like this: `item amount`. '
'Each pair is separated by '
'a space. Amounts can be '
'specified as `all` to '
'donate all you have of '
'that item. Example: `('
'prefix)donate @bob coral 2 meat 5 sky_blade all` to donate 2 Coral, 5 Meat, and all your Sky Blades to bob. \
**Players must be in the same level to donate to each other.** ', groups=('items',), indefinite_args=True, 
required_args=('target', 'item_1', 'amount_1'), optional_args=('item_2', 'amount_2', '...'), special_args_check=donate_args_check) 
@commands.requires_game
@commands.requires_player
@commands.requires_uo_game_turn
async def whitelist_donate(self, report, player, target, *to_donate): 
    mentions = self.decode_mentions(report, (target,)) 
    
    mention = tuple(mentions)[0] 
    
    donate_to = player.game.get_player(mention.id) 

    if donate_to is not None: 
        if donate_to is player: 
            report.add("Unlike {}, {} is smart and realizes there's no point in trying to donate to themselves. ".format(player.mention, player.name)) 
        elif player.current_level != donate_to.current_level: 
            report.add("{0} can't donate to {1} because they're in different levels; {0} is in the {2} while {1} is in the {3}. ".format(player.name, donate_to.name, player.current_level.name, donate_to.current_level.name)) 
        else: 
            donation_dict = convert_donation(to_donate)  
            
            donation = [(item, amount) for item, amount in donation_dict.items()] 
            
            print(donation) 

            await player.whitelist_donate(report, donate_to, donation) 
    else: 
        report.add('{} cannot donate to {} because they are not in this game. '.format(player.name, mention.mention)) 

@TTD_Bot.command('donateall', 'Donates everything except for the specified items', special_note=f'Same restrictions and usage as \
`{whitelist_donate.name}` command', groups=('items',), indefinite_args=True, required_args=('target',), 
optional_args=('item_1', 'amount_1', 'item_2', 'amount_2', '...'), special_args_check=donate_args_check) 
@commands.requires_game
@commands.requires_player
@commands.requires_uo_game_turn
async def blacklist_donate(self, report, player, target, *blacklist): 
    mentions = self.decode_mentions(report, (target,)) 

    mention = tuple(mentions)[0] 

    donate_to = player.game.get_player(mention.id) 

    if donate_to is not None: 
        if donate_to is player: 
            report.add("Unlike {}, {} is smart and realizes there's no point in trying to donate to themselves. ".format(player.mention, player.name)) 
        elif player.current_level != donate_to.current_level: 
            report.add("{0} can't donate to {1} because they're in different levels; {0} is in the {2} while {1} is in the {3}. ".format(player.name, donate_to.name, player.current_level.name, donate_to.current_level.name)) 
        else: 
            blacklist_dict = convert_donation(blacklist) 

            await player.blacklist_donate(report, donate_to, blacklist_dict) 
    else: 
        report.add('{} cannot donate to {} because they are not in this game. '.format(player.name, mention.mention)) 

@TTD_Bot.command('setname', "Without an argument, brings up a prompt to change your player's name. With an argument, changes your player's name to the argument. ", groups=('player',), optional_args=('name',), special_args_check=catalog.Player.setname_args_check) 
@commands.requires_game
@commands.requires_player
@commands.modifying
async def set_name(self, report, player, name=None): 
    await player.set_name(report, name) 

async def move_args_check(self, report, author, direction): 
    if direction.lower() not in ('up', 'down'): 
        report.add('{}, argument `direction` must be `up` or `down`. '.format(author.mention)) 
    else: 
        return True

@TTD_Bot.command('move', 'Moves `up` or `down` a level', special_note='This command takes your move', groups=('movement',), required_args=('direction',), special_args_check=move_args_check) 
@commands.requires_game
@commands.requires_player
@commands.requires_can_move
async def move(self, report, player, direction): 
    await player.change_levels(report, direction) 

async def craft_args_check(self, report, author, item, amount): 
    target_item = ttd_tools.search(catalog.items, item) 

    if target_item is None or not target_item.craftable(): 
        report.add('{}, argument `item` must be a craftable item. '.format(author.mention)) 
    elif not amount.isnumeric() or int(amount) <= 0: 
        report.add('{}, argument `amount` must be a whole number greater than 0. '.format(author.mention)) 
    else: 
        return True

@TTD_Bot.command('craft', 'Crafts the specified amount of the specified item', special_note='This command takes your move', groups=('items', 'movement'), required_args=('item', ' \
                                                                                                                                         ''amount'), 
                 special_args_check=craft_args_check) 
@commands.requires_game
@commands.requires_player
@commands.requires_can_move
async def craft(self, report, player, item, amount): 
    await player.craft(report, item, amount) 

@TTD_Bot.command('drag', 'Moves either `up` or `down`, dragging your opponent with you. ', 
                 special_note=f'This command is only usable by the {catalog.Diver.name} class. It also takes your battle turn. ', 
                 groups=('battle',), required_args=('direction',), special_args_check=move_args_check) 
@commands.requires_game
@commands.requires_player
@commands.requires_battle_turn
async def drag(self, report, player, direction): 
    if player.is_a(catalog.Diver): 
        await player.drag(report, direction) 
    else: 
        report.add("{} can't drag because they aren't a Diver. ".format(player.name)) 

async def mine_args_check(self, report, author, item, side): 
    target_item = ttd_tools.search(catalog.items, item) 
    
    if target_item is None or not target_item.is_a(catalog.Mineable): 
        report.add(f'{author.mention}, argument `item` must be a valid mineable item. ') 
    elif side.lower() not in ('heads', 'tails'): 
        report.add(f'{author.mention}, argument `side` can only be `heads` or `tails`. ') 
    else: 
        return True

@TTD_Bot.command('mine', 'Attempts to mine the specified item, calling the specified side', special_note=f'A {catalog.Shovel.name} or '
                                                                                                         f'{catalog.Big_Shovel.name} is required to '
                                                                                                         f'mine. This command also takes your move. ', 
groups=('items', 'movement'), required_args=('item', 'side'), special_args_check=mine_args_check) 
@commands.requires_game
@commands.requires_player
@commands.requires_can_move
async def mine(self, report, player, item, side): 
    if player.has_item(catalog.Shovel) or player.has_item(catalog.Big_Shovel): 
        to_mine = ttd_tools.search(catalog.items, item) 
        
        await player.mine(report, to_mine, side) 
    else: 
        report.add(f"{player.name} can't mine because they don't have a {catalog.Shovel.name} or {catalog.Big_Shovel.name}. ") 

@TTD_Bot.command('regenshield', f"Fully regenerates your player's shield, at the cost of {catalog.Watt.name}", 
                 special_note=f'The {catalog.Watt.name} cost to regen your shield is the sum of the {catalog.Watt.name} costs of all your shields. '
                              f'The {catalog.Watt.name} cost of any shield item can be viewed by looking it up with the `help` command. ', 
groups=('player', 'items')) 
@commands.requires_game
@commands.requires_player
@commands.requires_uo_game_turn
async def regen_shield(self, report, player): 
    await player.regen_shield(report) 

@TTD_Bot.command('deletegame', 'Deletes the game') 
@commands.requires_owner
@commands.requires_game
@commands.modifying
async def delete_game(self, report, game, author): 
    report.add(f'{author.mention}, are you sure you want to delete this game? ') 

    emoji = await self.prompt_for_reaction(report, author.id, emojis=(thumbs_up_emoji, 
thumbs_down_emoji), timeout=10, default_emoji=thumbs_down_emoji) 

    if emoji == thumbs_up_emoji: 
        del self.game_data[game.channel.id]

        report.add('The game was successfully deleted. ') 
    else: 
        report.add('The game was not deleted. ') 

@TTD_Bot.command('clearlogs', 'Clears the logs file') 
@commands.requires_owner
async def clear_logs(self, report, author): 
    clear_file(self.logs_file) 

    report.add(f'The file was cleared. ') 

async def sendfile_args_check(self, report, author, file_type): 
    sendable_names = self.sendable_filenames() 

    if file_type.lower() not in sendable_names: 
        valid_names = ttd_tools.format_iterable(sendable_names.keys(), formatter='`{}`') 

        report.add(f'{author.mention}, argument `filetype` can only be one of the following: {valid_names}') 
    else: 
        return True 

@TTD_Bot.command('sendfile', 'Sends the requested file', required_args=('filetype',), 
special_args_check=sendfile_args_check) 
@commands.requires_owner
async def send_logs(self, report, author, file_type): 
    filename = self.sendable_names()[file_type.lower()] 

    if filename: 
        with open(filename, mode='rb'): 
            report.add(discord.File(filename)) 
    else: 
        report.add(f"{author.mention}, this file isn't sendable. ") 