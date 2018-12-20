import builtins
import time

def print(*values, sep=' ', end='\n'): 
	builtins.print('{} - '.format(time.asctime()), end='', flush=True) 
	builtins.print(*values, sep=sep, end=end + '\n', flush=True) 
