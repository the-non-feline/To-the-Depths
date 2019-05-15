import discord
from . import ttd_tools, catalog

articles = [] 

class Article_Meta(ttd_tools.GO_Meta): 
    append_to = articles

class Article(metaclass=Article_Meta, append=False): 
    name = '' 
    description = '' 
    fields = () 
    
    @classmethod
    def help_embed(cls): 
        embed = discord.Embed(type='rich', title=f'Information on {cls.name}', description=cls.description) 
        
        for name, value in cls.fields: 
            embed.add_field(name=name, value=value, inline=False) 
        
        return embed

class Fighting(Article): 
    bt_actions = ('attack', 'Attack your opponent'), \
    ('flee', f'Try to flee the fight. You will flip a coin, and if you win the flip, \
you successfully flee. However, if you lose, your opponent will get to attack you {catalog.Player.failed_flee_punishment} times, \
for free! {catalog.Forager.name} is exempt from this coin flip in the {catalog.Levels.Surface.name}. '), \
    ('drag', f'Can only be used by the {catalog.Diver.name} class. Drag your opponent one level `up` or `down`. Note that doing \
this on a creature will result in it only dropping half its normal drops on death. ') 
    bt_actions_gen = (f'`{action_name}` - {action_description}' for action_name, action_description in bt_actions) 
    bt_actions_str = ttd_tools.make_list(bt_actions_gen) 
    
    name = 'fighting' 
    description = 'Fighting is an integral part of To the Depths. This section explains the mechanics and commands behind fighting. ' 
    
    fields = ('Starting a fight', 'Starting a fight is done with the `fight` command. This starts a fight with a random creature from \
your current level. Fights can also be forced, through the "surprise attack" mechanic. '), \
    ('Deciding first hit', 'After a fight has started, the game will determine who gets the first battle turn. Every player and creature has a \
stat called "Priority". Whoever has the higher priority stat gets first hit. In the case that both have equal priorities, a coin \
flip is used to determine who gets the first hit. Creatures automatically get a +1 priority boost when surprise attacking. '), \
    ('Calling after the first hit', "After the first battle turn is decided and finished, you'll need to manually `call` to decide \
who gets the next battle turn. "), \
    ('Battle turns', 'When you get first hit or win the coinflip after using the `call` command, it becomes your "battle turn". \
On your battle turn, you can do anything that does not require a move. Additionally, you can perform any of the actions listed in the \
following section. '), \
    ('Special actions', f'''These actions can only be performed on your battle turn. The commands to perform them are the same as the \
name of the action: 

{bt_actions_str} 

Performing any of these actions instantly ends your battle turn. '''), \
    ('Surprise attack', f'At the start of your turn (not battle turn), at the same time that you lose oxygen, you roll the die. If \
it lands on any of the numbers listed in your current level\'s "Surprise attack chance" stat, you are surprise attacked by a \
random creature in your current level. You can also be surprise attacked by {catalog.Stonefish.name} while mining. ') 
    
