import sys
import time
import os

def clear_file(file):
    file.seek(0)
    file.truncate(0)

    log('cleared') 

def text_dump(file, thing): 
    thing = str(thing) 
    
    log('thing = {}'.format(thing)) 

    clear_file(file) 
    
    file.write(thing) 
    
    file.flush()
    os.fsync(file.fileno()) 

    log('successfully dumped') 

def text_load(file, default): 
    file.seek(0) 
    
    contents = file.read() 
    
    log(contents) 
    
    if len(contents) > 0: 
        result = eval(contents) 
        
        log(result) 
        
        return result
    else: 
        log('empty') 

        return default

MAX_SIZE = 1000000

def log(*values, sep=' ', end='\n', file=None): 
    file = file or sys.stdout
    #make this function restrict file size

    if file.seekable(): 
        file.seek(0, 2) 
    
    try: 
        print('{}{} - '.format('\n', time.asctime()), end='', file=file, flush=True) 
        print(*values, sep=sep, end=end, file=file, flush=True) 
    except UnicodeEncodeError: 
        log("couldn't print that for some reason") 

    if file.seekable() and file.readable() and file.tell() > MAX_SIZE: 
        file.seek(0) 

        contents = file.read() 
        trimmed_contents = contents[len(contents) - MAX_SIZE:] 

        clear_file(file) 
        file.write(trimmed_contents) 

        file.seek(0, 2) 

        file.flush() 