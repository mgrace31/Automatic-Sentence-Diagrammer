# -*- coding: utf-8 -*-
"""
Created on Wed Dec  7 12:38:42 2022

@author: mcg19
"""
import nltk
from nltk.corpus import treebank
from nltk import ParentedTree
from nltk import treetransforms
from nltk import induce_pcfg
from nltk.parse import pchart
from nltk import Nonterminal
from nltk.tag.mapping import tagset_mapping

#%%%

# extract productions from three trees and induce the PCFG
def create_parser():
    print("Induce PCFG grammar from treebank data:")
    treebank.tagged_sents(tagset="universal") 
    productions = []
    for item in treebank.fileids()[:]:
      for tree in treebank.parsed_sents(item):
        # perform optional tree transformations, e.g.:
        tree.collapse_unary(collapsePOS = False)# Remove branches A-B-C into A-B+C
        tree.chomsky_normal_form(horzMarkov = 2)# Remove A->(B,C,D) into A->B,C+D->D
        productions += tree.productions()    
    pcfg = induce_pcfg(Nonterminal("S"), productions)
    parser = nltk.ViterbiParser(pcfg)
    print("parser created")
    return parser


#%%

def parse_sentence(parser, sentence):
    words = nltk.word_tokenize(sentence)
    words=[word.lower() for word in words if word.isalpha()]
    tree = parser.parse(words)
    for t in tree:
        return ParentedTree.convert(t)
    
#%% CURRENT TRY
def filt_M(x):
    nouns = ["CD", "DT", "JJ", "JJR", "JJS", "LS", "PDT", "PRP$", "RB", "RBR", "RBS"]
    for n in nouns:
        if n in x.label():
            return n in x.label()
        
def is_adj(x):
    words = ["CD", "DT", "JJ", "JJR", "JJS","LS", "PDT", "PRP$"]
    return x.label() in words

def is_adv(x):
    words = ["RB", "RBR", "RBS"]
    return x.label() in words
    
def filter_VP(x):
    return "VP" in x.label()

def filt_subj(x):
    return "SBJ" in x.label()

def filt_N(x):
    nouns = ["PRP", "NN", "NNP", "NNPS", "NNS","VBG"]
    for n in nouns:
        if n == x.label():
            return n in x.label()

def filt_V(x):
    return "VB" in x.label() or "MD" in x.label()

def filt_PP(x):
    return "PP" == x.label()[0:2]
def filt_P(x):
    preps = ["TO", "IN"]
    for prep in preps:
        if prep in x.label():
            return prep in x.label()
def filt_NP(x):
    return "NP" in x.label()

def check_if_op(s):
    while s != None:
        if s.parent().label() == "PP":
            return True
        else:
            s = s.parent()
    return False

def already_in(x, mods):
    for i in mods.keys():
        if x in mods[i]:
            return True
    return False

modifiers = {}
def get_type(s):
    #expects to receive (word,pos):
    pos = s[1]
    if pos in ["CD", "DT", "JJ", "JJR", "JJS", "LS", "PDT", "PRP$", "RB", "RBR", "RBS","VBG"]:
        return "M"
    if pos in ["TO", "IN"]:
        return "P"
    if pos in ["NN", "NNP", "NNPS", "NNS", "PRP"]:
        return "N"
    if pos in ["MD", "VB", "VBD", "VBN", "VBP", "VBZ"]:
        return "V"
    else:
        print("Can't handle " + pos)
        
def get_basics(ptree):
    basics = {"S": None, "V":[], "IO": None, "DO":None}
    for child in ptree:
        if "SBJ" in child.label():
            subject = child
            while basics["S"] == None:
                for s_child in subject:
                    if "PP" not in s_child.label():
                        if s_child.height() == 2:
                            if get_type(s_child.pos()[0]) == "N":
                                basics["S"] = s_child.leaves()[0]
                        else:
                            subject = s_child
                            
    nouns = []
    for word in ptree.subtrees(filter = filter_VP):      
        for verb in word.subtrees(filter = filt_V):
            if verb.leaves()[0] not in basics["V"]:
                basics["V"].append(verb.leaves()[0])
        for noun in word.subtrees(filter = filt_N):
            if noun not in nouns:
                nouns.append(noun)
        for PP in word.subtrees(filter = filt_PP):
            for op in PP.subtrees(filter = filt_N):
                for noun in nouns:
                    if noun == op:
                        nouns.remove(noun)
    
    if len(nouns) >= 1:
        basics["DO"] = nouns[-1].pos()[0][0]
        if len(nouns) >= 2:
            basics["IO"] = nouns[0].pos()[0][0]
    
    basics["V"] = ' '.join(basics["V"])
    return basics

def get_mods(ptree,basics):
    mods = {}
    for word in ptree.subtrees(filter = filter_VP):      
        for prep in word.subtrees(filter = filt_P):
            prep_word = prep.leaves()[0]
            if prep_word not in mods.keys():
                if basics["V"] not in mods:
                    mods[basics["V"]] = {}
                    mods[basics["V"]][prep_word] = "P"  
                if prep_word not in mods:
                    mods[prep_word] = {}
            for PP in word.subtrees(filter = filt_PP):
                for noun in PP.subtrees(filter = filt_N):
                    if noun.height() == 2:
                        op = noun.leaves()[0]
                        mods[prep_word][op] = "op"
                for modifier in PP.subtrees(filter = filt_M):
                    if modifier.height() == 2:
                        mod_word = modifier.leaves()[0]
                        if op not in mods:
                            mods[op] = {}
                        mods[op][mod_word] = "M"
                        
        #Add in the Noun phrases from the other Verb Phrases : DO
        for NP in word.subtrees(filter = filt_NP):
            for modifier in NP.subtrees(filter = filt_M):
                if modifier.height() == 2:
                    mod_word = modifier.leaves()[0]
                    print("mod_word: " + mod_word)
                    if not already_in(mod_word, mods):
                        if is_adj(modifier):
                            if basics["DO"] != None:
                                if basics["DO"] not in mods:
                                    mods[basics["DO"]] = {}
                                mods[basics["DO"]][mod_word] = "M"
                        else:
                            if basics["V"] not in mods:
                                mods[basics["V"]] = {}
                            mods[basics["V"]][mod_word] = "M"
                            
      #IO              
        for modifier in word.subtrees(filter = filt_M):
            print(modifier)
            if modifier.height() == 2:
                mod_word = modifier.leaves()[0]
                if not already_in(mod_word, mods):
                    if is_adj(modifier):
                        if basics["DO"] != None:
                            if basics["DO"] not in mods:
                                mods[basics["DO"]] = {}
                            mods[basics["DO"]][mod_word] = "M"
                    else:
                        if basics["V"] not in mods:
                            mods[basics["V"]] = {}
                        mods[basics["V"]][mod_word] = "M"
            
        
                    
    for word in ptree.subtrees(filter = filt_subj):      
        for prep in word.subtrees(filter = filt_P):
            prep_word = prep.leaves()[0]
            if prep_word not in mods.keys():
                if basics["S"] not in mods:
                    mods[basics["S"]] = {}
                    mods[basics["S"]][prep_word] = "P"  
                if prep_word not in mods:
                    mods[prep_word] = {}
            for PP in word.subtrees(filter = filt_PP):
                for noun in PP.subtrees(filter = filt_N):
                    if noun.height() ==2:
                        op = noun.leaves()[0]
                        mods[prep_word][op] = "op"
                for modifier in PP.subtrees(filter = filt_M):
                    if modifier.height() == 2:
                        mod_word = modifier.leaves()[0]
                        if op not in mods:
                            mods[op] = {}
                        mods[op][mod_word] = "M"
        for modifier in word.subtrees(filter = filt_M):
            if modifier.height() == 2:
                mod_word = modifier.leaves()[0]
                if not already_in(mod_word, mods):
                    if basics["S"] not in mods:
                        mods[basics["S"]] = {}
                    mods[basics["S"]][mod_word] = "M"
        
        
    return mods

def run_converter(ptree):
    basics = get_basics(ptree)
    mods = get_mods(ptree,basics)
    return basics, mods
