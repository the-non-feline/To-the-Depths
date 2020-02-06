import copy
from . import file_io
from .file_io import debug

class D_Meta(type): 
    def __repr__(cls): 
        type_repr = type.__repr__(cls) 
        
        #debug(type_repr) 
        
        class_name = type_repr[8:len(type_repr) - 2] 
        
        return class_name

class Deconstructable(metaclass=D_Meta): 
    def __init__(self): 
        self.class_name = repr(self.__class__) 

    @staticmethod
    def reconstruct(to_reconstruct, *args, **kwargs): 
        import to_the_depths_beta
        from . import catalog, game
        
        class_name = to_reconstruct['class_name'] 
        class_object = eval(class_name) 
        
        reconstructed = class_object(*args, **kwargs)

        for attribute, value in to_reconstruct.items(): 
            if hasattr(reconstructed, attribute): 
                setattr(reconstructed, attribute, value) 

        reconstructed.reconstruct_next()

        return reconstructed
    
    @staticmethod
    def modify_deconstructed(deconstructed): 
        pass

    def deconstruct(self):
        deconstructed = self.__dict__.copy()

        debug('Pre-modification info for {} below: '.format(self))
        debug('self.__dict__ = {}'.format(self.__dict__))
        debug('deconstructed = {}'.format(deconstructed))

        self.modify_deconstructed(deconstructed)

        debug('Post-modification info for {} below: '.format(self))
        debug('self.__dict__ = {}'.format(self.__dict__))
        debug('deconstructed = {}'.format(deconstructed))

        return deconstructed

    def reconstruct_next(self):
        pass
