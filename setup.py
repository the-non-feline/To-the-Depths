import setuptools

requires = [] 

with open('requirements.txt') as file: 
  requires = file.read().splitlines() 

setuptools.setup(name='To the Depths', version='0.1', packages=['to_the_depths']) 
