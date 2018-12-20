# -*- coding: utf-8 -*- 

import pickle
import asyncio
import logging
import os
import copy
import discord
from . import printing, storage, game as g
from .printing import print

thumbs_up_emoji = chr(0x1F44D) 
thumbs_down_emoji = chr(0x1F44E) 

prefix = '.' 

def clear_file(file): 
  file.seek(0) 
  file.truncate(0) 

  print('cleared') 

def pickle_dump(file, thing): 
  print('thing = {}'.format(thing)) 

  clear_file(file) 

  pickle.dump(thing, file) 
  file.flush() 
  os.fsync(file.fileno()) 

def pickle_load(file): 
  try: 
    result = pickle.load(file) 

    print(result) 

    return result
  except EOFError: 
    print('empty') 

    return {} 

class Command_Embed(discord.Embed): 
  def __init__(self, title, description, **arguments): 
    discord.Embed.__init__(self, title=title, type='rich', description=description) 
    syntax = prefix + title

    for argument in arguments: 
      syntax += ' ' + argument
    
    self.add_field(name='Syntax', value='`{}`'.format(syntax)) 

    if len(arguments) > 0: 
      arguments_string = '\n'.join(('`{}` - {}'.format(argument, purpose) for argument, purpose in arguments.items())) 

      self.add_field(name='Arguments', value=arguments_string) 

help_embed = Command_Embed('help', 'Displays info about the requested thing(s) ', thing='OPTIONAL. A list of things that you want info on, separated by spaces. Leaving this blank displays help on the `help` command itself. ') 
commands_list_embed = Command_Embed('commands', 'Displays all valid commands for this bot') 
game_command_embed = Command_Embed('game', 'Allows you to view and manage games', action='OPTIONAL. The action that you want to perform. Valid actions are `enter`, `invite`, `start`, and `leave`. Leaving this blank displays the info for the current game in the current channel. ', mentions='Member mentions. Using with `invite` invites all valid mentioned members into the queue. Does nothing otherwise. ')  

things = {
  'commands': {
    'commands': commands_list_embed, 
    'game': game_command_embed, 
    'help': help_embed, 
  }, 
} 

class TTD_Bot(discord.Client, storage.Deconstructable): 
  def __init__(self, file): 
    self.tasks = 0
    self.listening = False
    self.storage_file = file
    self.game_data = pickle_load(self.storage_file) 

    discord.Client.__init__(self, status=discord.Status.offline) 
    storage.Deconstructable.__init__(self) 
  
  def save(self): 
    deconstructed = {channel_id: game.deconstruct() for channel_id, game in self.game_data.items()} 

    '''
    copied = {} 

    for channel_id, game in self.game_data.items(): 
      copied[channel_id] = game.deconstruct() 
    ''' 

    pickle_dump(self.storage_file, deconstructed) 
  
  async def edit_tasks(self, amount): 
    self.tasks += amount

    print('now running {} tasks'.format(self.tasks)) 

    if not(self.listening) and self.tasks == 0: 
      print('all tasks done, will now shut down') 

      await self.logout() 
  
  async def on_ready(self): 
    for channel_id, game_info in self.game_data.items(): 
      self.game_data[channel_id] = reconstructed_game = self.reconstruct(game_info, self, self.get_channel(channel_id)) 

      print(reconstructed_game) 
    
    await self.change_presence(status=discord.Status.online, activity=discord.Game('To the Depths')) 

    self.listening = True

    print('IM READY AF')
  
  async def logout(self): 
    '''
    for channel_id, game in self.game_data.items(): 
      self.game_data[channel_id] = game.deconstruct() 
    
    pickle_dump(self.storage_file, self.game_data) 
    ''' 
    await self.change_presence(activity=discord.Game('nothing')) 

    self.save() 

    print('logging out! ') 

    await discord.Client.logout(self) 
  
  async def prompt_for_message(self, channel, member_id, choices=None, custom_check=lambda message: True, timeout=None, default_choice=None): 
    if choices is not None: 
      options = ', '.join(tuple('`{}`'.format(choice) for choice in choices))  

      await channel.send(content='Valid replies are {} '.format(options)) 
    
    if timeout is not None: 
      if default_choice is not None: 
        await channel.send(content='There is a time limit of {} seconds to reply, after which your answer will default to {}. '.format(timeout, default_choice)) 
      else: 
        await channel.send(content='There is a time limit of {} seconds to reply. '.format(timeout)) 
    
    def check(message): 
      return message.channel.id == channel.id and message.author.id == member_id and (choices is None or message.content.lower() in choices) and custom_check(message) 

    try: 
      message = await self.wait_for('message', check=check, timeout=timeout) 

      return message.content.lower() 
    except asyncio.TimeoutError: 
      return default_choice
    
  async def prompt_for_reaction(self, message, member_id, emojis=None, custom_check=lambda reaction, member: True, timeout=None, default_emoji=None): 
    if emojis is not None: 
      for emoji in emojis: 
        await message.add_reaction(emoji) 
    
    if timeout is not None: 
      if default_emoji is not None: 
        await message.channel.send(content='There is a time limit of {} seconds to react, after which your reaction will default to {}. '.format(timeout, default_emoji)) 
      else: 
        await message.channel.send(content='There is a time limit of {} seconds. '.format(timeout)) 
    
    def check(reaction, member): 
      return reaction.message.id == message.id and member.id == member_id and (emojis is None or reaction.emoji in emojis) and custom_check(reaction, member) 
    
    try: 
      reaction, member = await self.wait_for('reaction_add', check=check, timeout=timeout) 

      return reaction.emoji
    except asyncio.TimeoutError: 
      return default_emoji
  
  async def on_message(self, message): 
    if self.listening and message.author.id != self.user.id: 
      message_content = message.content.lower() 
      words = message_content.split() 
      
      if len(words) > 0 and words[0].startswith(prefix): 
        await self.edit_tasks(1) 

        print('handling: {}'.format(message.content)) 
        
        try: 
          channel = message.channel
          author = message.author
          game = self.game_data.get(channel.id) 
          command = words[0].strip(prefix) 
          arguments = words[1:] 

          '''
          if command == 'help': 
            if len(arguments) > 0: 
              for thing in arguments: 
                if thing in things: 
                  await channel.send(embed=things[thing]) 
                else: 
                  await channel.send(content='`{}` does not correspond to any valid things'.format(thing)) 
            else: 
              await channel.send(embed=things['commands']['help']) 
          ''' 

          if command == 'shutdown': 
            if author.id == 315682382147485697: 
              self.listening = False

              await self.change_presence(status=discord.Status.do_not_disturb) 

              await channel.send(content='Preparing to shutdown') 
            else: 
              await channel.send(content='nice try') 
          
          elif command == 'commands': 
            commands_string = ', '.join(('`{}`'.format(valid_command) for valid_command in things['commands']))  

            await channel.send(content='All the valid commands for the game: {} '.format(commands_string)) 
          
          elif command == 'creategame': 
            if game is None: 
              invited = tuple(message.mentions + [author]) 
              new_game = g.Game(self, channel, queue=invited)  

              self.game_data[channel.id] = new_game

              await channel.send(content='Success! A new game was created. ') 

              self.save() 
            else: 
              await channel.send(content='There is already a game running in this channel. ') 
          
          elif command == 'game': 
            if game is not None: 
              print(game.__dict__) 

              if len(arguments) > 0: 
                action = arguments[0] 
                
                if action == 'enter': 
                  await game.add_player(author) 

                  self.save() 

                  #pickle_dump(storage_file, game_data) 
                
                elif action == 'invite': 
                  if game.has_power(author.id): 
                    if len(message.mentions) > 0: 
                      for member in message.mentions: 
                        await game.add_member(member) 

                        self.save() 
                  else: 
                    await channel.send(content='You have no power here. ') 
                
                elif action == 'start': 
                  if game.has_power(author.id): 
                    await game.start() 

                    self.save() 
                  else: 
                    await channel.send(content='You have no power here. ') 

                elif action == 'leave': 
                  await game.remove_member(author) 

                  self.save() 

                  ''' 
                  if dead_game: 
                    await channel.send(content='This game is dead. Deleting... ') 

                    del self.game_data[channel.id] 
                  ''' 
                  
                  #pickle_dump(storage_file, game_data) 
                
                else: 
                  await channel.send(content='`{}` is not a valid action. '.format(action)) 
              else: 
                await channel.send(embed=game.object_embed()) 
            else: 
              await channel.send(content='There is no game currently running in this channel. ') 
          
          elif command == 'act': 
            print(game.__dict__) 
            
            if game is not None: 
              #print(game.__dict__) 

              player = game.get_player(author.id) 

              if player is not None: 
                if player.uo_game_turn: 
                  if len(arguments) > 0: 
                    action = arguments[0] 

                    if action == 'endturn': 
                      if player.o_game_turn: 
                        await game.next_turn() 

                        self.save() 
                      else: 
                        await channel.send(content="It's not your turn anyways but ok") 
                    
                    elif action == 'suicide': 
                      await player.on_death() 

                      self.save() 
                    else: 
                      await channel.send(content='{} is not a valid action. '.format(action)) 
                  else: 
                    await channel.send(content='Please specify an action. ') 
                else: 
                  await channel.send(content='You can only act on your game turn. ') 
              else: 
                await channel.send(content="You're not even in the game") 
            else: 
              await channel.send(content='There is no game here') 
        
        finally: 
          print('finished handling: {}'.format(message.content)) 
          
          await self.edit_tasks(-1) 

