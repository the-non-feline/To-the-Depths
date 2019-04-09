import copy
import printing
from printing import print

class Deconstructable:
    def __init__(self):
        self.class_object = self.__class__ 

        print('test') 

    @staticmethod
    def reconstruct(to_reconstruct, *args, **kwargs):
        import ttd_tools
        import catalog
        import game

        class_object = to_reconstruct['class_object'] 
        class_object = eval(class_object) 
        
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
        class_object = str(self.__class__)

        self.class_object = class_object[8:len(class_object) - 2]
        
        deconstructed = self.__dict__.copy() 

        print('Pre-modification info for {} below: '.format(self))
        print('self.__dict__ = {}'.format(self.__dict__))
        print('deconstructed = {}'.format(deconstructed))

        self.modify_deconstructed(deconstructed)

        print('Post-modification info for {} below: '.format(self))
        print('self.__dict__ = {}'.format(self.__dict__))
        print('deconstructed = {}'.format(deconstructed))

        return deconstructed

    def reconstruct_next(self):
        pass
