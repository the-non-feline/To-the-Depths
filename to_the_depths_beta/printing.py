import builtins
import sys
import time

# noinspection PyShadowingBuiltins
def print(*values, sep=' ', end='\n', file=sys.stdout): 
    try: 
        builtins.print('{}{} - '.format('\n', time.asctime()), end='', file=file, flush=True) 
        builtins.print(*values, sep=sep, end=end, file=file, flush=True) 
    except UnicodeEncodeError: 
        print("couldn't print that for some reason") 