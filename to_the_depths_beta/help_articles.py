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
    
    name = 'Fighting' 
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
    
class Games(Article): 
    name = 'Games' 
    description = 'This section explains how to create and join games in To the Depths, and how to invite \
other people to them' 

    fields = ('Creating a game', "Creating a game is done with the `creategame` command. When using this \
command, you can also mention (ping) all the people who you'd like to invite to the game as well. Note that \
the creator of the game will be invited automatically; you don't need to mention yourself. "), 
    ('The queue', "Users who have been invited to a game but haven't joined as players are placed \
in the queue. You also get placed here if you die in-game. "), 
    ('Joining as a player', 'Once in the queue, you can join the game as a player using the `enter` command. \
You must also specify your player class as an argument to this command. A list of player classes can be found \
with `(prefix)helptopics classes`. Each class has unique pros and cons; look each class up with the `help` \
command for details. '), 
    ('Leaving the game', "Use the `leave` command if and only if you want to leave the **queue**. To leave \
the game as a player, you must first `suicide`. This will place you in the queue, and then you can `leave`. \
Note that you can only rejoin by being invited again. "), 
    ('Inviting other users', 'After a game has started, you can invite more users with the `invite` command. \
Mention (ping) the users to invite them. You must be a player in the game to invite other people. '), 