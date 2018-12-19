import builtins
import time
import discord

def print(*values, sep=' ', end='\n'): 
	builtins.print('{} - '.format(time.asctime()), end='', flush=True) 
	builtins.print(*values, sep=sep, end=end + '\n', flush=True) 

from . import storage

class Game_Object(storage.Deconstructable): 
  def __init__(self, client, channel): 
    self.client = client
    self.channel = channel

    storage.Deconstructable.__init__(self) 
  
  def modify_deconstructed(self, deconstructed): 
    del deconstructed['client'], deconstructed['channel'] 

    storage.Deconstructable.modify_deconstructed(self, deconstructed) 
  
  def on_shutdown(self): 
    pass
  
  async def on_turn_on(self): 
    pass
  
  @classmethod
  def class_embed(self): 
    return discord.Embed(type='rich')  
  
  def object_embed(self): 
    return self.class_embed() 
