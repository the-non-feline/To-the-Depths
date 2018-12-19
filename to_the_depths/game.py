import random
import asyncio
import logging
import discord
from . import ttd_tools, catalog
from .ttd_tools import print

class Game(ttd_tools.Game_Object): 
  def __init__(self, client, channel, queue=()): 
    self.queue = [member.id for member in queue if not(member.bot)] 
    self.players = [] 
    self.current_turn_index = -1
    self.current_player = None

    ttd_tools.Game_Object.__init__(self, client, channel) 
  
  def modify_deconstructed(self, deconstructed): 
    del deconstructed['current_player'] 

    players = deconstructed['players'].copy() 

    for index in range(len(players)): 
      players[index] = players[index].deconstruct() 
    
    deconstructed['players'] = players

    ttd_tools.Game_Object.modify_deconstructed(self, deconstructed) 
  
  def reconstruct_next(self): 
    for index in range(len(self.players)): 
      self.players[index] = reconstructed_player = self.reconstruct(self.players[index], self.client, self.channel, self) 
    
    if self.current_turn_index >= 0: 
      self.current_player = self.players[self.current_turn_index] 
  
  def on_shutdown(self): 
    for player in self.players: 
      player.on_shutdown() 
  
  def object_embed(self): 
    embed = self.class_embed() 

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
    
    embed.add_field(name='Current turn', value=self.current_player.name if self.current_player is not None else None) 

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
  
  async def pause_or_delete(self): 
    if len(self.queue) > 0: 
      #pause
      self.current_turn_index = -1
      self.current_player = None

      await self.channel.send(content='All players have left, but queue is not empty, so the game is now paused. ') 
    else: 
      #delete
      del self.client.game_data[self.channel.id] 

      await self.channel.send(content='All players have left and the queue is empty, so the game was deleted. ') 
  
  async def remove_player(self, player): 
    removed_player_index = self.players.index(player) 

    self.players.remove(player) 

    #account for changed length of self.players
    if self.current_turn_index >= removed_player_index: 
      self.current_turn_index -= 1
    
    await self.channel.send(content='{} was removed from the game. '.format(player.name)) 
    
    if player.o_game_turn: 
      await self.next_turn() 
  
  async def add_member(self, member): 
    player = self.get_player(member.id) 

    if player is not None: 
      await self.channel.send(content='{} is already in the game, as {}. '.format(member.name, player.name)) 
    elif member.id in self.queue: 
      await self.channel.send(content='{} is already in the queue. '.format(member.name)) 
    elif not(member.bot): 
      self.queue.append(member.id) 
      await self.channel.send(content='{} was added to the queue. '.format(member.name)) 
    else: 
      await self.channel.send(content='Bots are not allowed in games. ') 
  
  async def add_player(self, member): 
    player = self.get_player(member.id) 

    if player is not None: 
      await self.channel.send('{} is already in the game, as {}. '.format(member.name, player.name)) 
    elif member.id in self.queue: 
      self.queue.remove(member.id) 

      await self.channel.send(content='Enter your name: ') 
      player_name = await self.client.prompt_for_message(self.channel, member.id, timeout=20, default_choice=member.name) 

      await self.channel.send(content='Enter your class: ') 
      class_choice = await self.client.prompt_for_message(self.channel, member.id, custom_check=lambda message: 
        catalog.search(catalog.classes, message.content) is not None, timeout=20) 

      if class_choice is not None: 
        chosen_class = catalog.search(catalog.classes, class_choice) 
        new_player = chosen_class(self.client, self.channel, name=player_name, member_id=member.id, game=self) 

        #choose a random position to insert the new player into
        random_index = random.randint(0, len(self.players)) 

        self.players.insert(random_index, new_player) 

        #if the current player's index is above this new index, the current player's index increments by 1
        if self.current_turn_index >= random_index: 
          self.current_turn_index += 1
        
        await self.channel.send(content='Success! {} joined the game as {}. '.format(member.name, player_name)) 

        await new_player.on_life_start() 
      else: 
        self.queue.append(member.id) 
        
        await self.channel.send(content='Time limit exceeded. Operation was canceled. ') 
    else: 
      await self.channel.send(content='{} cannot join the game as they are not in the queue. '.format(member.name)) 
  
  async def remove_member(self, member): 
    player = self.get_player(member.id) 

    if player is not None: 
      await player.on_death(allow_respawn=False) 
    elif member.id in self.queue: 
      self.queue.remove(member.id) 

      await self.channel.send(content='{} was removed from the queue. '.format(member.name)) 

      if len(self.players) == 0: 
        await self.pause_or_delete() 
    else: 
      await self.channel.send(content="{}? Who is that? Not anyone in this game, that's for sure. ".format(member.name)) 
  
  async def start(self, ): 
    if len(self.queue) > 0: 
      await self.channel.send(content='There are still {} players who have not joined. '.format(len(self.queue))) 
    elif len(self.players) == 0: 
      await self.channel.send(content='No players have joined. ') 
    elif self.current_turn_index >= 0: 
      await self.channel.send(content='The game has already started. ') 
    else: 
      #shuffle the players so it's not restricted to the order that they joined
      await self.channel.send(content='Starting! ') 

      await self.next_turn() 
  
  async def next_turn(self): 
    if self.current_player is not None: 
      self.current_player.o_game_turn = False

      await self.current_player.on_global_event('game_turn_end') 

    if len(self.players) > 0: 
      self.current_turn_index += 1

      if self.current_turn_index >= len(self.players): 
        self.current_turn_index = 0
      
      self.current_player = self.players[self.current_turn_index] 

      self.current_player.o_game_turn = True

      await self.channel.send(content="It is now {}'s turn. ".format(self.current_player.name)) 

      await self.current_player.on_global_event('game_turn_start') 
      await self.current_player.before_action() 
    else: 
      await self.pause_or_delete() 
    
    ''' 
    elif len(self.queue) > 0: 
      self.current_turn_index = -1

      await self.channel.send(content='All players have left; the game has been paused') 
    else: 
      del self.client.game_data[self.channel.id] 

      await self.channel.send(content='All players have left and the queue is empty. The game will now be deleted. ') 
    ''' 
