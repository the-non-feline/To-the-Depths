# To-the-Depths

This is the framework for a Discord bot to play the card game To the Depths, available as a Python package.

**Installation: ** 

Installing the stable version: 
`py -m pip install --upgrade git+https://github.com/the-non-feline/To-the-Depths` 

Installing the beta version: 
`py -m pip install --upgrade git+https://github.com/the-non-feline/To-the-Depths@beta` 

Installing the stable version installs a package named `to_the_depths`; installing the beta version installs a package called `to_the_depths_beta` 

**Running the bot: ** 

First, import the `TTD_Bot` class from the package: `from PACKAGE_NAME import TTD_Bot`, where `PACKAGE_NAME` is the name of the package you installed (see above). 

Second, instantiate `TTD_Bot` like so: `bot = TTD_Bot(STORAGE_FILE, LOG_FILE, STORAGE_FILE_2, OWNER_ID, DEFAULT_PREFIX)`. `STORAGE_FILE` and `STORAGE_FILE_2` are used for storing game data and **must** be opened in `r+` mode; `LOG_FILE` is used for logging and should be opened in `w` mode. **All of these files must be text file objects.** `OWNER_ID` is an `int`, the id of the Discord user who the bot will recognize as its "owner". This will be the only user allowed to run commands such as `announce` and `shutdown`. Finally, `DEFAULT_PREFIX` is a `str`, the default prefix that the bot will use on servers where no prefix has been specified. 

Finally, start the bot: `bot.run(TOKEN)`, where `TOKEN` is your bot user's token. 
