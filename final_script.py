# -*- coding: utf-8 -*-
"""
Created on Wed Dec  7 17:15:55 2022

@author: mcg19
"""

from parse_tree import create_parser, parse_sentence, run_converter
from draw_words import run_diagrammer
from PIL import ImageDraw

#%%
example_sentences = ["the pretty girl with curly hair recently gave me a book on Mars",
                     "We take our green bags to the store",
                     "The girl with pretty hair gave me a book",
                     "I will not ask you again",
                     "The children ate the cake with a spoon",
                     "Teacher gave the children homework",
                     "will you go to the store",
                     "can we go",
                     "My father recently gave me a book near that park"]
#%%
parser = create_parser()
#%%
sentence = example_sentences[1]
tree = parse_sentence(parser,sentence)
print("Parsed tree:")
print(tree)

basics, mods = run_converter(tree)
print("sentence structure:" + str(basics))
print("modifiers" + str(mods))

#%%
print("Running diagrammer ...")
image = run_diagrammer(basics,mods, debug = False)
image.show()



