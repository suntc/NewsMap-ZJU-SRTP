#coding:utf-8
'''
Created on 2015-11-14

@author: sun
'''

import os
import nltk
from nltk import word_tokenize

#specify the JAVA_PATH, modify it according to your own PATH
java_path = 'F:/Java/jdk1.8.0_40/bin/java.exe'
os.environ['JAVAHOME'] = java_path

BASE_DIR = os.path.dirname(__file__)

def stanfordNE2BIO(tagged_sent):
    bio_tagged_sent = []
    prev_tag = "O"
    for token, tag in tagged_sent:
        if tag == "O":
            bio_tagged_sent.append((token,tag))
            prev_tag = tag
            continue
        if tag != "O" and prev_tag == "O":
            bio_tagged_sent.append((token,"B-"+tag))
            prev_tag = tag
        elif prev_tag != "O" and prev_tag == tag:
            bio_tagged_sent.append((token,"I-"+tag))
            prev_tag = tag
        elif prev_tag != "O" and prev_tag != tag:
            bio_tagged_sent.append((token,"B-"+tag))
            prev_tag = tag
    return bio_tagged_sent

def stanfordNE2tree(ne_tagged_sent):
    bio_tagged_sent = stanfordNE2BIO(ne_tagged_sent)
    sent_tokens, sent_ne_tags = zip(*bio_tagged_sent)#split tokens and tags into 2 tuples
    sent_pos_tags = [pos for token, pos in nltk.pos_tag(sent_tokens)]#add nltk's pos tag to the output
    #print "sent_pos_tags: ",sent_pos_tags
    sent_conlltags = [(token, pos, ne) for token, pos, ne in zip(sent_tokens, sent_pos_tags, sent_ne_tags)]
    #print "sent_colltags: ",sent_conlltags
    ne_tree = nltk.chunk.conlltags2tree(sent_conlltags)
    #print ne_tree
    return ne_tree
    
def chunk_stanfordNE(text):
    st = nltk.StanfordNERTagger(os.path.join(BASE_DIR,'stanford-ner-2015-04-20/classifiers/english.all.3class.distsim.crf.ser.gz'),os.path.join(BASE_DIR,'stanford-ner-2015-04-20/stanford-ner.jar'))
    ne_tagged_sent = st.tag(word_tokenize(text))
    tree = stanfordNE2tree(ne_tagged_sent)
    ne_in_sent = []
    for subtree in tree:
        #print subtree
        if type(subtree) == nltk.tree.Tree:
            ne_label = subtree.label()
            ne_string = " ".join([token for token, pos in subtree.leaves()])
            ne_in_sent.append((ne_string, ne_label))
    return ne_in_sent
