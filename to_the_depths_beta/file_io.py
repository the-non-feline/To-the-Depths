import sys
import time
import os
import logging

logger = logging.getLogger(__name__) 

logger.setLevel(logging.DEBUG) 

def clear_file(file, should_log=True):
    file.seek(0)
    file.truncate(0)

    if should_log: 
        debug('cleared') 

def text_dump(file, thing): 
    thing = str(thing) 
    
    debug('thing = {}'.format(thing)) 

    clear_file(file) 
    
    file.write(thing) 
    
    file.flush()
    os.fsync(file.fileno()) 

    debug('successfully dumped') 

def text_load(file, default): 
    file.seek(0) 
    
    contents = file.read() 
    
    debug(contents) 
    
    if len(contents) > 0: 
        result = eval(contents) 
        
        debug(result) 
        
        return result
    else: 
        debug('empty') 

        return default

class Max_Size_Handler(logging.StreamHandler): 
    def __init__(self, stream, max_size): 
        super().__init__(stream) 

        self.max_size = max_size
    
    def emit(self, record): 
        super().emit(record) 

        file = self.stream

        if file.seekable() and file.readable(): 
            file.seek(0, 2) 

            size = file.tell() 

            if size > self.max_size: 
                extra_bytes = size - self.max_size

                file.seek(extra_bytes) 

                contents = file.read() 

                #trimmed_contents = contents[len(contents) - self.max_size - 1:] 

                #print(len(contents)) 
                #print(len(trimmed_contents)) 
                
                clear_file(file, should_log=False) 
                file.write(contents) 

                file.flush() 

def add_file(file, size_limit): 
    logger.addHandler(Max_Size_Handler(file, size_limit)) 

def debug(msg, *args, **kwargs): 
    return logger.debug(str(msg) + '\n', *args, **kwargs) 

'''
def debug(*values, sep=' ', end='\n', file=None): 
    file = file or sys.stdout
    #make this function restrict file size

    if file.seekable(): 
        file.seek(0, 2) 
    
    try: 
        print('{}{} - '.format('\n', time.asctime()), end='', file=file, flush=True) 
        print(*values, sep=sep, end=end, file=file, flush=True) 
    except UnicodeEncodeError: 
        debug("couldn't print that for some reason", file=file) 

    if file.seekable() and file.readable() and file.tell() > MAX_SIZE: 
        file.seek(0) 

        contents = file.read() 
        trimmed_contents = contents[len(contents) - MAX_SIZE:] 
        
        clear_file(file) 
        file.write(trimmed_contents) 

        file.seek(0, 2) 

        file.flush() 
''' 