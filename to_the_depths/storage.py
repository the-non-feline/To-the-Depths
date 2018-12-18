import copy
import ttd_tools
from ttd_tools import print

class Deconstructable: 
  def __init__(self): 
    self.class_object = self.__class__ 
  
  def reconstruct(self, to_reconstruct, *args, **kwargs): 
    class_object = to_reconstruct['class_object'] 
    reconstructed = class_object(*args, **kwargs) 

    for attribute, value in to_reconstruct.items(): 
      setattr(reconstructed, attribute, value) 
    
    reconstructed.reconstruct_next() 

    return reconstructed
  
  def modify_deconstructed(self, deconstructed): 
    pass
  
  def deconstruct(self): 
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