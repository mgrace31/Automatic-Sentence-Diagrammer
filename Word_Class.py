# -*- coding: utf-8 -*-
"""
Created on Wed Oct  5 13:30:35 2022

@author: mcg19
"""
from PIL import Image, ImageFont, ImageDraw
import numpy as np
import aggdraw

fnt= ImageFont.truetype("arial.ttf", 30)
agg_font = aggdraw.Font(1, "arial.ttf", size = 30)
box_pad = 40

class Word_Class:
    def __init__(self, text, pos, location):
        self.text = text
        self.pos = pos
        self.location = location
    
    def get_location(self,horizontal, vertical):
        x,y = 0,0
        if horizontal == "left":
            x = self.location[0]
        if horizontal == "right":
            x = self.location[2]
        if horizontal == "middle":
            x = (self.location[0] + self.location[2]) /2
        if vertical == "top":
            y = self.location[1]
        if vertical == "bottom":
            y = self.location[3]
        if vertical == "middle":
            y = (self.location[1] + self.location[3]) /2
        return x,y
    
    def get_point(self, point_ratio):
        left_x, y = self.get_location("left", "bottom")
        right_x, y = self.get_location("right", "bottom")
        x = (right_x -left_x)*(point_ratio) + left_x
        return x,y
            
    
    def set_location(self,location):
        self.location = location
        
    def update_location(self, padding):
        return self.location
    

def plot_subject(Word, img, location):
    # create rectangle image
    word_tl = location
    img1 = ImageDraw.Draw(img)  
    img1.text(location, Word.text, font=fnt, fill = "black", anchor = "lt")

    bbox = img1.textbbox(word_tl, Word.text, font = fnt, spacing = 0)
    vert_line = [(bbox[2]+ box_pad, bbox[1]-box_pad), (bbox[2] + box_pad, bbox[3] + 100)]
    img1.line(vert_line, fill ="black", width = 2)
    hori_line = [(bbox[0]- 3 *box_pad, bbox[3]+box_pad), (bbox[2] + box_pad, bbox[3] + box_pad)]
    img1.line(hori_line, fill ="black", width = 2)
    Word.set_location([bbox[0]- 3* box_pad, bbox[1]-box_pad, bbox[2] + box_pad, bbox[3] + box_pad])
    return img

def plot_verb (Word, img, location):
    #create next part
    word_tl = location
    word_tl= (word_tl[0] + box_pad , word_tl[1] +box_pad)
    img1 = ImageDraw.Draw(img)  
    img1.text(word_tl, Word.text, font=fnt, fill = "black", anchor = "lt")
    bbox = img1.textbbox(word_tl, Word.text, font = fnt, spacing = 0)
    hori_line = [(bbox[0]- box_pad, bbox[3]+box_pad -8), (bbox[2] + 4* box_pad, bbox[3]+box_pad-8)]
    img1.line(hori_line, fill ="black", width = 2)
    Word.set_location([bbox[0] -box_pad, bbox[1]-box_pad, bbox[2] + 4 *box_pad, bbox[3] + box_pad- 8])
    return img

def translate(x, y):
    return np.array([[1, 0, x], [0, 1, y], [0, 0, 1]])


def rotate(angle):
    c, s = np.cos(angle), np.sin(angle)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def plot_adj(M,image, parent, point_ratio, text_size = 30):
    """Draw text at x,y and rotated angle radians on the given PIL image"""
    text = M.text
    x,y = parent.get_point(point_ratio)
    x+=20
    
    #angle = 0.872
    angle = 1.04
    img1 = ImageDraw.Draw(image) 
    text_x,text_y = img1.textsize(text, fnt)
    y-= 2
    m = np.matmul(translate(x, y), rotate(angle))
    transform = [m[0][0], m[0][1], m[0][2], m[1][0], m[1][1], m[1][2]]
    
    draw = aggdraw.Draw(image)
    draw.settransform(transform)
    draw.text((transform[0], transform[3]), text, agg_font)
    
    c = 0.4
    draw.line((0-0.3*text_x,0+text_y,0+ (1/0.7)* text_x, 0+text_y),aggdraw.Pen("black", 2))
    draw.settransform()
    
    bbox = img1.textbbox((x,y), text, font = fnt, spacing = 0)
    M.set_location([bbox[0]-box_pad, bbox[1]-box_pad, bbox[2] + box_pad, bbox[3] + box_pad- 8])
  
    draw.flush()

    return image

def plot_op(Word,image, parent):
    img1 = ImageDraw.Draw(image)
    word_tl=parent.get_location("middle", "bottom")
    word_tl = (word_tl[0], word_tl[1])
  
    img1.text(word_tl, Word.text, font=fnt, fill = "black", anchor = "lb")
    bbox = img1.textbbox(word_tl, Word.text, font = fnt, spacing = 2, anchor = "lb")
    hori_line = [(bbox[0]-25, bbox[3]), (bbox[2] +5 , bbox[3])]
    img1.line(hori_line, fill ="black", width = 2)
    Word.set_location((bbox[0] -25, bbox[1], bbox[2], bbox[3]))

    
    return image

def plot_DO(Word, img, parent):
    word_tl = parent.get_location("right", "bottom")
    word_tl= (word_tl[0] + box_pad, word_tl[1] - box_pad -20)
    img1 = ImageDraw.Draw(img)  
    img1.text(word_tl, Word.text, font=fnt, fill = "black", anchor = "lt")
    bbox = img1.textbbox(word_tl, Word.text, font = fnt, spacing = 0)
    vert_line = [parent.get_location("right", "top"), parent.get_location("right", "bottom")]
    img1.line(vert_line, fill ="black", width = 2)
    
    hori_line = [(bbox[0]-box_pad, bbox[3]+box_pad -8), (bbox[2] + 4*box_pad, bbox[3]+box_pad-8)]
    img1.line(hori_line, fill ="black", width = 2)
    Word.set_location([bbox[0]-box_pad, bbox[1]-box_pad, bbox[2] + 4*box_pad, bbox[3] + box_pad- 8])
    return img

def plot_IO(Word,parent, img):
    """Draw text at x,y and rotated angle radians on the given PIL image"""
    fake_text = "    (x)   "
    x,y = parent.get_point(1)
    angle = 0.872
    img1 = ImageDraw.Draw(img) 
    text_x,text_y = img1.textsize(fake_text, fnt)
    m = np.matmul(translate(x, y), rotate(angle))
    transform = [m[0][0], m[0][1], m[0][2], m[1][0], m[1][1], m[1][2]]
    
    draw = aggdraw.Draw(img)
    draw.settransform(transform)
    draw.text((transform[0], transform[3]), fake_text, agg_font)
    draw.line((0-0.2*text_x,0+text_y,0 + text_x, 0+text_y),aggdraw.Pen("black", 2))
    draw.settransform()
    draw.flush()
    
    bbox = img1.textbbox((x,y), fake_text, font = fnt, spacing = 0)
    Word.set_location([bbox[0], bbox[1], bbox[2], bbox[3]])
  
    #Add in the rest of it
    word_tl=Word.get_location("right", "bottom")
    word_tl = (word_tl[0] - 50, word_tl[1]+50)
    print(word_tl)
  
    img1.text(word_tl, Word.text, font=fnt, fill = "black", anchor = "lb")
    bbox = img1.textbbox(word_tl, Word.text, font = fnt, spacing = 2, anchor = "lb")
    hori_line = [(bbox[0]-25, bbox[3]), (bbox[2] +5 , bbox[3])]
    img1.line(hori_line, fill ="black", width = 2)
    Word.set_location((bbox[0] -25, bbox[1], bbox[2], bbox[3]))

    return img
    
    
def plot_CC(Word, img, parent_Word):
    pass
    

    
    
    
    
    