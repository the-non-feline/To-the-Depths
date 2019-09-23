import discord
from . import ttd_tools, catalog

articles = ttd_tools.Filterable() 

def rel_comms_field(group): 
    return ('Related commands', f'Use the `{group}` filter when listing commands to display {group}-related commands')

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
    ('drag', f'Can only be used by the {catalog.Diver.name} class. Drag your opponent one level `up` or `down`. ') 
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
random creature in your current level. You can also be surprise attacked by {catalog.Stonefish.name} while mining. '), \
    rel_comms_field('battle')  
    
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
with `(prefix)list classes`. Each class has unique pros and cons; look each class up with the `help` \
command for details. '), \
    ('Leaving the game', "Use the `leave` command if and only if you want to leave the **queue**. To leave \
the game as a player, you must first `suicide`. This will place you in the queue, and then you can `leave`. \
Note that you can only rejoin by being invited again. "), \
    ('Inviting other users', 'After a game has started, you can invite more users with the `invite` command. \
Mention (ping) the users to invite them. You must be a player in the game to invite other people. '), \
    rel_comms_field('game') 

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
    ('Your "move"', f'''The following actions, known as "movements", use your move: 

{move_using_str}

This means you can only do one of these "movements", once, per turn. '''), \
    ('Ending your turn', "Ending your turn is done through the `endturn` command. Note that you can't end your \
turn in the middle of a fight. Your turn also ends if you die. "), \
    rel_comms_field('movement') 

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
must be in the same level to do this. '), \
    rel_comms_field('items')  

class Commands(Article): 
    name = 'Commands' 
    description = 'To the Depths is a game played through interacting with this Discord bot. This section \
covers the basics of using this bot. ' 

    fields = ('Commands', '''The bot is controlled mostly through commands. Commands consist of 3 parts, the \
prefix, the command name, and the arguments (or parameters). If you've used Discord bots before, you probably \
already understand how it works. 

All commands must start with the prefix. This is needed so the bot knows you're talking to it. If you're \
reading this you should already know what the prefix for your server is. 

The second part of the command is the command name. This tells the bot what to do. It must always be \
attached to the prefix (not separated by a space or something). A full list of valid command names can be \
found by typing `(prefix)list commands`. 

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
    ('Additional help', 'You can look up any command with `help` command for details about using it') 

class HP(Article): 
    name = 'HP/Damage' 
    description = 'This section explains HP and damage mechanics' 
    
    fields = ('HP', 'Everything that can participate in a fight has HP. When it reaches 0, the thing dies. '), \
    ('The "HP Multiplier" stat', 'Your HP is multiplied by this when you start. Furthermore, any bonuses to your max HP are \
multiplied by this stat. '), \
    ('Shield', 'Shield, when it is not empty, will always take damage before HP, unless the damage bypasses shield. The shield \
will absorb all overkill to itself, unless the damage bleeds shield. '), \
    ('Damage', 'Damage decreases HP. It can have special properties, such as penetrating (completely bypasses the specified \
thing) or bleeding (overkilling damage carries over onto the next thing) '), \
    ('The "Attack Multiplier" stat', 'Like the "HP Multiplier" stat but applies to attack damage instead'), \
    ('The "Enemy Attack Multiplier" stat', 'When an entity is taking damage from an enemy attack, the incoming damage is \
multiplied by this stat to determine how much damage they actually take. Damage from sources other than attacks (such as pressure \
or oxygen damage) is not affected by this stat. '), \
    ('Electric and fire damage', 'These types of damage are not dealt immediately, rather they are dealt after a delay. Damage \
dealt from the release of such damage counts as damage from the environment, rather than damage from attacks, and as such are not \
affected by the "Enemy Attack Multiplier" stat. However, the stat **does** affect how much damage gets "built-up" each time. '), \

class Introduction(Article): 
    name = 'Introduction' 
    description = 'Welcome, new player! This section will give you a basic overview of the game. ' 
    
    fields = ('Basic mechanics', 'To the Depths is a turn-based game. Each player chooses one of the various player classes, \
and take turns doing stuff. The game centers on fighting NPC creatures and obtaining items to upgrade your player. '), \
    ('Turns', f'See the `{Turns.name}` guide for details on the turn-based nature of this game'), \
    ('Fighting', f'The majority of items are gained through fightng and defeating NPC creatures. Fighting centers around the \
mechanic of "battle turns". Only one side can have the battle turn at any given \
time, and only the side with the battle turn can act. Battle turns are decided through random coin flips. A fight lasts until \
one side flees or dies. More information in the `{Fighting.name}` guide. '), \
    ('Items', f'Items enhance your player. Some will upgrade your player upon being received, while some must be used to give an \
effect. More information in the `{Items.name}` guide. '), \
    ('Using the bot', f'See the `{Commands.name}` guide for help on using this bot. '), \
    ('Using the `help` and `list` commands', 'These two commands are crucial to understanding the game. The \
`help` command is the command you will use to look up information regarding everything in the game. To use, \
simply type the command followed by the names of the things you want to look up. The `list` command is used \
to "list" stuff so you know they exist. This command must be followed by a category and unlimited, optional \
filter names. **The category for listing other guides like this is `guides`**. '), \
    ('Some other tips', f"When in a level deeper than the {catalog.Levels.Surface.name}, keep track of your \
oxygen; it would be very frustrating to die because you didn't. Also remember to look at your HP before \
throwing yourself into a fight. The `viewstats` command is your friend here. Also **please don't forget \
to end your turn with `endturn` command**. It is very annoying to other people when you forget. ") 
