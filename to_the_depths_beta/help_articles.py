import discord
from . import ttd_tools, catalog

articles = ttd_tools.Filterable() 

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
            embed.add_field(name=name, value=value + '\n', inline=False) 
        
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
following section. You are locked out of all actions during your enemy\'s battle turn. '), \
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
the creator of the game will be invited automatically; you don't need to mention yourself. "), \
    ('The queue', "Users who have been invited to a game but haven't joined as players are placed \
in the queue. You also get placed here if you die in-game. "), \
    ('Joining as a player', 'Once in the queue, you can join the game as a player using the `enter` command. \
You must also specify your player class as an argument to this command. A list of player classes can be found \
with `(prefix)helptopics classes`. Each class has unique pros and cons; look each class up with the `help` \
command for details. '), \
    ('Leaving the game', "Use the `leave` command if and only if you want to leave the **queue**. To leave \
the game as a player, you must first `suicide`. This will place you in the queue, and then you can `leave`. \
Note that you can only rejoin by being invited again. "), \
    ('Inviting other users', 'After a game has started, you can invite more users with the `invite` command. \
Mention (ping) the users to invite them. You must be a player in the game to invite other people. ') 

class Turns(Article): 
    before_turn_stuff = (f"If you're not protected from pressure damage in your level, you will take \
pressure damage ({catalog.Player.pd_slope} damage for every level past safety) ", 
    'You lose 1 oxygen', 
    f'If you have 0 oxygen left at this point, you immediately take {catalog.Player.oxygen_damage} \
damage', 
    f"You're checked to see if you get surprise attacked. Surprise attack is explained in the \
`{Fighting.name}` guide. ") 
    before_turn_str = ttd_tools.make_list(before_turn_stuff, numbered=True) 
    move_using = ('`craft`ing items', 'Starting a `fight`', '`gather`ing items', '`mine`ing', 
    '`move`ing levels (unless through using an ability or item)', '`regen`ning your own HP') 
    move_using_str = ttd_tools.make_list(move_using) 

    name = 'Turns' 
    description = 'This section explains the "game turns" in To the Depths' 

    fields = ('"Game turn"', 'Your player can only do things on their "game turn". Only one person can have \
the game turn. This is sometimes referred to as just "turn". '), \
    ('Starting your game turn', f'''Your game turn starts when the player before you ends theirs, or when \
you're the first player in the players list when the game starts. \
When your turn starts, you are given back your "move". However, if you\'re in a level deeper than the \
{catalog.Levels.Surface.name}, you can\'t immediately act when your turn starts; a few things must happen \
first, in this order: 

{before_turn_str} 

After these, you're allowed to act (although if you get surprise attacked you\'ll be forced into a fight). '''), \
    ('What you can do during your turn', 'You can do basically anything during your turn. Note however that \
certain actions (detailed in the next part) will use your "move". '), \
    ('Your "move"', f'''The following actions use your move: 

{move_using_str}

This means you can only do one of these actions, once, per turn. '''), \
    ('Ending your turn', "Ending your turn is done through the `endturn` command. Note that you can't end your \
turn in the middle of a fight. Your turn also ends if you die. ") 

class Items(Article): 
    obtainments = ('`craft`ing (explained below) ', 'Having another player `donate` to you', 'Most creatures \
drop items upon dying. The items and amounts dropped depend on the creature. ', '`gather`ing', '`mine`ing') 
    obtainments_str = ttd_tools.make_list(obtainments) 

    name = 'Items' 
    description = 'This section covers items in To the Depths' 

    fields = ('Overview', "Items are an integral part of the game. They can be obtained through various \
methods, and usually boost your player. "), \
    ('How to obtain items', f'''Items can be obtained through any of the following methods: 

{obtainments_str}'''), \
    ('Crafting items', 'Some items can be used to craft other items through the `craft` command. Note that \
you can only craft one type of item per turn, as doing this takes your move. You can, however, craft \
multiple of that item at once. '), \
    ('The "Item Multipliers" stat', f'Some players will get a bonus on certain items, listed in their "Item \
Multipliers" stat. Some items can give you bonuses on other items too. Multipliers stack; if you have a \
1.5x multiplier on all items and a 2x multiplier on {catalog.Steel.name}, you\'ll receive 3x \
{catalog.Steel.name}. Items you receive from crafting and donations are not affected by this stat. '), \
    ('"Stacking"', f"In most cases, a given item's bonuses don't stack with the same bonuses of another of \
the same item. For example, 2 {catalog.Suit.name}s won't both give you HP; only the first one will. "), \
    ('Using items', 'Some items are usable through the `use` command. Each of them does something \
different upon being used. Most items disappear after being used, although there are some exceptions. Some \
items also have restrictions on when and how often you can use them. '), \
    ('Donating', 'You can donate items to another player using the `donate` command. Note that both players \
must be in the same level to do this. ') 

class Introduction(Article): 
    name = 'Introduction' 
    description = 'To the Depths is a game played through interacting with this Discord bot. This section \
covers the basics of using this bot. ' 

    fields = ('Commands', '''The bot is controlled mostly through commands. Commands consist of 3 parts, the \
prefix, the command name, and the arguments (or parameters). If you've used Discord bots before, you probably \
already understand how it works. 

All commands must start with the prefix. This is needed so the bot knows you're talking to it. If you're \
reading this you should already know what the prefix for your server is. 

The second part of the command is the command name. This tells the bot what to do. It must always be \
attached to the prefix (not separated by a space or something). A full list of valid command names can be \
found by typing `(prefix)helptopics commands`. 

The last part of the command is the arguments/parameters. These give more information about what exactly \
you're trying to do. Each one of these must be separated by a space. Note that each command accepts a \
different number of arguments. '''), \
    ('Prompts', '''Occasionally, the bot will directly ask you for provide information. There are 2 forms of prompts. 

The first kind is a message prompt, asking you to respond with a message. Respond to these just like how you \
would respond to a regular person asking you for an answer; you don't need to format your message like a \
command. 

The second kind is a reaction prompt, asking you to respond with a reaction. The bot will tell you what you \
can react with. 

Note that most prompts have a time limit. If you don't respond within the time limit, the bot will just \
choose a default response for you. '''), \
    ('Additional help', 'Additional help is provided through the `help` and `helptopics` commands. `help` \
displays useful info on all topics that you specified in its arguments. `helptopics` is used to list valid \
topic names. ') 