import random
import asyncio
import logging
# noinspection PyPackageRequirements
import discord
from . import custom_contextlib as contextlib, printing, ttd_tools, catalog
from .printing import print
from .ttd_tools import format_iterable

'''
to-do

change how users choose their names
''' 

class Game(ttd_tools.Game_Object): 
    def __init__(self, client, channel): 
        self.queue = [] 
        self.players = []
        self.current_turn_index = -1
        self.current_player = None
        self.saved_stuff = {} 

        ttd_tools.Game_Object.__init__(self, client, channel) 
    
    @staticmethod
    def modify_deconstructed(deconstructed): 
        del deconstructed['current_player']

        players = deconstructed['players'].copy()

        for index in range(len(players)):
            players[index] = players[index].deconstruct()

        deconstructed['players'] = players

        ttd_tools.Game_Object.modify_deconstructed(deconstructed) 

    def reconstruct_next(self):
        for index in range(len(self.players)):
            self.players[index] = self.reconstruct(self.players[index], self.client, self.channel, self)

        if self.current_turn_index >= 0:
            self.current_player = self.players[self.current_turn_index] 
    
    async def on_shutdown(self): 
        for player in self.players: 
            await player.on_global_event(None, 'shutdown') 
    
    async def on_turn_on(self, report): 
        actings = (player.acting(report) for player in self.players) 

        async with contextlib.AsyncExitStack() as stack: 
            for acting in actings: 
                await stack.enter_async_context(acting) 

            for player in self.players: 
                await player.on_global_event(report, 'turn_on') 
    
    def stats_embed(self): 
        embed = discord.Embed(type='rich') 
        
        queue_str = format_iterable(self.queue, formatter='<@{}>') 
        player_names = (player.name for player in self.players) 
        players_str = format_iterable(player_names) 

        embed.add_field(name='Queue', value=queue_str if len(queue_str) > 0 else 'Empty') 
        embed.add_field(name='Players', value=players_str if len(players_str) > 0 else 'Empty') 

        ''' 
        if len(self.queue) > 0:
            queue_names = ('`{}`'.format(self.channel.guild.get_member(member_id)) for member_id in self.queue)

            embed.add_field(name='Queue', value=', '.join(queue_names)) 
        else:
            embed.add_field(name='Queue', value='Empty')

        if len(self.players) > 0:
            players_names = ('`{}`'.format(player.name) for player in self.players) 

            embed.add_field(name='Players', value=', '.join(players_names))
        else:
            embed.add_field(name='Players', value='Empty') 
        ''' 

        embed.add_field(name='Current turn', value=self.current_player.name if self.current_player is not None else None) 

        embed.add_field(name='Saved stuff', value=self.saved_stuff) 

        return embed

    '''
    def current_player(self): 
      if len(self.players) > 0: 
        return self.players[self.current_turn_index] 
      else: 
        return None
    '''

    def get_player(self, member_id):
        for player in self.players:
            if player.member_id == member_id:
                return player

        return None

    def has_power(self, member_id):
        return self.get_player(member_id) is not None or member_id in self.queue
    
    async def pause_or_delete(self, report):
        if len(self.queue) > 0:
            # pause
            self.current_turn_index = -1
            self.current_player = None

            report.add('All players have left, but queue is not empty, so the game is now paused. ')
        else:
            # delete
            del self.client.game_data[self.channel.id]

            report.add('All players have left and the queue is empty, so the game was deleted. ') 
    
    async def remove_player(self, report, player): 
        removed_player_index = self.players.index(player)

        self.players.remove(player) 
        self.queue.append(player.member_id) 

        # account for changed length of self.players
        if self.current_turn_index >= removed_player_index:
            self.current_turn_index -= 1
        
        report.add(f'{player.mention} was removed from the game and added to the queue. ') 

        if len(self.players) == 0: 
            await self.pause_or_delete(report) 
        elif player.o_game_turn: 
            await self.next_turn(report) 
    
    async def add_member(self, report, member):
        player = self.get_player(member.id)

        if player is not None:
            report.add('{} is already in the game, as {}. '.format(member.mention, player.name))
        elif member.id in self.queue:
            report.add('{} is already in the queue. '.format(member.mention)) 
        else: 
            self.queue.append(member.id) 
            
            report.add('{} was added to the queue. '.format(member.mention))
        '''
        else: 
            report.add('{} was not added as bots are not allowed in games. '.format(member.mention)) 
        ''' 
    
    async def invite_members(self, report, members): 
        for member in members: 
            await self.add_member(report, member) 
    
    async def add_player(self, report, member, class_choice): 
        if member.id in self.queue: 
            chosen_class = ttd_tools.search(catalog.classes, class_choice) 

            new_player = chosen_class(self.client, self.channel, self, member_id=member.id) 

            if self.current_turn_index >= 0: 
                index = self.current_turn_index
                
                # increments current_turn_index to account for player inserted before
                self.current_turn_index += 1
            else: 
                # choose a random position to insert the new player into
                index = random.randint(0, len(self.players)) 

            self.players.insert(index, new_player) 
            self.queue.remove(member.id) 

            async with new_player.acting(report): 
                await new_player.on_life_start(report) 
                
                report.add('Success! {} joined the game. '.format(member.mention)) 
        else:
            report.add('{} cannot join the game as they are not in the queue. '.format(member.mention)) 
    
    async def remove_member(self, report, member): 
        '''
        player = self.get_player(member.id) 

        if player is not None: 
            await player.suicide() 
        ''' 

        if member.id in self.queue: 
            self.queue.remove(member.id)

            report.add('{} was removed from the queue. '.format(member.mention))

            if len(self.players) == 0: 
                await self.pause_or_delete(report) 
        else: 
            report.add("{} is not in this game's queue. ".format(member.mention)) 
    
    async def remove_members(self, report, members): 
        for member in members: 
            await self.remove_member(report, member) 
    
    async def start(self, report): 
        if self.current_turn_index >= 0: 
            report.add('The game has already started. ') 
        else:
            report.add('Starting! ') 

            await self.next_turn(report) 
    
    async def next_turn(self, report):
        if self.current_player is not None:
            self.current_player.o_game_turn = False

            await self.current_player.on_global_event(report, 'game_turn_end') 
        
        self.current_turn_index += 1

        if self.current_turn_index >= len(self.players):
            self.current_turn_index = 0

        self.current_player = self.players[self.current_turn_index]

        self.current_player.o_game_turn = True
        
        report.add("It is now {}'s turn. ".format(self.current_player.mention)) 

        async with self.current_player.acting(report): 
            await self.current_player.on_global_event(report, 'game_turn_start') 
            await self.current_player.before_action(report) 

        ''' 
        elif len(self.queue) > 0: 
          self.current_turn_index = -1
    
          report.add('All players have left; the game has been paused') 
        else: 
          del self.client.game_data[self.channel.id] 
    
          report.add('All players have left and the queue is empty. The game will now be deleted. ') 
        '''
