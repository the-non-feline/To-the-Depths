import discord
from . import chars, printing, storage
from .chars import * 
from .printing import print

def make_list(list_items, numbered=False):
    to_join = list(list_items)

    for index in range(len(to_join)):
        if numbered:
            point = '{}.'.format(index + 1)
        else:
            point = bullet_point

        to_join[index] = '{} {}'.format(point, to_join[index])

    joined = '\n'.join(to_join)

    return joined

def format_iterable(iterable, formatter='{}', sep=', '):
    return sep.join((formatter.format(item) for item in iterable)) 

def search(to_search, name): 
    query = name.lower().replace('_', ' ') 

    for thing in to_search: 
        '''
        print('thing.name = {}'.format(thing.name.lower()))
        print('name = {}'.format(name.lower())) 
        ''' 

        if thing.name.lower() == query: 
            return thing

    return None

def bulk_search(to_search, names, converter=set): 
    return converter((search(to_search, name) for name in names)) 

class Game_Object(storage.Deconstructable):
    def __init__(self, client, channel):
        self.client = client
        self.channel = channel

        storage.Deconstructable.__init__(self) 
    
    @classmethod
    def is_a(cls, other): 
        return issubclass(cls, other) 
    
    @staticmethod
    def modify_deconstructed(deconstructed): 
        del deconstructed['client'], deconstructed['channel'] 

        storage.Deconstructable.modify_deconstructed(deconstructed) 
    
    async def on_shutdown(self, report): 
        pass
    
    async def on_turn_on(self, report): 
        pass

    @classmethod
    def help_embed(cls):
        return discord.Embed(type='rich')

    def stats_embed(self): 
        return discord.Embed(type='rich') 

class GO_Meta(storage.D_Meta): 
    append_to = None
    
    def __new__(mcs, name, bases, namespace, append=True): 
        cls = type.__new__(mcs, name, bases, namespace) 
        
        if append: 
            mcs.append_to.append(cls) 
        
        return cls

class Filterable(list): 
    def __init__(self, iterable=(), **filters): 
        self.filters = filters

        list.__init__(self, iterable) 
    
    def valid_names(self, names): 
        valid_gen = ((name.lower() in self.filters) for name in names) 

        return all(valid_gen) 
    
    @staticmethod
    def passes_all(filters, to_check): 
        passes_gen = (current_filter(to_check) for current_filter in filters) 

        return all(passes_gen) 
    
    def get_filtered(self, filters): 
        filters = [self.filters[name.lower()] for name in filters] 

        filtered = [to_check for to_check in self if self.passes_all(filters, to_check)] 

        return filtered