import discord
from . import storage, printing
from .printing import print

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
