import discord
from . import printing
from printing import print

class Report: 
    def __init__(self, client, channel): 
        self.client = client
        self.channel = channel
        self.contents = [] 
    
    async def send_message(self, sent_messages, texts, embed=None): 
        if len(texts) > 0 or embed is not None: 
            sent_messages.append(await self.client.do(self.channel.send(content='\n'.join(texts), embed=embed))) 

            texts.clear() 
    
    def add(self, to_add): 
        self.contents.append(to_add) 
    
    async def send_self(self): 
        sent_messages = [] 

        to_send = [] 

        for message in self.contents: 
            if isinstance(message, discord.Embed): 
                await self.send_message(sent_messages, to_send, embed=message) 
            else: 
                buffer = to_send + [message] 
                proposed = '\n'.join(buffer) 

                if len(proposed) > 2000: 
                    await self.send_message(sent_messages, to_send) 
                
                to_send.append(message) 
        
        await self.send_message(sent_messages, to_send) 
        
        self.contents.clear() 

        return sent_messages
