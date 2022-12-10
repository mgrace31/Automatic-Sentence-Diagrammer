# -*- coding: utf-8 -*-
"""
Created on Wed Oct  5 12:50:03 2022

@author: mcg19
"""

from PIL import Image, ImageFont, ImageDraw, ImageEnhance
from Word_Class import Word_Class, plot_subject, plot_verb, plot_adj, plot_op, plot_DO, plot_IO

#Parse sentence
basic = {'S': 'girl', 'V': 'has given', 'IO': 'me', 'DO': 'books'}
modifiers = {'books': {'long': 'M'}, 'me': {'little': 'M'}, 'girl': {'by': 'P', 'a': 'M', 'pretty': 'M'}, 'by': {'car': 'op'}, 'car': {'the': 'M', 'red': 'M'}}

def run_diagrammer(basic,modifiers,debug = False):
    w, h = 1000, 1000
    word_tl = (.25*w,.25*h)
    img = Image.new("RGB", (w, h), color = "white")
    word_dict = {} #dict storing each word and class
    for i in basic.keys():
        #createa new word class instance
        pos= i
        w = basic[i]
        if w != None:
            W = Word_Class(w, pos, word_tl) 
            word_dict[w] = W
            #plot based on word pos
            if pos == "S":
                img = plot_subject(W,img, W.location)
                print("plotting subject")
            if pos == "V":
                img = plot_verb(W,img, W.location)
                print("plotting verb")
            if pos == "DO":
                print("plotting DO")
                img = plot_DO(W, img,  word_dict[basic["V"]])
            if pos == "IO":
                print("plotting IO")
                img = plot_IO(W, word_dict[basic["V"]],img)
            #set next word to have location of top right of prev word
            word_tl = W.get_location("right", "top")
        #check if padding needed, update word locations



    for w in modifiers.keys():
        num_modifiers = len(modifiers[w].keys()) + 2
        count_modifiers = 1
        for m in (modifiers[w].keys()):
            print(m)
            if modifiers[w][m] == "M" or modifiers[w][m] == "P":
                M = Word_Class(m,modifiers[w][m], word_dict[w]) 
                word_dict[m] = M
                img = plot_adj(M, img, word_dict[w], count_modifiers/num_modifiers)
                print("printing dangle: " + m)
                count_modifiers+=2
        for m in (modifiers[w].keys()):
            print("finding ops:" + m)
            if modifiers[w][m] == "op":
                print("check")
                OP = Word_Class(m,modifiers[w][m], word_dict[w]) 
                word_dict[m] = OP
                img = plot_op(OP, img, word_dict[w])
                print("printing op: " + m)
    
    if debug:
        test_word = "about"
        img1 = ImageDraw.Draw(img)        
        img1.rectangle(word_dict[test_word].location, outline = "blue")
        p1 = word_dict[test_word].get_location("middle", "bottom")
        img1 = draw_circle(p1,img1, "orange")
    return img
            
def draw_circle(coord, draw,color):
    x,y = coord
    r = 5
    #draw = ImageDraw.Draw(img)
    leftUpPoint = (x-r, y-r)
    rightDownPoint = (x+r, y+r)
    twoPointList = [leftUpPoint, rightDownPoint]
    draw.ellipse(twoPointList, fill=color)
    return draw


#%%
# test_word = "me"
# img1 = ImageDraw.Draw(img)        
# img1.rectangle(word_dict[test_word].location, outline = "blue")
# p1 = word_dict[test_word].get_location("middle", "bottom")
# img1 = draw_circle(p1,img1, "orange")

run_diagrammer(basic,modifiers)
    

    


    
    